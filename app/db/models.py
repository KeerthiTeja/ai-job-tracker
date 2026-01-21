from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    company: Mapped[str] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(120))
    country: Mapped[str] = mapped_column(String(80))
    location: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(30))  # wishlist/applied/interview/offer/rejected
    url: Mapped[str | None] = mapped_column(String(300), nullable=True)
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tailor_runs = relationship(
        "TailorRun",
        back_populates="job",
        cascade="all, delete-orphan"
    )
