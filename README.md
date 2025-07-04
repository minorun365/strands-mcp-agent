# Strands MCP エージェント

Microsoft Learning MCPと連携してAzureやMicrosoft技術について学習できる！ AWS発のOSS「[Strands Agents SDK](http://strandsagents.com)」で作ったAIエージェントWebアプリです。

**参考記事**: minorun365さんの「[Strands Agents SDK + MCPサーバーでAIエージェントを作ろう](https://qiita.com/minorun365/items/428ca505a8dd40136b5d)」を参考にして作成しました。

## 概要

このアプリケーションは、Azure資格勉強用のAIエージェントです。

HTTPプロトコル経由でMicrosoft Learning MCPに接続し、Microsoft AzureやMicrosoft技術に関する専門的な情報にアクセスして、効果的な学習支援を提供します。

## 機能

- 🎓 **Azure資格勉強支援**: Microsoft AzureやMicrosoft技術に特化した学習支援
- 🤖 **Strandsエージェント統合**: AIエージェント構築のためのStrandsフレームワークを活用
- 🔌 **Microsoft Learning MCP統合**: HTTPプロトコル経由でMicrosoft Learning MCPに接続
- 🌐 **Streamlit Webインターフェイス**: エージェントと対話するための使いやすいWebインターフェイス
- ⚡ **リアルタイムストリーミング**: ツール実行の可視化とともにエージェントの応答をライブストリーミング
- 🛠️ **OpenAI統合**: OpenAIのGPT-4.1モデルを活用してインテリジェントな応答を生成
- 📊 **LangSmithトレース**: LangSmithによる詳細なトレースと観測機能

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

1. 依存関係をインストール:

```bash
uv sync
```

## 設定

### OpenAI API認証情報

ローカル開発の場合、以下の方法でOpenAI APIキーを設定します:

環境変数:

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### LangSmithトレース設定（オプション）

LangSmithトレースを有効にする場合:

```bash
export LANGSMITH_API_KEY="your-langsmith-api-key"
```

## 使い方

### ローカル開発

アプリケーションをローカルで実行:

```bash
streamlit run main.py
```

### アプリケーションの使用

1. **質問**: Microsoft AzureやMicrosoft技術に関するクエリを入力（資格試験対策、技術的な疑問など）
2. 「質問する」をクリックして送信

エージェントは以下を実行します:

- Microsoft Learning MCPに接続
- OpenAI GPT-4.1モデルを使用してクエリを処理
- Microsoft技術に関する専門的な情報を取得
- リアルタイムで応答をストリーミング
- ツールの実行を発生時に表示

## Microsoft Learning MCP統合

このアプリケーションは、Microsoft Learning MCPに固定で接続し、Azure資格勉強に特化した以下の機能を提供します：

- **Azure サービス**: Azureの各種サービスに関する詳細情報（試験対策に最適）
- **Microsoft 技術**: .NET、Azure、Microsoft 365などの技術情報
- **学習リソース**: Microsoft Learnの公式ドキュメントへのアクセス
- **ベストプラクティス**: Microsoft技術の推奨される使用方法
- **資格試験対策**: Azure認定試験に関する情報とガイダンス

## 観測性とトレース

このアプリケーションはLangSmithと統合されており、すべてのエージェントの動作をトレースできます。LangSmithダッシュボードで以下の情報を確認できます:

- エージェントの実行トレース
- モデルの入出力
- ツールの実行履歴
- レイテンシとパフォーマンスメトリクス
- コストの追跡

### LangSmithの設定

1. [LangSmith](https://smith.langchain.com)でアカウントを作成
2. プロジェクトを作成してAPIキーを取得
3. 環境変数にLangSmith認証情報を追加（上記の設定セクションを参照）

## セキュリティに関する考慮事項

- OpenAI APIキーをリポジトリにコミットしない
- 機密情報にはStreamlitシークレットを使用
- OpenAI APIキーの使用量とコストを監視
- デプロイ前にMCPサーバーの権限を確認
- LangSmithの認証情報も同様に保護

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

## 参考

- [Strands Agents SDK](https://github.com/awslabs/strands-agents-sdk) - エージェントフレームワーク
- [MCP](https://modelcontextprotocol.io) - Model Context Protocol
- [OpenAI](https://openai.com) - GPT-4.1 APIサービス
- [Streamlit](https://streamlit.io) - Webアプリフレームワーク
