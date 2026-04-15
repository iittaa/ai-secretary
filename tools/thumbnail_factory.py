#!/usr/bin/env python3
"""
特典サムネ量産ツール
背景＋ゴージャス金フォントテキスト＋キャラを合成して大量生産

CSVから一括生成:
  python3 tools/thumbnail_factory.py data/batch.csv

CSVフォーマット (UTF-8, ヘッダー必須):
  character,line1,line2,line3,output_name
  girl_01.png,月収30万円,マネタイズロードマップ,,thumb_001.png
  girl_02.png,SNS集客,3つの極意,完全攻略,thumb_002.png
  - line3 は空欄でもOK（2行で済む場合）
  - character は assets/characters/ 内のファイル名

設定:
  - 背景: assets/bg/特典サムネ背景.png（--bg で上書き可能）
  - フォント: assets/fonts/NotoSerifJP.ttf
  - 出力先: output/thumbnails/

オプション:
  --bg PATH       背景画像を上書き
  --char-size F   キャラ幅の画面比 (デフォルト: 0.08)
  --char-margin F 右下余白の画面比 (デフォルト: 0.10)
  --text-area F   テキスト配置エリアの幅比 (デフォルト: 0.60)
  --text-left F   テキスト左端の画面比 (デフォルト: 0.06)
"""

from __future__ import annotations
import argparse
import csv
import os
import sys
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont, ImageChops

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BG = ROOT / "assets" / "bg" / "特典サムネ背景.png"
FONT_PATH = ROOT / "assets" / "fonts" / "NotoSerifJP.ttf"
CHARS_DIR = ROOT / "assets" / "characters"
OUTPUT_DIR = ROOT / "output" / "thumbnails"

# ゴージャス金グラデ（上→下）
GOLD_GRADIENT = [
    (255, 240, 180),  # 上：明るいシャンパンゴールド
    (240, 200, 100),  # 中：鮮やかなゴールド
    (180, 130, 50),   # 下：ディープゴールド／ブロンズ
]
OUTLINE_COLOR = (40, 25, 10)      # ダークブラウン
SHADOW_COLOR = (0, 0, 0, 100)     # 半透明黒
HIGHLIGHT_COLOR = (255, 250, 220, 200)  # 上部ハイライト


def auto_remove_white_bg(img: Image.Image, tolerance: int = 15) -> Image.Image:
    """キャラ画像のコーナーから flood-fill して白背景を透過にする。
    内部の白（瞳のハイライト等）は隔離されてれば残る。"""
    img = img.convert("RGBA")
    w, h = img.size
    # アルファマスク作成（最初は全部不透明）
    mask = Image.new("L", (w, h), 255)

    rgb = img.convert("RGB")

    def is_bg_like(pixel, ref):
        return all(abs(pixel[i] - ref[i]) <= tolerance for i in range(3))

    # 4コーナーから flood-fill
    visited = [[False] * w for _ in range(h)]
    rgb_pixels = rgb.load()

    from collections import deque
    for cx, cy in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        ref = rgb_pixels[cx, cy]
        # 白っぽくないコーナーはスキップ
        if not all(c >= 240 for c in ref):
            continue
        queue = deque([(cx, cy)])
        while queue:
            x, y = queue.popleft()
            if x < 0 or x >= w or y < 0 or y >= h or visited[y][x]:
                continue
            if not is_bg_like(rgb_pixels[x, y], ref):
                continue
            visited[y][x] = True
            mask.putpixel((x, y), 0)
            queue.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])

    img.putalpha(mask)
    return img


