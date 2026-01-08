import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
from flask import current_app

def send_email(to: str, subject: str, html: str):
    msg = EmailMessage()
    msg["From"] = f"{current_app.config['EMAIL_FROM_NAME']} <{current_app.config['EMAIL_FROM_ADDRESS']}>"
    msg["To"] = to
    msg["Subject"] = subject
    msg["Reply-To"] = current_app.config["EMAIL_FROM_ADDRESS"]
    msg["Message-ID"] = make_msgid(domain="academichubpro.com")

    msg.set_content("This is an automated message. Please view in HTML.")
    msg.add_alternative(html, subtype="html")

    print(f"Connecting to SMTP {current_app.config['ZOHO_SMTP_HOST']}:{current_app.config['ZOHO_SMTP_PORT']}")

    try:
        with smtplib.SMTP_SSL(
            current_app.config["ZOHO_SMTP_HOST"],
            current_app.config["ZOHO_SMTP_PORT"]
        ) as server:
            server.login(
                current_app.config["EMAIL_FROM_ADDRESS"],
                current_app.config["ZOHO_APP_PASSWORD"]
            )
            server.send_message(msg)
            print(f"Email sent successfully to {to}")
    except Exception as e:
        print(f"Failed to send email to {to}: {e}")
        raise
