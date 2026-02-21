from dotenv import load_dotenv

load_dotenv()

from rds_postgres.connection import engine as engine
from rds_postgres.connection import get_session


def get_db():  # type: ignore[no-untyped-def]
    with get_session() as session:
        yield session
