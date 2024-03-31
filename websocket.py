import asyncio
import websockets
import json
import whisper
from pydub import AudioSegment
import soundfile as sf
from io import BytesIO
import numpy as np  # 确保导入 numpy
import openai


# # 加载 Whisper 模型
try:
    model = whisper.load_model("base", device="cuda")
except Exception as e:
    print(e)
    model = whisper.load_model("base", device="cpu")

async def recognize_audio(audio_bytes):
    # 使用 BytesIO 直接从字节数据创建 AudioSegment 对象，假定音频数据为 WAV 格式
    audio_segment = AudioSegment.from_file(BytesIO(audio_bytes), format="webm")
    audio_segment.export("output.wav", format="wav")
    # # 转换为单声道，以确保与 Whisper 模型兼容
    # audio_segment = audio_segment.set_channels(1)
    
    # # 将 AudioSegment 对象导出到字节对象中，以便使用 soundfile 读取
    # audio_bytes_io = BytesIO()
    # audio_segment.export(audio_bytes_io, format="wav")
    # audio_bytes_io.seek(0)
    
    # 使用 soundfile 读取 BytesIO 中的数据为一个 NumPy 数组
    # audio, _ = sf.read(audio_bytes_io, dtype='float32')
    # audio_segment.export("output.mp3", format="mp3")
    # 使用 Whisper 进行语音识别
    result = model.transcribe("output.wav")
    for segment in result["segments"]:
        print(segment["text"])
    return result['text']


# 假设你已经设置了你的 OpenAI API 密钥
openai.api_key = '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'
openai.proxy = {"http": "http://127.0.0.1:1080", "https": "http://127.0.0.1:1080"}
async def recognize_audio_openai(audio_bytes):
    # 将字节数据转换为音频数据，使用 pydub 来处理 webm 格式
    audio_segment = AudioSegment.from_file(BytesIO(audio_bytes), format="webm")
    # 转换为单声道，以确保与 Whisper 模型兼容
    audio_segment.export("output.wav", format="wav")
    # 将音频文件发送到 OpenAI 的 Whisper API 进行语音识别
    response = await openai.Whisper.create(
        audio="output.wav")
    
    # 打印和返回识别结果
    print(response["data"]["text"])
    return response["data"]["text"]

async def handler(websocket):
    async for message in websocket:
        print(len(message))
        if isinstance(message, bytes):
            transcription = await recognize_audio(message)
            await websocket.send(json.dumps({'type': 'transcription', 'data': transcription}))

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # 运行直到被取消

if __name__ == "__main__":
    asyncio.run(main())