def make_gold_text_image(text: str, font: ImageFont.FreeTypeFont, outline_w: int) -> Image.Image:
    """1行のゴージャス金テキストを透過PNG画像として返す。"""
    # 1) サイズ計測（フチ込み）
    bbox = font.getbbox(text, stroke_width=outline_w)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    pad = max(outline_w * 2, 4)
    canvas_w = text_w + pad * 2
    canvas_h = text_h + pad * 2

    # 2) 文字マスク（白文字、透明背景）— グラデ適用用
    mask_img = Image.new("L", (canvas_w, canvas_h), 0)
    mask_draw = ImageDraw.Draw(mask_img)
    mask_draw.text(
        (pad - bbox[0], pad - bbox[1]),
        text,
        fill=255,
        font=font,
        stroke_width=0,
    )

    # 3) ゴールドグラデーション生成（縦方向）
    grad = Image.new("RGB", (canvas_w, canvas_h), GOLD_GRADIENT[1])
    grad_pixels = grad.load()
    n = len(GOLD_GRADIENT) - 1
    for y in range(canvas_h):
        ratio = y / max(canvas_h - 1, 1)
        seg = min(int(ratio * n), n - 1)
        local = ratio * n - seg
        c1 = GOLD_GRADIENT[seg]
        c2 = GOLD_GRADIENT[seg + 1]
        r = int(c1[0] + (c2[0] - c1[0]) * local)
        g = int(c1[1] + (c2[1] - c1[1]) * local)
        b = int(c1[2] + (c2[2] - c1[2]) * local)
        for x in range(canvas_w):
            grad_pixels[x, y] = (r, g, b)

    # 4) 上部ハイライト（細い明るい線）
    highlight_h = max(int(text_h * 0.18), 2)
    highlight = Image.new("RGBA", (canvas_w, highlight_h), HIGHLIGHT_COLOR)
    grad_rgba = grad.convert("RGBA")
    grad_rgba.alpha_composite(highlight, dest=(0, pad))

    # 5) ベースキャンバス（透過）
    out = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(out)

    # 6) 影（少しオフセット）
    shadow_offset = max(outline_w // 2, 2)
    draw.text(
        (pad - bbox[0] + shadow_offset, pad - bbox[1] + shadow_offset),
        text,
        fill=SHADOW_COLOR,
        font=font,
        stroke_width=outline_w,
        stroke_fill=SHADOW_COLOR,
    )

    # 7) フチ
    draw.text(
        (pad - bbox[0], pad - bbox[1]),
        text,
        fill=OUTLINE_COLOR,
        font=font,
        stroke_width=outline_w,
        stroke_fill=OUTLINE_COLOR,
    )

    # 8) グラデ本体（マスクで形を切り抜いて貼る）
    out.paste(grad_rgba, (0, 0), mask_img)

    return out


def fit_font_size(text: str, max_w: int, start: int = 200, min_size: int = 30, max_size: Optional[int] = None) -> int:
    """text が max_w に収まる最大フォントサイズを探す。max_size を超えない。"""
    if max_size is not None:
        start = min(start, max_size)
    size = start
    while size > min_size:
        font = load_font(size)
        bbox = font.getbbox(text)
        if bbox[2] - bbox[0] <= max_w:
            return size
        size -= 4
    return min_size


def load_font(size: int) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(FONT_PATH), size)
    # 変数フォント: Black (900) を指定
    try:
        font.set_variation_by_axes([900])
    except Exception:
        pass
    return font


def render_text_block(lines: list, max_w: int, max_h: int, font_min: int = 30, font_max: int = 400) -> Image.Image:
    """複数行を1ブロックにまとめてレンダリング。左揃え、行間あり。"""
    # 各行の最大サイズを揃えて選定（一番長い行で決定）
    longest = max(lines, key=lambda s: len(s))
    start = min(int(max_h * 0.45 / max(len(lines), 1) * 1.5), font_max)
    base_size = fit_font_size(longest, max_w, start=start, min_size=font_min, max_size=font_max)

    # 行ごとに最終サイズを決める（差を1.5倍以内に揃える）
    sizes = []
    for line in lines:
        if line == longest:
            sizes.append(base_size)
        else:
            # 短い行はやや大きめにできるが上限は base_size * 1.4 に（かつ font_max を超えない）
            upper = min(int(base_size * 1.4), font_max)
            cand = fit_font_size(line, max_w, start=upper, min_size=font_min, max_size=upper)
            sizes.append(cand)

    # 行ごとの画像生成
    line_imgs = []
    line_h_total = 0
    line_gap = int(base_size * 0.15)
    for line, sz in zip(lines, sizes):
        font = load_font(sz)
        outline_w = max(int(sz * 0.04), 2)
        img = make_gold_text_image(line, font, outline_w)
        line_imgs.append(img)
        line_h_total += img.height
    line_h_total += line_gap * (len(lines) - 1)

    # 左揃えで合成
    block_w = max(img.width for img in line_imgs)
    block = Image.new("RGBA", (block_w, line_h_total), (0, 0, 0, 0))
    y = 0
    for img in line_imgs:
        block.alpha_composite(img, dest=(0, y))
        y += img.height + line_gap

    # 高さ調整: max_h を超える場合は縮小
    if block.height > max_h:
        scale = max_h / block.height
        block = block.resize(
            (int(block.width * scale), int(block.height * scale)),
            Image.LANCZOS,
        )
    return block


