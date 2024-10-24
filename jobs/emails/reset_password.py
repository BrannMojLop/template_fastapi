from typing import List
from utils.settings import Settings
from fastapi_mail import MessageSchema, FastMail, ConnectionConfig
from pydantic import BaseModel, EmailStr

settings = Settings()

EMAIL = settings.email
PASSWORD_EMAIL = settings.email_password
BASE_URL = settings.url


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


async def reset_password(email: EmailSchema, token: str, type: str):
    if type == 'user_platform':

        template = open(
            'jobs/emails/reset_password.py', 'r').read()

        template = template.format(url=BASE_URL, token=token)

        message = MessageSchema(
            subject="Recuperación de contraseña",
            recipients=email,  # List of recipients, as many as you can pass
            body=template,
            subtype="html"
        )

        fm = FastMail(conf)
        await fm.send_message(message)
