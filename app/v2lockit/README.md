# V2LocKit

**Victoria 2 Localisation Toolkit** — A GUI application for managing mod localisations.

![Status](https://img.shields.io/badge/status-MVP-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

## Features

- 📁 **File Browser** — Tree view of mod localisation folder with status icons
- ✅ **Validation** — Check encoding, column count, line endings, empty lines
- 🔍 **Missing Key Detection** — Find keys referenced in events/decisions but missing from CSVs
- 🔧 **One-Click Fix** — Apply repairs with preview and automatic backup
- 🌙 **Dark Mode** — Easy on the eyes for late-night modding
- 📄 **Reports** — Export validation results to Markdown

## Installation

### From Source

```bash
cd app/v2lockit
pip install -e .
v2lockit
```

### Standalone Executable

Download the latest release from the Releases page.

## Usage

1. **Open Folder** — Select your mod's localisation directory
2. **Validate** — Click "Validate All" to scan for issues
3. **Review** — Click on issues to see details
4. **Fix** — Preview and apply fixes with backup

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Build executable
pyinstaller scripts/v2lockit.spec
```

## License

MIT License — See [LICENSE](LICENSE) for details.

---

*Built for the Concert of Europe: Roar of Industry - Reignited mod.*
