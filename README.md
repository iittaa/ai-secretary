# AI Secretary

Claude Code を使った専用AI秘書パッケージ。
セットアップするだけで、あなた専用の記憶を持つAI秘書が使えるようになります。

## 特徴

- **パーソナライズ可能** — 秘書の名前や性格をカスタマイズ
- **記憶システム** — セッションをまたいで学習・記憶を蓄積
- **Discord連携対応** — Discord経由でのやり取りも可能
- **すぐ使える** — セットアップは1コマンド

## 必要なもの

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) がインストール済みであること
- Discord連携を使う場合は Discord Bot Token

## セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/iittaa/ai-secretary.git
cd ai-secretary

# スクリプトに実行権限を付与
chmod +x setup.sh start.sh

# セットアップ（秘書の名前を設定）
./setup.sh
```

## 使い方

```bash
# 通常起動
./start.sh

# Discord連携で起動
./start.sh --discord
```

## カスタマイズ

### 性格・話し方を変更

`CLAUDE.md.template` を編集して、再度 `./setup.sh` を実行してください。

### 記憶システム

秘書は以下のディレクトリで記憶を管理します：

| ディレクトリ | 内容 |
|---|---|
| `memory/facts/` | 変わらない事実（オーナー情報など） |
| `memory/lessons/` | 失敗・成功から学んだ教訓 |
| `memory/decisions/` | オーナーと決めた重要な方針 |
| `memory/howto/` | 繰り返す作業の手順書 |
| `memory/today.md` | 日次の引き継ぎメモ |

## ディレクトリ構成

```
ai-secretary/
├── README.md              # このファイル
├── .gitignore             # 個人データを除外
├── setup.sh               # 初回セットアップ
├── start.sh               # 起動スクリプト
├── CLAUDE.md.template     # 秘書の性格テンプレート
├── CLAUDE.md              # (setup.shで生成、git管理外)
└── memory/                # (setup.shで生成、git管理外)
```

## ライセンス

MIT
