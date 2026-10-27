#!/usr/bin/env python3
"""Add a black caption banner above a video using FFmpeg."""

import argparse
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


CUSTOM_FFMPEG_DIR = Path.home() / "opt" / "ffmpeg-color-emoji" / "bin"
CUSTOM_FFMPEG = CUSTOM_FFMPEG_DIR / "ffmpeg"
CUSTOM_FFPROBE = CUSTOM_FFMPEG_DIR / "ffprobe"
FFMPEG = str(CUSTOM_FFMPEG) if CUSTOM_FFMPEG.is_file() else shutil.which("ffmpeg")
FFPROBE = str(CUSTOM_FFPROBE) if CUSTOM_FFPROBE.is_file() else shutil.which("ffprobe")


EMOJI_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
]

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
]


def find_font():
    for candidate in FONT_CANDIDATES:
        if Path(candidate).is_file():
            return candidate
    raise RuntimeError(
        "Couldn't find a usable font. Install one with: "
        "sudo apt install fonts-dejavu-core"
    )



def find_emoji_font():
    for candidate in EMOJI_FONT_CANDIDATES:
        if Path(candidate).is_file():
            return candidate
    raise RuntimeError(
        "Couldn't find Noto Color Emoji. Install it with: "
        "sudo apt install fonts-noto-color-emoji"
    )


def is_emoji_base(char):
    cp = ord(char)
    return (
        0x1F000 <= cp <= 0x1FAFF
        or 0x2600 <= cp <= 0x27BF
        or 0x2300 <= cp <= 0x23FF
        or cp in (0x00A9, 0x00AE, 0x203C, 0x2049, 0x2122, 0x2139)
    )


def split_text_segments(text):
    """Split text into ordinary runs and complete common emoji sequences."""
    result = []
    i = 0
    while i < len(text):
        if not is_emoji_base(text[i]):
            j = i + 1
            while j < len(text) and not is_emoji_base(text[j]):
                j += 1
            result.append(("text", text[i:j]))
            i = j
            continue

        j = i + 1
        if (0x1F1E6 <= ord(text[i]) <= 0x1F1FF
                and j < len(text)
                and 0x1F1E6 <= ord(text[j]) <= 0x1F1FF):
            j += 1
        while j < len(text):
            cp = ord(text[j])
            if (cp in (0xFE0E, 0xFE0F, 0x20E3, 0x200D)
                    or 0x1F3FB <= cp <= 0x1F3FF
                    or 0xE0020 <= cp <= 0xE007F):
                is_zwj = text[j] == "\u200d"
                j += 1
                if is_zwj and j < len(text):
                    j += 1
            elif text[j - 1] == "\u200d" and is_emoji_base(text[j]):
                j += 1
            else:
                break
        result.append(("emoji", text[i:j]))
        i = j
    return result


