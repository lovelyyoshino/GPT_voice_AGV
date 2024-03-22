import os.path

from libs.helper import *
import streamlit as st
import uuid
import pandas as pd
import openai
from requests.models import ChunkedEncodingError
from streamlit.components import v1
from voice_toolkit import voice_toolkit
import time

if "apibase" in st.secrets:
    openai.api_base = st.secrets["apibase"]
else:
    os.environ["http_proxy"] = st.secrets["proxies"]
    os.environ["https_proxy"] = st.secrets["proxies"]
    openai.proxy = {"http": st.secrets["proxies"], "https": st.secrets["proxies"]}
    openai.api_base = "https://api.openai.com/v1"
    # openai.proxy = {'http': st.secrets["proxies"], 'https': st.secrets["proxies"]}

st.set_page_config(page_title="ChatGPT Assistant", layout="wide", page_icon="🤖")
# 自定义元素样式
st.markdown(css_code, unsafe_allow_html=True)

if "initial_settings" not in st.session_state:#初始化设置
    # 历史聊天窗口
    st.session_state["path"] = "history_chats_file"#聊天记录保存路径
    st.session_state["history_chats"] = get_history_chats(st.session_state["path"])#获取聊天记录
    # ss参数初始化
    st.session_state["delete_dict"] = {}#删除字典
    st.session_state["delete_count"] = 0#删除计数
    st.session_state["voice_flag"] = ""#语音标志
    st.session_state["user_voice_value"] = ""#用户语音值
    st.session_state["error_info"] = ""#错误信息
    st.session_state["current_chat_index"] = 0#当前聊天索引
    st.session_state["user_input_content"] = ""#用户输入内容
    # 读取全局设置，如果存在则加载
    if os.path.exists("./set.json"):
        with open("./set.json", "r", encoding="utf-8") as f:
            data_set = json.load(f)
        for key, value in data_set.items():
            st.session_state[key] = value
    # 设置完成
    st.session_state["initial_settings"] = True

with st.sidebar:#侧边栏
    side_title="聊天记录"
    st.sidebar.markdown(f"\n<div class='avatar'>{gpt_svg}<h1>{side_title}</h1></div>", unsafe_allow_html=True)
    # 创建容器的目的是配合自定义组件的监听操作
    chat_container = st.container()
    with chat_container:#聊天容器
        current_chat = st.radio(
            label="历史聊天窗口",
            format_func=lambda x: x.split("_")[0] if "_" in x else x,
            options=st.session_state["history_chats"],
            label_visibility="collapsed",
            index=st.session_state["current_chat_index"],
            key="current_chat"
            + st.session_state["history_chats"][st.session_state["current_chat_index"]],
            # on_change=current_chat_callback  # 此处不适合用回调，无法识别到窗口增减的变动
        )#创建一个单选框，用于选择聊天窗口
    st.write("---")


# 数据写入文件
def write_data(new_chat_name=current_chat):
    if "apikey" in st.secrets:
        st.session_state["paras"] = {
            "temperature": st.session_state["temperature" + current_chat],
            "top_p": st.session_state["top_p" + current_chat],
            "presence_penalty": st.session_state["presence_penalty" + current_chat],
            "frequency_penalty": st.session_state["frequency_penalty" + current_chat],
        }#将参数保存到paras中
        st.session_state["contexts"] = {
            "context_select": st.session_state["context_select" + current_chat],
            "context_input": st.session_state["context_input" + current_chat],
            "context_level": st.session_state["context_level" + current_chat],
        }#将上下文保存到contexts中
        save_data(
            st.session_state["path"],
            new_chat_name,
            st.session_state["history" + current_chat],
            st.session_state["paras"],
            st.session_state["contexts"],
        )#保存数据

