from flask import Flask
from sqlalchemy.exc import OperationalError
import sys
from src.di.container import Container
from src.web.route import init_routes

def main():
    app = Flask(__name__)

    container = Container()

    try:
        init_routes(app, container)
        app.run()
    except OperationalError as exc:
        print(exc)
        sys.exit(1)

if __name__ == '__main__':
    main()

