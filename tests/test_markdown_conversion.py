"""Tests for to_markdown() conversion function."""

import re
from pathlib import Path


from email2md import ConvertOptions, to_markdown


class TestMarkdownConversion:
    """Test email to Markdown conversion."""

    def test_simple_eml_to_markdown(self, simple_eml_bytes: bytes) -> None:
        """Should convert simple EML to Markdown."""
        md = to_markdown(simple_eml_bytes)
        assert "# Hello World" in md
        assert "This is a test." in md

    def test_markdown_includes_headers(self, simple_eml_bytes: bytes) -> None:
        """Should include email headers in Markdown."""
        md = to_markdown(simple_eml_bytes)
        assert "**From:** sender@example.com" in md
        assert "**To:** recipient@example.com" in md
        assert "**Subject:** Test Email" in md
        assert "**Date:**" in md

    def test_markdown_without_headers(self, simple_eml_bytes: bytes) -> None:
        """Should exclude headers when requested."""
        opts = ConvertOptions(include_headers=False)
        md = to_markdown(simple_eml_bytes, opts)
        assert "**From:**" not in md
        assert "**To:**" not in md
        assert "# Hello World" in md

    def test_markdown_with_inline_images(self, eml_with_images: bytes) -> None:
        """Should include base64 images in Markdown."""
        md = to_markdown(eml_with_images)
        assert "![" in md  # Markdown image syntax
        assert "data:image/png;base64," in md

    def test_markdown_without_images(self, eml_with_images: bytes) -> None:
        """Should exclude images from Markdown."""
        opts = ConvertOptions(include_images=False)
        md = to_markdown(eml_with_images, opts)
        assert "![" not in md
        assert "data:image/png;base64," not in md

    def test_markdown_with_links(self, eml_with_links: bytes) -> None:
        """Should preserve links in Markdown."""
        md = to_markdown(eml_with_links)
        assert "[website](https://example.com)" in md
        assert "[link here](https://test.com)" in md

    def test_markdown_without_hrefs(self, eml_with_links: bytes) -> None:
        """Should strip hrefs from Markdown links."""
        opts = ConvertOptions(include_hrefs=False)
        md = to_markdown(eml_with_links, opts)
        # Should have link text but no URLs
        assert "website" in md
        assert "link here" in md
        assert "https://example.com" not in md
        assert "https://test.com" not in md

    def test_markdown_attachment_list(self, eml_with_attachments: bytes) -> None:
        """Should include attachment list in Markdown."""
        md = to_markdown(eml_with_attachments)
        assert "**Attachments:**" in md
        assert "document.pdf" in md

    def test_markdown_plain_fallback(self, eml_plain_only: bytes) -> None:
        """Should convert plain text to Markdown."""
        md = to_markdown(eml_plain_only)
        assert "This is plain text only." in md
        assert "No HTML here." in md

    def test_real_msg_to_markdown(self, test_msg_file) -> None:
        """Should convert real .msg file to Markdown."""
        md = to_markdown(test_msg_file)
        assert isinstance(md, str)
        assert len(md) > 0

    def test_markdown_formatting_preserved(self, simple_eml_bytes: bytes) -> None:
        """Should preserve basic markdown formatting from HTML."""
        md = to_markdown(simple_eml_bytes)
        # Headers should use ATX style (#)
        assert re.search(r"^# ", md, re.MULTILINE) or "# " in md

    def test_markdown_reference_images(
        self, tmp_path: Path, eml_with_images: bytes
    ) -> None:
        """Should reference image files in Markdown."""
        opts = ConvertOptions(
            inline_images=False,
            save_attachments=True,
            output_dir=tmp_path,
        )
        md = to_markdown(eml_with_images, opts)
        assert "test.png" in md
        assert "data:image/png;base64," not in md
        assert (tmp_path / "test.png").exists()

    def test_markdown_custom_headers(self, simple_eml_bytes: bytes) -> None:
        """Should include only specified headers in Markdown."""
        opts = ConvertOptions(headers=("Subject",))
        md = to_markdown(simple_eml_bytes, opts)
        assert "**Subject:** Test Email" in md
        assert "**From:**" not in md
        assert "**To:**" not in md
        assert "**Date:**" not in md

    def test_markdown_no_attachment_list(self, eml_with_attachments: bytes) -> None:
        """Should exclude attachment list when requested."""
        opts = ConvertOptions(include_attachment_list=False)
        md = to_markdown(eml_with_attachments, opts)
        assert "**Attachments:**" not in md
        assert "document.pdf" not in md

    def test_markdown_save_attachments(
        self, tmp_path: Path, eml_with_attachments: bytes
    ) -> None:
        """Should save attachments when converting to Markdown."""
        opts = ConvertOptions(save_attachments=True, output_dir=tmp_path)
        md = to_markdown(eml_with_attachments, opts)
        assert (tmp_path / "document.pdf").exists()
        # Should still list attachment in output
        assert "document.pdf" in md
