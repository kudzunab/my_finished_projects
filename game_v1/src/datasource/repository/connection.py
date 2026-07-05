import os
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError, ArgumentError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.datasource.model.model import Base

def init_my_db():
    try:
        load_dotenv()
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT')
        db_name = os.getenv('DB_NAME')
        bd_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(bd_url, pool_pre_ping=True, pool_size=10, max_overflow=20)
        # если нужно будет удалить базу данных, можно использовать команду:
        # Base.metadata.drop_all(bind=engine), а можно удалить через postgresql
        Base.metadata.create_all(bind=engine)
        result=sessionmaker(bind=engine)
    except (OperationalError, ArgumentError) as e:
        print(f"Ошибка при подключении к postgresql: {e}")
        print("Для работы программы данные будут использовать базу sqlite")
        bd_url = "sqlite:///cross_nulls_db.sqlite"
        engine = create_engine(bd_url)
        Base.metadata.create_all(bind=engine)
        result=sessionmaker(bind=engine)
    return result

# sudo systemctl status postgresql - проверка состояния
# sudo systemctl start postgresql - запуск
# sudo systemctl enable postgresql - автозапуск
# sudo -u postgres psql - заходим в postgresql
# создаем сначала пользователя admin, чтобы под ним заходить в базу:
# CREATE USER admin WITH PASSWORD '********'; - создаем пользователя
# CREATE DATABASE cross_nulls_db OWNER admin; - создаем базу данных
# GRANT ALL PRIVILIGES ON DATABASE cross_nulls_db TO admin; - даем права на доступ к базе
# \q - выход из консоли