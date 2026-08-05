#!/usr/bin/env python3
"""Generate QR codes from text on the command line."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import qrcode
from PIL import Image, ImageColor


DEFAULT_WIDTH = 256
DEFAULT_HEIGHT = 256
DEFAULT_FORMAT = "png"
DEFAULT_BACKGROUND = "white"
DEFAULT_FOREGROUND = "black"


def parse_color(value: str) -> tuple[int, int, int]:
    """Parse a color name or hex string into an RGB tuple."""
    try:
        rgb = ImageColor.getrgb(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid color: {value!r}") from exc
    if len(rgb) == 4:
        return rgb[:3]
    return rgb


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a QR code image from text.",
    )
    parser.add_argument(
        "text",
        help="Text to encode in the QR code.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file path (default: qr.<format> in the current directory).",
    )
    parser.add_argument(
        "-W",
        "--width",
        type=int,
        default=DEFAULT_WIDTH,
        help=f"Output image width in pixels (default: {DEFAULT_WIDTH}).",
    )
    parser.add_argument(
        "-H",
        "--height",
        type=int,
        default=DEFAULT_HEIGHT,
        help=f"Output image height in pixels (default: {DEFAULT_HEIGHT}).",
    )
    parser.add_argument(
        "-f",
        "--format",
        dest="image_format",
        default=DEFAULT_FORMAT,
        help=f"Output image format, e.g. png, jpeg, bmp (default: {DEFAULT_FORMAT}).",
    )
    parser.add_argument(
        "--background",
        "--bg",
        dest="background",
        type=parse_color,
        default=parse_color(DEFAULT_BACKGROUND),
        help=f"Background color as a name or hex value (default: {DEFAULT_BACKGROUND}).",
    )
    parser.add_argument(
        "--foreground",
        "--fg",
        "--code-color",
        dest="foreground",
        type=parse_color,
        default=parse_color(DEFAULT_FOREGROUND),
        help=f"QR code color as a name or hex value (default: {DEFAULT_FOREGROUND}).",
    )
    return parser


def color_to_name(rgb: tuple[int, int, int]) -> str:
    """Convert RGB to a hex string for qrcode.make_image."""
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def generate_qr(
    text: str,
    width: int,
    height: int,
    background: tuple[int, int, int],
    foreground: tuple[int, int, int],
) -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(
        fill_color=color_to_name(foreground),
        back_color=color_to_name(background),
    ).convert("RGB")
    if img.size != (width, height):
        img = img.resize((width, height), Image.Resampling.NEAREST)
    return img


def resolve_output_path(output: Path | None, image_format: str) -> Path:
    if output is not None:
        return output
    return Path(f"qr.{image_format.lower()}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.width <= 0 or args.height <= 0:
        parser.error("width and height must be positive integers")

    image_format = args.image_format.lower().lstrip(".")
    output_path = resolve_output_path(args.output, image_format)

    try:
        img = generate_qr(
            text=args.text,
            width=args.width,
            height=args.height,
            background=args.background,
            foreground=args.foreground,
        )
        img.save(output_path, format=image_format.upper())
    except OSError as exc:
        print(f"Error writing image: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Error generating image: {exc}", file=sys.stderr)
        return 1

    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
