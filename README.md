# env-diff

Compare environment variables between processes, containers, or .env files to debug configuration issues

## Features

- Compare environment variables from two running processes by PID
- Diff two .env files with full path support
- Parse and compare shell export scripts (bash/zsh format)
- Colorized terminal output showing additions (green), deletions (red), and changes (yellow)
- Value diff display for changed variables showing old -> new
- Mask sensitive values using pattern matching (password, token, key, secret)
- Export comparison results to JSON format with structured diff data
- Export comparison results to CSV format for spreadsheet analysis
- Filter comparison by variable name patterns (include/exclude)
- Show only differences or all variables with --all flag
- Sort output alphabetically or by change type
- Support for reading from stdin for piped input

## How to Use

Use this project when you need to:

- Quickly solve problems related to env-diff
- Integrate python functionality into your workflow
- Learn how python handles common patterns with click

## Installation

```bash
# Clone the repository
git clone https://github.com/KurtWeston/env-diff.git
cd env-diff

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Built With

- python using click

## Dependencies

- `click`
- `rich`
- `python-dotenv`
- `psutil`

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
