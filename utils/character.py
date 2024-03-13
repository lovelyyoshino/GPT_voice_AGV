import datetime
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, JSON, String
from sqlalchemy.inspection import inspect

from utils.database_base import Base


class Character(Base):
    __tablename__ = "characters"

    id = Column(String(), primary_key=True, index=True, nullable=False)
    name = Column(String(1024), nullable=False)
    system_prompt = Column(String(262144), nullable=True)
    user_prompt = Column(String(262144), nullable=True)
    text_to_speech_use = Column(String(100), nullable=True)
    voice_id = Column(String(100), nullable=True)
    author_id = Column(String(100), nullable=True)
    visibility = Column(String(100), nullable=True)
    data = Column(JSON(), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)
    tts = Column(String(64), nullable=True)
    avatar_id = Column(String(100), nullable=True)
    background_text = Column(String(262144), nullable=True)
    rebyte_api_project_id = Column(String(100), nullable=True)
    rebyte_api_agent_id = Column(String(100), nullable=True)
    rebyte_api_version = Column(Integer(), nullable=True)

    def to_dict(self):
        return {
            c.key: getattr(self, c.key).isoformat()
            if isinstance(getattr(self, c.key), datetime.datetime)
            else getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs
        }

    def save(self, db):
        db.add(self)
        db.commit()


class CharacterRequest(BaseModel):
    name: str
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None
    tts: Optional[str] = None
    voice_id: Optional[str] = None
    visibility: Optional[str] = None
    data: Optional[dict] = None
    avatar_id: Optional[str] = None
    background_text: Optional[str] = None
    rebyte_api_project_id: Optional[str] = None
    rebyte_api_agent_id: Optional[str] = None
    rebyte_api_version: Optional[int] = None


class EditCharacterRequest(BaseModel):
    id: str
    name: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None
    tts: Optional[str] = None
    voice_id: Optional[str] = None
    visibility: Optional[str] = None
    data: Optional[dict] = None
    avatar_id: Optional[str] = None
    background_text: Optional[str] = None
    rebyte_api_project_id: Optional[str] = None
    rebyte_api_agent_id: Optional[str] = None
    rebyte_api_version: Optional[int] = None


class DeleteCharacterRequest(BaseModel):
    character_id: str


class GeneratePromptRequest(BaseModel):
    name: str
    background: Optional[str] = None


class GenerateHighlightRequest(BaseModel):
    context: str
    prompt: Optional[str] = None
