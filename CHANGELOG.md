# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.3] - 2025-12-19

### Changed

- Changed default attachment `output_dir` behavior: when converting from a file path, attachments now save alongside the input email; when reading from stdin or bytes, attachments save to the current working directory.
- Updated CLI `--output-dir/-o` default to follow the same behavior as the library (file directory vs current working directory).

## [0.1.2] - 2025-12-19

### Changed

- Added `Cc` and `Bcc` to default headers.

## [0.1.1] - 2025-12-19

### Fixed

- Fixed image inlining for MSG files: Strip null bytes (`\x00`) from Content-ID, Content-Type, and filename fields that are appended by the `extract-msg` library during MSG to EML conversion. This fixes images not being embedded as base64 data URIs and appearing as `cid:` references instead.

## [0.1.0] - 2025-12-19

### Added

- Initial release of email2md
- Support for `.eml` (RFC 822) and `.msg` (Outlook) email formats
- Convert emails to Markdown or HTML
- CLI tool (`email2md` command) with rich options
- Email header extraction (From, To, Subject, Date, etc.)
- Attachment handling:
  - Inline base64 image embedding
  - Save attachments to disk
  - Reference saved images instead of inline embedding
- Flexible output options:
  - Strip images for cleaner output
  - Remove hyperlinks (keep text only)
  - Disable headers
  - Customize which headers to include
  - Attachment list generation
- Stdin/stdout support for piping
- Fallback to plain text when HTML body is unavailable

[Unreleased]: https://github.com/hewliyang/email2md/compare/v0.1.3...HEAD
[0.1.3]: https://github.com/hewliyang/email2md/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/hewliyang/email2md/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/hewliyang/email2md/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/hewliyang/email2md/releases/tag/v0.1.0
