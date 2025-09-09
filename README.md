# Python API using FastAPI
## Installation

### Note about UV Package manager
*This application uses [uv](https://github.com/astral-sh/uv) to manage dependencies.*

*If you do not have uv installed, [install it](#install-uv) before continuing.*

### Install Dependencies

```bash
# Install dependencies
uv sync
```

## Running
### Run the server in development mode
```bash
uv run main.py
```

### Run server in production mode (4 workers, no reload)
```bash
uv run main.py --production
```

### Run (in development mode) with custom port
```bash
uv run main.py --port 3000
```

### Server Options
- --host
  - Sets server host
  - default = 0.0.0.0
- --port
  - Sets server port
  - default = 8000
- --workers
  - Set number of workers
  - default = 1 (in development mode)
  - default = 4 (in production mode)
- --production
  - Run in production mode 
  - Disables auto-reload, enables multiple workers, defaulting to 4

## Install uv
```bash
## macOS and Linux ##
curl -LsSf https://astral.sh/uv/install.sh | sh

## Windows ##
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"


# After installing, make sure to open a new terminal or update your shell source (e.g. `source ~/.bashrc` for bash, `source ~/.zshrc` for zsh)
```

## Notes
### 'python' command
  - If you have not aliased 'python' to your preferred python 3 installation you will need to either do that first or, if you are on a Mac, you can use 'python3' instead which will use MacOS's default python 3 installation.