def render_emoji(emoji, emoji_font, temp_dir, cache):
    """Render one color emoji with patched FFmpeg and cache its cropped PNG."""
    if emoji in cache:
        return cache[emoji]

    index = len(cache)
    text_file = temp_dir / f"emoji_{index:03d}.txt"
    png_file = temp_dir / f"emoji_{index:03d}.png"
    text_file.write_text(emoji, encoding="utf-8")
    vf = (
        f"drawtext=fontfile='{escape_filter_path(emoji_font)}':"
        f"textfile='{escape_filter_path(text_file)}':"
        "fontsize=109:fontcolor=white:x=24:y=24"
    )
    command = [
        FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
        "-f", "lavfi", "-i",
        "color=c=black@0.0:s=256x256:r=1,format=rgba",
        "-vf", vf, "-frames:v", "1", str(png_file),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode or not png_file.is_file():
        raise RuntimeError(
            f"Could not render emoji {emoji!r}: {result.stderr.strip()}"
        )

    image = Image.open(png_file).convert("RGBA")
    bbox = image.getchannel("A").getbbox()
    if not bbox:
        raise RuntimeError(
            f"FFmpeg produced a blank image for emoji {emoji!r}; "
            "check the patched FFmpeg build."
        )
    cache[emoji] = image.crop(bbox)
    return cache[emoji]


def make_caption_line(line, width, line_height, font_size,
                      normal_font, emoji_font, temp_dir, emoji_cache):
    """Compose regular text and color emoji into a centered transparent PNG."""
    canvas = Image.new("RGBA", (width, line_height), (0, 0, 0, 0))
    if not line:
        return canvas

    font = ImageFont.truetype(normal_font, font_size)
    segments = []
    total_width = 0
    for kind, value in split_text_segments(line):
        if kind == "text":
            segment_width = font.getlength(value)
            segments.append((kind, value, segment_width))
        else:
            emoji_image = render_emoji(value, emoji_font, temp_dir, emoji_cache)
            emoji_height = font_size
            emoji_width = max(
                1, round(emoji_image.width * emoji_height / emoji_image.height)
            )
            emoji_image = emoji_image.resize(
                (emoji_width, emoji_height), getattr(Image, "Resampling", Image).LANCZOS
            )
            segments.append((kind, emoji_image, emoji_width))
        total_width += segments[-1][2]

    x = round((width - total_width) / 2)
    draw = ImageDraw.Draw(canvas)
    bbox = font.getbbox("Ag")
    text_y = round((line_height - (bbox[3] - bbox[1])) / 2 - bbox[1])
    for kind, value, segment_width in segments:
        if kind == "text":
            draw.text((x, text_y), value, font=font, fill=(255, 255, 255, 255))
        else:
            canvas.alpha_composite(
                value, (x, round((line_height - value.height) / 2))
            )
        x += round(segment_width)
    return canvas


def wrap_text(text, max_chars):
    """Wrap paragraphs without splitting words; retain blank paragraph gaps."""
    result = []
    for paragraph in text.splitlines():
        if not paragraph.strip():
            result.append("")
        else:
            result.extend(textwrap.wrap(
                paragraph.strip(),
                width=max_chars,
                break_long_words=False,
                break_on_hyphens=False,
            ) or [""])
    while result and not result[-1]:
        result.pop()
    return result


def escape_filter_path(path):
    # Temporary paths are generated under /tmp and normally contain no special
    # characters, but escape FFmpeg filter syntax characters defensively.
    value = str(path)
    for char in ("\\", ":", "'", ",", "[", "]"):
        value = value.replace(char, "\\" + char)
    return value


def unique_output_path(source):
    candidate = source.with_name(source.stem + "_with_caption.mp4")
    index = 2
    while candidate.exists():
        candidate = source.with_name(f"{source.stem}_with_caption_{index}.mp4")
        index += 1
    return candidate


def main():
    parser = argparse.ArgumentParser(
        description="Add a black banner with centered white text above a video."
    )
    parser.add_argument("video", help="Input video file")
    parser.add_argument(
        "-o", "--output",
        help="Output MP4 path (default: <input>_with_caption.mp4; never overwrites)",
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

    print("Enter the body text one line at a time. Enter END on its own line when done.")
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
        font = find_font()
        emoji_font = find_emoji_font()
    except RuntimeError as exc:
        sys.exit(f"Error: {exc}")

    # Read source dimensions using ffprobe.
    probe = subprocess.run(
        [
            FFPROBE, "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "csv=s=x:p=0", str(source),
        ],
        check=True, capture_output=True, text=True,
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

    body_height = sum(body_line_height if line else int(body_line_height * 0.55)
                      for line in body_rows)
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

    output = Path(args.output).expanduser() if args.output else unique_output_path(source)
    if output.exists():
        sys.exit(f"Error: output already exists, refusing to overwrite: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="caption_banner_") as temp_name:
        temp_dir = Path(temp_name)
        overlays = []
        y = top_margin

        def add_line(line, size, y_position, line_height):
            overlays.append((line, size, y_position, line_height))
            return y_position + line_height

        for line in title_rows:
            y = add_line(line, title_size, y, title_line_height)

        y += gap_after_title
        for line in body_rows:
            if not line:
                y += int(body_line_height * 0.55)
            else:
                y = add_line(line, body_size, y, body_line_height)

        emoji_cache = {}
        line_pngs = []
        line_positions = []
        for index, (line, size, ypos, line_height) in enumerate(overlays):
            image = make_caption_line(
                line, width, line_height, size, font, emoji_font,
                temp_dir, emoji_cache
            )
            png_path = temp_dir / f"line_{index:03d}.png"
            image.save(png_path)
            line_pngs.append(png_path)
            line_positions.append(ypos)

        filter_parts = [
            f"[0:v]pad=iw:ih+{banner_height}:0:{banner_height}:color=black[base0]"
        ]
        for index, ypos in enumerate(line_positions):
            filter_parts.append(f"[{index + 1}:v]format=rgba[line{index}]")
            filter_parts.append(
                f"[base{index}][line{index}]"
                f"overlay=x=0:y={ypos}:shortest=1[base{index + 1}]"
            )

        command = [FFMPEG, "-hide_banner", "-i", str(source)]
        for png_path in line_pngs:
            command.extend(["-loop", "1", "-framerate", "25", "-i", str(png_path)])
        command.extend([
            "-filter_complex", ";".join(filter_parts),
            "-map", f"[base{len(line_pngs)}]", "-map", "0:a?",
            "-c:v", "libx264", "-crf", "18", "-preset", "medium",
            "-c:a", "copy", "-movflags", "+faststart",
            str(output),
        ])

        print(f"\nFFmpeg: {FFMPEG}")
        print(f"Input:  {source}")
        print(f"Output: {output}")
        print(f"Banner: {width}x{banner_height}; final video: {width}x{height + banner_height}")
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