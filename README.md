# AI秘書

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

## Discord連携セットアップ

Discord経由でAI秘書とやり取りしたい場合の手順です。

### 1. Discord Botを作成

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
2. 「New Application」をクリックしてアプリを作成
3. 左メニューの「Bot」セクションでボットを作成
4. 「Token」の「Reset Token」をクリックしてトークンをコピー（⚠️ 一度しか表示されないので必ず控える）

### 2. Botの権限を設定

**Privileged Gateway Intents**

Botの設定画面で以下を有効化：
- ✅ Message Content Intent

**OAuth2 URL の生成**

1. 左メニュー「OAuth2」→「URL Generator」
2. **Scopes** で `bot` を選択
3. **Bot Permissions** で以下を有効化：
   - View Channels
   - Send Messages
   - Send Messages in Threads
   - Read Message History
   - Attach Files
   - Add Reactions
4. 生成されたURLをブラウザで開いて、Botをサーバーに追加

### 3. Claude CodeにDiscordプラグインをインストール

Claude Codeを起動して以下を実行：

```bash
/plugin install discord@claude-plugins-official
```

### 4. Botトークンを設定

```bash
/discord:configure YOUR_BOT_TOKEN_HERE
```

### 5. Discord連携モードで起動

```bash
./start.sh --discord
```

### 6. アカウントをペアリング

1. DiscordでBotにDMを送信
2. Botがペアリングコードを返信
3. Claude Code側で確認：
   ```bash
   /discord:access pair PAIRING_CODE
   ```
4. 自分のアカウントのみに制限する場合：
   ```bash
   /discord:access policy allowlist
   ```

### トラブルシューティング

| 症状 | 確認ポイント |
|---|---|
| Botが返信しない | Claude Codeが `--discord` フラグで起動しているか確認 |
| メッセージを読めない | Developer PortalでMessage Content Intentが有効か確認 |
| 権限エラー | OAuth2 URL GeneratorでBot Permissionsを再設定 |
| トークンが無効 | Developer Portalでトークンをリセットして再設定 |

## ライセンス

MIT
