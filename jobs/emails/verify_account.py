from typing import List
from utils.settings import Settings
from fastapi_mail import MessageSchema, FastMail, ConnectionConfig
from pydantic import BaseModel, EmailStr

settings = Settings()

EMAIL = settings.email
PASSWORD_EMAIL = settings.email_password


class EmailSchema(BaseModel):
    email: List[EmailStr]


conf = ConnectionConfig(
    MAIL_USERNAME=EMAIL,
    MAIL_PASSWORD=PASSWORD_EMAIL,
    MAIL_FROM=EMAIL,
    MAIL_PORT=465,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True
)


async def send_email(email: EmailSchema, token: str, type: str):
    if type == 'user_platform':
        template = open(
            'jobs/emails/templetes/verify_user.html', 'r').read()

        template = template.format(token=token)

        message = MessageSchema(
            subject="Verificación de usuario",
            recipients=email,  # List of recipients, as many as you can pass
            body=template,
            subtype="html"
        )

        fm = FastMail(conf)
        await fm.send_message(message)
