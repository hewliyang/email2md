# Release Process

## Prerequisites

1. Ensure all tests pass: `uv run pytest`
2. Ensure code quality checks pass:
   ```bash
   uv run ruff format --check
   uv run ruff check
   uv run ty check
   ```

## Release Steps

### 1. Update Version

Edit `pyproject.toml`:
```toml
[project]
version = "0.2.0"  # Update this
```

### 2. Update CHANGELOG.md

Move items from `[Unreleased]` to a new version section:

```markdown
## [Unreleased]

(empty for now)

## [0.2.0] - 2024-12-20

### Added
- New feature X
- New feature Y

### Fixed
- Bug fix Z
```

Update the comparison links at the bottom:
```markdown
[Unreleased]: https://github.com/yourusername/email2md/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/yourusername/email2md/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/yourusername/email2md/releases/tag/v0.1.0
```

### 3. Commit Changes

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 0.2.0"
git push origin main
```

### 4. Create Git Tag

```bash
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

### 5. Create GitHub Release

Go to https://github.com/yourusername/email2md/releases/new

- **Choose tag**: v0.2.0
- **Release title**: v0.2.0
- **Description**: Copy the relevant section from CHANGELOG.md

Example:
```markdown
## What's Changed

### Added
- New feature X
- New feature Y

### Fixed
- Bug fix Z

**Full Changelog**: https://github.com/yourusername/email2md/compare/v0.1.0...v0.2.0
```

Click **"Publish release"**

### 6. Automated Publishing

The GitHub Action will automatically:
1. Run all code quality checks
2. Run tests
3. Build the package
4. Publish to PyPI

Monitor the action at: https://github.com/yourusername/email2md/actions

### 7. Verify

After ~2 minutes, check:
- PyPI: https://pypi.org/project/email2md/
- Installation: `uv pip install email2md==0.2.0`

## Quick Commands

```bash
# Check current version
grep "^version" pyproject.toml

# See all tags
git tag -l

# Delete a tag (if you make a mistake)
git tag -d v0.2.0
git push origin :refs/tags/v0.2.0
```

## Version Naming

- Patch release (bug fixes): `0.1.0` → `0.1.1`
- Minor release (new features): `0.1.0` → `0.2.0`
- Major release (breaking changes): `0.9.0` → `1.0.0`

## Hotfix Process

If you need to release a critical fix immediately:

```bash
# From main branch
git checkout -b hotfix/0.1.1

# Make your fix
# Update version to 0.1.1
# Update CHANGELOG

git commit -m "fix: critical bug"
git push origin hotfix/0.1.1

# Create PR, merge, then follow release steps above
```
