from dotenv import load_dotenv

load_dotenv()

from rds_postgres.connection import get_session


def get_db():
    with get_session() as session:
        yield session
