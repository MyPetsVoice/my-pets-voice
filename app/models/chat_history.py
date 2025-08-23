from app.models import db
from app.models.base import BaseModel
from datetime import datetime

# 추후 개발
class ChatHistory(BaseModel):
    __tablename__='chat_histories'

    chat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)