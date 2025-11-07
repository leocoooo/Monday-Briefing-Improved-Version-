import smtplib
from email.message import EmailMessage
from monday_report.core.config import settings

class EmailService:
    @staticmethod
    def send_email(subject: str, body: str) -> dict:
        if not all([settings.smtp_host, settings.smtp_user, settings.smtp_password,
                    settings.email_from, settings.email_to]):
            print("⚠️ Configuration SMTP incomplète. Écriture dans fichier...")
            try:
                with open('last_briefing.txt', 'w', encoding='utf-8') as f:
                    f.write(body)
                print("✅ Rapport écrit dans last_briefing.txt")
                return {"status": "written_file", "path": "last_briefing.txt"}
            except Exception as e:
                print(f"❌ Erreur écriture fichier : {e}")
                return {"status": "print", "body": body}

        # pour éviter les erreurs mypy 
        assert settings.smtp_host is not None
        assert settings.smtp_user is not None
        assert settings.smtp_password is not None
        assert settings.email_from is not None
        assert settings.email_to is not None

        smtp_host: str = settings.smtp_host
        smtp_port: int = settings.smtp_port
        smtp_user: str = settings.smtp_user
        smtp_password: str = settings.smtp_password
        email_from: str = settings.email_from
        email_to: str = settings.email_to

        try:
            msg = EmailMessage()
            msg['From'] = email_from
            msg['To'] = email_to
            msg['Subject'] = subject
            msg.set_content(body)

            print(f"📧 Tentative d'envoi email via {smtp_host}:{smtp_port}")

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)

            print(f"✅ Email envoyé avec succès à {email_to}")
            return {"status": "sent_email", "to": email_to}

        except Exception as e:
            print(f"❌ Erreur envoi email : {e}")
            return {"status": "email_error", "error": str(e)}
