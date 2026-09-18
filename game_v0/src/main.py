import sys
from pathlib import Path

# не запускается без флага m в строке.
root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))

from src.web.module.module import main

if __name__ == "__main__":
    main()