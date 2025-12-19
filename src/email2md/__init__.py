import logging
import re
import sys
from base64 import b64encode
from dataclasses import dataclass, field
from email import message_from_bytes
from pathlib import Path
from typing import cast

import extract_msg
import markdownify

__all__ = [
    "ConvertOptions",
    "to_html",
    "to_markdown",
    "SUPPORTED_FORMATS",
    "DEFAULT_HEADERS",
]

logger = logging.getLogger("email2md")

SUPPORTED_FORMATS = {".eml", ".msg"}
_MSG_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
HTML_TAGS = [
    "table",
    "tr",
    "td",
    "div",
    "span",
    "p",
    "a",
    "img",
    "strong",
    "b",
    "em",
    "i",
    "ul",
    "ol",
    "li",
    "br",
    "hr",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
]


DEFAULT_HEADERS = ("From", "To", "Subject", "Date")


@dataclass
class ConvertOptions:
    """Configuration options for email conversion.

    Attributes:
        save_attachments: Save embedded attachments to output_dir.
        include_images: Include images in output. If False, images are stripped.
        inline_images: Embed images as base64 data URIs. If False, reference
            saved attachment files (requires save_attachments=True).
        output_dir: Directory for saving attachments. Defaults to current dir.
        include_headers: Prepend email headers to output.
        headers: Which headers to include. Defaults to From, To, Subject, Date.
        fallback_to_plain: Use plain text body if no HTML part exists.
        include_attachment_list: Include list of non-image attachments below headers.
        include_hrefs: Include href attributes in <a> tags. If False, strips hrefs.
    """

    save_attachments: bool = False
    include_images: bool = True
    inline_images: bool = True
    output_dir: str | Path = field(default_factory=Path.cwd)
    include_headers: bool = True
    headers: tuple[str, ...] = DEFAULT_HEADERS
    fallback_to_plain: bool = True
    include_attachment_list: bool = True
    include_hrefs: bool = True

    def __post_init__(self) -> None:
        if isinstance(self.output_dir, str):
            object.__setattr__(self, "output_dir", Path(self.output_dir))
        if not self.inline_images and not self.save_attachments:
            raise ValueError(
                "save_attachments must be True when inline_images is False "
                "(need saved files to reference)"
            )


def _detect_format(data: bytes) -> str:
    if data[:8] == _MSG_MAGIC:
        return ".msg"
    return ".eml"


def _msg_to_eml(msg_bytes: bytes) -> bytes:
    """Convert .msg bytes to .eml format using extract-msg."""
    msg = extract_msg.openMsg(msg_bytes)
    try:
        email_message = msg.asEmailMessage()  # type: ignore[union-attr]
        return email_message.as_bytes()
    finally:
        msg.close()


def _read_input(source: str | Path | bytes | None = None) -> tuple[bytes, str]:
    """Read email bytes from path, bytes, or stdin.

    Format is auto-detected from content using magic bytes.
    Logs a warning if file extension doesn't match detected format.

    Returns:
        Tuple of (email_bytes, detected_format like '.eml' or '.msg')
    """
    if source is None:
        # Read from stdin
        data = sys.stdin.buffer.read()
        extension = None
    elif isinstance(source, bytes):
        data = source
        extension = None
    else:
        path = Path(source)
        data = path.read_bytes()
        extension = path.suffix.lower() if path.suffix else None

    detected = _detect_format(data)

    if extension is not None and extension != detected:
        logger.warning(
            f"File extension '{extension}' doesn't match detected format '{detected}'. "
            f"Using detected format."
        )

    return data, detected


