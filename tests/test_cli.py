"""Tests for CLI interface."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from email2md.__main__ import main


class TestCLI:
    """Test command-line interface."""

    def test_cli_basic_markdown_output(
        self, capsys, tmp_path: Path, simple_eml_bytes: bytes
    ) -> None:
        """Should convert EML to Markdown via CLI."""
        eml_file = tmp_path / "test.eml"
        eml_file.write_bytes(simple_eml_bytes)

        with patch.object(sys, "argv", ["email2md", str(eml_file)]):
            exit_code = main()

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "# Hello World" in captured.out
        assert "**From:** sender@example.com" in captured.out

    def test_cli_html_output(
        self, capsys, tmp_path: Path, simple_eml_bytes: bytes
    ) -> None:
        """Should output HTML when --html flag is used."""
        eml_file = tmp_path / "test.eml"
        eml_file.write_bytes(simple_eml_bytes)

        with patch.object(sys, "argv", ["email2md", str(eml_file), "--html"]):
            exit_code = main()

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "<h1>Hello World</h1>" in captured.out
        assert "<p>This is a test.</p>" in captured.out

    def test_cli_no_headers(
        self, capsys, tmp_path: Path, simple_eml_bytes: bytes
    ) -> None:
        """Should exclude headers with --no-headers."""
        eml_file = tmp_path / "test.eml"
        eml_file.write_bytes(simple_eml_bytes)

        with patch.object(sys, "argv", ["email2md", str(eml_file), "--no-headers"]):
            exit_code = main()

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "**From:**" not in captured.out

    def test_cli_no_images(
        self, capsys, tmp_path: Path, eml_with_images: bytes
    ) -> None:
        """Should exclude images with --no-images."""
        eml_file = tmp_path / "test.eml"
        eml_file.write_bytes(eml_with_images)

        with patch.object(sys, "argv", ["email2md", str(eml_file), "--no-images"]):
            exit_code = main()

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "data:image/png;base64," not in captured.out

    def test_cli_save_attachments(
        self, capsys, tmp_path: Path, eml_with_attachments: bytes
    ) -> None:
        """Should save attachments with --save-attachments."""
        eml_file = tmp_path / "test.eml"
        eml_file.write_bytes(eml_with_attachments)
        output_dir = tmp_path / "output"

        with patch.object(
            sys,
            "argv",
            [
                "email2md",
                str(eml_file),
                "--save-attachments",
                "-o",
                str(output_dir),
            ],
        ):
            exit_code = main()

        assert exit_code == 0
        assert (output_dir / "document.pdf").exists()

    def test_cli_reference_images(
        self, capsys, tmp_path: Path, eml_with_images: bytes
    ) -> None:
        """Should reference images with --reference-images."""
        eml_file = tmp_path / "test.eml"
        eml_file.write_bytes(eml_with_images)
        output_dir = tmp_path / "output"

        with patch.object(
            sys,
            "argv",
            [
                "email2md",
                str(eml_file),
                "--save-attachments",
                "--reference-images",
                "-o",
                str(output_dir),
            ],
        ):
            exit_code = main()

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "data:image/png;base64," not in captured.out
        assert (output_dir / "test.png").exists()

    def test_cli_reference_without_save_error(
        self, capsys, tmp_path: Path, simple_eml_bytes: bytes
    ) -> None:
        """Should error when --reference-images without --save-attachments."""
        eml_file = tmp_path / "test.eml"
        eml_file.write_bytes(simple_eml_bytes)

        with patch.object(
            sys, "argv", ["email2md", str(eml_file), "--reference-images"]
        ):
            with pytest.raises(SystemExit):
                main()

    def test_cli_custom_headers(
        self, capsys, tmp_path: Path, simple_eml_bytes: bytes
    ) -> None:
        """Should include only specified headers."""
        eml_file = tmp_path / "test.eml"
        eml_file.write_bytes(simple_eml_bytes)

        with patch.object(
            sys,
            "argv",
            ["email2md", str(eml_file), "--header", "From", "--header", "Subject"],
        ):
            exit_code = main()

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "**From:** sender@example.com" in captured.out
        assert "**Subject:** Test Email" in captured.out
        assert "**To:**" not in captured.out
        assert "**Date:**" not in captured.out

    def test_cli_no_hrefs(self, capsys, tmp_path: Path, eml_with_links: bytes) -> None:
        """Should strip hrefs with --no-hrefs."""
        eml_file = tmp_path / "test.eml"
        eml_file.write_bytes(eml_with_links)

        with patch.object(sys, "argv", ["email2md", str(eml_file), "--no-hrefs"]):
            exit_code = main()

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "https://example.com" not in captured.out
        assert "website" in captured.out

    def test_cli_no_attachment_list(
        self, capsys, tmp_path: Path, eml_with_attachments: bytes
    ) -> None:
        """Should exclude attachment list with --no-attachment-list."""
        eml_file = tmp_path / "test.eml"
        eml_file.write_bytes(eml_with_attachments)

        with patch.object(
            sys, "argv", ["email2md", str(eml_file), "--no-attachment-list"]
        ):
            exit_code = main()

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "**Attachments:**" not in captured.out

    def test_cli_file_not_found(self, capsys) -> None:
        """Should handle missing file gracefully."""
        with patch.object(sys, "argv", ["email2md", "/nonexistent/file.eml"]):
            exit_code = main()

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "File not found" in captured.err

    def test_cli_msg_file(self, capsys, test_msg_file) -> None:
        """Should handle .msg files via CLI."""
        with patch.object(sys, "argv", ["email2md", str(test_msg_file)]):
            exit_code = main()

        assert exit_code == 0
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_cli_stdin_input(self, capsys, simple_eml_bytes: bytes) -> None:
        """Should read from stdin when no file specified."""
        import io
        from types import SimpleNamespace

        # Create a fake stdin with buffer attribute
        fake_stdin = SimpleNamespace(buffer=io.BytesIO(simple_eml_bytes))

        with patch.object(sys, "stdin", fake_stdin):
            with patch.object(sys, "argv", ["email2md"]):
                exit_code = main()

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "# Hello World" in captured.out

    def test_cli_minimal_output(
        self, capsys, tmp_path: Path, eml_with_images: bytes
    ) -> None:
        """Should produce minimal output with all flags disabled."""
        eml_file = tmp_path / "test.eml"
        eml_file.write_bytes(eml_with_images)

        with patch.object(
            sys,
            "argv",
            [
                "email2md",
                str(eml_file),
                "--no-headers",
                "--no-images",
                "--no-hrefs",
                "--no-attachment-list",
            ],
        ):
            exit_code = main()

        assert exit_code == 0
        captured = capsys.readouterr()
        # Should have content but no headers, images, etc.
        assert "**From:**" not in captured.out
        assert "data:image/png;base64," not in captured.out

    def test_cli_no_fallback_plain(
        self, capsys, tmp_path: Path, eml_plain_only: bytes
    ) -> None:
        """Should skip plain text fallback with --no-fallback-plain."""
        eml_file = tmp_path / "test.eml"
        eml_file.write_bytes(eml_plain_only)

        with patch.object(
            sys, "argv", ["email2md", str(eml_file), "--no-fallback-plain"]
        ):
            exit_code = main()

        assert exit_code == 0
        # Output should be minimal (maybe just headers)
