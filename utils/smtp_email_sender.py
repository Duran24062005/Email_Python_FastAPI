import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from interfaces.email_interfaces import IEmailSender
import os
from dotenv import load_dotenv

load_dotenv()


class SMTPEmailSender(IEmailSender):
    """
    Implementación de envío de emails usando SMTP
    (Single Responsibility: solo se encarga de enviar emails)
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
        print(f"🔧 SMTP Config: Host={self.smtp_host}, Port={self.smtp_port}, SSL={self.use_ssl}, TLS={self.use_tls}")
    
    async def send(
        self,
        recipient: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Envía un email usando SMTP
        
        Args:
            recipient: Email del destinatario
            subject: Asunto del email
            body: Cuerpo en texto plano
            html_body: Cuerpo en HTML (opcional)
            
        Returns:
            bool: True si se envió correctamente, False si falló
        """
        try:
            # Crear mensaje
            message = MIMEMultipart("alternative")
            message["From"] = self.smtp_user
            message["To"] = recipient
            message["Subject"] = subject
            
            # Agregar cuerpo en texto plano
            part_text = MIMEText(body, "plain", "utf-8")
            message.attach(part_text)
            
            # Agregar cuerpo HTML si existe
            if html_body:
                part_html = MIMEText(html_body, "html", "utf-8")
                message.attach(part_html)
            
            # Conectar y enviar
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)
            
            print(f"✅ Email enviado exitosamente a {recipient}")
            return True
            
        except Exception as e:
            print(f"❌ Error al enviar email a {recipient}: {str(e)}")
            return False


class MockEmailSender(IEmailSender):
    """
    Implementación mock para desarrollo/testing
    (Liskov Substitution: puede reemplazar a SMTPEmailSender sin problemas)
    """
    
    async def send(
        self,
        recipient: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """Simula el envío de un email (para desarrollo/testing)"""
        print("=" * 60)
        print(f"📧 MOCK EMAIL")
        print(f"Para: {recipient}")
        print(f"Asunto: {subject}")
        print(f"Cuerpo: {body[:100]}...")
        if html_body:
            print(f"HTML: {html_body[:100]}...")
        print("=" * 60)
        return True