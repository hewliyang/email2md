"""Tests for to_html() conversion function."""

import email.message
import io
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import cast

from email2md import ConvertOptions, to_html


class TestHtmlConversion:
    """Test email to HTML conversion."""

    def test_simple_eml_to_html(self, simple_eml_bytes: bytes) -> None:
        """Should convert simple EML to HTML."""
        html = to_html(simple_eml_bytes)
        assert "<h1>Hello World</h1>" in html
        assert "<p>This is a test.</p>" in html

    def test_includes_headers_by_default(self, simple_eml_bytes: bytes) -> None:
        """Should include email headers by default."""
        html = to_html(simple_eml_bytes)
        assert "From:</strong> sender@example.com" in html
        assert "To:</strong> recipient@example.com" in html
        assert "Subject:</strong> Test Email" in html
        assert "Date:</strong>" in html
        assert '<div class="email-headers">' in html

    def test_exclude_headers(self, simple_eml_bytes: bytes) -> None:
        """Should exclude headers when requested."""
        opts = ConvertOptions(include_headers=False)
        html = to_html(simple_eml_bytes, opts)
        assert "From:</strong>" not in html
        assert "To:</strong>" not in html
        assert '<div class="email-headers">' not in html

    def test_custom_headers_only(self, simple_eml_bytes: bytes) -> None:
        """Should include only specified headers."""
        opts = ConvertOptions(headers=("From", "Subject"))
        html = to_html(simple_eml_bytes, opts)
        assert "From:</strong>" in html
        assert "Subject:</strong>" in html
        assert "To:</strong>" not in html
        assert "Date:</strong>" not in html

    def test_inline_images_as_base64(self, eml_with_images: bytes) -> None:
        """Should embed images as base64 data URIs by default."""
        html = to_html(eml_with_images)
        assert "data:image/png;base64," in html
        assert "cid:image001" not in html

    def test_exclude_images(self, eml_with_images: bytes) -> None:
        """Should strip images when include_images=False."""
        opts = ConvertOptions(include_images=False)
        html = to_html(eml_with_images, opts)
        assert "<img" not in html
        assert "data:image/png;base64," not in html

    def test_reference_images(self, tmp_path: Path, eml_with_images: bytes) -> None:
        """Should reference saved image files when inline_images=False."""
        opts = ConvertOptions(
            inline_images=False,
            save_attachments=True,
            output_dir=tmp_path,
        )
        html = to_html(eml_with_images, opts)

        # Should reference filename, not inline base64
        assert "test.png" in html
        assert "data:image/png;base64," not in html

        # Should save the file
        assert (tmp_path / "test.png").exists()

    def test_save_attachments(
        self, tmp_path: Path, eml_with_attachments: bytes
    ) -> None:
        """Should save attachments to output directory."""
        opts = ConvertOptions(save_attachments=True, output_dir=tmp_path)
        to_html(eml_with_attachments, opts)

        assert (tmp_path / "document.pdf").exists()
        content = (tmp_path / "document.pdf").read_bytes()
        assert content == b"Test document content"

    def test_default_output_dir_uses_input_file_directory(
        self, tmp_path: Path, eml_with_attachments: bytes
    ) -> None:
        eml_dir = tmp_path / "emails"
        eml_dir.mkdir()
        eml_file = eml_dir / "test.eml"
        eml_file.write_bytes(eml_with_attachments)

        opts = ConvertOptions(save_attachments=True, output_dir=None)
        to_html(eml_file, opts)

        assert (eml_dir / "document.pdf").exists()

    def test_default_output_dir_stdin_uses_cwd(
        self, monkeypatch, tmp_path: Path, eml_with_attachments: bytes
    ) -> None:
        monkeypatch.chdir(tmp_path)
        fake_stdin = SimpleNamespace(buffer=io.BytesIO(eml_with_attachments))
        monkeypatch.setattr(sys, "stdin", fake_stdin)

        opts = ConvertOptions(save_attachments=True, output_dir=None)
        to_html(None, opts)

        assert (tmp_path / "document.pdf").exists()

    def test_default_output_dir_bytes_uses_cwd(
        self, monkeypatch, tmp_path: Path, eml_with_attachments: bytes
    ) -> None:
        monkeypatch.chdir(tmp_path)

        opts = ConvertOptions(save_attachments=True, output_dir=None)
        to_html(eml_with_attachments, opts)

        assert (tmp_path / "document.pdf").exists()

    def test_attachment_list_included(self, eml_with_attachments: bytes) -> None:
        """Should list non-image attachments by default."""
        html = to_html(eml_with_attachments)
        assert "Attachments:</strong>" in html
        assert "document.pdf" in html
        assert '<div class="attachments">' in html

    def test_attachment_list_excluded(self, eml_with_attachments: bytes) -> None:
        """Should exclude attachment list when requested."""
        opts = ConvertOptions(include_attachment_list=False)
        html = to_html(eml_with_attachments, opts)
        assert "Attachments:</strong>" not in html
        assert '<div class="attachments">' not in html

    def test_attachment_list_without_headers(self, eml_with_attachments: bytes) -> None:
        """Should show attachment list at top when headers disabled."""
        opts = ConvertOptions(include_headers=False, include_attachment_list=True)
        html = to_html(eml_with_attachments, opts)
        assert "Attachments:</strong>" in html
        assert "document.pdf" in html
        # Should not have email-headers div
        assert '<div class="email-headers">' not in html

    def test_fallback_to_plain(self, eml_plain_only: bytes) -> None:
        """Should fallback to plain text when no HTML body."""
        html = to_html(eml_plain_only)
        assert "<pre>" in html
        assert "This is plain text only." in html
        assert "&lt;" not in html  # Should not double-escape

    def test_no_fallback_to_plain(self, eml_plain_only: bytes) -> None:
        """Should not fallback when fallback_to_plain=False."""
        opts = ConvertOptions(fallback_to_plain=False)
        html = to_html(eml_plain_only, opts)
        assert "<pre>" not in html
        # Should be mostly empty (just headers if enabled)

    def test_include_hrefs(self, eml_with_links: bytes) -> None:
        """Should include href attributes by default."""
        html = to_html(eml_with_links)
        assert 'href="https://example.com"' in html
        assert 'href="https://test.com"' in html

    def test_exclude_hrefs(self, eml_with_links: bytes) -> None:
        """Should strip href attributes when include_hrefs=False."""
        opts = ConvertOptions(include_hrefs=False)
        html = to_html(eml_with_links, opts)
        assert "href=" not in html
        assert "<a" in html  # Tags should still exist
        assert "website" in html  # Link text should remain
        assert "link here" in html

    def test_real_msg_file_conversion(self, test_msg_file) -> None:
        """Should convert real .msg file to HTML."""
        html = to_html(test_msg_file)
        assert isinstance(html, str)
        assert len(html) > 0
        # Should have some HTML structure
        assert "From:</strong>" in html or "<" in html

    def test_msg_from_bytes(self, test_msg_file) -> None:
        """Should handle .msg file passed as bytes."""
        msg_bytes = test_msg_file.read_bytes()
        html = to_html(msg_bytes)
        assert isinstance(html, str)
        assert len(html) > 0

    def test_image_alt_attribute_added(self, eml_with_images: bytes) -> None:
        """Should add alt attribute from filename if missing."""
        html = to_html(eml_with_images)
        assert 'alt="test.png"' in html or 'alt="Test Image"' in html

    def test_multiple_images(self) -> None:
        """Should handle multiple inline images."""
        msg = email.message.EmailMessage()
        msg["From"] = "test@example.com"
        msg["To"] = "recipient@example.com"
        msg["Subject"] = "Multiple Images"

        html = """
        <html><body>
            <img src="cid:img1">
            <img src="cid:img2">
        </body></html>
        """
        msg.add_alternative(html, subtype="html")

        img1 = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        img2 = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x02"

        payload = cast(list[email.message.EmailMessage], msg.get_payload())
        payload[0].add_related(img1, "image", "png", cid="img1", filename="1.png")
        payload[0].add_related(img2, "image", "png", cid="img2", filename="2.png")

        result = to_html(msg.as_bytes())
        assert "data:image/png;base64," in result
        assert result.count("data:image/png;base64,") == 2
