import os
from sqlalchemy.exc import OperationalError, ArgumentError
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.datasource.model.model import Base

def init_my_db():
    try:
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
        with engine.connect() as connection:
            connection.execute(text("""
                ALTER TABLE games 
                ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL;
            """))
            connection.commit()
        result=sessionmaker(bind=engine)
    except (OperationalError, ArgumentError) as e:
        print(f"Ошибка при подключении к postgresql: {e}")
        print("Для работы программы данные будут использовать базу sqlite")
        bd_url = "sqlite:///cross_nulls_db.sqlite"
        engine = create_engine(bd_url)
        Base.metadata.create_all(bind=engine)
        result=sessionmaker(bind=engine)
    return result