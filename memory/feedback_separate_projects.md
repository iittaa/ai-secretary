---
name: johnディレクトリにシステムを作らない
description: johnは秘書専用ディレクトリ。実装・システムは別ディレクトリに作る
type: feedback
---

`/Users/kosukeitamoto/projects/john/` は秘書ジョン専用ディレクトリ。動画生成システムなどの実装プロジェクトは別ディレクトリで作る。

**Why:** オーナー指示（2026-04-29）「ここのディレクトリにはシステムは作らないでね 新しいディレクトリに作るから」。秘書の memory・howto と、実装プロジェクトのコードを分離しておきたい。

**How to apply:**
- 実装系プロジェクトを始める時は、まず作る場所をオーナーに確認
- デフォルトの提案先は `/Users/kosukeitamoto/projects/<新プロジェクト名>/`
- john配下に作るのは memory・howto・プロンプトテンプレート・小さなツール（thumbnail_factoryなど）まで
- システム本体・サービス・大きな実装は別ディレクトリ
