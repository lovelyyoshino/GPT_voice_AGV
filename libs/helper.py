import json
import os
import re
import uuid
import streamlit as st
import pandas as pd
from .custom import *
import copy
import io
from text_toolkit import text_toolkit
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain.chains.question_answering import load_qa_chain
from langchain_community.llms import OpenAI
from langchain.prompts import PromptTemplate, prompt
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import Document
import docx2txt
from bs4 import BeautifulSoup

def get_history_chats(path: str) -> list:
    if "apikey" in st.secrets:
        os.makedirs(path, exist_ok=True)
        files = [f for f in os.listdir(f'./{path}') if f.endswith('.json')]
        files_with_time = [(f, os.stat(f'./{path}/' + f).st_ctime) for f in files]
        sorted_files = sorted(files_with_time, key=lambda x: x[1], reverse=True)
        chat_names = [os.path.splitext(f[0])[0] for f in sorted_files]
        if len(chat_names) == 0:
            chat_names.append('New Chat_' + str(uuid.uuid4()))
    else:
        chat_names = ['New Chat_' + str(uuid.uuid4())]
    return chat_names


def save_data(path: str, file_name: str, history: list, paras: dict, contexts: dict, **kwargs):
    if not os.path.exists(path):
        os.makedirs(path)
    with open(f"./{path}/{file_name}.json", 'w', encoding='utf-8') as f:
        json.dump({"history": history, "paras": paras, "contexts": contexts, **kwargs}, f)


def remove_data(path: str, chat_name: str):
    try:
        os.remove(f"./{path}/{chat_name}.json")
    except FileNotFoundError:
        pass
    # 清除缓存
    try:
        st.session_state.pop('history' + chat_name)
        for item in ["context_select", "context_input", "context_level", *initial_content_all['paras']]:
            st.session_state.pop(item + chat_name + "value")
    except KeyError:
        pass


def load_data(path: str, file_name: str) -> dict:
    try:
        with open(f"./{path}/{file_name}.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        content = copy.deepcopy(initial_content_all)
        if "apikey" in st.secrets:
            with open(f"./{path}/{file_name}.json", 'w', encoding='utf-8') as f:
                f.write(json.dumps(content))
        return content


def show_each_message(message: str, role: str, idr: str, area=None):
    if area is None:
        area = [st.markdown] * 2
    if role == 'user':
        icon = user_svg
        name = user_name
        background_color = user_background_color
        data_idr = idr + "_user"
        class_name = 'user'
    else:
        icon = gpt_svg
        name = gpt_name
        background_color = gpt_background_color
        data_idr = idr + "_assistant"
        class_name = 'assistant'
    message = url_correction(message)
    area[0](f"\n<div class='avatar'>{icon}<h2>{name}：</h2></div>", unsafe_allow_html=True)
    area[1](
        f"""<div class='content-div {class_name}' data-idr='{data_idr}' style='background-color: {background_color};'>\n\n{message}""",
        unsafe_allow_html=True)


def show_messages(current_chat: str, messages: list):
    id_role = 0
    id_assistant = 0
    for each in messages:
        if each["role"] == "user":
            idr = id_role
            id_role += 1
        elif each["role"] == "assistant":
            idr = id_assistant
            id_assistant += 1
        else:
            idr = False
        if idr is not False:
            show_each_message(each["content"], each["role"], str(idr))
            if "open_text_toolkit_value" not in st.session_state or st.session_state["open_text_toolkit_value"]:
                st.session_state['delete_dict'][current_chat + ">" + str(idr)] = text_toolkit(
                    data_idr=str(idr) + '_' + each["role"])
        if each["role"] == "assistant":
            st.write("---")


# 根据context_level提取history
def get_history_input(history: list, level: int) -> list:
    if level != 0 and history:
        df_input = pd.DataFrame(history).query('role!="system"')
        df_input = df_input[-level * 2:]
        res = df_input.to_dict('records')
    else:
        res = []
    return res


# 去除#号右边的空格
# def remove_hashtag_right__space(text: str) -> str:
#     text = re.sub(r"(#+)\s*", r"\1", text)
#     return text


# 提取文本
def extract_chars(text: str, num: int) -> str:
    char_num = 0
    chars = ''
    for char in text:
        # 汉字算两个字符
        if '\u4e00' <= char <= '\u9fff':
            char_num += 2
        else:
            char_num += 1
        chars += char
        if char_num >= num:
            break
    return chars


@st.cache_data(max_entries=20, show_spinner=False)
def download_history(history: list):
    md_text = ""
    for msg in history:
        if msg['role'] == 'user':
            md_text += f'## {user_name}：\n{msg["content"]}\n'
        elif msg['role'] == 'assistant':
            md_text += f'## {gpt_name}：\n{msg["content"]}\n'
    output = io.BytesIO()
    output.write(md_text.encode('utf-8'))
    output.seek(0)
    return output


def filename_correction(filename: str) -> str:#去除文件名中的特殊字符
    pattern = r'[^\w\.-]'
    filename = re.sub(pattern, '', filename)
    return filename


def url_correction(text: str) -> str:
    pattern = r'((?:http[s]?://|www\.)(?:[a-zA-Z0-9]|[$-_\~#!])+)'
    text = re.sub(pattern, r' \g<1> ', text)
    return text


# Function to extract text from a PDF file
def pdf_to_text(pdf): 
    pdf_reader=PdfReader(pdf)
    text=''
    for page in pdf_reader.pages:
        text+=page.extract_text()
    return text 

def doc_to_text(doc):
    text = docx2txt.process(doc)
    return text

def md_to_text(md):
    with open(md, 'r', encoding='utf-8') as f:
        text=f.read()
    return text

def html_to_plaintext_doc(html_text, url: str) -> Document:
    soup = BeautifulSoup(html_text, features="lxml")
    for script in soup(["script", "style"]):
        script.extract()

    strings = '\n'.join([s.strip() for s in soup.stripped_strings])
    webpage_document = Document(page_content=strings, metadata={"source": url})
    return webpage_document

# Function to split text into chunks
def text_split_into_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=100,
            length_function=len,
            add_start_index=True)
    chunks=text_splitter.split_text(text)
    return chunks

