#!/usr/bin/env python3
"""
サムネイル合成ツール
背景画像（テキスト入り）+ キャラ画像 → 右下にキャラを固定サイズで合成

Usage:
  python3 thumbnail_composer.py BG CHAR [-o OUT] [-s SIZE] [-m MARGIN]

  BG       背景画像（テキスト入り、1枚目）
  CHAR     キャラクター画像（透過PNG推奨、2枚目）
  -o OUT   出力先（デフォルト: output.png）
  -s SIZE  キャラ幅の画面比 0〜1（デフォルト: 0.08 = 8%）
  -m MARGIN 右端・下端からの余白の画面比 0〜1（デフォルト: 0.10 = 10%）

例:
  python3 thumbnail_composer.py base.png char.png
  python3 thumbnail_composer.py base.png char.png -s 0.06 -m 0.08
  python3 thumbnail_composer.py base.png char.png -o final.png -s 0.10
"""

import argparse
import sys
from pathlib import Path
from PIL import Image


def compose(bg_path: Path, char_path: Path, out_path: Path, size_ratio: float, margin_ratio: float) -> None:
    bg = Image.open(bg_path).convert("RGBA")
    char = Image.open(char_path).convert("RGBA")

    target_w = max(1, int(bg.width * size_ratio))
    scale = target_w / char.width
    target_h = max(1, int(char.height * scale))
    char_resized = char.resize((target_w, target_h), Image.LANCZOS)

    margin_x = int(bg.width * margin_ratio)
    margin_y = int(bg.height * margin_ratio)
    pos = (bg.width - target_w - margin_x, bg.height - target_h - margin_y)

    composite = bg.copy()
    composite.alpha_composite(char_resized, dest=pos)
    composite.convert("RGB").save(out_path, "PNG")

    print(f"✅ 合成完了: {out_path}")
    print(f"   背景サイズ: {bg.width}x{bg.height}")
    print(f"   キャラサイズ: {target_w}x{target_h} (画面の{size_ratio*100:.1f}%)")
    print(f"   配置位置: 右下から ({margin_x}, {margin_y})px = {margin_ratio*100:.1f}%")


def main() -> int:
    p = argparse.ArgumentParser(description="サムネ右下にキャラを固定サイズで合成")
    p.add_argument("bg", type=Path, help="背景画像（テキスト入り）")
    p.add_argument("char", type=Path, help="キャラクター画像（透過PNG推奨）")
    p.add_argument("-o", "--output", type=Path, default=Path("output.png"), help="出力ファイル名")
    p.add_argument("-s", "--size", type=float, default=0.08, help="キャラ幅の画面比 0〜1（例: 0.08 = 8%%）")
    p.add_argument("-m", "--margin", type=float, default=0.10, help="右端・下端余白の画面比 0〜1（例: 0.10 = 10%%）")
    args = p.parse_args()

    if not args.bg.exists():
        print(f"❌ 背景画像が見つかりません: {args.bg}", file=sys.stderr)
        return 1
    if not args.char.exists():
        print(f"❌ キャラ画像が見つかりません: {args.char}", file=sys.stderr)
        return 1
    if not (0 < args.size <= 1):
        print(f"❌ サイズは0〜1の範囲で指定してください: {args.size}", file=sys.stderr)
        return 1
    if not (0 <= args.margin < 1):
        print(f"❌ 余白は0〜1の範囲で指定してください: {args.margin}", file=sys.stderr)
        return 1

    compose(args.bg, args.char, args.output, args.size, args.margin)
    return 0


if __name__ == "__main__":
    sys.exit(main())