# 重命名文件
def reset_chat_name_fun(chat_name):
    chat_name = chat_name + "_" + str(uuid.uuid4())#给聊天窗口命名
    new_name = filename_correction(chat_name)#文件名纠正
    current_chat_index = st.session_state["history_chats"].index(current_chat)#获取当前聊天索引
    st.session_state["history_chats"][current_chat_index] = new_name#将新的聊天窗口名字赋值给当前聊天索引
    st.session_state["current_chat_index"] = current_chat_index#将当前聊天索引赋值给当前聊天索引
    # 写入新文件
    write_data(new_name)
    # 转移数据
    st.session_state["history" + new_name] = st.session_state["history" + current_chat]
    for item in [
        "context_select",
        "context_input",
        "context_level",
        *initial_content_all["paras"],
    ]:#遍历参数
        st.session_state[item + new_name + "value"] = st.session_state[
            item + current_chat + "value"
        ]
    remove_data(st.session_state["path"], current_chat)#删除当前聊天窗口

# 创建新的聊天窗口
def create_chat_fun():
    st.session_state["history_chats"] = [
        "New Chat_" + str(uuid.uuid4())
    ] + st.session_state["history_chats"]#创建一个新的聊天窗口
    st.session_state["current_chat_index"] = 0

# 删除聊天窗口
def delete_chat_fun():
    if len(st.session_state["history_chats"]) == 1:
        chat_init = "New Chat_" + str(uuid.uuid4())#设置初始聊天窗口
        st.session_state["history_chats"].append(chat_init)#将初始聊天窗口添加到聊天窗口列表中
    pre_chat_index = st.session_state["history_chats"].index(current_chat)#获取当前聊天索引
    if pre_chat_index > 0:
        st.session_state["current_chat_index"] = (
            st.session_state["history_chats"].index(current_chat) - 1
        )#将当前聊天索引赋值给当前聊天索引
    else:
        st.session_state["current_chat_index"] = 0
    st.session_state["history_chats"].remove(current_chat)
    remove_data(st.session_state["path"], current_chat)#删除当前聊天窗口

# 保存设置
def save_set(arg):
    st.session_state[arg + "_value"] = st.session_state[arg]
    if "apikey" in st.secrets:
        with open("./set.json", "w", encoding="utf-8") as f:
            json.dump(
                {
                    "open_text_toolkit_value": st.session_state["open_text_toolkit"],
                    "open_voice_toolkit_value": st.session_state["open_voice_toolkit"],
                    "hand_free_toolkit_value": st.session_state["hand_free_toolkit"],
                },
                f,
            )#将设置保存到set.json文件中


with st.sidebar:#侧边栏
    c1, c2 = st.columns(2)
    create_chat_button = c1.button(
        "新建", use_container_width=True, key="create_chat_button"
    )#创建一个新建按钮
    if create_chat_button:
        create_chat_fun()#调用创建新的聊天窗口函数
        st.rerun()#重新渲染页面

    delete_chat_button = c2.button(
        "删除", use_container_width=True, key="delete_chat_button"
    )
    if delete_chat_button:
        delete_chat_fun()#调用删除聊天窗口函数
        st.rerun()

with st.sidebar:#侧边栏
    if ("set_chat_name" in st.session_state) and st.session_state[
        "set_chat_name"
    ] != "":#如果set_chat_name在ss中且不为空
        reset_chat_name_fun(st.session_state["set_chat_name"])#调用重命名文件函数
        st.session_state["set_chat_name"] = ""#将set_chat_name赋值为空
        st.rerun()#重新渲染页面

    st.write("\n")
    st.write("\n")
    st.text_input("设定窗口名称：", key="set_chat_name", placeholder="点击输入")
    st.selectbox(
        "选择模型：", index=0, options=["gpt-3.5-turbo-0125","gpt-3.5-turbo-1106","gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k-0613",
               "gpt-4", "gpt-4-0613", "gpt-4-32k", "gpt-4-32k-0613", "gpt-3.5-turbo-1106"], key="select_model"
    )#创建一个选择框，用于选择模型
    st.write("\n")
    st.caption(
        """
    - 双击页面直接定位输入栏
    - Ctrl + Enter 快捷提交问题
    - 如果选择使用hand free模式，可以直接说话，停止说话后会自动提交
    """
    )#创建一个标题，用于提示信息
    st.write("\n")
    if "apikey_input" in st.secrets:
        dbapi_key = st.session_state["apikey_input"]
    # 配置临时apikey，此时不会留存聊天记录，适合公开使用
    elif "apikey_tem" in st.secrets:
        dbapi_key = st.secrets["apikey_tem"]
    # 注：当st.secrets中配置apikey后将会留存聊天记录，即使未使用此apikey
    else:
        dbapi_key = st.secrets["apikey"]
    #支持上传pdf,doc,docx,txt,md文件
    all_files = st.file_uploader("上传文件", type=["pdf", "doc", "docx", "txt", "md"], accept_multiple_files=True)
    
    if all_files is not None:  # Process PDF files if uploaded
        multiple_pdfFiles_to_text(all_files,dbapi_key)

    if "hand_free_toolkit_value" in st.session_state:#如果hand_free_toolkit_value在ss中，这个是用于判断是否开启自动语音输入。默认是false
        default = st.session_state["hand_free_toolkit_value"]
    else:
        default = False
    st.checkbox(
        "开启自动语音输入(需要在比较安静的环境下使用)",
        value=default,
        key="hand_free_toolkit",
        on_change=save_set,
        args=("hand_free_toolkit",),
    )#创建一个复选框，用于选择是否开启自动语音输入

