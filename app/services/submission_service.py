import os
import uuid
from flask import current_app
from app.extensions import db
from app.models.submission import Submission
from app.models.order import Order
from app.services.order_service import update_order_status
from app.services.order_service import save_uploaded_file
from sqlalchemy import func

def create_submission(*, order: Order, writer, files, message=None, file_types=None):
    last_number = (
        db.session.query(func.max(Submission.submission_number))
        .filter_by(order_id=order.id)
        .scalar()
    ) or 0

    next_number = last_number + 1

    submission = Submission(
        id=f"SUB-{uuid.uuid4().hex[:8]}",
        order_id=order.id,
        submission_number=next_number,
        writer_id=writer.id,
        message=message,
        status="pending"
    )

    db.session.add(submission)
    db.session.flush()

    root_dir = current_app.config.get("SUBMISSIONS_FOLDER", "uploads/submissions")
    submission_dir = os.path.join(root_dir, order.id, submission.id)

    saved_files = []

    for idx, file in enumerate(files):
        if not file or not file.filename:
            continue

        fname, fpath = save_uploaded_file(file, submission_dir)

        # Assign type if provided, else default to None
        file_type = file_types[idx] if file_types and idx < len(file_types) else None

        saved_files.append({
            "name": fname,
            "path": fpath,
            "type": file_type   # NEW: store the type
        })

    submission.files = saved_files
    db.session.commit()

    return submission


def list_submissions(order: Order):
    return (
        Submission.query
        .filter_by(order_id=order.id)
        .order_by(Submission.submission_number.desc())
        .all()
    )


def request_revision(submission: Submission, message: str):
    submission.status = "revision_requested"
    submission.message = message
    db.session.commit()
