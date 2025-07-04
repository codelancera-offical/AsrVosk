# 🚀 AsrVosk 热词检测：您的语音交互利器

还在为寻找一个**开源、鲁棒、精准**的热词检测方案而烦恼吗？`AsrVosk` 将是您的终极答案！

一个基于 [[Vosk]] 和 [[PyPinyin]] 的高性能、流式热词检测 Python 类，专为需要实时、准确识别特定语音命令或唤醒词的场景而设计。

## ✨ 功能特性

*   **多热词并发检测**：支持同时配置多个热词，每个热词独立追踪，互不干扰，实现高效并行检测。
*   **⚡ 实时流式匹配**：基于语音流的拼音序列进行实时检测，匹配成功即刻返回信号，响应速度快如闪电。
*   **🎯 高精度与鲁棒性**：利用 Vosk 的中间识别结果和 PyPinyin 的拼音转换，确保检测的准确性和对口音的适应性。
*   **🔄 智能重叠匹配**：即使热词部分重叠，也能灵活处理，提高检测的容错率和用户体验，避免漏检。
*   **💡 轻量高效**：采用单线程轮询机制，资源占用低，易于集成到现有项目中，维护成本极低。
*   **🗣️ 广泛应用场景**：完美适用于语音唤醒、命令词识别、智能助手触发、智能家居控制等需要精准短语检测的场景。

## ❓ 什么是热词检测？

热词检测（Hotword Detection），又称唤醒词检测或命令词识别，是指在连续的语音流中，实时、准确地识别出预设的特定短语或词汇。它是实现自然人机交互的关键技术，广泛应用于智能音箱、语音助手、智能家居控制、车载系统等领域，让设备能够“听懂”您的特定指令并做出响应。

## ⚙️ 工作原理

本库的核心在于其巧妙的流式拼音匹配机制：

1.  **语音转拼音**：利用 [[Vosk]] 模型实时获取语音的中间识别结果（`partial result`），并通过 [[pypinyin]] 库将其高效转换为拼音序列流。
2.  **独立指针追踪**：为每个预设的热词维护一个独立的“识别序列指针”。这个指针负责追踪当前语音流中已匹配到热词的第几个拼音。
3.  **实时匹配与响应**：当新的拼音进入流中时，所有热词的指针会同步向前推进。一旦某个热词的拼音序列被完全匹配，系统会立即返回预设的信号值。
4.  **智能回溯与重叠**：如果当前拼音无法匹配热词的下一个字符，该热词的指针会智能回溯到0，准备重新开始匹配。同时，系统支持热词的重叠匹配，确保在复杂语境下的鲁棒性。
5.  **高效单线程**：整个检测过程通过主循环轮询实现单线程并发，既保证了高效的资源利用，又简化了代码逻辑，易于理解和维护。

## 📦 安装

确保您已安装 Python 3.6+。您可以通过 pip 安装所有依赖：

```bash
pip install vosk pyaudio pypinyin
```

**注意**：您还需要下载并指定 Vosk 模型文件。例如，中文小模型 `vosk-model-small-cn-0.22`。您可以从 [Vosk 官方网站](https://alphacephei.com/vosk/models) 下载所需模型。

## 🚀 使用方法

### 热词格式

热词以 Python 字典形式传入 `AsrVosk` 类的构造函数。字典的 `key` 为您希望检测的中文热词字符串，`value` 为该热词被检测到后希望返回的任意信号值（例如整数、字符串等）。

```python
hotwords = {
    "小新小新": 1,
    "再见": 2,
    "你好世界": "hello_world_signal"
}
```

### 典型用法示例

以下是一个简单的示例，展示如何初始化 `AsrVosk` 并开始监听热词：

```python
from asr_vosk import AsrVosk
import os

# 1. 定义您的热词及其对应的信号值
hotwords = {
    "小新小新": 1,
    "再见": 2,
    "开始录音": 3
}

# 2. 指定 Vosk 模型路径
# 请确保您已下载模型文件，例如：https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip
# 并将其解压到指定路径，例如 'models/vosk-model-small-cn-0.22'
model_path = "../models/vosk-model-small-cn-0.22"
if not os.path.exists(model_path):
    print(f"错误：Vosk 模型未找到！请下载模型并放置在 {model_path}。")
    print("下载地址示例：https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip")
    exit()

# 3. 初始化 AsrVosk 实例
# 第一个参数是 Vosk 模型路径，第二个参数是热词字典
asr = AsrVosk(model_path, hotwords)

print("请说话，等待检测热词……")

try:
    # 4. 调用 listen_for_hotword() 方法开始监听
    # 该方法会阻塞，直到检测到热词并返回其对应的信号值
    signal = asr.listen_for_hotword()
    print(f"🎉 检测到热词！返回信号：{signal}")
except KeyboardInterrupt:
    print("\n程序已终止。")
except Exception as e:
    print(f"发生错误：{e}")
finally:
    # 5. 清理资源 (如果 AsrVosk 内部有资源需要释放，例如关闭麦克风流)
    # 假设 AsrVosk 类内部有 cleanup 方法，用于关闭 PyAudio 流等
    if hasattr(asr, 'cleanup'):
        asr.cleanup()
```

## 🤝 贡献

欢迎对本项目进行贡献！如果您有任何建议、bug 报告或功能请求，请随时提交 Issue 或 Pull Request。您的支持是项目持续改进的动力！
