from app.models import db
from app.models.base import BaseModel
from datetime import datetime

class ChatHistory(BaseModel):
    __tablename__='chat_histories'

    chat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.pet_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    message_type = db.Column(db.String(20), nullable=False)  # 'user' or 'pet'
    message_content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Pet과 User 관계는 해당 모델에서 정의