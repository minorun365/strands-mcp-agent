import asyncio
import os
import streamlit as st
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
from mcp.client import ClientSession
import httpx
import websockets
import json

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
    # 接続タイプの選択
    connection_type = st.selectbox("接続タイプ", ["ローカル", "リモート"])
    
    if connection_type == "ローカル":
        package_manager = st.selectbox("パッケージマネージャー", ["uvx", "npx"])
        mcp_args = st.text_input(f"MCPサーバーのパッケージ名（{package_manager}用）", "awslabs.aws-documentation-mcp-server@latest")
    else:  # リモート
        transport_type = st.selectbox("リモート接続方式", ["HTTP", "WebSocket"])
        if transport_type == "HTTP":
            mcp_url = st.text_input("MCPサーバーのURL", "https://your-mcp-server.com/mcp")
        else:  # WebSocket
            mcp_url = st.text_input("MCPサーバーのWebSocket URL", "wss://your-mcp-server.com/mcp")
        
        # 認証設定（オプション）
        with st.expander("認証設定（オプション）"):
            auth_type = st.selectbox("認証方式", ["なし", "Bearer Token", "API Key"])
            if auth_type == "Bearer Token":
                auth_token = st.text_input("Bearer Token", type="password")
            elif auth_type == "API Key":
                api_key = st.text_input("API Key", type="password")
                api_key_header = st.text_input("API Keyヘッダー名", "X-API-Key")
    
    model_id = st.text_input("BedrockのモデルID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
    st.text("")
    st.markdown("このアプリの作り方 [https://qiita.com/minorun365/items/dd05a3e4938482ac6055](https://qiita.com/minorun365/items/dd05a3e4938482ac6055)")


class HTTPTransport:
    """HTTP transport for MCP servers"""
    
    def __init__(self, url, headers=None):
        self.url = url
        self.headers = headers or {}
        self.session = httpx.AsyncClient()
        self._id_counter = 0
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.aclose()
    
    async def send_request(self, method, params=None):
        """Send JSON-RPC request over HTTP"""
        self._id_counter += 1
        request = {
            "jsonrpc": "2.0",
            "id": self._id_counter,
            "method": method,
            "params": params or {}
        }
        
        response = await self.session.post(
            self.url,
            json=request,
            headers=self.headers
        )
        response.raise_for_status()
        
        return response.json()


class WebSocketTransport:
    """WebSocket transport for MCP servers"""
    
    def __init__(self, url, headers=None):
        self.url = url
        self.headers = headers or {}
        self.websocket = None
        self._id_counter = 0
    
    async def __aenter__(self):
        extra_headers = {}
        if self.headers:
            extra_headers.update(self.headers)
        
        self.websocket = await websockets.connect(
            self.url,
            extra_headers=extra_headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.websocket:
            await self.websocket.close()
    
    async def send_request(self, method, params=None):
        """Send JSON-RPC request over WebSocket"""
        self._id_counter += 1
        request = {
            "jsonrpc": "2.0",
            "id": self._id_counter,
            "method": method,
            "params": params or {}
        }
        
        await self.websocket.send(json.dumps(request))
        response = await self.websocket.recv()
        
        return json.loads(response)


class RemoteMCPClient:
    """Remote MCP Client wrapper"""
    
    def __init__(self, transport):
        self.transport = transport
        self._tools_cache = None
    
    async def __aenter__(self):
        await self.transport.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.transport.__aexit__(exc_type, exc_val, exc_tb)
    
    async def list_tools(self):
        """List available tools from remote MCP server"""
        if self._tools_cache is None:
            response = await self.transport.send_request("tools/list")
            if "result" in response:
                self._tools_cache = response["result"]["tools"]
            else:
                self._tools_cache = []
        return self._tools_cache
    
    def list_tools_sync(self):
        """Synchronous wrapper for list_tools"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.list_tools())
        finally:
            loop.close()
    
    async def call_tool(self, name, arguments=None):
        """Call a tool on the remote MCP server"""
        response = await self.transport.send_request(
            "tools/call",
            {"name": name, "arguments": arguments or {}}
        )
        return response


def create_local_mcp_client(mcp_args, package_manager):
    """ローカルMCPクライアントを作成"""
    # npxの場合は-yフラグを追加
    if package_manager == "npx":
        args = ["-y", mcp_args]
    else:
        args = [mcp_args]
    
    return MCPClient(lambda: stdio_client(
        StdioServerParameters(command=package_manager, args=args)
    ))


def create_remote_mcp_client(url, transport_type, auth_headers=None):
    """リモートMCPクライアントを作成"""
    if transport_type == "HTTP":
        transport = HTTPTransport(url, auth_headers)
    else:  # WebSocket
        transport = WebSocketTransport(url, auth_headers)
    
    return RemoteMCPClient(transport)


def create_agent(client, model_id):
    """エージェントを作成"""
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
    # 認証ヘッダーの準備
    auth_headers = {}
    if connection_type == "リモート":
        if 'auth_type' in locals() and auth_type == "Bearer Token" and 'auth_token' in locals() and auth_token:
            auth_headers["Authorization"] = f"Bearer {auth_token}"
        elif 'auth_type' in locals() and auth_type == "API Key" and 'api_key' in locals() and api_key:
            header_name = api_key_header if 'api_key_header' in locals() and api_key_header else "X-API-Key"
            auth_headers[header_name] = api_key
    
    with st.spinner("回答を生成中…"):
        try:
            if connection_type == "ローカル":
                # ローカルMCPサーバー接続
                client = create_local_mcp_client(mcp_args, package_manager)
                with client:
                    agent = create_agent(client, model_id)
                    container = st.container()
                    
                    # 非同期実行
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete(stream_response(agent, question, container))
                    loop.close()
            else:
                # リモートMCPサーバー接続
                async def run_remote_agent():
                    client = create_remote_mcp_client(mcp_url, transport_type, auth_headers)
                    async with client:
                        # ツールを取得してエージェントを作成
                        tools = await client.list_tools()
                        agent = Agent(
                            model=BedrockModel(model_id=model_id),
                            tools=tools
                        )
                        container = st.container()
                        await stream_response(agent, question, container)
                
                # 非同期実行
                loop = asyncio.new_event_loop()
                loop.run_until_complete(run_remote_agent())
                loop.close()
        
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
            st.error("接続設定を確認してください。")