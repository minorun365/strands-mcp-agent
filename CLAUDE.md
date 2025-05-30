# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

このリポジトリは「Strands MCP エージェント」というWebアプリケーションで、AWS発のOSS「Strands Agents SDK」を使用して構築されています。任意のMCPサーバーを設定し、AWS BedrockのClaudeモデルと対話できるStreamlitベースのインターフェースを提供します。

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
# 依存関係のインストール
pip install -r requirements.txt
```

### AWS認証設定
```bash
# AWS CLIで認証情報を設定
aws configure

# または環境変数で設定
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_DEFAULT_REGION="us-west-2"
```

## コードアーキテクチャと構造

### ファイル構成
- `main.py` - Streamlitアプリケーションのメインファイル
- `requirements.txt` - Python依存関係の定義
- `.github/workflows/claude.yml` - Claude Code GitHub Actionの設定

### 主要なコンポーネント

#### 1. Streamlitアプリケーション (`main.py`)
- **UI構成**:
  - メインエリア: 質問入力フィールドと回答表示
  - サイドバー: BedrockモデルIDとMCPサーバーの設定
  
- **主要な関数**:
  - `create_mcp_client()`: MCPクライアントの作成（uvx/npx対応）
  - `create_agent_with_multiple_tools()`: 複数ツールを持つエージェントの作成
  - `stream_response()`: 非同期でレスポンスをストリーミング表示
  - `extract_tool_info()`: ツール実行情報の抽出
  - `extract_text()`: チャンクからテキストの抽出

#### 2. 技術スタック
- **フレームワーク**: Streamlit（Webインターフェース）
- **AIエージェント**: Strands Agents SDK
- **LLMプロバイダー**: AWS Bedrock（Claudeモデル）
- **MCPプロトコル**: stdio_client経由でMCPサーバーと通信
- **パッケージマネージャー**: uvxまたはnpx（MCPサーバー実行用）

#### 3. セッション管理
- `st.session_state`を使用してMCPサーバー設定を永続化
- 動的にMCPサーバーの追加・削除が可能

#### 4. 認証とシークレット管理
- ローカル開発: AWS環境変数または~/.aws/credentials
- Streamlit Community Cloud: st.secretsを使用
  - AWS認証情報
  - Langfuseトレース設定（オプション）

## 重要な注意点

1. **MCPサーバー接続**: stdioプロトコルをサポートする任意のMCPサーバーに接続可能
2. **非同期処理**: asyncioを使用してストリーミングレスポンスを実装
3. **エラーハンドリング**: MCPサーバー接続エラーやBedrock認証エラーに注意
4. **デプロイ**: Streamlit Community Cloudへのデプロイ時はシークレット設定が必須

## GitHub Actions

Claude Code Actionが設定されており、以下のトリガーで動作:
- Issue/PRコメントに`@claude`を含む場合
- Issue本文/タイトルに`@claude`を含む場合

## 開発のヒント

1. MCPサーバーの追加時は、パッケージマネージャー（uvx/npx）に応じた適切なパッケージ名を指定
2. Bedrockモデルは利用可能なモデルIDを確認してから使用
3. ツール実行の可視化により、エージェントの動作を把握しやすい設計