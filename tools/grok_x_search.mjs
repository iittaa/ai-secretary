#!/usr/bin/env node
// Grok API × X検索でリアルタイム情報をリサーチ → ポスト下書き生成
// Usage: node tools/grok_x_search.mjs "検索クエリ"

import { readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// .envからAPIキー読み込み
const envPath = resolve(__dirname, '../.env');
const envContent = readFileSync(envPath, 'utf-8');
const apiKey = envContent.match(/XAI_API_KEY=(.+)/)?.[1]?.trim();

if (!apiKey) {
  console.error('.envにXAI_API_KEYが設定されていません');
  process.exit(1);
}

const query = process.argv[2];
if (!query) {
  console.error('Usage: node tools/grok_x_search.mjs "検索クエリ"');
  process.exit(1);
}

const res = await fetch('https://api.x.ai/v1/responses', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${apiKey}`,
  },
  body: JSON.stringify({
    model: 'grok-4-1-fast',
    tools: [{ type: 'x_search' }],
    input: [
      {
        role: 'user',
        content: `以下のトピックについてX(Twitter)で最新の情報をリサーチしてください。

検索トピック: ${query}

以下の形式で出力してください：

## リサーチ結果
- 最新の動向を箇条書きで3〜5個
- 各項目にソース（ユーザー名）を付ける

## Xポスト下書き
上記の情報を元に、日本語のXポスト（280文字以内）を1つ作成してください。
- 読者の興味を引くフック
- 要点を簡潔に
- 絵文字を適度に使用
- ハッシュタグ1〜2個`,
      },
    ],
  }),
});

const data = await res.json();

if (!res.ok) {
  console.error('APIエラー:', JSON.stringify(data, null, 2));
  process.exit(1);
}

// レスポンスからテキスト部分を抽出
const outputText = data.output
  ?.filter(item => item.type === 'message')
  ?.map(item => item.content?.map(c => c.text).join(''))
  ?.join('\n') || JSON.stringify(data, null, 2);

console.log(outputText);