def to_html(
    source: str | Path | bytes | None = None,
    options: ConvertOptions | None = None,
) -> str:
    """Convert email to HTML.

    Args:
        source: Path to .eml/.msg file, raw bytes, or None to read from stdin.
        options: Conversion options. Uses defaults if not provided.

    Returns:
        HTML string with embedded images (if include_images is True).
    """
    if options is None:
        options = ConvertOptions()

    output_dir = cast(Path, options.output_dir)

    raw_bytes, suffix = _read_input(source)
    eml_bytes = _msg_to_eml(raw_bytes) if suffix == ".msg" else raw_bytes
    msg = message_from_bytes(eml_bytes)

    cid_map: dict[str, tuple[str, bytes, str | None]] = {}
    html_content = ""
    plain_content = ""
    attachments: list[str] = []

    for part in msg.walk():
        content_type = part.get_content_type().rstrip("\x00")
        content_id = part.get("Content-ID", "").strip("<>").rstrip("\x00")
        filename = part.get_filename()
        if filename:
            filename = filename.rstrip("\x00")

        if content_type == "text/html":
            payload = part.get_payload(decode=True)
            charset = part.get_content_charset() or "utf-8"
            html_content = payload.decode(charset) if isinstance(payload, bytes) else ""
        elif content_type == "text/plain" and not filename:
            payload = part.get_payload(decode=True)
            charset = part.get_content_charset() or "utf-8"
            plain_content = (
                payload.decode(charset) if isinstance(payload, bytes) else ""
            )
        elif content_id or filename:
            payload = part.get_payload(decode=True)
            if isinstance(payload, bytes):
                # Track in cid_map for inline image replacement
                if content_id:
                    cid_map[content_id] = (content_type, payload, filename)

                # Track non-image attachments for listing
                if filename and not content_type.startswith("image/"):
                    attachments.append(filename)

                if options.save_attachments and filename:
                    output_dir.mkdir(parents=True, exist_ok=True)
                    (output_dir / filename).write_bytes(payload)

    # Fallback to plain text if no HTML
    if not html_content and plain_content and options.fallback_to_plain:
        # Convert plain text to basic HTML
        escaped = (
            plain_content.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        html_content = f"<pre>{escaped}</pre>"

    if not options.include_images:
        # Strip all img tags
        html_content = re.sub(
            r"<img\s[^>]*>", "", html_content, flags=re.IGNORECASE | re.DOTALL
        )
    else:

        def cid_to_uri(cid: str) -> str | None:
            if cid not in cid_map:
                return None
            mime, data, filename = cid_map[cid]
            if options.inline_images:
                return f"data:{mime};base64,{b64encode(data).decode('ascii')}"
            else:
                # Reference saved file
                return filename if filename else None

        def replace_img_tag(match: re.Match[str]) -> str:
            tag, cid = match.group(0), match.group(1)
            uri = cid_to_uri(cid)
            if uri is None:
                return tag
            tag = tag.replace(f"cid:{cid}", uri)
            _, _, filename = cid_map[cid]
            if filename and not re.search(r"\balt\s*=", tag, re.IGNORECASE):
                tag = re.sub(r"/?>$", f' alt="{filename}">', tag)
            return tag

        def replace_other_cid(match: re.Match[str]) -> str:
            return cid_to_uri(match.group(1)) or match.group(0)

        html_content = re.sub(
            r'<img\s[^>]*src=["\']cid:([^"\']+)["\'][^>]*/?>',
            replace_img_tag,
            html_content,
            flags=re.IGNORECASE,
        )
        html_content = re.sub(r"cid:([^\"\'\s>]+)", replace_other_cid, html_content)

    # Strip href attributes from <a> tags if requested
    if not options.include_hrefs:
        html_content = re.sub(
            r'(<a\s[^>]*)href=["\'][^"\']*["\']([^>]*>)',
            r"\1\2",
            html_content,
            flags=re.IGNORECASE,
        )
        # Also handle hrefs without quotes (though rare)
        html_content = re.sub(
            r"(<a\s[^>]*)href=[^\s>]+([^>]*>)",
            r"\1\2",
            html_content,
            flags=re.IGNORECASE,
        )

    # Prepend headers (and attachment list) if requested
    if options.include_headers:
        header_lines = []
        for header_name in options.headers:
            value = msg.get(header_name)
            if value:
                escaped_value = (
                    str(value)
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )
                header_lines.append(f"<strong>{header_name}:</strong> {escaped_value}")
        if header_lines:
            headers_html = "<br>\n".join(header_lines)
            # Add attachment list directly below headers if requested
            if options.include_attachment_list and attachments:
                attachment_items = "\n".join(f"<li>{a}</li>" for a in attachments)
                headers_html += (
                    f'\n<br>\n<div class="attachments">'
                    f"<strong>Attachments:</strong>\n<ul>\n{attachment_items}\n</ul></div>"
                )
            html_content = (
                f'<div class="email-headers">{headers_html}</div>\n<hr>\n{html_content}'
            )
    elif options.include_attachment_list and attachments:
        # Headers disabled but attachment list enabled - put at top
        attachment_items = "\n".join(f"<li>{a}</li>" for a in attachments)
        html_content = (
            f'<div class="attachments">'
            f"<strong>Attachments:</strong>\n<ul>\n{attachment_items}\n</ul></div>"
            f"\n<hr>\n{html_content}"
        )

    return html_content


def to_markdown(
    source: str | Path | bytes | None = None,
    options: ConvertOptions | None = None,
) -> str:
    """Convert email to Markdown.

    Args:
        source: Path to .eml/.msg file, raw bytes, or None to read from stdin.
        options: Conversion options. Uses defaults if not provided.

    Returns:
        Markdown string.
    """
    html = to_html(source, options)
    return markdownify.markdownify(
        html,
        keep_inline_images_in=HTML_TAGS,
        heading_style=markdownify.ATX,
    )
