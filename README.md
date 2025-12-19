# email2md

Convert email files (`.eml`, `.msg`) to **Markdown** (default) or **HTML**.

## Install

```bash
pip install email2md
```

## CLI usage

Prefix with `uvx` to run as a portable tool "without installing".

```bash
# markdown (default)
email2md message.msg

# HTML
email2md message.eml --html

# read from stdin
cat message.msg | email2md > message.md

# save attachments, reference image instead of inlining as b64
email2md message.msg --save-attachments --reference-images -o ./output > message.md
```

For all flags:

```bash
email2md --help
```

## Python usage

```python
from email2md import ConvertOptions, to_markdown

md = to_markdown(
    "message.eml",
    ConvertOptions(include_headers=True, save_attachments=False, inline_images=True),
)
```

## License

This project is licensed under the **MIT License**.

**Note:** This project depends on `extract-msg`, which is licensed under **GPL-3.0**. Distribution of this project as a combined work may be subject to the terms of the GPL-3.0.
