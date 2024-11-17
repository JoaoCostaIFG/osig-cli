import io
import importlib

import logging
import requests
from PIL import Image, ImageFont


logger = logging.getLogger(__name__)


def get_image_dimensions(site):
    if site.lower() == "meta":
        width, height = 1200, 630
    else:  # default to X (Twitter)
        width, height = 1600, 900

    return int(width / 2), int(height / 2)


def draw_wrapped_text(
    draw,
    text,
    font,
    max_width,
    y_position,
    text_spacing,
    text_color,
    width,
    align="left",
    is_title=False,
    height=None,
):
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = font.getbbox(test_line)
        if bbox[2] <= max_width:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    for line in lines:
        bbox = font.getbbox(line)
        left_margin = (width - bbox[2]) // 2 if align == "center" else 0

        if is_title and height:
            bold_offset = int(height * 0.002)
            for offset_x in range(-bold_offset - 1, bold_offset + 1):
                for offset_y in range(-bold_offset, bold_offset + 1):
                    draw.text(
                        (left_margin + offset_x, y_position + offset_y),
                        line,
                        font=font,
                        fill=text_color,
                    )
        else:
            draw.text((left_margin, y_position), line, font=font, fill=text_color)

        y_position += bbox[3] - bbox[1] + text_spacing

    return y_position


def load_font(font, size):
    try:
        with importlib.resources.path(
            "osig_cli.resources.fonts", f"{font}.ttc"
        ) as font_path:
            return ImageFont.truetype(font_path, size)
    except Exception as e:
        logger.error("Error loading font: [font=%s], [error=%s]", font, str(e))
        return ImageFont.load_default().font_variant(size=size)


def create_image_buffer(img):
    buffer = io.BytesIO()
    img = img.convert("RGB")
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def load_and_resize_image(image_url, width, height):
    response = requests.get(image_url)
    img = Image.open(io.BytesIO(response.content)).convert("RGB")
    return img.resize((width, height), Image.LANCZOS)
