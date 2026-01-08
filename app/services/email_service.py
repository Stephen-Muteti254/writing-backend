import smtplib
from email.message import EmailMessage
from flask import current_app, render_template
from datetime import datetime
from app.utils.mailer import send_email

COMPANY_NAME = "Academic Hub"

def send_verification_email(user, token):
    verify_url = f"{current_app.config['FRONTEND_URL']}/verify-email?token={token}"
    html = render_template(
        "emails/verify_email.html",
        full_name=user.full_name,
        verify_url=verify_url,
        year=datetime.utcnow().year
    )
    try:
        send_email(
            to=user.email,
            subject="Verify your Academic Hub account",
            html=html
        )
    except Exception as e:
        print(f"Failed to send email to {user.email}: {e}")


def send_application_received_email(user):
    try:
        send_email(
            to=user.email,
            subject="We’ve received your writer application",
            html=render_template(
                "emails/application_received.html",
                title="Application Received",
                full_name=user.full_name,
                company_name=COMPANY_NAME,
            ),
        )
    except Exception as e:
        print(f"Failed to send email to {to}: {e}")


def send_application_approved_email(user, feedback=None):
    try:
        send_email(
            to=user.email,
            subject="Your writer application has been approved",
            html=render_template(
                "emails/application_approved.html",
                title="Application Approved",
                full_name=user.full_name,
                feedback=feedback,
                company_name=COMPANY_NAME,
            ),
        )
    except Exception as e:
        print(f"Failed to send email to {to}: {e}")


def send_application_rejected_email(user, feedback=None):
    try:
        send_email(
            to=user.email,
            subject="Update on your writer application",
            html=render_template(
                "emails/application_rejected.html",
                title="Application Update",
                full_name=user.full_name,
                feedback=feedback,
                company_name=COMPANY_NAME,
            ),
        )
    except Exception as e:
        print(f"Failed to send email to {to}: {e}")

def send_deposit_approved_email(user):
    """
    Notify the writer that their initial deposit has been approved,
    and they now have access to orders after completing their profile.
    """
    try:
        send_email(
            to=user.email,
            subject="Your initial deposit has been approved",
            html=render_template(
                "emails/deposit_approved.html",
                title="Deposit Approved",
                full_name=user.full_name,
                company_name=COMPANY_NAME,
            ),
        )
    except Exception as e:
        print(f"Failed to send deposit approval email to {user.email}: {e}")