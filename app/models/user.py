from datetime import datetime
from app.models import db
from app.models.base import BaseModel

class User(BaseModel):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    profile_img_url = db.Column(db.String(500))
    authority = db.Column(db.String(20), default='user', nullable=False)
    last_login_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<User {self.username}>'

