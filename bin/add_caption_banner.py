#!/usr/bin/env python3
"""Add a black caption banner above a video, with color emoji support."""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


# Prefer the custom FFmpeg build, falling back to PATH if it is unavailable.
CUSTOM_FFMPEG_DIR = Path.home() / "opt" / "ffmpeg-color-emoji" / "bin"

CUSTOM_FFMPEG = CUSTOM_FFMPEG_DIR / "ffmpeg"
CUSTOM_FFPROBE = CUSTOM_FFMPEG_DIR / "ffprobe"

FFMPEG = str(CUSTOM_FFMPEG) if CUSTOM_FFMPEG.is_file() else shutil.which("ffmpeg")
FFPROBE = str(CUSTOM_FFPROBE) if CUSTOM_FFPROBE.is_file() else shutil.which("ffprobe")


FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
]

EMOJI_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
]


def find_font(candidates, description):
    for candidate in candidates:
        if Path(candidate).is_file():
            return candidate

    raise RuntimeError(f"Couldn't find {description}.")


def contains_emoji(text):
    """Detect common emoji and emoji presentation characters."""
    for char in text:
        cp = ord(char)

        if (
            0x1F000 <= cp <= 0x1FAFF
            or 0x2600 <= cp <= 0x27BF
            or 0x2300 <= cp <= 0x23FF
            or cp in (0x00A9, 0x00AE, 0x203C, 0x2049, 0x2122, 0x2139)
        ):
            return True

    return False


def wrap_text(text, max_chars):
    """Wrap paragraphs without splitting words; retain blank paragraph gaps."""
    result = []

    for paragraph in text.splitlines():
        if not paragraph.strip():
            result.append("")
        else:
            result.extend(
                textwrap.wrap(
                    paragraph.strip(),
                    width=max_chars,
                    break_long_words=False,
                    break_on_hyphens=False,
                ) or [""]
            )

    while result and not result[-1]:
        result.pop()

    return result


def escape_filter_path(path):
    """Escape a path for use in an FFmpeg filter argument."""
    value = str(path)

    for char in ("\\", ":", "'", ",", "[", "]"):
        value = value.replace(char, "\\" + char)

    return value


def unique_output_path(source):
    candidate = source.with_name(source.stem + "_with_caption.mp4")
    index = 2

    while candidate.exists():
        candidate = source.with_name(
            f"{source.stem}_with_caption_{index}.mp4"
        )
        index += 1

    return candidate


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Add a black banner with centered white text "
            "above a video."
        )
    )

    parser.add_argument("video", help="Input video file")
    parser.add_argument(
        "-o",
        "--output",
        help=(
            "Output MP4 path (default: "
            "<input>_with_caption.mp4; never overwrites)"
        ),
    )

    args = parser.parse_args()

    if not FFMPEG:
        sys.exit("Error: ffmpeg isn't installed or isn't on PATH.")

    if not FFPROBE:
        sys.exit("Error: ffprobe isn't installed or isn't on PATH.")

    source = Path(args.video).expanduser()

    if not source.is_file():
        sys.exit(f"Error: input video not found: {source}")

    title = input("Title: ").strip()

    if not title:
        sys.exit("Error: title cannot be empty.")

    print(
        "Enter the body text one line at a time. "
        "Enter END on its own line when done."
    )
    print("You can use an empty line between paragraphs.")

    body_lines = []

    while True:
        try:
            line = input()
        except EOFError:
            break

        if line.strip() == "END":
            break

        body_lines.append(line)

    body = "\n".join(body_lines).strip()

    try:
        normal_font = find_font(
            FONT_CANDIDATES,
            "a usable regular font. Install one with: "
            "sudo apt install fonts-dejavu-core",
        )

        emoji_font = find_font(
            EMOJI_FONT_CANDIDATES,
            "Noto Color Emoji. Install it with: "
            "sudo apt install fonts-noto-color-emoji",
        )

    except RuntimeError as exc:
        sys.exit(f"Error: {exc}")

    # Read source dimensions using the matching ffprobe executable.
    probe = subprocess.run(
        [
            FFPROBE,
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "csv=s=x:p=0",
            str(source),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    try:
        width, height = map(int, probe.stdout.strip().split("x"))
    except (ValueError, TypeError):
        sys.exit("Error: couldn't determine the video's dimensions.")

    title_size = max(22, min(32, round(width * 0.023)))
    body_size = max(18, min(26, round(width * 0.019)))

    # Approximate average character width, leaving horizontal margins.
    title_chars = max(12, int((width - 80) / (title_size * 0.56)))
    body_chars = max(16, int((width - 80) / (body_size * 0.56)))

    title_rows = wrap_text(title, title_chars)
    body_rows = wrap_text(body, body_chars) if body else []

    top_margin = 20
    title_line_height = int(title_size * 1.35)
    body_line_height = int(body_size * 1.45)
    gap_after_title = 12 if body_rows else 0
    bottom_margin = 20

    body_height = sum(
        body_line_height if line else int(body_line_height * 0.55)
        for line in body_rows
    )

    banner_height = (
        top_margin
        + len(title_rows) * title_line_height
        + gap_after_title
        + body_height
        + bottom_margin
    )

    # Pad height should be even for common video encoders.
    if banner_height % 2:
        banner_height += 1

    output = (
        Path(args.output).expanduser()
        if args.output
        else unique_output_path(source)
    )

    if output.exists():
        sys.exit(
            f"Error: output already exists, refusing to overwrite: {output}"
        )

    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="caption_banner_") as temp_name:
        temp_dir = Path(temp_name)

        filters = [
            f"pad=iw:ih+{banner_height}:0:{banner_height}:color=black"
        ]

        y = top_margin
        text_file_index = 0

        def add_line(line, size, y_position, line_height):
            nonlocal text_file_index

            text_file = temp_dir / f"text_{text_file_index:03d}.txt"
            text_file_index += 1

            text_file.write_text(line, encoding="utf-8")

            # Color emoji require the patched FFmpeg build and the
            # Noto Color Emoji bitmap font. Ordinary lines use DejaVu.
            font = emoji_font if contains_emoji(line) else normal_font

            filters.append(
                "drawtext="
                f"fontfile='{escape_filter_path(font)}':"
                f"textfile='{escape_filter_path(text_file)}':"
                f"fontcolor=white:fontsize={size}:"
                "x=(w-text_w)/2:"
                f"y={y_position}"
            )

            return y_position + line_height

        for line in title_rows:
            y = add_line(line, title_size, y, title_line_height)

        y += gap_after_title

        for line in body_rows:
            if not line:
                y += int(body_line_height * 0.55)
            else:
                y = add_line(line, body_size, y, body_line_height)

        command = [
            FFMPEG,
            "-hide_banner",
            "-i", str(source),
            "-vf", ",".join(filters),
            "-map", "0:v:0",
            "-map", "0:a?",
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "medium",
            "-c:a", "copy",
            "-movflags", "+faststart",
            str(output),
        ]

        print(f"\nFFmpeg: {FFMPEG}")
        print(f"Input:  {source}")
        print(f"Output: {output}")
        print(
            f"Banner: {width}x{banner_height}; "
            f"final video: {width}x{height + banner_height}"
        )
        print("Encoding video; audio will be copied without re-encoding...\n")

        result = subprocess.run(command)

    if result.returncode:
        # FFmpeg may leave a partial output after failure.
        if output.exists() and output.stat().st_size == 0:
            output.unlink()

        sys.exit(result.returncode)

    print(f"\nDone: {output}")


if __name__ == "__main__":
    main()