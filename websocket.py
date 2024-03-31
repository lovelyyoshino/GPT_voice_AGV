import asyncio
import websockets
import json
from whisper import load_model
from pydub import AudioSegment
import soundfile as sf
from io import BytesIO
import numpy as np  # 确保导入 numpy

# 加载 Whisper 模型
model = load_model("base", device="cuda")

async def recognize_audio(audio_bytes):
    # 将字节数据转换为音频数据，使用 pydub 来处理 webm 格式
    audio_segment = AudioSegment.from_file(BytesIO(audio_bytes), format="webm")
    # 转换为单声道，以确保与 Whisper 模型兼容
    audio_segment = audio_segment.set_channels(1)
    # 将 AudioSegment 对象导出到字节对象中
    audio_bytes_io = BytesIO()
    audio_segment.export(audio_bytes_io, format="wav")
    audio_bytes_io.seek(0)
    
    # 使用 soundfile 读取 BytesIO 中的数据为一个 NumPy 数组
    audio, _ = sf.read(audio_bytes_io)
    audio = audio.astype(np.float32)  # 将音频数据转换为 float32 类型
    
    # 使用 Whisper 进行语音识别，注意这里不再传递 sample_rate 参数
    result = model.transcribe(audio, temperature=0.0, beam_size=5,language="zh")
    print(result)
    return result['text']


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
