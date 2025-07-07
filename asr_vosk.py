"""
ASR语音识别类，基于Vosk和PyAudio。
支持多热词拼音流式检测，每个热词有独立指针，实时检测拼音序列，匹配即返回信号。
"""
from vosk import Model, KaldiRecognizer
import pyaudio
import json
from pypinyin import lazy_pinyin
import threading
import numpy as np

class HotwordSequence:
    def __init__(self, name, pinyin_seq, signal):
        self.name = name
        self.pinyin_seq = pinyin_seq  # 期望的拼音序列
        self.signal = signal          # 匹配到后返回的信号
        self.pointer = 0             # 当前匹配到第几个拼音

    def reset(self):
        self.pointer = 0

    def match(self, pinyin_stream):
        """
        在拼音流中推进指针，若完全匹配则返回True，否则False。
        匹配失败时指针回到0。
        """
        # 思路说明：
        # 1. 遍历输入的拼音流，每次取一个拼音p。
        # 2. 如果p是空格，直接跳过（因为拼音流中可能有空格分隔）。
        # 3. 如果p等于当前热词序列指针所指的拼音（self.pinyin_seq[self.pointer]），指针前进一位。
        #    - 如果指针已经到达热词序列末尾，说明完全匹配，重置指针并返回True。
        # 4. 如果p不等于当前指针所指拼音，说明匹配失败，指针重置为0。
        #    - 但如果p正好等于热词序列的第一个拼音，指针设为1（支持“重叠”匹配）。
        # 5. 如果遍历结束都没有完全匹配，返回False。
        for p in pinyin_stream:
            if p == ' ':
                continue
            elif p == self.pinyin_seq[self.pointer]:
                self.pointer += 1
                if self.pointer == len(self.pinyin_seq):
                    self.reset()
                    return True
            else:
                self.reset()
                if p == self.pinyin_seq[0]:
                    self.pointer = 1
        return False

class AsrVosk:
    def __init__(self, model_path, hotwords_dict, sample_rate=16000):
        """
        model_path: 语音识别模型路径
        hotwords_dict: {热词: 信号值} 的字典
        sample_rate: 采样率，默认16000
        """
        self.model = Model(model_path)
        self.sample_rate = sample_rate
        self.rec = KaldiRecognizer(self.model, self.sample_rate)
        self.stream = None
        # 构建热词序列对象列表
        self.hotword_sequences = []
        for word, signal in hotwords_dict.items():
            pinyin_seq = lazy_pinyin(word)
            self.hotword_sequences.append(HotwordSequence(word, pinyin_seq, signal))

    def start(self):
        self.p = pyaudio.PyAudio() # 改到这里初始化音频设备
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=self.sample_rate, input=True, frames_per_buffer=4096)
        self.stream.start_stream()

    def stop(self):
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate() # 这里断开与音频设备的连接

    def listen_for_hotword(self):
        """
        阻塞式监听，实时检测拼音流，匹配到热词序列即返回信号。
        """
        self.start()
        try:
            while self.stream is not None:
                data = self.stream.read(4096)
                self.rec.AcceptWaveform(data) # 如果识别成功，则输出识别结果
                
                result = self.rec.PartialResult()
                try:
                    text = json.loads(result).get('partial', '')
                    print(f"中间结果：{text}")
                except Exception:
                    text = ''
                pinyin_stream = lazy_pinyin(text)
                print(f"拼音流：{pinyin_stream}")
                # 多热词并发检测
                for seq in self.hotword_sequences:
                    if seq.match(pinyin_stream):
                        self.rec.Reset() # 
                        self.stop()
                        return seq.signal
                # 如果Pinyin_stream超过15仍然没有识别到
                if len(pinyin_stream) > 15:
                    self.rec.Reset()
        finally:
            self.stop()

if __name__ == "__main__":
    # 示例用法：检测到"小心 小心"或"再见"时返回对应信号
    hotwords = {"小新小新": 1, "再见": 2}
    asr = AsrVosk("../models/vosk-model-small-cn-0.22", hotwords)
    print("请说话，等待检测热词……")
    signal = asr.listen_for_hotword()
    
    print(f"检测到热词，返回信号：{signal}") 
