# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

このリポジトリは「Strands MCP エージェント」というWebアプリケーションで、AWS発のOSS「Strands Agents SDK」を使用して構築されています。Microsoft Learning MCPサーバーを使用し、OpenAIのGPT-4.1モデルと対話できるStreamlitベースのインターフェースを提供します。

## 一般的なコマンド

### アプリケーションの実行
```bash
# ローカルでStreamlitアプリを起動
streamlit run main.py

# デバッグモードで実行
streamlit run main.py --logger.level=debug
```

### 依存関係の管理
```bash
# 依存関係のインストール（uvを使用）
uv sync
```

### OpenAI API設定
```bash
# 環境変数でOpenAI API キーを設定
export OPENAI_API_KEY="your-openai-api-key"
```

### LangSmithトレース設定
```bash
# 環境変数でLangSmith設定（オプション）
export LANGSMITH_API_KEY="your-langsmith-api-key"
```

## コードアーキテクチャと構造

### ファイル構成
- `main.py` - Streamlitアプリケーションのメインファイル
- `pyproject.toml` - Python依存関係の定義（uv管理）
- `uv.lock` - 依存関係のロックファイル
- `.github/workflows/claude.yml` - Claude Code GitHub Actionの設定

### 主要なコンポーネント

#### 1. Streamlitアプリケーション (`main.py`)
- **UI構成**:
  - メインエリア: 質問入力フィールドと回答表示
  - Microsoft Learning MCP固定設定
  
- **主要な関数**:
  - `create_mcp_client()`: MCPクライアントの作成（HTTP形式）
  - `create_agent()`: MCPツールを持つエージェントの作成
  - `stream_response()`: 非同期でレスポンスをストリーミング表示
  - `extract_tool_info()`: ツール実行情報の抽出
  - `extract_text()`: チャンクからテキストの抽出
  - `setup_langsmith_tracing()`: LangSmithトレース設定

#### 2. 技術スタック
- **フレームワーク**: Streamlit（Webインターフェース）
- **AIエージェント**: Strands Agents SDK（OTEL対応）
- **LLMプロバイダー**: OpenAI（GPT-4.1モデル）
- **MCPプロトコル**: http_client経由でMCPサーバーと通信
- **MCPサーバー**: Microsoft Learning MCP（固定設定）
- **トレーシング**: OpenTelemetry → LangSmith

#### 3. セッション管理
- Microsoft Learning MCPサーバーに固定接続
- シンプルな質問・回答インターフェース

#### 4. 認証とシークレット管理
- 環境変数で直接設定
  - OPENAI_API_KEY: OpenAI API認証（必須）
  - LANGSMITH_API_KEY: LangSmithトレース（オプション）
- 設定例:
  ```bash
  export OPENAI_API_KEY="your-openai-api-key"
  export LANGSMITH_API_KEY="your-langsmith-api-key"
  ```

## 重要な注意点

1. **MCPサーバー接続**: Microsoft Learning MCPサーバーにHTTPプロトコルで接続
2. **非同期処理**: asyncioを使用してストリーミングレスポンスを実装
3. **エラーハンドリング**: MCPサーバー接続エラーやOpenAI API認証エラーに注意
4. **デプロイ**: 環境変数としてOpenAI API キーの設定が必須
5. **LangSmithトレース**: OTELエンドポイント経由でトレース情報を送信（オプション機能）

## GitHub Actions

Claude Code Actionが設定されており、以下のトリガーで動作:
- Issue/PRコメントに`@claude`を含む場合
- Issue本文/タイトルに`@claude`を含む場合

## 開発のヒント

1. Microsoft Learning MCPサーバーは固定設定のため、変更不要
2. OpenAI GPT-4.1モデルを使用（temperature=0.5に設定）
3. ツール実行の可視化により、エージェントの動作を把握しやすい設計
4. LangSmithトレースは環境変数から自動設定されるオプション機能
5. OTEL形式でトレースデータがLangSmithに自動送信される