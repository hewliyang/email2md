"""Tests for email format detection."""

from email2md import _detect_format


class TestFormatDetection:
    """Test email format detection from magic bytes."""

    def test_detect_msg_format(self, msg_magic_bytes: bytes) -> None:
        """Should detect .msg format from magic bytes."""
        data = msg_magic_bytes + b"some other data"
        assert _detect_format(data) == ".msg"

    def test_detect_eml_format(self, simple_eml_bytes: bytes) -> None:
        """Should detect .eml format (default when not MSG)."""
        assert _detect_format(simple_eml_bytes) == ".eml"

    def test_detect_eml_from_arbitrary_data(self) -> None:
        """Should default to .eml for unknown data."""
        data = b"random data that isn't MSG format"
        assert _detect_format(data) == ".eml"

    def test_detect_msg_exact_magic(self) -> None:
        """Should detect MSG with exact 8-byte magic."""
        magic = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
        assert _detect_format(magic) == ".msg"

    def test_detect_eml_when_magic_not_at_start(self, msg_magic_bytes: bytes) -> None:
        """Should detect .eml when magic bytes not at file start."""
        data = b"prefix" + msg_magic_bytes
        assert _detect_format(data) == ".eml"

    def test_detect_with_empty_data(self) -> None:
        """Should handle empty data gracefully."""
        assert _detect_format(b"") == ".eml"

    def test_detect_with_short_data(self) -> None:
        """Should handle data shorter than magic bytes."""
        assert _detect_format(b"\xd0\xcf") == ".eml"
