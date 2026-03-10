import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Optional
from interfaces.email_interfaces import IEmailSender
import os
from dotenv import load_dotenv

load_dotenv()


class SMTPEmailSender(IEmailSender):
    """
    Implementación de envío de emails usando SMTP
    """
    
    def __init__(
        self,
        smtp_host: str = None,
        smtp_port: int = None,
        smtp_user: str = None,
        smtp_password: str = None,
        use_tls: bool = True,
        use_ssl: bool = False
    ):
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
        self.use_tls = use_tls
        self.use_ssl = use_ssl
    
    async def send(
        self,
        recipient: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachment: Optional[bytes] = None,
        attachment_filename: Optional[str] = None
    ) -> bool:
        """
        Envía un email usando SMTP, con soporte para adjuntos.
        """
        try:
            # Crear mensaje
            message = MIMEMultipart("mixed") if attachment else MIMEMultipart("alternative")
            message["From"] = self.smtp_user
            message["To"] = recipient
            message["Subject"] = subject
            
            # Contenido del cuerpo
            body_part = MIMEMultipart("alternative")
            body_part.attach(MIMEText(body, "plain", "utf-8"))
            if html_body:
                body_part.attach(MIMEText(html_body, "html", "utf-8"))
            
            message.attach(body_part)
            
            # Adjuntar archivo si existe
            if attachment and attachment_filename:
                part_attachment = MIMEApplication(attachment, Name=attachment_filename)
                part_attachment["Content-Disposition"] = f'attachment; filename="{attachment_filename}"'
                message.attach(part_attachment)
                print(f"📎 Adjuntando archivo: {attachment_filename}")
            
            # Conectar y enviar
            if self.use_ssl:
                print(f"🔌 Conectando a {self.smtp_host}:{self.smtp_port} con SSL...")
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=30)
                print("🔐 Autenticando...")
                server.login(self.smtp_user, self.smtp_password)
                print("📧 Enviando mensaje...")
                server.send_message(message)
                server.quit()
                print("✅ Conexión cerrada correctamente")
            else:
                print(f"🔌 Conectando a {self.smtp_host}:{self.smtp_port} con TLS...")
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30)
                server.ehlo()
                if self.use_tls:
                    server.starttls()
                    server.ehlo()
                
                print("🔐 Autenticando...")
                server.login(self.smtp_user, self.smtp_password)
                print("📧 Enviando mensaje...")
                server.send_message(message)
                server.quit()
                print("✅ Conexión cerrada correctamente")
            
            print(f"✅ Email enviado exitosamente a {recipient}")
            return True
            
        except Exception as e:
            print(f"❌ Error al enviar email a {recipient}: {str(e)}")
            return False


class MockEmailSender(IEmailSender):
    """
    Implementación mock para desarrollo/testing
    """
    
    async def send(
        self,
        recipient: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachment: Optional[bytes] = None,
        attachment_filename: Optional[str] = None
    ) -> bool:
        """Simula el envío de un email (para desarrollo/testing)"""
        print("=" * 60)
        print(f"📧 MOCK EMAIL")
        print(f"Para: {recipient}")
        print(f"Asunto: {subject}")
        print(f"Cuerpo: {body[:100]}...")
        if html_body:
            print(f"HTML: {html_body[:100]}...")
        if attachment:
            print(f"📎 Adjunto: {attachment_filename} ({len(attachment)} bytes)")
        print("=" * 60)
        return True