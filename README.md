# Strands MCP エージェント

あなたの好きなMCPサーバーを設定できる！ AWS発のOSS「[Strands Agents SDK](http://strandsagents.com)」で作ったAIエージェントWebアプリです。

- このアプリの作り方： https://qiita.com/minorun365/items/428ca505a8dd40136b5d

## 主な機能

画面でMCPサーバーのパッケージ名を指定すると、エージェントがそのサーバーにつながり、Amazon Bedrock の Claude で質問に答えます。stdio で動くMCPサーバーなら、uvx と npx のどちらのパッケージでも使えます。ツールの実行状況は回答と一緒にストリーミングで表示され、Langfuse を設定すればエージェントの動きをトレースとして残せます。

| パッケージ | MCPサーバーの例 |
|---|---|
| uvx | awslabs.aws-documentation-mcp-server@latest |
| npx | @modelcontextprotocol/server-filesystem |
| npx | @modelcontextprotocol/server-github |

## 必要なもの

- Python 3.10 以上
- Bedrock のモデルを使えるAWSアカウントと、その認証情報
- トレースを残す場合は Langfuse のAPIキー

## セットアップ

```bash
git clone https://github.com/minorun365/strands-mcp-agent.git
cd strands-mcp-agent
pip install -r requirements.txt
streamlit run main.py
```

AWSの認証情報は aws configure か環境変数で渡します。Streamlit Community Cloud へ載せる場合は、アプリ設定の Secrets に次の形で入れます。

```toml
[aws]
AWS_ACCESS_KEY_ID = "your-access-key-id"
AWS_SECRET_ACCESS_KEY = "your-secret-access-key"
AWS_DEFAULT_REGION = "us-west-2"

[langfuse]
LANGFUSE_PUBLIC_KEY = "your-langfuse-public-key"
LANGFUSE_SECRET_KEY = "your-langfuse-secret-key"
LANGFUSE_HOST = "https://us.cloud.langfuse.com"
```

## 使い方

画面でモデルID、パッケージマネージャー（uvx か npx）、MCPサーバーのパッケージ名を入れ、質問を書いて「質問する」を押します。MCPサーバーはローカルでコマンドとして起動されるので、使う前にそのサーバーが何にアクセスするかを確かめてください。

## ライセンス

MIT License。詳細は [LICENSE](LICENSE) を参照してください。
