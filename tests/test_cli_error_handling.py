"""Tests for CLI error handling to achieve 100% coverage."""

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from email2md.__main__ import main


class TestCLIErrorHandling:
    """Test CLI error handling edge cases."""

    def test_cli_value_error_during_conversion(
        self, capsys, tmp_path: Path, simple_eml_bytes: bytes
    ) -> None:
        """Should handle ValueError during conversion."""
        eml_file = tmp_path / "test.eml"
        eml_file.write_bytes(simple_eml_bytes)

        # Mock to_markdown to raise ValueError
        with patch("email2md.__main__.to_markdown") as mock_convert:
            mock_convert.side_effect = ValueError("Test conversion error")
            with patch.object(sys, "argv", ["email2md", str(eml_file)]):
                exit_code = main()

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Error: Test conversion error" in captured.err

    def test_cli_runtime_error_during_conversion(
        self, capsys, tmp_path: Path, simple_eml_bytes: bytes
    ) -> None:
        """Should handle RuntimeError during conversion."""
        eml_file = tmp_path / "test.eml"
        eml_file.write_bytes(simple_eml_bytes)

        # Mock to_markdown to raise RuntimeError
        with patch("email2md.__main__.to_markdown") as mock_convert:
            mock_convert.side_effect = RuntimeError("Test runtime error")
            with patch.object(sys, "argv", ["email2md", str(eml_file)]):
                exit_code = main()

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Error: Test runtime error" in captured.err

    def test_cli_value_error_during_html_conversion(
        self, capsys, tmp_path: Path, simple_eml_bytes: bytes
    ) -> None:
        """Should handle ValueError during HTML conversion."""
        eml_file = tmp_path / "test.eml"
        eml_file.write_bytes(simple_eml_bytes)

        # Mock to_html to raise ValueError
        with patch("email2md.__main__.to_html") as mock_convert:
            mock_convert.side_effect = ValueError("HTML conversion error")
            with patch.object(sys, "argv", ["email2md", str(eml_file), "--html"]):
                exit_code = main()

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Error: HTML conversion error" in captured.err

    def test_cli_runtime_error_during_html_conversion(
        self, capsys, tmp_path: Path, simple_eml_bytes: bytes
    ) -> None:
        """Should handle RuntimeError during HTML conversion."""
        eml_file = tmp_path / "test.eml"
        eml_file.write_bytes(simple_eml_bytes)

        # Mock to_html to raise RuntimeError
        with patch("email2md.__main__.to_html") as mock_convert:
            mock_convert.side_effect = RuntimeError("HTML runtime error")
            with patch.object(sys, "argv", ["email2md", str(eml_file), "--html"]):
                exit_code = main()

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Error: HTML runtime error" in captured.err

    def test_cli_convert_options_value_error(
        self, capsys, tmp_path: Path, simple_eml_bytes: bytes
    ) -> None:
        """Should handle ValueError from ConvertOptions construction."""
        eml_file = tmp_path / "test.eml"
        eml_file.write_bytes(simple_eml_bytes)

        # Create fake args that would trigger ConvertOptions ValueError
        # Note: reference_images=False to bypass line 115 check
        fake_args = SimpleNamespace(
            input=eml_file,
            html=False,
            output_dir=tmp_path,
            save_attachments=False,
            no_images=False,
            reference_images=False,  # Set to False to bypass argparse check
            no_hrefs=False,
            no_headers=False,
            header=[],
            no_fallback_plain=False,
            no_attachment_list=False,
        )

        # Patch ConvertOptions to raise ValueError in __post_init__
        from email2md import ConvertOptions

        original_post_init = ConvertOptions.__post_init__

        def failing_post_init(self):
            original_post_init(self)
            # Trigger a different ValueError after the normal check
            raise ValueError("Simulated validation error")

        with patch.object(ConvertOptions, "__post_init__", failing_post_init):
            with patch("argparse.ArgumentParser.parse_args", return_value=fake_args):
                # Should call parser.error which raises SystemExit
                with pytest.raises(SystemExit) as exc_info:
                    main()
                # parser.error exits with code 2
                assert exc_info.value.code == 2
