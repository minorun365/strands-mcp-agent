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

# メインエリア
title = "Microsoft Learning Agent"
st.title(title)
st.markdown(
    "このアプリでは、MS LearnのMCP APIを使ってAzureの資格勉強や学習サポートもできちゃうよ！\n"
    "\n💡 Azureの公式ラーニング教材を活用して、資格取得を目指そう！"
)
question = st.text_area("質問を入力", "Microsoft Azureとは何ですか？主要なサービスについて教えてください。", height=80)

# Microsoft Learning MCP設定（固定）
MICROSOFT_LEARNING_MCP_URL = "https://learn.microsoft.com/api/mcp"


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

    # OpenAIModelの初期化方法を最新版に修正
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


async def stream_response(agent, question, container):
    """レスポンスをストリーミング表示"""
    text_holder = container.empty()
    buffer = ""
    shown_tools = set()

    async for chunk in agent.stream_async(question):
        if isinstance(chunk, dict):
            # ツール実行を検出して表示
            tool_id, tool_name = extract_tool_info(chunk)
            if tool_id and tool_name and tool_id not in shown_tools:
                shown_tools.add(tool_id)
                if buffer:
                    text_holder.markdown(buffer)
                    buffer = ""
                container.info(f"🔧 **{tool_name}** ツールを実行中...")
                text_holder = container.empty()

            # テキストを抽出して表示
            if text := extract_text(chunk):
                buffer += text
                text_holder.markdown(buffer)

    # 最終表示
    if buffer:
        text_holder.markdown(buffer)


# ボタンを押したら生成開始
if st.button("質問する"):
    # Microsoft Learning MCPクライアントを作成
    client = create_mcp_client(MICROSOFT_LEARNING_MCP_URL)
    clients = [client]

    with st.spinner("回答を生成中…"):
        try:
            # すべてのクライアントをコンテキストマネージャで管理
            for client in clients:
                client.__enter__()

            agent = create_agent(clients)
            container = st.container()

            # 非同期実行
            loop = asyncio.new_event_loop()
            loop.run_until_complete(stream_response(agent, question, container))
            loop.close()

        except asyncio.TimeoutError:
            st.error("タイムアウトエラーが発生しました。もう一度お試しください。")
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
            st.info("Microsoft Learning MCPサーバーへの接続を確認してください。")
        finally:
            # すべてのクライアントを終了
            for client in clients:
                try:
                    client.__exit__(None, None, None)
                except Exception:
                    pass
