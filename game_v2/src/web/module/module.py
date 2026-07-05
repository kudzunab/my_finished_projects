from flask import Flask
from sqlalchemy.exc import OperationalError
import sys
from src.di.container import Container
from src.web import init_routes

def main():
    app = Flask(__name__)

    container = Container()
    try:
        init_routes(app, container)
        app.run(threaded=True)
    except OperationalError as exc:
        print(f"Критическая ошибка: {exc}")
        sys.exit(1)
    except ValueError as exc:
        print(f"Не введен секретный ключ, без этого приложение не запустится: {exc}")
        sys.exit(1)

if __name__ == '__main__':
    main()

