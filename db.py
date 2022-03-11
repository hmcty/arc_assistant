from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Member(Base):
    __tablename__ = "member"

    id = Column(Integer, primary_key=True)
    member_id = Column(Integer)
    guild_id = Column(Integer)
    verified = Column(Integer)
    code = Column(Integer)