def compose_thumbnail(
    bg: Image.Image,
    char_path: Optional[Path],
    lines: list,
    char_size_ratio: float,
    char_margin_ratio: float,
    text_area_ratio: float,
    text_left_ratio: float,
    font_min: int = 30,
    font_max: int = 400,
) -> Image.Image:
    out = bg.copy().convert("RGBA")

    # キャラが占有する右側の幅（実体幅 + 右側余白）を計算
    char_occupied_w = 0
    if char_path and char_path.exists():
        char_target_w = int(out.width * char_size_ratio)
        char_margin_px = int(out.width * char_margin_ratio)
        char_occupied_w = char_target_w + char_margin_px

    # テキストブロックが使える幅 = キャラ領域を除いた画面幅
    available_w = out.width - char_occupied_w
    text_max_w = int(available_w * text_area_ratio)  # 余白を残すため割合をかける
    text_max_h = int(out.height * 0.7)

    text_block = render_text_block(lines, text_max_w, text_max_h, font_min=font_min, font_max=font_max)

    # テキストブロックを「キャラ領域を除いたエリアの中央」に配置
    text_x = (available_w - text_block.width) // 2
    text_y = (out.height - text_block.height) // 2
    out.alpha_composite(text_block, dest=(text_x, text_y))

    # キャラ合成
    if char_path and char_path.exists():
        char = Image.open(char_path).convert("RGBA")
        char = auto_remove_white_bg(char)
        target_w = max(1, int(out.width * char_size_ratio))
        scale = target_w / char.width
        target_h = max(1, int(char.height * scale))
        char_resized = char.resize((target_w, target_h), Image.LANCZOS)
        margin_x = int(out.width * char_margin_ratio)
        margin_y = int(out.height * char_margin_ratio)
        pos = (out.width - target_w - margin_x, out.height - target_h - margin_y)
        out.alpha_composite(char_resized, dest=pos)

    return out.convert("RGB")


def process_csv(csv_path: Path, args) -> int:
    bg_path = Path(args.bg) if args.bg else DEFAULT_BG
    if not bg_path.exists():
        print(f"❌ 背景画像が見つかりません: {bg_path}", file=sys.stderr)
        return 1
    bg = Image.open(bg_path)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    success = 0
    fail = 0
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            char_name = row.get("character", "").strip()
            line1 = row.get("line1", "").strip()
            line2 = row.get("line2", "").strip()
            line3 = row.get("line3", "").strip()
            output_name = row.get("output_name", f"thumb_{i:03d}.png").strip()

            lines = [l for l in [line1, line2, line3] if l]
            if not lines:
                print(f"⚠️  行{i}: テキストが空のためスキップ")
                fail += 1
                continue

            char_path = CHARS_DIR / char_name if char_name else None
            try:
                result = compose_thumbnail(
                    bg, char_path, lines,
                    args.char_size, args.char_margin,
                    args.text_area, args.text_left,
                    font_min=args.font_min, font_max=args.font_max,
                )
                out_path = OUTPUT_DIR / output_name
                result.save(out_path, "PNG")
                print(f"✅ [{i}] {output_name}  ({' / '.join(lines)})")
                success += 1
            except Exception as e:
                print(f"❌ [{i}] {output_name} 失敗: {e}", file=sys.stderr)
                fail += 1

    print(f"\n📊 完了: 成功 {success}件 / 失敗 {fail}件 → {OUTPUT_DIR}")
    return 0 if fail == 0 else 2


def main() -> int:
    p = argparse.ArgumentParser(description="特典サムネ量産ツール")
    p.add_argument("csv", type=Path, help="入力CSVファイル")
    p.add_argument("--bg", type=str, default=None, help="背景画像パスの上書き")
    p.add_argument("--char-size", type=float, default=0.24, help="キャラ幅の画面比 (デフォルト: 0.24)")
    p.add_argument("--char-margin", type=float, default=0.05, help="右下余白の画面比 (デフォルト: 0.05)")
    p.add_argument("--text-area", type=float, default=0.90, help="テキストが利用可能エリア(キャラ除外後)に占める幅比 (デフォルト: 0.90)")
    p.add_argument("--text-left", type=float, default=0.06, help="(現在未使用) 旧:テキスト左端の画面比")
    p.add_argument("--font-min", type=int, default=100, help="フォント最小サイズ px (デフォルト: 100)")
    p.add_argument("--font-max", type=int, default=300, help="フォント最大サイズ px (デフォルト: 300)")
    args = p.parse_args()

    if not args.csv.exists():
        print(f"❌ CSVが見つかりません: {args.csv}", file=sys.stderr)
        return 1
    if not FONT_PATH.exists():
        print(f"❌ フォントが見つかりません: {FONT_PATH}", file=sys.stderr)
        return 1

    return process_csv(args.csv, args)


if __name__ == "__main__":
    sys.exit(main())
