from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy import func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    repo_url = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, fixing, success, failed
    error = Column(Text)
    logs = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())