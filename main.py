import asyncio
import os
import streamlit as st
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
import uuid

# Streamlit secretsからAWS認証情報を設定
if "aws" in st.secrets:
    os.environ["AWS_ACCESS_KEY_ID"] = st.secrets["aws"]["AWS_ACCESS_KEY_ID"]
    os.environ["AWS_SECRET_ACCESS_KEY"] = st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"]
    os.environ["AWS_DEFAULT_REGION"] = st.secrets["aws"]["AWS_DEFAULT_REGION"]

# Streamlit secretsからLangfuse認証情報を設定
if "langfuse" in st.secrets:
    os.environ["LANGFUSE_PUBLIC_KEY"] = st.secrets["langfuse"]["LANGFUSE_PUBLIC_KEY"]
    os.environ["LANGFUSE_SECRET_KEY"] = st.secrets["langfuse"]["LANGFUSE_SECRET_KEY"]
    os.environ["LANGFUSE_HOST"] = st.secrets["langfuse"]["LANGFUSE_HOST"]

st.title("Strands MCPエージェント")
st.text("あなたの好きなMCPサーバーを設定して、Strands Agentsを動かしてみよう！")

model_id = st.text_input("BedrockのモデルID", "us.anthropic.claude-3-7-sonnet-20250219-v1:0")
mcp_args = st.text_input("MCPサーバーのパッケージ名（uvx用）", "awslabs.aws-documentation-mcp-server@latest")
question = st.text_input("質問を入力", "BedrockのClaude 4 OpusのモデルIDは？")


def create_mcp_client(mcp_args):
    """MCPクライアントを作成"""
    return MCPClient(lambda: stdio_client(
        StdioServerParameters(command="uvx", args=[mcp_args])
    ))


def create_agent(client, model_id):
    """エージェントを作成"""
    # Langfuseトレーシングは trace_attributes で設定
    return Agent(
        model=BedrockModel(model_id=model_id),
        tools=client.list_tools_sync(),
        trace_attributes={
            "session.id": f"strands-mcp-{os.getpid()}",
            "user.id": "streamlit-user",
            "langfuse.tags": [
                "strands-mcp-agent",
                "streamlit-app",
                "bedrock-model"
            ]
        }
    )


def extract_tool_info(chunk):
    """チャンクからツール情報を抽出"""
    event = chunk.get('event', {})
    if 'contentBlockStart' in event:
        tool_use = event['contentBlockStart'].get('start', {}).get('toolUse', {})
        return tool_use.get('toolUseId'), tool_use.get('name')
    return None, None


def extract_text(chunk):
    """チャンクからテキストを抽出"""
    if text := chunk.get('data'):
        return text
    elif delta := chunk.get('delta', {}).get('text'):
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
                text_holder.markdown(buffer + "▌")
    
    # 最終表示
    if buffer:
        text_holder.markdown(buffer)


if st.button("質問する"):
    client = create_mcp_client(mcp_args)
    
    with st.spinner("回答を生成中…"):
        with client:
            agent = create_agent(client, model_id)
            container = st.container()
            
            # 非同期実行
            loop = asyncio.new_event_loop()
            loop.run_until_complete(stream_response(agent, question, container))
            loop.close()