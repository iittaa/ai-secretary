---
name: リサーチ方法10選の実装計画
description: AIニュースキャッチアップのための10のリサーチ方法と実装状況
type: project
---

## 元記事
@SuguruKun_ai の「AIニュースを毎日キャッチアップできるリサーチ方法10選」
- ポスト: https://x.com/SuguruKun_ai/status/2040473238447456408
- 記事: https://x.com/i/article/2040469282157637632

## 参考URL
- Grok API公式: https://console.x.ai
- Grok APIドキュメント: https://docs.x.ai/developers/models
- Grok API料金・使い方ガイド: https://help.apiyi.com/en/xai-grok-api-x-search-web-search-guide-en.html

## ゴール
リサーチ → Xポスト用にリライト → 下書き保存（投稿は手動）

## 10のリサーチ方法と実装状況

| # | 方法 | コスト | 状況 |
|---|------|--------|------|
| 1 | Grok API × X検索 | 月~75円 | ✅ 完了 |
| 2 | YouTube字幕取得 × 海外AI動画 | 無料 | ⬜ 未着手 |
| 3 | HackerNews API | 無料 | ⬜ 未着手 |
| 4 | Reddit分析 | 無料 | ⬜ 未着手 |
| 5 | 中国SNSトレンド | 無料 | ⬜ 未着手 |
| 6 | Google Trends | 無料 | ⬜ 未着手 |
| 7 | Product Hunt分析 | 無料 | ⬜ 未着手 |
| 8 | SerpApi × Google検索 | 月250回無料 | ⬜ 未着手 |
| 9 | Xブックマーク × 直感 | 無料 | ⬜ 未着手 |
| 10 | Claude Codeログ × セマンティック検索 | 無料 | ⬜ 未着手 |

## ツール保存先
`tools/` ディレクトリに各スクリプトを配置
