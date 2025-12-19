"""CLI entry point for email2md."""

import argparse
import sys
from pathlib import Path

from . import DEFAULT_HEADERS, ConvertOptions, to_html, to_markdown


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="email2md",
        description="Convert email files (.eml, .msg) to HTML or Markdown.",
        epilog="""
Examples:
  # Convert to markdown (default)
  email2md message.eml

  # Convert to HTML
  email2md message.eml --html

  # Pipe from stdin (format auto-detected)
  cat message.msg | email2md

  # Minimal output (no headers, no images, no attachment list)
  email2md message.eml --no-headers --no-images --no-attachment-list

  # Save attachments and reference them (not inline base64)
  email2md message.eml --save-attachments --reference-images -o ./output

  # Only include specific headers
  email2md message.eml --header From --header Subject
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="Input email file (.eml or .msg). Reads from stdin if omitted.",
    )

    parser.add_argument(
        "--html",
        action="store_true",
        help="Output HTML instead of Markdown.",
    )

    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=Path.cwd(),
        help="Directory for saving attachments (default: current directory).",
    )

    parser.add_argument(
        "--save-attachments",
        "-a",
        action="store_true",
        help="Save embedded attachments to output directory.",
    )

    parser.add_argument(
        "--no-images",
        action="store_true",
        help="Strip images from output (cleaner markdown, no base64 noise).",
    )

    parser.add_argument(
        "--reference-images",
        "-r",
        action="store_true",
        help="Reference saved attachment files instead of inline base64. "
        "Requires --save-attachments.",
    )

    parser.add_argument(
        "--no-headers",
        action="store_true",
        help="Do not prepend email headers.",
    )

    parser.add_argument(
        "--header",
        action="append",
        default=[],
        metavar="NAME",
        help="Header to include (repeatable). Defaults to: "
        + ", ".join(DEFAULT_HEADERS),
    )

    parser.add_argument(
        "--no-fallback-plain",
        action="store_true",
        help="Do not fallback to plain text when HTML body is missing.",
    )

    parser.add_argument(
        "--no-attachment-list",
        action="store_true",
        help="Do not include a list of non-image attachments below headers.",
    )

    args = parser.parse_args()

    # Validate args
    if args.reference_images and not args.save_attachments:
        parser.error("--reference-images requires --save-attachments")

    # Build options
    try:
        options = ConvertOptions(
            save_attachments=args.save_attachments,
            include_images=not args.no_images,
            inline_images=not args.reference_images,
            output_dir=args.output_dir,
            include_headers=not args.no_headers,
            headers=tuple(args.header) if args.header else DEFAULT_HEADERS,
            fallback_to_plain=not args.no_fallback_plain,
            include_attachment_list=not args.no_attachment_list,
        )
    except ValueError as e:
        parser.error(str(e))

    # Convert
    try:
        if args.html:
            result = to_html(args.input, options)
        else:
            result = to_markdown(args.input, options)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        return 1

    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
