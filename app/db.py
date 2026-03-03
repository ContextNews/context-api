from dotenv import load_dotenv

load_dotenv()

from context_db.connection import engine as engine
from context_db.connection import get_session


def get_db():  # type: ignore[no-untyped-def]
    with get_session() as session:
        yield session
