import asyncio
from dataclasses import field
from time import perf_counter
from typing import Callable, Optional, TypedDict

from langchain.schema import AIMessage, BaseMessage, HumanMessage, SystemMessage
from pydantic.dataclasses import dataclass
from starlette.websockets import WebSocket, WebSocketState
from sqlalchemy.orm import Session

from logger import get_logger


logger = get_logger(__name__)


@dataclass
class Character:
    character_id: str
    name: str
    llm_system_prompt: str
    llm_user_prompt: str
    source: str = ""
    location: str = ""
    voice_id: str = ""
    author_name: str = ""
    author_id: str = ""
    visibility: str = ""
    tts: Optional[str] = ""
    order: int = 10**9  # display order on the website
    data: Optional[dict] = None
    rebyte_api_project_id: Optional[str] = None
    rebyte_api_agent_id: Optional[str] = None
    rebyte_api_version: Optional[int] = None


@dataclass
class TranscriptSlice:
    id: str
    audio_id: str
    start: float
    end: float
    speaker_id: str
    text: str


@dataclass
class Transcript:
    id: str
    audio_bytes: bytes
    slices: list[TranscriptSlice]
    timestamp: float
    duration: float


class DiarizedSingleSegment(TypedDict):
    start: float
    end: float
    text: str
    speaker: str


class SingleWordSegment(TypedDict):
    word: str
    start: float
    end: float
    score: float


class WhisperXResponse(TypedDict):
    segments: list[DiarizedSingleSegment]
    language: str
    word_segments: list[SingleWordSegment]


class Singleton:
    _instances = {}

    @classmethod
    def get_instance(cls, *args, **kwargs):
        """Static access method."""
        if cls not in cls._instances:
            cls._instances[cls] = cls(*args, **kwargs)

        return cls._instances[cls]

    @classmethod
    def initialize(cls, *args, **kwargs):
        """Static access method."""
        if cls not in cls._instances:
            cls._instances[cls] = cls(*args, **kwargs)


class ConnectionManager(Singleton):
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"Client #{id(websocket)} left the chat")
        # await self.broadcast_message(f"Client #{id(websocket)} left the chat")

    async def send_message(self, message: str, websocket: WebSocket):
        if websocket.application_state == WebSocketState.CONNECTED:
            await websocket.send_text(message)

    async def broadcast_message(self, message: str):
        for connection in self.active_connections:
            if connection.application_state == WebSocketState.CONNECTED:
                await connection.send_text(message)


def get_connection_manager():
    return ConnectionManager.get_instance()


class Timer(Singleton):
    def __init__(self):
        self.start_time: dict[str, float] = {}
        self.elapsed_time = {}

    def start(self, id: str):
        self.start_time[id] = perf_counter()

    def log(self, id: str, callback: Optional[Callable] = None):
        if id in self.start_time:
            elapsed_time = perf_counter() - self.start_time[id]
            del self.start_time[id]
            if id in self.elapsed_time:
                self.elapsed_time[id].append(elapsed_time)
            else:
                self.elapsed_time[id] = [elapsed_time]
            if callback:
                callback()

    def report(self):
        for id, t in self.elapsed_time.items():
            logger.info(
                f"{id:<30s}: {sum(t)/len(t):.3f}s [{min(t):.3f}s - {max(t):.3f}s] "
                f"({len(t)} samples)"
            )

    def reset(self):
        self.start_time = {}
        self.elapsed_time = {}


def get_timer() -> Timer:
    return Timer.get_instance()


def timed(func):
    if asyncio.iscoroutinefunction(func):

        async def async_wrapper(*args, **kwargs):
            timer = get_timer()
            timer.start(func.__qualname__)
            result = await func(*args, **kwargs)
            timer.log(func.__qualname__)
            return result

        return async_wrapper
    else:

        def sync_wrapper(*args, **kwargs):
            timer = get_timer()
            timer.start(func.__qualname__)
            result = func(*args, **kwargs)
            timer.log(func.__qualname__)
            return result

        return sync_wrapper


def task_done_callback(task: asyncio.Task):
    exception = task.exception()
    if exception:
        logger.error(f"Error in task {task.get_name()}: {exception}")