# Function to save text chunks to Chroma DB
def save_to_chromadb(chunks,openai_api_key,CHROMA_PATH):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large",openai_api_key=openai_api_key)
    db = Chroma.from_texts(chunks, embeddings,persist_directory=CHROMA_PATH)
    db.persist()


# Function to process multiple PDF files into text and save them into Chroma DB
def multiple_pdfFiles_to_text(pdf_files,openai_api_key,CHROMA_PATH="chromaDB"):
    for pdf in pdf_files:
        if pdf.endswith('.pdf'):
            text=pdf_to_text(pdf)
        elif pdf.endswith('.txt'):
            with open(pdf, 'r', encoding='utf-8') as f:
                text=f.read()
        elif pdf.endswith('.docx'):
            text=doc_to_text(pdf)
        elif pdf.endswith('.doc'):
            text=doc_to_text(pdf)
        elif pdf.endswith('.md'):
            text=md_to_text(pdf)
        chunks=text_split_into_chunks(text)
        save_to_chromadb(chunks,openai_api_key,CHROMA_PATH)

# Function to retrieve the question-answering chain
def getting_chain(openai_api_key, model,prompt_template):
    prompt_template = prompt_template
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])  
    llm = ChatOpenAI(model=model,api_key=openai_api_key)
    chain = load_qa_chain(llm, chain_type="stuff",prompt=prompt)
    return chain

# Function to provide response to user's question
def user_query_response(question,pre_chat,openai_api_key,model,prompt_template,CHROMA_PATH="chromaDB"):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large",openai_api_key=openai_api_key)
    db=Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    docs = db.similarity_search(question)
    # print(docs)
    chain=getting_chain(openai_api_key, model,prompt_template)
    response = chain.run(input_documents=docs, question=question)
    return response

# st的markdown会错误渲染英文引号加英文字符，例如 :abc
# def colon_correction(text):
#     pattern = r':[a-zA-Z]'
#     if re.search(pattern, text):
#         text = text.replace(":", "&#58;")
#         pattern = r'`([^`]*)&#58;([^`]*)`|```([^`]*)&#58;([^`]*)```'
#         text = re.sub(pattern, lambda m: m.group(0).replace('&#58;', ':') if '&#58;' in m.group(0) else m.group(0),
#                       text)
#     return text
