#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================="
echo "  AI Secretary - セットアップ"
echo "========================================="
echo ""

# 秘書の名前を設定
read -p "秘書の名前を入力してください（例: ジョン）: " SECRETARY_NAME

if [ -z "$SECRETARY_NAME" ]; then
  echo "名前が入力されませんでした。デフォルト名「アシスタント」を使用します。"
  SECRETARY_NAME="アシスタント"
fi

# CLAUDE.md を生成
sed "s/{{NAME}}/$SECRETARY_NAME/g" CLAUDE.md.template > CLAUDE.md
echo "✅ CLAUDE.md を生成しました（秘書名: $SECRETARY_NAME）"

# memory ディレクトリを初期化
mkdir -p memory/facts
mkdir -p memory/lessons
mkdir -p memory/decisions
mkdir -p memory/howto
touch memory/today.md
touch memory/lessons/inbox.md
echo "✅ memory/ ディレクトリを初期化しました"

echo ""
echo "========================================="
echo "  セットアップ完了！"
echo "========================================="
echo ""
echo "起動方法:"
echo "  ./start.sh              # 通常起動"
echo "  ./start.sh --discord    # Discord連携で起動"
echo ""