# 加载数据
if "history" + current_chat not in st.session_state:
    for key, value in load_data(st.session_state["path"], current_chat).items():#遍历加载数据
        if key == "history":
            st.session_state[key + current_chat] = value#将value赋值给ss中的key+current_chat
        else:
            for k, v in value.items():
                st.session_state[k + current_chat + "value"] = v#将v赋值给ss中的k+current_chat+value

# 保证不同chat的页面层次一致，否则会导致自定义组件重新渲染
container_show_messages = st.container()#创建一个容器
container_show_messages.write("")
# 对话展示
with container_show_messages:
    if st.session_state["history" + current_chat]:#如果history+current_chat在ss中
        show_messages(current_chat, st.session_state["history" + current_chat])#展示消息

# 核查是否有对话需要删除
if any(st.session_state["delete_dict"].values()):
    for key, value in st.session_state["delete_dict"].items():#遍历删除字典
        try:
            deleteCount = value.get("deleteCount")
        except AttributeError:
            deleteCount = None
        if deleteCount == st.session_state["delete_count"]:#如果deleteCount等于ss中的delete_count
            delete_keys = key
            st.session_state["delete_count"] = deleteCount + 1
            delete_current_chat, idr = delete_keys.split(">")
            df_history_tem = pd.DataFrame(
                st.session_state["history" + delete_current_chat]
            )#将ss中的history+delete_current_chat转换为DataFrame
            df_history_tem.drop(
                index=df_history_tem.query("role=='user'").iloc[[int(idr)], :].index,
                inplace=True,
            )#删除用户
            df_history_tem.drop(
                index=df_history_tem.query("role=='assistant'")
                .iloc[[int(idr)], :]
                .index,
                inplace=True,
            )#删除助手
            st.session_state["history" + delete_current_chat] = df_history_tem.to_dict(
                "records"
            )#将df_history_tem转换为字典
            write_data()#写入数据
            st.rerun()

# 保存设置
def callback_fun(arg):
    # 连续快速点击新建与删除会触发错误回调，增加判断
    if ("history" + current_chat in st.session_state) and (
        "frequency_penalty" + current_chat in st.session_state
    ):
        write_data()
        st.session_state[arg + current_chat + "value"] = st.session_state[
            arg + current_chat
        ]

# 清空聊天记录
def clear_button_callback():
    st.session_state["history" + current_chat] = []
    write_data()

# 删除所有窗口
def delete_all_chat_button_callback():
    if "apikey" in st.secrets:
        folder_path = st.session_state["path"]
        file_list = os.listdir(folder_path)
        for file_name in file_list:
            file_path = os.path.join(folder_path, file_name)
            if file_name.endswith(".json") and os.path.isfile(file_path):
                os.remove(file_path)
    st.session_state["current_chat_index"] = 0
    st.session_state["history_chats"] = ["New Chat_" + str(uuid.uuid4())]



