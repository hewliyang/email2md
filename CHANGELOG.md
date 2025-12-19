# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-12-19

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

[Unreleased]: https://github.com/hewliyang/email2md/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/hewliyang/email2md/releases/tag/v0.1.0
