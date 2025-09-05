from datetime import datetime, timezone, date, timedelta
from app.models import db

def get_utc_now():
    return datetime.now(timezone.utc)

class BaseModel(db.Model):
    __abstract__ = True

    created_at = db.Column(db.DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    def to_dict(self):
            result = {}
            for c in self.__table__.columns:
                value = getattr(self, c.name)
                if isinstance(value, datetime):
                    result[c.name] = value.isoformat()
                elif isinstance(value, date):
                    result[c.name] = value.isoformat()
                else:
                    result[c.name] = value
            return result