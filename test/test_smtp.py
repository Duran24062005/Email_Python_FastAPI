import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

print("🔧 Probando conexión SMTP...")

msg = MIMEMultipart()
msg["Subject"] = "Test desde Python"
msg["From"] = "alexisdurangomez588@gmail.com"
msg["To"] = "alexisdurangomez588@gmail.com"
msg.attach(MIMEText("Este es un email de prueba", "plain"))

try:
    print("📡 Conectando a smtp.gmail.com:465 con SSL...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
        print("🔐 Autenticando...")
        server.login("alexisdurangomez588@gmail.com", "TU_PASSWORD_AQUI")
        print("📧 Enviando...")
        server.send_message(msg)
        print("✅ Email enviado exitosamente!")
except Exception as e:
    print(f"❌ Error: {e}")