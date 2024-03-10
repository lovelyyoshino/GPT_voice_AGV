import os
from dotenv import load_dotenv

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import utils.json_analysis as ja
from utils.logger import get_logger


load_dotenv()
logger = get_logger(__name__)


def get_chroma(embedding: bool = True):
    if embedding:
        openai_api_key = ja.get_nested_value("config/params.json",["env","OPENAI_API_KEY"], None)
        if not openai_api_key:
            raise Exception("OPENAI_API_KEY is required to generate embeddings")
        if ja.get_nested_value("config/params.json",["env","OPENAI_API_TYPE"], "openai") == "azure":
            embedding_function = OpenAIEmbeddings(
                openai_api_key=openai_api_key,
                deployment=ja.get_nested_value("config/params.json",["env“,”OPENAI_API_EMBEDDING_DEPLOYMENT_NAME"], "text-embedding-ada-002"),
                chunk_size=1,
            )
        else:
            embedding_function = OpenAIEmbeddings(openai_api_key=openai_api_key)
    else:
        embedding_function = None

    chroma = Chroma(
        collection_name="llm",
        embedding_function=embedding_function,
        persist_directory="./chroma.db",
    )
    return chroma
