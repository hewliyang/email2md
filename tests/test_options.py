"""Tests for ConvertOptions validation and behavior."""

from pathlib import Path

import pytest

from email2md import ConvertOptions


class TestConvertOptions:
    """Test ConvertOptions dataclass validation and defaults."""

    def test_output_dir_string_conversion(self) -> None:
        """Should convert string output_dir to Path."""
        opts = ConvertOptions(output_dir="/tmp/test")
        assert isinstance(opts.output_dir, Path)
        assert opts.output_dir == Path("/tmp/test")

    def test_invalid_combo_reference_without_save(self) -> None:
        """Should reject inline_images=False without save_attachments=True."""
        with pytest.raises(ValueError, match="save_attachments must be True"):
            ConvertOptions(inline_images=False, save_attachments=False)
