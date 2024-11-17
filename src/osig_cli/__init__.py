import argparse
from pathlib import Path
from sys import argv

from osig_cli.image_styles import LogoImage, BaseImage


def main():
    def add_common_args(parser):
        site_choices = ["x", "meta"]
        parser.add_argument(
            "-s",
            "--site",
            help="Either x or meta",
            choices=site_choices,
            type=str,
            default=site_choices[0],
        )
        font_choices = ["helvetica", "markerfelt", "papyrus"]
        parser.add_argument(
            "-f",
            "--font",
            help="The text font to use",
            type=str,
            choices=font_choices,
            default=font_choices[0],
        )
        parser.add_argument("-t", "--title", help="The title", type=str, default="")
        parser.add_argument(
            "-u",
            "--subtitle",
            help="The small text below the title",
            type=str,
            default="",
        )
        parser.add_argument(
            "-i",
            "--image-url",
            help="Image URL for logo/background",
            type=str,
            default="",
        )
        parser.add_argument(
            "-o", "--output", help="Outfile name", type=Path, required=True
        )

    def handle_logo(args):
        LogoImage(
            args.site, args.font, args.title, args.subtitle, args.image_url
        ).output(args.output)

    def handle_base(args):
        BaseImage(
            args.site,
            args.font,
            args.title,
            args.subtitle,
            args.image_url,
            args.eyebrow,
        ).output(args.output)

    parser = argparse.ArgumentParser("osig_cli")
    subparsers = parser.add_subparsers(required=True)

    parser_logo = subparsers.add_parser("logo")
    add_common_args(parser_logo)
    parser_logo.set_defaults(func=handle_logo)

    parser_base = subparsers.add_parser("base")
    add_common_args(parser_base)
    parser_base.add_argument(
        "-e",
        "--eyebrow",
        help="The small text on top of the title",
        type=str,
        default="",
    )
    parser_base.set_defaults(func=handle_base)

    args, _ = parser.parse_known_args(argv[1:])
    args.func(args)