# 输入内容展示
area_user_svg = st.empty()
area_user_content = st.empty()
# 回复展示
area_gpt_svg = st.empty()
area_gpt_content = st.empty()
# 报错展示
area_error = st.empty()

st.write("\n")
st.header("SHINE AGV Assistant")
tap_input, tap_context, tap_model, tab_func = st.tabs(
    ["💬 聊天", "🗒️ 预设", "⚙️ 模型", "🛠️ 功能"]
)#创建一个标签页

# 预设窗口，包含上下文和模型参数
with tap_context:
    set_context_list = list(set_context_all.keys())
    context_select_index = set_context_list.index(
        st.session_state["context_select" + current_chat + "value"]
    )#获取上下文索引，这里st.session_state["context_select" + current_chat + "value"]是一个字符串,在set_context_list中找到这个字符串的索引
    st.selectbox(
        label="选择上下文",
        options=set_context_list,
        key="context_select" + current_chat,
        index=context_select_index,
        on_change=callback_fun,
        args=("context_select",),
    )#创建一个选择框，用于选择上下文
    st.caption(set_context_all[st.session_state["context_select" + current_chat]])#创建一个标题，用于展示上下文的内容

    st.text_area(
        label="补充或自定义上下文：",
        key="context_input" + current_chat,
        value=st.session_state["context_input" + current_chat + "value"],
        on_change=callback_fun,
        args=("context_input",),
    )#创建一个文本输入框，用于输入上下文

# 模型参数
with tap_model:
    st.markdown("OpenAI API Key (可选)")
    st.text_input(
        "OpenAI API Key (可选)",
        type="password",
        key="apikey_input",
        label_visibility="collapsed",
    )#创建一个文本输入框，用于输入OpenAI API Key
    st.caption(
        "此Key仅在当前网页有效，且优先级高于Secrets中的配置，仅自己可用，他人无法共享。[官网获取](https://platform.openai.com/account/api-keys)"
    )

    st.markdown("包含对话次数：")
    st.slider(
        "Context Level",
        0,
        10,
        st.session_state["context_level" + current_chat + "value"],
        1,
        on_change=callback_fun,
        key="context_level" + current_chat,
        args=("context_level",),
        help="表示每次会话中包含的历史对话次数，预设内容不计算在内。",
    )#创建一个滑块，用于选择包含对话次数

    st.markdown("模型参数：")
    st.slider(
        "Temperature",
        0.0,
        2.0,
        st.session_state["temperature" + current_chat + "value"],
        0.1,
        help="""在0和2之间，应该使用什么样的采样温度？较高的值（如0.8）会使输出更随机，而较低的值（如0.2）则会使其更加集中和确定性。
          我们一般建议只更改这个参数或top_p参数中的一个，而不要同时更改两个。""",
        on_change=callback_fun,
        key="temperature" + current_chat,
        args=("temperature",),
    )#创建一个滑块，用于选择温度
    st.slider(
        "Top P",
        0.1,
        1.0,
        st.session_state["top_p" + current_chat + "value"],
        0.1,
        help="""一种替代采用温度进行采样的方法，称为“基于核心概率”的采样。在该方法中，模型会考虑概率最高的top_p个标记的预测结果。
          因此，当该参数为0.1时，只有包括前10%概率质量的标记将被考虑。我们一般建议只更改这个参数或采样温度参数中的一个，而不要同时更改两个。""",
        on_change=callback_fun,
        key="top_p" + current_chat,
        args=("top_p",),
    )#创建一个滑块，用于选择top_p
    st.slider(
        "Presence Penalty",
        -2.0,
        2.0,
        st.session_state["presence_penalty" + current_chat + "value"],
        0.1,
        help="""该参数的取值范围为-2.0到2.0。正值会根据新标记是否出现在当前生成的文本中对其进行惩罚，从而增加模型谈论新话题的可能性。""",
        on_change=callback_fun,
        key="presence_penalty" + current_chat,
        args=("presence_penalty",),
    )#创建一个滑块，用于选择presence_penalty
    st.slider(
        "Frequency Penalty",
        -2.0,
        2.0,
        st.session_state["frequency_penalty" + current_chat + "value"],
        0.1,
        help="""该参数的取值范围为-2.0到2.0。正值会根据新标记在当前生成的文本中的已有频率对其进行惩罚，从而减少模型直接重复相同语句的可能性。""",
        on_change=callback_fun,
        key="frequency_penalty" + current_chat,
        args=("frequency_penalty",),
    )#创建一个滑块，用于选择frequency_penalty
    st.caption(
        "[官网参数说明](https://platform.openai.com/docs/api-reference/completions/create)"
    )

