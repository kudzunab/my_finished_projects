from flask import Flask
from src.di.container import Container
from src.web.route import init_routes

def main():
    app = Flask(__name__)

    container = Container()
    init_routes(app, container)
    app.run()

if __name__ == '__main__':
    main()

