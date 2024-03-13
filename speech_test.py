from speech_to_text import get_speech_to_text, SpeechToText
from text_to_speech import get_text_to_speech, TextToSpeech
from character_catalog.catalog_manager import (
    CatalogManager,
    get_catalog_manager,
)

import speech_recognition as sr
import asyncio
import os
import uuid
import time
import asyncio

# 运行主函数
async def main():
    catalog_manager = CatalogManager.initialize()
    character = catalog_manager.get_character("bruce_wayne")
    print(character.name, character.id,character.llm_system_prompt)
    # text_to_speech = get_text_to_speech()
    # audio_bytes = await text_to_speech.generate_audio(text="你好，我是培立，很高兴认识你。", voice_id="en-US-ChristopherNeural", language="zh-CN")

    # print(f"Generated audio bytes: {audio_bytes[:20]}...")

    # 创建一个识别器实例
    recognizer = sr.Recognizer()
    # 读取 WAV 文件
    wav_path = 'test.wav'  # 更改为你的 WAV 文件路径
    with open(wav_path, 'rb') as f:
        audio_bytes = f.read()
    speech_to_text = get_speech_to_text()

    # 尝试使用 Google Web Speech API 进行语音识别
    try:
        # 默认使用英语识别，如果是其他语言，可以通过修改 recognize_google 函数的 language 参数来设置
        text: str = (
                    await asyncio.to_thread(
                        speech_to_text.transcribe,
                        audio_bytes,
                        platform="byte",
                        prompt="Elon Musk",
                        language="zh-CN",
                    )
                ).strip()
        # text = speech_to_text.transcribe(audio_bytes, platform="byte", language="zh-CN")
        print(f"Recognized text: {text}")
    except sr.UnknownValueError:
        # 语音识别不清楚
        print("Google Web Speech API could not understand audio")
    except sr.RequestError as e:
        # 请求 Google Web Speech API 出错
        print(f"Could not request results from Google Web Speech API; {e}")


# 运行主函数
asyncio.run(main())