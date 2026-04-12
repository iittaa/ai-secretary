#!/usr/bin/env node
// X(Twitter)のポスト・長文記事をPlaywrightで取得するスクリプト
// Usage:
//   node tools/fetch_x_post.mjs login        — ブラウザが開くのでXにログイン → Cookie保存
//   node tools/fetch_x_post.mjs <URL>         — ポスト/記事を取得

import { chromium } from 'playwright';
import { existsSync, readFileSync, writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const COOKIE_PATH = resolve(__dirname, '../.x_cookies.json');

const arg = process.argv[2];
if (!arg) {
  console.error('Usage:\n  node tools/fetch_x_post.mjs login\n  node tools/fetch_x_post.mjs <X_POST_URL>');
  process.exit(1);
}

// ログインモード: ブラウザを開いて手動ログイン → Cookie保存
if (arg === 'login') {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto('https://x.com/login');
  console.log('ブラウザでXにログインしてください');
  console.log('ログイン完了したらターミナルでEnterを押してください...');

  await new Promise(r => process.stdin.once('data', r));

  const cookies = await context.cookies();
  writeFileSync(COOKIE_PATH, JSON.stringify(cookies, null, 2));
  console.log(`Cookie保存完了！ (${COOKIE_PATH})`);
  await browser.close();
  process.exit(0);
}

// 取得モード
const url = arg;

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
  });

  // 保存済みCookieがあれば読み込み
  if (existsSync(COOKIE_PATH)) {
    const cookies = JSON.parse(readFileSync(COOKIE_PATH, 'utf-8'));
    await context.addCookies(cookies);
  }

  const page = await context.newPage();

  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });

    // ログインモーダルが出たら閉じる
    try {
      const closeBtn = page.locator('[data-testid="xMigrationBottomBar"] button, [role="button"][aria-label="Close"]');
      await closeBtn.first().click({ timeout: 3000 });
    } catch {}

    // ツイートテキストが表示されるまで待つ
    try {
      await page.waitForSelector('[data-testid="tweetText"], article', { timeout: 15000 });
    } catch {}
    await page.waitForTimeout(2000);

    // 「さらに表示」ボタンがあればクリックして展開
    try {
      const showMore = page.locator('text=さらに表示').first();
      await showMore.click({ timeout: 3000 });
      await page.waitForTimeout(2000);
    } catch {}

    // 長文記事（X Article）の場合
    if (url.includes('/article/') || url.includes('/i/article/')) {
      // スクロールして遅延読み込みコンテンツを全部表示させる
      let prevHeight = 0;
      for (let i = 0; i < 30; i++) {
        await page.evaluate(() => window.scrollBy(0, 600));
        await page.waitForTimeout(300);
        const curHeight = await page.evaluate(() => document.body.scrollHeight);
        if (curHeight === prevHeight) break;
        prevHeight = curHeight;
      }
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.waitForTimeout(500);

      // メインコンテンツエリアのテキストを取得
      const articleContent = await page.evaluate(() => {
        // mainタグ内 or 記事全体を取得
        const main = document.querySelector('main') || document.body;
        return main.innerText;
      });
      console.log(articleContent);
    } else {
      // 通常のポストの場合
      const tweetTexts = await page.evaluate(() => {
        const tweets = document.querySelectorAll('[data-testid="tweetText"]');
        return Array.from(tweets).map(t => t.innerText).join('\n\n---\n\n');
      });

      if (tweetTexts) {
        console.log(tweetTexts);
      } else {
        // フォールバック: ページ全体のテキスト
        const bodyText = await page.evaluate(() => document.body.innerText);
        console.log(bodyText);
      }
    }
  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    if (process.env.SCREENSHOT) {
      await page.screenshot({ path: '/tmp/x_debug.png', fullPage: true });
      console.error('Screenshot saved to /tmp/x_debug.png');
    }
    await browser.close();
  }
})();
