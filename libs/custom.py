from .set_context import set_context

# 用户名
user_name = 'User'
gpt_name = 'SHINE AGV CHAT'
# 头像(svg格式) 来自 https://www.dicebear.com/playground?style=identicon
user_svg = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 5 5" fill="none" shape-rendering="crispEdges" width="512" height="512"><desc>"Identicon" by "Florian Körner", licensed under "CC0 1.0". / Remix of the original. - Created with dicebear.com</desc><metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:RDF><cc:Work><dc:title>Identicon</dc:title><dc:creator><cc:Agent rdf:about="https://dicebear.com"><dc:title>Florian Körner</dc:title></cc:Agent></dc:creator><dc:source>https://dicebear.com</dc:source><cc:license rdf:resource="https://creativecommons.org/publicdomain/zero/1.0/" /></cc:Work></rdf:RDF></metadata><mask id="viewboxMask"><rect width="5" height="5" rx="0" ry="0" x="0" y="0" fill="#fff" /></mask><g mask="url(#viewboxMask)"><path d="M0 0h1v1H0V0ZM4 0h1v1H4V0ZM3 0H2v1h1V0Z" fill="#00acc1"/><path fill="#00acc1" d="M2 1h1v1H2z"/><path fill="#00acc1" d="M1 2h3v1H1z"/><path fill="#00acc1" d="M2 3h1v1H2z"/><path d="M2 4H1v1h1V4ZM4 4H3v1h1V4Z" fill="#00acc1"/></g></svg>
"""
gpt_svg = """
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="41px" height="31px" viewBox="0 0 41 31" enable-background="new 0 0 41 31" xml:space="preserve">  <image id="image0" width="41" height="31" x="0" y="0"
    xlink:href="data:image/png;base64,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
ODvtAAAAAElFTkSuQmCC" />
</svg>


"""
# 内容背景
user_background_color = 'rgba(235, 245, 251, 0.3)'
gpt_background_color = 'rgba(235, 245, 251, 0.3)'
# 模型初始设置
initial_content_all = {
    "history": [],
    "paras": {
        "temperature": 1.0,
        "top_p": 1.0,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0,
    },
    "contexts": {
        'context_select': '场景判断',
        'context_input': '',
        'context_level': 4
    }
}
# 上下文
set_context_all = {"场景判断": "你现在是一个通信调用协议架构师。我现在总共有13个接口，分别是: 1. 地图数据上传，2. 地图数据下载， 3. AMR地图列表查询接口， 4. AMR地图切换， 5. 站点数据批量上传，6. 站点数据批量下载， 7. 路线数据批量上传， 8. 路线数据批量下载，9. AMR动作查询接口，10.任务指令下发，11.任务状态查询，12. 任务取消接口，13. 获取AMR状态接口。这十三种数据接口，现在你要根据我的指令来挑选出需要使用的接口索引，并直接以对应阿拉伯数字作为结果，如果不符合则直接输出不符合即可："}
set_context_all.update(set_context)# 从set_context.py中导入

# 自定义css、js
css_code = """
    <style>
    /* 侧边框背景*/
    section[data-testid="stSidebar"] > div > div:nth-child(2) {
        padding-top: 0.75rem !important;
        background-color: rgba(235, 245, 251, 0.4)
    }

    /* 右边主聊天界面背景*/
    section.main > div {
        padding-top: 10px;
    }
    
    /* 侧边框标题*/
    section[data-testid="stSidebar"] h1 {

        text-shadow: 2px 2px #ccc;
        font-size: 28px !important;
        font-family: "微软雅黑", "auto";
        margin-bottom: 6px;
        font-weight: 500 !important;
    }
    
    /*侧边栏单选框区域*/
    section[data-testid="stSidebar"] .stRadio {
        overflow: overlay;
        height: 28vh;
    }
    
    /*页面中水平线*/
    hr {
        margin-top: 20px;
        margin-bottom: 30px;
        background-color: #ebf5fb
    }
    
    .avatar {
        display: flex;
        align-items: center;
        gap: 10px;
        pointer-events: none;
        margin: -8px 10px -16px;
    }
    
    .avatar svg {
        width: 30px;
        height: 30px;
    }
    
    .avatar h2 {
        font-size: 20px;
        margin: 0;
    }
    
    /*用户提问和GPT回答的div*/
    .content-div {
        padding: 5px 20px;
        margin: 5px;
        text-align: left;
        border-radius: 10px;
        border: none;
        line-height: 1.6;
        font-size: 17px;
    }

    /*GPT回答的div*/
    .content-div.assistant p {
        padding: 4px;
        margin: 2px;
    }
    
    /*用户提问的div*/
    .content-div.user p {
        padding: 4px;
        margin: -5px 2px -3px;
    }
    
    
    div[data-testid="stForm"] {
        border: none;
        padding: 0;
    }
    
    button[kind="primaryFormSubmit"] {
        border: none;
        padding: 0;
    }
    
    div[data-testid="stForm"] + div[data-testid="stHorizontalBlock"] div[data-baseweb="select"] > div:nth-child(1) {
        background-color: transparent;
        justify-content: center;
        font-weight: 300;
        border-radius: 0.25rem;
        margin: 0;
        line-height: 1.4;
        border: 1px solid rgba(49, 51, 63, 0.2);
    }
    </style>
