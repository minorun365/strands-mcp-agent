# Strands MCP エージェント

Microsoft Learning MCPと連携してAzureやMicrosoft技術について学習できる！ AWS発のOSS「[Strands Agents SDK](http://strandsagents.com)」で作ったAIエージェントWebアプリです。

- このアプリの作り方： https://qiita.com/minorun365/items/428ca505a8dd40136b5d


## 概要

このアプリケーションは、AWS BedrockのClaudeモデルを使用して、Microsoft Learning MCPとWebインターフェース経由で対話できるようにします。HTTPプロトコル経由でMicrosoft Learning MCPに接続し、Microsoft AzureやMicrosoft技術に関する専門的な情報にアクセスできます。

## 機能

- 🤖 **Strandsエージェント統合**: AIエージェント構築のためのStrandsフレームワークを活用
- 🔌 **Microsoft Learning MCP統合**: HTTPプロトコル経由でMicrosoft Learning MCPに接続
- 🌐 **Streamlit Webインターフェース**: エージェントと対話するための使いやすいWebインターフェース
- ⚡ **リアルタイムストリーミング**: ツール実行の可視化とともにエージェントの応答をライブストリーミング
- 🛠️ **OpenAI統合**: OpenAIのGPT-4.1モデルを活用してインテリジェントな応答を生成
- 📊 **Langfuseトレース**: Langfuseによる詳細なトレースと観測機能

## 前提条件

- Python 3.10以上
- OpenAI APIキー
- Microsoft Learning MCP APIへのアクセス

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

### OpenAI API認証情報

ローカル開発の場合、以下の方法でOpenAI APIキーを設定します:

環境変数:
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### Streamlit Community Cloudへのデプロイ

Streamlit Community Cloudにデプロイする場合:

1. Streamlit Community Cloudでアプリの設定に移動
2. 「Secrets」セクションに移動
3. 以下のシークレットを追加:
```toml
[openai]
OPENAI_API_KEY = "your-openai-api-key"

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

1. **質問**: Microsoft AzureやMicrosoft技術に関するクエリを入力
2. 「質問する」をクリックして送信

エージェントは以下を実行します:
- Microsoft Learning MCPに接続
- OpenAI GPT-4.1モデルを使用してクエリを処理
- Microsoft技術に関する専門的な情報を取得
- リアルタイムで応答をストリーミング
- ツールの実行を発生時に表示

## Microsoft Learning MCP統合

このアプリケーションは、Microsoft Learning MCPに固定で接続し、以下の機能を提供します：

- **Azure サービス**: Azure の各種サービスに関する詳細情報
- **Microsoft 技術**: .NET、Azure、Microsoft 365 などの技術情報
- **学習リソース**: Microsoft Learn の公式ドキュメントへのアクセス
- **ベストプラクティス**: Microsoft技術の推奨される使用方法

## Streamlit Community Cloudへのデプロイ

1. コードをGitHubにプッシュ
2. [share.streamlit.io](https://share.streamlit.io)にアクセス
3. 「New app」をクリック
4. GitHubリポジトリを接続
5. デプロイ設定:
   - リポジトリ: `yourusername/strands-mcp-agent`
   - ブランチ: `main`
   - メインファイルパス: `main.py`
6. アプリ設定でOpenAIシークレットを追加（設定セクションを参照）
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

- OpenAI APIキーをリポジトリにコミットしない
- 機密情報にはStreamlitシークレットを使用
- OpenAI APIキーの使用量とコストを監視
- デプロイ前にMCPサーバーの権限を確認
- Langfuseの認証情報も同様に保護

## トラブルシューティング

### よくある問題

1. **OpenAI APIキーエラー**: OpenAI APIキーが正しく設定されているか確認
2. **OpenAI API制限**: API使用量やレート制限に達していないか確認
3. **Microsoft Learning MCP接続失敗**: インターネット接続とMicrosoft Learning MCP APIへのアクセスを確認

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
- [OpenAI](https://openai.com) - GPT-4.1 APIサービス
- [Streamlit](https://streamlit.io) - Webアプリフレームワーク