# 功能组件
with tab_func:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.button("清空聊天记录", use_container_width=True, on_click=clear_button_callback)
    with c2:
        btn = st.download_button(
            label="导出聊天记录",
            data=download_history(st.session_state["history" + current_chat]),
            file_name=f'{current_chat.split("_")[0]}.md',
            mime="text/markdown",
            use_container_width=True,
        )
    with c3:
        st.button(
            "删除所有窗口", use_container_width=True, on_click=delete_all_chat_button_callback
        )

    st.write("\n")
    st.markdown("自定义功能：")
    c1, c2 = st.columns(2)#自定义功能，创建两个按钮
    with c1:#第一个按钮默认为
        if "open_text_toolkit_value" in st.session_state:
            default = st.session_state["open_text_toolkit_value"]#如果open_text_toolkit_value在ss中
        else:
            default = True#否则默认为True
        st.checkbox(
            "开启文本下的功能组件",
            value=default,
            key="open_text_toolkit",
            on_change=save_set,
            args=("open_text_toolkit",),
        )#创建一个复选框，将值保存到ss中
    with c2:
        if "open_voice_toolkit_value" in st.session_state:
            default = st.session_state["open_voice_toolkit_value"]
        else:
            default = True
        st.checkbox(
            "开启语音输入组件",
            value=default,
            key="open_voice_toolkit",
            on_change=save_set,
            args=("open_voice_toolkit",),
        )

# 输入框
with tap_input:

    def input_callback():#输入回调
        if st.session_state["user_input_area"] != "":
            # 修改窗口名称
            user_input_content = st.session_state["user_input_area"]
            df_history = pd.DataFrame(st.session_state["history" + current_chat])
            if df_history.empty or len(df_history.query('role!="system"')) == 0:
                new_name = extract_chars(user_input_content, 18)
                reset_chat_name_fun(new_name)

    with st.form("input_form", clear_on_submit=True):#创建一个表单
        user_input = st.text_area(
            "**输入：**",
            key="user_input_area",
            help="内容将以Markdown格式在页面展示，建议遵循相关语言规范，同样有利于GPT正确读取，例如："
            "\n- 代码块写在三个反引号内，并标注语言类型"
            "\n- 以英文冒号开头的内容或者正则表达式等写在单反引号内",
            value=st.session_state["user_voice_value"],
        )#创建一个文本输入框，用于输入内容
        submitted = st.form_submit_button(
            "确认提交", use_container_width=True, on_click=input_callback
        )#创建一个提交按钮
    if submitted:
        st.session_state["user_input_content"] = user_input#将user_input赋值给ss中的user_input_content
        st.session_state["user_voice_value"] = ""
        st.rerun()

    if (
        "open_voice_toolkit_value" not in st.session_state
        or st.session_state["open_voice_toolkit_value"] 
        or "hand_free_toolkit_value" not in st.session_state
        or st.session_state["hand_free_toolkit_value"]
    ):  # 如果没有被点击过或者被点击过且值为True
        # 语音输入功能
        # voice_result = voice_toolkit()
        # 调用自定义组件，并传递录音状态
        if "hand_free_toolkit_value" not in st.session_state:
            voice_result = False
        else:
            print("hand_free_toolkit_value:",st.session_state["hand_free_toolkit_value"])
            voice_result = voice_toolkit(is_recording=st.session_state["hand_free_toolkit_value"])
        # voice_result会保存最后一次结果
        if (
            voice_result and voice_result["voice_result"]["flag"] == "interim"
        ) or st.session_state["voice_flag"] == "interim":#如果voice_result不为空且voice_result的flag为interim
            st.session_state["voice_flag"] = "interim"
            st.session_state["user_voice_value"] = voice_result["voice_result"]["value"]
            print("user_voice_value:",st.session_state["user_voice_value"])
            if voice_result["voice_result"]["flag"] == "final":#如果voice_result的flag为final
                st.session_state["voice_flag"] = "final"
                # 检查是否开启了hand free模式
                if st.session_state["hand_free_toolkit_value"]:
                    time.sleep(1)
                    input_callback()  # 手动调用处理函数
                    st.session_state["user_input_content"] = st.session_state["user_voice_value"]
                    st.session_state["user_voice_value"] = ""  # 清除语音输入值
                    st.rerun()  # 重新渲染页面
                else:
                    st.rerun()  # 如果不在hand free模式下，仍然需要重新渲染以更新状态

