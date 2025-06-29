import asyncio
import os

import streamlit as st
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.models.openai import OpenAIModel
from strands.tools.mcp import MCPClient

# ページ設定
st.set_page_config(
    page_title="Microsoft Learning MCP × Strands Agents SDK",
    page_icon="📚🤖",
    initial_sidebar_state="expanded",
    menu_items={"About": "Microsoft Learning MCPとStrands Agents SDKでAIエージェントを体験できるアプリだよ！"},
)

# 環境変数の設定
if "openai" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["openai"]["OPENAI_API_KEY"]

# Microsoft Learning MCP設定（固定）
MICROSOFT_LEARNING_MCP_URL = "https://learn.microsoft.com/api/mcp"
SYSTEM_PROMPT = """
あなたは、Microsoft Azureに関する学習をサポートする親切なAIアシスタントです。
Microsoft Learning MCP APIを利用して、Azureの資格や学習教材に関する質問に答えることができます。
回答は、学習者にとって明確で、簡潔で、励みになるように心がけてください。
"""


def create_mcp_client(mcp_url):
    """MCPクライアントを作成（HTTP形式）"""

    def transport():
        return streamablehttp_client(mcp_url)

    return MCPClient(transport)


def create_agent(clients):
    """複数のMCPクライアントからツールを集約してエージェントを作成"""
    all_tools = []
    for client in clients:
        tools = client.list_tools_sync()
        all_tools.extend(tools)

    model = OpenAIModel(
        client_args={
            "api_key": os.getenv("OPENAI_API_KEY"),
        },
        model_id="gpt-4.1",
        params={
            "max_tokens": 1000,
            "temperature": 0.5,
        },
    )
    return Agent(model=model, tools=all_tools)


def extract_tool_info(chunk):
    """チャンクからツール情報を抽出"""
    event = chunk.get("event", {})
    if "contentBlockStart" in event:
        tool_use = event["contentBlockStart"].get("start", {}).get("toolUse", {})
        return tool_use.get("toolUseId"), tool_use.get("name")
    return None, None


def extract_text(chunk):
    """チャンクからテキストを抽出"""
    if text := chunk.get("data"):
        return text
    elif delta := chunk.get("delta", {}).get("text"):
        return delta
    return ""


async def stream_response(agent, messages):
    """レスポンスをストリーミング表示し、完全なレスポンスを返す"""
    text_holder = st.empty()
    buffer = ""
    full_response = ""
    shown_tools = set()

    async for chunk in agent.stream_async(messages):
        if isinstance(chunk, dict):
            tool_id, tool_name = extract_tool_info(chunk)
            if tool_id and tool_name and tool_id not in shown_tools:
                shown_tools.add(tool_id)
                if buffer:
                    text_holder.markdown(buffer)
                    full_response += buffer
                    buffer = ""
                st.info(f"🔧 **{tool_name}** ツールを実行中...")
                text_holder = st.empty()

            if text := extract_text(chunk):
                buffer += text
                text_holder.markdown(buffer)

    if buffer:
        full_response += buffer
        text_holder.markdown(buffer)

    return full_response


# --- App ---
st.title("Microsoft Learning Agent")
st.markdown(
    "このアプリでは、MS LearnのMCP APIを使ってAzureの資格勉強や学習サポートもできちゃうよ！\n"
    "\n💡 Azureの公式ラーニング教材を活用して、資格取得を目指そう！"
)

# チャット履歴の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# 履歴からチャットメッセージを表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ユーザーの入力を受け付ける
if prompt := st.chat_input("質問を入力してください"):
    # ユーザーメッセージを履歴に追加して表示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # アシスタントの応答
    with st.chat_message("assistant"):
        with st.spinner("回答を生成中…"):
            client = create_mcp_client(MICROSOFT_LEARNING_MCP_URL)
            clients = [client]
            try:
                for client in clients:
                    client.__enter__()

                agent = create_agent(clients)

                # システムプロンプトとチャット履歴を結合
                messages = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages

                # 非同期でレスポンスをストリーミング
                response = asyncio.run(stream_response(agent, messages))

                # アシスタントの完全な応答を履歴に追加
                st.session_state.messages.append({"role": "assistant", "content": response})

            except asyncio.TimeoutError:
                st.error("タイムアウトエラーが発生しました。もう一度お試しください。")
            except Exception as e:
                st.error(f"エラーが発生しました: {str(e)}")
                st.info("Microsoft Learning MCPサーバーへの接続を確認してください。")
            finally:
                for client in clients:
                    try:
                        client.__exit__(None, None, None)
                    except Exception:
                        pass

