# Strands MCP エージェント

あなたの好きなMCPサーバーを設定できる！ AWS発のOSS「[Strands Agents SDK](http://strandsagents.com)」で作ったAIエージェントWebアプリです。

- このアプリの作り方： https://qiita.com/minorun365/items/428ca505a8dd40136b5d


## 概要

このアプリケーションは、AWS BedrockのClaudeモデルを使用して、様々なMCPサーバーとWebインターフェース経由で対話できるようにします。stdioプロトコルをサポートする任意のMCPサーバーに接続し、専門的なツールやデータソースにアクセスできます。

## 機能

- 🤖 **Strandsエージェント統合**: AIエージェント構築のためのStrandsフレームワークを活用
- 🔌 **MCPサーバーサポート**: stdioプロトコル経由で任意のMCPサーバーに接続
- 🌐 **Streamlit Webインターフェース**: エージェントと対話するための使いやすいWebインターフェース
- ⚡ **リアルタイムストリーミング**: ツール実行の可視化とともにエージェントの応答をライブストリーミング
- 🛠️ **AWS Bedrock統合**: AWS BedrockのClaudeモデルを活用してインテリジェントな応答を生成
- 📊 **Langfuseトレース**: Langfuseによる詳細なトレースと観測機能

## 前提条件

- Python 3.10以上
- Bedrockアクセス権限を持つAWSアカウント
- 設定済みのAWS認証情報
- 使用したいMCPサーバーへのアクセス

## インストール

1. リポジトリをクローン:
```bash
git clone https://github.com/yourusername/strands-mcp-agent.git
cd strands-mcp-agent
```

2. 依存関係をインストール:
```bash
pip install -r requirements.txt
```

## 設定

### AWS認証情報

ローカル開発の場合、以下のいずれかの方法でAWS認証情報を設定します:

1. AWS CLI設定:
```bash
aws configure
```

2. 環境変数:
```bash
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_DEFAULT_REGION="us-west-2"
```

### Streamlit Community Cloudへのデプロイ

Streamlit Community Cloudにデプロイする場合:

1. Streamlit Community Cloudでアプリの設定に移動
2. 「Secrets」セクションに移動
3. 以下のシークレットを追加:
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

### ローカル開発

アプリケーションをローカルで実行:
```bash
streamlit run main.py
```

### アプリケーションの使用

1. **モデルID**: BedrockモデルIDを入力（デフォルト: `us.anthropic.claude-3-7-sonnet-20250219-v1:0`）
2. **MCPサーバー**: uvx用のMCPサーバーパッケージ名を指定（例: `awslabs.aws-documentation-mcp-server@latest`）
3. **質問**: クエリを入力
4. 「質問する」をクリックして送信

エージェントは以下を実行します:
- 指定されたMCPサーバーに接続
- 選択したBedrockモデルを使用してクエリを処理
- リアルタイムで応答をストリーミング
- ツールの実行を発生時に表示

## サポートされているMCPサーバー

このアプリケーションは、stdioプロトコルをサポートする任意のMCPサーバーに接続できます。例:

- `awslabs.aws-documentation-mcp-server@latest` - AWSドキュメント検索

## Streamlit Community Cloudへのデプロイ

1. コードをGitHubにプッシュ
2. [share.streamlit.io](https://share.streamlit.io)にアクセス
3. 「New app」をクリック
4. GitHubリポジトリを接続
5. デプロイ設定:
   - リポジトリ: `yourusername/strands-mcp-agent`
   - ブランチ: `main`
   - メインファイルパス: `main.py`
6. アプリ設定でAWSシークレットを追加（設定セクションを参照）
7. 「Deploy」をクリック

## 観測性とトレース

このアプリケーションはLangfuseと統合されており、すべてのエージェントの動作をトレースできます。Langfuseダッシュボードで以下の情報を確認できます:

- エージェントの実行トレース
- モデルの入出力
- ツールの実行履歴
- レイテンシとパフォーマンスメトリクス
- コストの追跡

### Langfuseの設定

1. [Langfuse](https://langfuse.com)でアカウントを作成
2. プロジェクトを作成してAPIキーを取得
3. Streamlit secretsにLangfuse認証情報を追加（上記の設定セクションを参照）

## セキュリティに関する考慮事項

- AWS認証情報をリポジトリにコミットしない
- 機密情報にはStreamlitシークレットを使用
- AWS IAMユーザーにはBedrockに必要な権限のみを付与
- デプロイ前にMCPサーバーの権限を確認
- Langfuseの認証情報も同様に保護

## トラブルシューティング

### よくある問題

1. **AWS認証情報エラー**: AWS認証情報が正しく設定されているか確認
2. **Bedrockアクセス拒否**: AWSアカウントが指定されたBedrockモデルにアクセスできるか確認
3. **MCPサーバー接続失敗**: MCPサーバーパッケージ名が正しく、アクセス可能か確認

### デバッグモード

デバッグのために、追加のログを有効にしてStreamlitを実行:
```bash
streamlit run main.py --logger.level=debug
```

## 貢献

貢献を歓迎します！お気軽にプルリクエストを送信してください。

## ライセンス

このプロジェクトはMITライセンスの下でライセンスされています - 詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 謝辞

- [Strands](https://github.com/yourusername/strands) - エージェントフレームワーク
- [MCP](https://modelcontextprotocol.io) - Model Context Protocol
- [AWS Bedrock](https://aws.amazon.com/bedrock/) - マネージドAIサービス
- [Streamlit](https://streamlit.io) - Webアプリフレームワーク