"""

# 为了解决输入框的问题，需要在页面加载完成后注入一些js代码
js_code = """
<script>
function checkElements() {
    const textinput = window.parent.document.querySelector("textarea[aria-label='**输入：**']");   //label需要相对应
    const textarea = window.parent.document.querySelector("div[data-baseweb = 'textarea']");
    const button = window.parent.document.querySelector("button[kind='secondaryFormSubmit']");
    const tabs = window.parent.document.querySelectorAll('button[data-baseweb="tab"] p');
    const tabs_div = window.parent.document.querySelector('div[role="tablist"]');
    const tab_panels = window.parent.document.querySelectorAll('div[data-baseweb="tab-panel"]');

    if (textinput && textarea && button && tabs && tabs_div && tab_panels) {
        // 双击点位输入框，同时抑制双击时选中文本事件
        window.parent.document.addEventListener('dblclick', function (event) {
            let activeTab = tabs_div.querySelector('button[aria-selected="true"]');
            if (activeTab.querySelector('p').textContent === '💬 聊天') {
                textinput.focus();
            } else {
                tabs[0].click();
                const waitMs = 50;

                function waitForFocus() {
                    if (window.parent.document.activeElement === textinput) {
                    } else {
                        setTimeout(function () {
                            textinput.focus();
                            waitForFocus();
                        }, waitMs);
                    }
                }

                waitForFocus();
            }
        });
        window.parent.document.addEventListener('mousedown', (event) => {
            if (event.detail === 2) {
                event.preventDefault();
            }
        });
        textinput.addEventListener('focusin', function (event) {
            event.stopPropagation();
            textarea.style.borderColor = 'rgb(73, 162, 223)';
        });
        textinput.addEventListener('focusout', function (event) {
            event.stopPropagation();
            textarea.style.borderColor = 'white';
        });

        // Ctrl + Enter快捷方式
        window.parent.document.addEventListener("keydown", event => {
            if (event.ctrlKey && event.key === "Enter") {
                if (textinput.textContent !== '') {
                    button.click();
                }
                textinput.blur();
            }
        });

        // 设置 Tab 键
        textinput.addEventListener('keydown', function (event) {
            if (event.keyCode === 9) {
                // 阻止默认行为
                event.preventDefault();
                if (!window.parent.getSelection().toString()) {
                    // 获取当前光标位置
                    const start = this.selectionStart;
                    const end = this.selectionEnd;
                    // 在光标位置插入制表符
                    this.value = this.value.substring(0, start) + '\t' + this.value.substring(end);
                    // 将光标移动到插入的制表符之后
                    this.selectionStart = this.selectionEnd = start + 1;
                }
            }
        });

        // 处理tabs 在第一次切换时的渲染问题
        tabs.forEach(function (tab, index) {
            const tab_panel_child = tab_panels[index].querySelectorAll("*");

            function set_visibility(state) {
                tab_panels[index].style.visibility = state;
                tab_panel_child.forEach(function (child) {
                    child.style.visibility = state;
                });
            }

            tab.addEventListener("click", function (event) {
                set_visibility('hidden')

                let element = tab_panels[index].querySelector('div[data-testid="stVerticalBlock"]');
                let main_block = window.parent.document.querySelector('section.main div[data-testid="stVerticalBlock"]');
                const waitMs = 50;

                function waitForLayout() {
                    if (element.offsetWidth === main_block.offsetWidth) {
                        set_visibility("visible");
                    } else {
                        setTimeout(waitForLayout, waitMs);
                    }
                }

                waitForLayout();
            });
        });
    } else {
        setTimeout(checkElements, 100);
    }
}

checkElements()
</script>
"""
