from app import db
from datetime import datetime

class ShoppingCartItem(db.Model):

    id=db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    hubfile_id = db.Column(db.Integer, db.ForeignKey('hubfile.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<CarItem U:{self.user_id} H:{self.hubfile_id}'
