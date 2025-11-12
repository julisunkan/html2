from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class EmailTemplate(db.Model):
    __tablename__ = 'email_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(300), nullable=False)
    header = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    button_text = db.Column(db.String(100))
    button_link = db.Column(db.String(500))
    footer = db.Column(db.Text)
    template_name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmailTemplate {self.title}>'
