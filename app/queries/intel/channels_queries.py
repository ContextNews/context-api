from context_db.models import TgChannel
from sqlalchemy.orm import Session


def query_channels(db: Session) -> list[TgChannel]:
    return db.query(TgChannel).order_by(TgChannel.username).all()  # type: ignore[no-any-return]


def query_channel(db: Session, channel_id: int) -> TgChannel | None:
    return db.query(TgChannel).filter(TgChannel.id == channel_id).first()