# 获取模型输入
def get_model_input():
    # 需输入的历史记录
    context_level = st.session_state["context_level" + current_chat]
    history = get_history_input(
        st.session_state["history" + current_chat], context_level
    ) + [{"role": "user", "content": st.session_state["pre_user_input_content"]}]#获取历史记录
    for ctx in [
        st.session_state["context_input" + current_chat],
        set_context_all[st.session_state["context_select" + current_chat]],
    ]:#遍历上下文
        if ctx != "":
            history = [{"role": "system", "content": ctx}] + history
    # 设定的模型参数
    paras = {
        "temperature": st.session_state["temperature" + current_chat],
        "top_p": st.session_state["top_p" + current_chat],
        "presence_penalty": st.session_state["presence_penalty" + current_chat],
        "frequency_penalty": st.session_state["frequency_penalty" + current_chat],
    }
    return history, paras


# 获取模型输入
def get_twice_model_input(idx_content):
    # 需输入的历史记录
    context_level = st.session_state["context_level" + current_chat]
    history = get_history_input(
        st.session_state["history" + current_chat], context_level
    ) + [{"role": "user", "content": st.session_state["pre_user_input_content"]}]#获取历史记录
    for ctx in [
        st.session_state["context_input" + current_chat],
        set_context_all[idx_content],
    ]:#遍历上下文
        if ctx != "":
            history = [{"role": "system", "content": ctx}] + history
    # 设定的模型参数
    paras = {
        "temperature": st.session_state["temperature" + current_chat],
        "top_p": st.session_state["top_p" + current_chat],
        "presence_penalty": st.session_state["presence_penalty" + current_chat],
        "frequency_penalty": st.session_state["frequency_penalty" + current_chat],
    }
    return history, paras


