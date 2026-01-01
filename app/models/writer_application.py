from app.extensions import db
from datetime import datetime

from app.extensions import db
from datetime import datetime

class WriterApplication(db.Model):
    __tablename__ = "writer_applications"

    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey("users.id"), nullable=False)
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    education = db.Column(db.String(120))
    specialization = db.Column(db.String(120))
    years_experience = db.Column(db.String(50))

    selected_prompt = db.Column(db.String(255))
    prompt_response = db.Column(db.Text)

    selected_essay_topic = db.Column(db.String(255))
    essay_file_path = db.Column(db.String(255))
    proficiency_answers = db.Column(db.JSON, default=dict)
    work_samples = db.Column(db.JSON, default=list)
    degree_certificates = db.Column(db.JSON, default=list)
    cv_file_path = db.Column(db.String(255))

    status = db.Column(db.String(50), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    admin_feedback = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("writer_application", uselist=False))

def serialize(self):
    return {
        "id": self.id,
        "user_id": self.user_id,
        "country": self.country,
        "city": self.city,
        "education": self.education,
        "specialization": self.specialization,
        "years_experience": self.years_experience,
        "phone_number": self.phone_number,
        "proficiency_answers": self.proficiency_answers,
        "selected_prompt": self.selected_prompt,
        "prompt_response": self.prompt_response,
        "selected_essay_topic": self.selected_essay_topic,
        "essay_file": self.essay_file,
        "work_samples": self.work_samples,
        "cv_file": self.cv_file,
        "degree_certificates": self.degree_certificates,
        "status": self.status,
        "admin_feedback": self.admin_feedback,
        "created_at": self.created_at.isoformat(),
    }