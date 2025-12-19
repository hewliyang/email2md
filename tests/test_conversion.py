"""Tests for MSG to EML conversion."""

import pytest

from email2md import _msg_to_eml, _read_input


class TestMsgToEmlConversion:
    """Test conversion of .msg format to .eml."""

    def test_msg_to_eml_with_real_fixture(self, test_msg_file) -> None:
        """Should convert real .msg file to .eml format."""
        msg_bytes = test_msg_file.read_bytes()
        eml_bytes = _msg_to_eml(msg_bytes)

        # Should produce valid EML (starts with headers)
        assert eml_bytes.startswith(b"From:") or b"\nFrom:" in eml_bytes[:500]
        assert isinstance(eml_bytes, bytes)
        assert len(eml_bytes) > 0

    def test_msg_to_eml_invalid_data(self) -> None:
        """Should raise error for invalid MSG data."""
        invalid_data = b"not a valid msg file"
        with pytest.raises(Exception):  # extract_msg will raise
            _msg_to_eml(invalid_data)


class TestReadInput:
    """Test reading input from various sources."""

    def test_read_from_bytes(self, simple_eml_bytes: bytes) -> None:
        """Should read email from bytes."""
        data, fmt = _read_input(simple_eml_bytes)
        assert data == simple_eml_bytes
        assert fmt == ".eml"

    def test_read_from_path(self, test_msg_file) -> None:
        """Should read email from file path."""
        data, fmt = _read_input(test_msg_file)
        assert isinstance(data, bytes)
        assert len(data) > 0
        assert fmt == ".msg"

    def test_read_from_string_path(self, test_msg_file) -> None:
        """Should read email from string path."""
        data, fmt = _read_input(str(test_msg_file))
        assert isinstance(data, bytes)
        assert len(data) > 0
        assert fmt == ".msg"

    def test_read_detects_msg_format(self, test_msg_file) -> None:
        """Should detect .msg format from magic bytes."""
        _, fmt = _read_input(test_msg_file)
        assert fmt == ".msg"

    def test_read_detects_eml_format(self, tmp_path, simple_eml_bytes: bytes) -> None:
        """Should detect .eml format."""
        eml_file = tmp_path / "test.eml"
        eml_file.write_bytes(simple_eml_bytes)
        _, fmt = _read_input(eml_file)
        assert fmt == ".eml"

    def test_read_warns_on_extension_mismatch(
        self, tmp_path, simple_eml_bytes: bytes, caplog
    ) -> None:
        """Should warn when extension doesn't match detected format."""
        # Write EML data to .msg file
        wrong_ext = tmp_path / "test.msg"
        wrong_ext.write_bytes(simple_eml_bytes)

        _read_input(wrong_ext)
        assert "doesn't match detected format" in caplog.text

    def test_read_nonexistent_file(self) -> None:
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            _read_input("/nonexistent/file.eml")

    def test_read_msg_magic_bytes_detection(self, msg_magic_bytes: bytes) -> None:
        """Should detect MSG from magic bytes even with wrong extension."""
        data = msg_magic_bytes + b"fake msg data"
        _, fmt = _read_input(data)
        assert fmt == ".msg"