if st.session_state["user_input_content"] != "":#如果user_input_content不为空,则认为用户已经输入
    if "r" in st.session_state:
        st.session_state.pop("r")
        st.session_state[current_chat + "report"] = ""
    st.session_state["pre_user_input_content"] = st.session_state["user_input_content"]
    st.session_state["user_input_content"] = ""
    # 临时展示
    show_each_message(
        st.session_state["pre_user_input_content"],
        "user",
        "tem",
        [area_user_svg.markdown, area_user_content.markdown],
    )
    # 模型输入
    history_need_input, paras_need_input = get_model_input()
    # 调用接口
    with st.spinner("🤔"):
        try:
            if apikey := st.session_state["apikey_input"]:
                openai.api_key = apikey
            # 配置临时apikey，此时不会留存聊天记录，适合公开使用
            elif "apikey_tem" in st.secrets:
                openai.api_key = st.secrets["apikey_tem"]
            # 注：当st.secrets中配置apikey后将会留存聊天记录，即使未使用此apikey
            else:
                openai.api_key = st.secrets["apikey"]
            
            set_context_list = list(set_context_all.keys())
            context_select_index = set_context_list.index(
                        st.session_state["context_select" + current_chat + "value"])
            
            num =0
            if context_select_index == 0:# 代表是需要从头开始理解
                while num > 13 or num < 1:
                    r = openai.ChatCompletion.create(
                        model=st.session_state["select_model"],
                        messages=history_need_input,
                        stream=True,
                        **paras_need_input,
                    )
                    respone_msg = ""
                    for e in r:
                        if "content" in e["choices"][0]["delta"]:
                            respone_msg += e["choices"][0]["delta"]["content"]
                    #找到回复中的数字，范围为1-13
                    num = re.findall(r"\d+", respone_msg)
                    if len(num) > 0:
                        num = int(num[0])
                        if num > 0 and num < 14:
                            index_contect = set_context_list[num]
                            history_need_input, paras_need_input = get_twice_model_input(index_contect)
                            break
                    else:
                        num = 0
            # print("context_select_index:",context_select_index)
            if context_select_index > 13:#这个代表不在指令集里面，需要借助chromaDB回答问题
                if apikey := st.session_state["apikey_input"]:
                    dbapi_key = apikey
                # 配置临时apikey，此时不会留存聊天记录，适合公开使用
                elif "apikey_tem" in st.secrets:
                    dbapi_key = st.secrets["apikey_tem"]
                # 注：当st.secrets中配置apikey后将会留存聊天记录，即使未使用此apikey
                else:
                    dbapi_key = st.secrets["apikey"]

                # print("api_key:",dbapi_key,st.session_state["pre_user_input_content"],history_need_input,paras_need_input)
                res = user_query_response(st.session_state["pre_user_input_content"],history_need_input,dbapi_key,st.session_state["select_model"],set_context_all[st.session_state["context_select" + current_chat]])
                # transform the response to the format of GPT
                r = []
                r.append({"choices": [{"delta": {"content": res}}]})
            else:
                r = openai.ChatCompletion.create(
                    model=st.session_state["select_model"],
                    messages=history_need_input,
                    stream=True,
                    **paras_need_input,
                )
        except (FileNotFoundError, KeyError):
            area_error.error(
                "缺失 OpenAI API Key，请在复制项目后配置Secrets，或者在模型选项中进行临时配置。"
                "详情见[项目仓库](https://github.com/PierXuY/ChatGPT-Assistant)。"
            )
        except openai.error.AuthenticationError:
            area_error.error("无效的 OpenAI API Key。")
        except openai.error.APIConnectionError as e:
            area_error.error("连接超时，请重试。报错：   \n" + str(e.args[0]))
        except openai.error.InvalidRequestError as e:
            area_error.error("无效的请求，请重试。报错：   \n" + str(e.args[0]))
        except openai.error.RateLimitError as e:
            area_error.error("请求受限。报错：   \n" + str(e.args[0]))
        else:
            st.session_state["chat_of_r"] = current_chat
            st.session_state["r"] = r
            st.rerun()

if ("r" in st.session_state) and (current_chat == st.session_state["chat_of_r"]):#如果r在ss中且当前聊天等于ss中的chat_of_r
    if current_chat + "report" not in st.session_state:#如果current_chat+report不在ss中
        st.session_state[current_chat + "report"] = ""
    try:
        for e in st.session_state["r"]:
            if "content" in e["choices"][0]["delta"]:
                st.session_state[current_chat + "report"] += e["choices"][0]["delta"][
                    "content"
                ]
                show_each_message(
                    st.session_state["pre_user_input_content"],
                    "user",
                    "tem",
                    [area_user_svg.markdown, area_user_content.markdown],
                )#展示消息
                show_each_message(
                    st.session_state[current_chat + "report"],
                    "assistant",
                    "tem",
                    [area_gpt_svg.markdown, area_gpt_content.markdown],
                )
    except ChunkedEncodingError:
        area_error.error("网络状况不佳，请刷新页面重试。")
    # 应对stop情形
    except Exception:
        pass
    else:
        # 保存内容
        st.session_state["history" + current_chat].append(
            {"role": "user", "content": st.session_state["pre_user_input_content"]}
        )
        st.session_state["history" + current_chat].append(
            {"role": "assistant", "content": st.session_state[current_chat + "report"]}
        )
        write_data()
    # 用户在网页点击stop时，ss某些情形下会暂时为空
    if current_chat + "report" in st.session_state:
        st.session_state.pop(current_chat + "report")
    if "r" in st.session_state:
        st.session_state.pop("r")
        st.rerun()

# 添加事件监听
v1.html(js_code, height=0)
