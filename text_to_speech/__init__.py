import os
from typing import Optional

from text_to_speech.base import TextToSpeech
import utils.json_analysis as ja

def get_text_to_speech(tts: Optional[str] = None) -> TextToSpeech:
    if (
        not tts
        or (tts == "ELEVEN_LABS" and not ja.get_nested_value("config/params.json",["env","ELEVEN_LABS_API_KEY"], None))
        or (tts == "GOOGLE_TTS" and not ja.get_nested_value("config/params.json",["env","GOOGLE_APPLICATION_CREDENTIALS"], None))
        or (tts == "XTTS" and not ja.get_nested_value("config/params.json",["env","XTTS_API_KEY"], None))
    ):
        tts = "EDGE_TTS"
    if tts == "ELEVEN_LABS":
        from text_to_speech.elevenlabs import ElevenLabs

        ElevenLabs.initialize()
        return ElevenLabs.get_instance()
    elif tts == "GOOGLE_TTS":
        from text_to_speech.google_cloud_tts import GoogleCloudTTS

        GoogleCloudTTS.initialize()
        return GoogleCloudTTS.get_instance()
    elif tts == "EDGE_TTS":
        from text_to_speech.edge_tts import EdgeTTS

        EdgeTTS.initialize()
        return EdgeTTS.get_instance()
    elif tts == "XTTS":
        from audio.text_to_speech.xtts import XTTS

        XTTS.initialize()
        return XTTS.get_instance()
    else:
        raise NotImplementedError(f"Unknown text to speech engine: {tts}")
