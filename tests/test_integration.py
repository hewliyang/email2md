"""Integration tests using real-world email fixtures."""

from email2md import to_html, to_markdown


class TestRealWorldFixtures:
    """Integration tests with actual email files."""

    def test_real_msg_to_html(self, test_msg_file) -> None:
        """Should successfully convert real .msg file to HTML."""
        html = to_html(test_msg_file)

        # Basic validation
        assert isinstance(html, str)
        assert len(html) > 100  # Should have substantial content

        # Should have some structure
        assert "From:</strong>" in html or "<" in html

    def test_real_msg_to_markdown(self, test_msg_file) -> None:
        """Should successfully convert real .msg file to Markdown."""
        md = to_markdown(test_msg_file)

        # Basic validation
        assert isinstance(md, str)
        assert len(md) > 50  # Should have content

    def test_real_msg_bytes_vs_path(self, test_msg_file) -> None:
        """Should produce same result from bytes vs path."""
        html_from_path = to_html(test_msg_file)
        html_from_bytes = to_html(test_msg_file.read_bytes())

        # Should produce similar output (exact match may differ in whitespace)
        assert len(html_from_path) > 0
        assert len(html_from_bytes) > 0
        # Core content should match
        assert html_from_path == html_from_bytes
