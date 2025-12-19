"""Shared pytest fixtures and test utilities."""

import email.message
from pathlib import Path
from typing import cast

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def test_msg_file(fixtures_dir: Path) -> Path:
    """Return path to the real-world test.msg file."""
    msg_path = fixtures_dir / "test.msg"
    if not msg_path.exists():
        pytest.skip(f"Test fixture not found: {msg_path}")
    return msg_path


@pytest.fixture
def simple_eml_bytes() -> bytes:
    """Generate a simple EML email with HTML body."""
    msg = email.message.EmailMessage()
    msg["From"] = "sender@example.com"
    msg["To"] = "recipient@example.com"
    msg["Subject"] = "Test Email"
    msg["Date"] = "Mon, 1 Jan 2024 12:00:00 +0000"
    msg.set_content("Plain text body")
    msg.add_alternative(
        "<html><body><h1>Hello World</h1><p>This is a test.</p></body></html>",
        subtype="html",
    )
    return msg.as_bytes()


@pytest.fixture
def eml_with_images() -> bytes:
    """Generate an EML with inline images."""
    msg = email.message.EmailMessage()
    msg["From"] = "sender@example.com"
    msg["To"] = "recipient@example.com"
    msg["Subject"] = "Email with Images"
    msg["Date"] = "Mon, 1 Jan 2024 12:00:00 +0000"

    # Add HTML body with cid reference
    html = """
    <html>
    <body>
        <p>Check out this image:</p>
        <img src="cid:image001" alt="Test Image">
    </body>
    </html>
    """
    msg.add_alternative(html, subtype="html")

    # Add inline image
    image_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    payload = cast(list[email.message.EmailMessage], msg.get_payload())
    payload[0].add_related(
        image_data,
        maintype="image",
        subtype="png",
        cid="image001",
        filename="test.png",
    )

    return msg.as_bytes()


@pytest.fixture
def eml_with_attachments() -> bytes:
    """Generate an EML with file attachments."""
    msg = email.message.EmailMessage()
    msg["From"] = "sender@example.com"
    msg["To"] = "recipient@example.com"
    msg["Subject"] = "Email with Attachments"
    msg["Date"] = "Mon, 1 Jan 2024 12:00:00 +0000"

    msg.set_content(
        "<html><body><p>Email with attachments</p></body></html>", subtype="html"
    )

    # Add non-image attachment
    msg.add_attachment(
        b"Test document content",
        maintype="application",
        subtype="pdf",
        filename="document.pdf",
    )

    return msg.as_bytes()


@pytest.fixture
def eml_plain_only() -> bytes:
    """Generate an EML with only plain text (no HTML)."""
    msg = email.message.EmailMessage()
    msg["From"] = "sender@example.com"
    msg["To"] = "recipient@example.com"
    msg["Subject"] = "Plain Text Only"
    msg["Date"] = "Mon, 1 Jan 2024 12:00:00 +0000"
    msg.set_content("This is plain text only.\nNo HTML here.")
    return msg.as_bytes()


@pytest.fixture
def eml_with_links() -> bytes:
    """Generate an EML with hyperlinks."""
    msg = email.message.EmailMessage()
    msg["From"] = "sender@example.com"
    msg["To"] = "recipient@example.com"
    msg["Subject"] = "Email with Links"
    msg["Date"] = "Mon, 1 Jan 2024 12:00:00 +0000"

    html = """
    <html>
    <body>
        <p>Visit our <a href="https://example.com">website</a>.</p>
        <p>Another <a href="https://test.com">link here</a>.</p>
    </body>
    </html>
    """
    msg.set_content(html, subtype="html")
    return msg.as_bytes()


@pytest.fixture
def msg_magic_bytes() -> bytes:
    """Return MSG format magic bytes."""
    return b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
