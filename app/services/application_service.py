import os
from werkzeug.utils import secure_filename
from app.models.writer_application import WriterApplication
from app.extensions import db
from datetime import datetime
import uuid
from flask import current_app

def save_uploaded_file(file, subdir):
    if not file:
        return None

    upload_folder = current_app.config.get("UPLOAD_FOLDER")
    if not upload_folder:
        raise RuntimeError("UPLOAD_FOLDER not configured in Flask app")

    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    upload_path = os.path.join(upload_folder, subdir)
    os.makedirs(upload_path, exist_ok=True)
    full_path = os.path.join(upload_path, unique_name)

    print(f"Saving file {file.filename} to {full_path}")
    file.save(full_path)
    if os.path.exists(full_path):
        print(f"File saved: {full_path}")
    else:
        print(f"Failed to save file: {full_path}")
    return full_path


def create_writer_application(user, form_data, files):
    existing = WriterApplication.query.filter_by(user_id=user.id).first()
    if existing:
        raise Exception("You already have a pending application.")

    essay_file = files.get("essayFile")
    cv_file = files.get("cvFile")

    essay_path = save_uploaded_file(essay_file, f"{user.id}/essay") if essay_file else None
    cv_path = save_uploaded_file(cv_file, f"{user.id}/cv") if cv_file else None

    # multiple files
    work_sample_paths = []
    for f in files.getlist("workSamples"):
        path = save_uploaded_file(f, f"{user.id}/work_samples")
        work_sample_paths.append(path)

    degree_paths = []
    for f in files.getlist("degreeCertificates"):
        path = save_uploaded_file(f, f"{user.id}/degree_certificates")
        degree_paths.append(path)

    application = WriterApplication(
        id=str(uuid.uuid4()),
        user_id=user.id,
        country=form_data.get("country"),
        city=form_data.get("city"),
        education=form_data.get("education"),
        specialization=form_data.get("specialization"),
        years_experience=form_data.get("yearsExperience"),
        proficiency_answers=form_data.get("proficiencyAnswers"),
        selected_prompt=form_data.get("selectedPrompt"),
        prompt_response=form_data.get("promptResponse"),
        selected_essay_topic=form_data.get("selectedEssayTopic"),
        essay_file_path=essay_path,
        work_samples=work_sample_paths,
        cv_file_path=cv_path,
        degree_certificates=degree_paths,
        status="pending",
        created_at=datetime.utcnow(),
    )

    db.session.add(application)
    user.application_status = "applied"
    db.session.commit()

    return application
