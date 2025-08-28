# Python API using FastAPI
## Installation
- Create and activate a virtual environment to keep packages isolated
```
python -m venv api_venv
source api_venv/bin/activate
```
- Install required packages
```
python -m pip install -r requirements.txt
```

## Running
- Run the server
```
uvicorn main:app --reload
```

## Notes
- 'python' command
  - If you have not aliased 'python' to your preferred python 3 installation you will need to either do that first or, if you are on a Mac, you can use 'python3' instead which will use MacOS's default python 3 installation.