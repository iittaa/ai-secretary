#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# セットアップ済みかチェック
if [ ! -f "CLAUDE.md" ]; then
  echo "⚠️  先にセットアップを実行してください: ./setup.sh"
  exit 1
fi

# Discord連携モード
if [ "$1" = "--discord" ]; then
  export DISCORD_STATE_DIR="$SCRIPT_DIR/.discord-state"
  echo "🚀 Discord連携モードで起動します..."
  claude --channels plugin:discord@claude-plugins-official --dangerously-skip-permissions
else
  echo "🚀 通常モードで起動します..."
  claude --dangerously-skip-permissions
fi
