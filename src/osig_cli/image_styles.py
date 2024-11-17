#!/usr/bin/env python3

from abc import ABC
from io import BytesIO
from typing import override
import argparse
from sys import argv
from pathlib import Path

from PIL import Image, ImageDraw
import logging

from osig_cli.image_utils import (
    create_image_buffer,
    draw_wrapped_text,
    get_image_dimensions,
    load_and_resize_image,
    load_font,
)

logger = logging.getLogger(__name__)


class ImageData(ABC):
    def __init__(
        self,
        site: str = "",
        font: str = "",
        title: str = "",
        subtitle: str = "",
        image_url: str = "",
    ) -> None:
        self.site = site
        self.font = font
        self.title = title
        self.subtitle = subtitle
        self.image_url = image_url

    @property
    def style(self):
        raise NotImplementedError()

    def generate(self) -> BytesIO:
        raise NotImplementedError()

    def output(self, file_path: Path) -> None:
        image_buf = self.generate()
        with open(file_path, "wb+") as f:
            f.write(image_buf.getbuffer())


class LogoImage(ImageData):
    def __init__(
        self,
        site: str = "",
        font: str = "",
        title: str = "",
        subtitle: str = "",
        image_url: str = "",
    ) -> None:
        super().__init__(site, font, title, subtitle, image_url)

    @property
    def style(self):
        return "base"

    def __repr__(self) -> str:
        return f"LogoImage([site={self.site}], [font={self.font}], [title={self.title}], [subtitle={self.subtitle}], [image_url={self.image_url}])"

    @override
    def generate(self):
        logger.info("Generating logo OG image: %s", self)
        width, height = get_image_dimensions(self.site)

        background_color = (30, 30, 30)  # Almost black
        img = Image.new("RGB", (width, height), color=background_color)

        draw = ImageDraw.Draw(img)
        text_color = (255, 255, 255)  # White text

        title_font = load_font(self.font, int(height * 0.08))
        subtitle_font = load_font(self.font, int(height * 0.05))

        if self.image_url:
            logo = load_and_resize_image(
                self.image_url, int(height * 0.4), int(height * 0.4)
            )
            logo = logo.convert("RGBA")

            mask = Image.new("L", logo.size, 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0) + logo.size, fill=255)

            logo = Image.composite(
                logo, Image.new("RGBA", logo.size, (0, 0, 0, 0)), mask
            )

            logo_x = (width - logo.width) // 2
            logo_y = int(height * 0.15)

            img.paste(logo, (logo_x, logo_y), logo)

        # Calculate text positions and dimensions
        left_margin = int(width * 0.05)
        text_spacing = int(height * 0.02)
        max_text_width = width - 2 * left_margin

        title_y = int(height * 0.62)
        subtitle_y = int(height * 0.72)

        # Draw title with text wrapping
        draw_wrapped_text(
            draw,
            self.title,
            title_font,
            max_text_width,
            title_y,
            text_spacing,
            text_color,
            width,
            align="center",
            is_title=True,
            height=height,
        )

        # Draw subtitle with text wrapping
        draw_wrapped_text(
            draw,
            self.subtitle,
            subtitle_font,
            max_text_width,
            subtitle_y,
            text_spacing,
            text_color,
            width,
            align="center",
        )

        return create_image_buffer(img)


class BaseImage(ImageData):
    def __init__(
        self,
        site: str = "",
        font: str = "",
        title: str = "",
        subtitle: str = "",
        image_url: str = "",
        eyebrow: str = "",
    ) -> None:
        super().__init__(site, font, title, subtitle, image_url)
        self.eyebrow = eyebrow

    @property
    def style(self):
        return "base"

    def __repr__(self) -> str:
        return f"BaseImage([site={self.site}], [font={self.font}], [title={self.title}], [subtitle={self.subtitle}], [eyebrow={self.eyebrow}], [image_url={self.image_url}])"

    @override
    def generate(self) -> BytesIO:
        logger.info("Generating base OG image: %s", self)
        width, height = get_image_dimensions(self.site)

        if self.image_url:
            img = load_and_resize_image(self.image_url, width, height)
        else:
            img = Image.new("RGB", (width, height), color=(255, 255, 255))

        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 180))
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay)

        draw = ImageDraw.Draw(img)
        text_color = (255, 255, 255)  # Always use white text

        title_font = load_font(self.font, int(height * 0.1))
        subtitle_font = load_font(self.font, int(height * 0.05))
        eyebrow_font = load_font(self.font, int(height * 0.03))

        left_margin = int(width * 0.05)
        top_margin = int(height * 0.3)
        text_spacing = int(height * 0.02)

        def draw_wrapped_text(text, font, max_width, y_position, is_title=False):
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
                if is_title:
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
                    draw.text(
                        (left_margin, y_position), line, font=font, fill=text_color
                    )
                y_position += bbox[3] - bbox[1] + text_spacing
            return y_position

        current_y = top_margin
        max_text_width = width - 2 * left_margin

        if self.eyebrow:
            current_y = draw_wrapped_text(
                self.eyebrow.upper(), eyebrow_font, max_text_width, current_y
            )
            current_y += text_spacing

        if self.title:
            print(self.title)
            current_y = draw_wrapped_text(
                self.title.upper(), title_font, max_text_width, current_y, is_title=True
            )
            current_y += text_spacing * 3.5

        if self.subtitle:
            if len(self.subtitle) > 150:
                self.subtitle = self.subtitle[:147] + "..."
            draw_wrapped_text(self.subtitle, subtitle_font, max_text_width, current_y)

        return create_image_buffer(img)
