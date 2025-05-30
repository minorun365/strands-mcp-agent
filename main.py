import asyncio
import os
import streamlit as st
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

# ページ設定
st.set_page_config(
    page_title="Strands MCPエージェント",
    page_icon="☁️",
    menu_items={'About': "Strands Agents SDKで作ったMCPホストアプリです。"}
)

# 環境変数の設定
if "aws" in st.secrets:
    os.environ["AWS_ACCESS_KEY_ID"] = st.secrets["aws"]["AWS_ACCESS_KEY_ID"]
    os.environ["AWS_SECRET_ACCESS_KEY"] = st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"]
    os.environ["AWS_DEFAULT_REGION"] = st.secrets["aws"]["AWS_DEFAULT_REGION"]

# メインエリア
st.title("Strands MCPエージェント")
st.markdown("👈 サイドバーで好きなMCPサーバーを設定して、[Strands Agents SDK](https://aws.amazon.com/jp/blogs/news/introducing-strands-agents-an-open-source-ai-agents-sdk/) を動かしてみよう！")
question = st.text_input("質問を入力", "Bedrockでマルチエージェントは作れる？")

# サイドバー
with st.sidebar:
    st.subheader("MCPサーバー設定")
    
    # セッション状態でMCPサーバーのリストを管理
    if 'mcp_configs' not in st.session_state:
        st.session_state.mcp_configs = [{
            "package_manager": "uvx",
            "package_name": "awslabs.aws-documentation-mcp-server@latest",
            "name": "AWS Documentation"
        }]
    
    # 新しいMCPサーバーを追加
    with st.expander("MCPサーバーを追加"):
        new_name = st.text_input("サーバー名", key="new_name", placeholder="例: GitHub Integration")
        new_package_manager = st.selectbox("パッケージマネージャー", ["uvx", "npx"], key="new_pm")
        new_mcp_package = st.text_input("パッケージ名", key="new_package", placeholder="例: @modelcontextprotocol/server-github")
        
        if st.button("追加") and new_mcp_package and new_name:
            st.session_state.mcp_configs.append({
                "name": new_name,
                "package_manager": new_package_manager,
                "package_name": new_mcp_package
            })
            st.rerun()
    
    # 設定済みのMCPサーバーを表示
    st.subheader("設定済みサーバー")
    for i, config in enumerate(st.session_state.mcp_configs):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{config['name']}**")
            st.caption(f"{config['package_manager']}: {config['package_name']}")
        with col2:
            if st.button("削除", key=f"delete_{i}"):
                st.session_state.mcp_configs.pop(i)
                st.rerun()
    
    st.divider()
    model_id = st.text_input("BedrockのモデルID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
    st.text("")
    st.markdown("このアプリの作り方 [https://qiita.com/minorun365/items/dd05a3e4938482ac6055](https://qiita.com/minorun365/items/dd05a3e4938482ac6055)")


def create_mcp_client(mcp_args, package_manager):
    """MCPクライアントを作成"""
    # npxの場合は-yフラグを追加
    if package_manager == "npx":
        args = ["-y", mcp_args]
    else:
        args = [mcp_args]
    
    return MCPClient(lambda: stdio_client(
        StdioServerParameters(command=package_manager, args=args)
    ))


def create_multiple_mcp_clients(mcp_configs):
    """複数のMCPクライアントを作成"""
    clients = []
    for config in mcp_configs:
        try:
            client = create_mcp_client(config["package_name"], config["package_manager"])
            clients.append({
                "client": client,
                "name": config["name"],
                "config": config
            })
        except Exception as e:
            st.error(f"MCPサーバー '{config['name']}' の初期化に失敗しました: {str(e)}")
    return clients


def create_agent_with_multiple_tools(client_objects, model_id):
    """複数のクライアントからツールを統合してエージェントを作成"""
    all_tools = []
    active_clients = []
    
    for client_obj in client_objects:
        try:
            # クライアントを開いてツールを取得
            client_obj["client"].__enter__()
            tools = client_obj["client"].list_tools_sync()
            all_tools.extend(tools)
            active_clients.append(client_obj)
            st.success(f"✅ {client_obj['name']}: {len(tools)}個のツール")
        except Exception as e:
            st.error(f"❌ {client_obj['name']}: 接続失敗 - {str(e)}")
            # 失敗したクライアントはクローズ
            try:
                client_obj["client"].__exit__(None, None, None)
            except:
                pass
    
    if not all_tools:
        st.error("利用可能なツールがありません。MCPサーバーの設定を確認してください。")
        # 全てのクライアントをクローズ
        for client_obj in active_clients:
            try:
                client_obj["client"].__exit__(None, None, None)
            except:
                pass
        return None, []
    
    agent = Agent(
        model=BedrockModel(model_id=model_id),
        tools=all_tools
    )
    
    return agent, active_clients


def create_agent(client, model_id):
    """エージェントを作成（後方互換性のため残す）"""
    return Agent(
        model=BedrockModel(model_id=model_id),
        tools=client.list_tools_sync()
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


# ボタンを押したら生成開始
if st.button("質問する"):
    if not st.session_state.mcp_configs:
        st.error("MCPサーバーが設定されていません。")
    else:
        with st.spinner("MCPサーバーに接続中…"):
            # 複数のMCPクライアントを作成
            client_objects = create_multiple_mcp_clients(st.session_state.mcp_configs)
            
            if not client_objects:
                st.error("利用可能なMCPサーバーがありません。")
            else:
                # エージェントを作成（複数のツールを統合）
                agent, active_clients = create_agent_with_multiple_tools(client_objects, model_id)
                
                if agent is None:
                    st.error("エージェントの作成に失敗しました。")
                else:
                    st.info(f"🚀 {len(active_clients)}個のMCPサーバーから統合されたエージェントで回答します")
                    
                    try:
                        with st.spinner("回答を生成中…"):
                            container = st.container()
                            
                            # 非同期実行
                            loop = asyncio.new_event_loop()
                            loop.run_until_complete(stream_response(agent, question, container))
                            loop.close()
                    finally:
                        # クライアントのクリーンアップ
                        for client_obj in active_clients:
                            try:
                                client_obj["client"].__exit__(None, None, None)
                            except:
                                pass