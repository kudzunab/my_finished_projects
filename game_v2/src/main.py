import sys
from pathlib import Path

root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))

from src.web.module.module import main
"""
    python3 -m venv .my_env
    source .my_env/bin/activate
    deactivate
    kill -9 $(lsof -t -i:5000)
    pip freeze > requirements.txt
    pip install -r requirements.txt
"""
if __name__ == "__main__":
    main()