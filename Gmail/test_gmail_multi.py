import sys
from libs.gmail import send_email

if __name__ == '__main__':
    # Ensure UTF-8 output
    sys.stdout.reconfigure(encoding='utf-8')
    
    targets = ["eugenetarget8@gmail.com", "larichevaanya@gmail.com"]
    subject = "🚀 NEXUS Printivo: Тестовая активация сервера"
    
    for email in targets:
        body = f"""
        <html>
            <body style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #f8f9fa; padding: 30px;">
                <div style="background-color: #ffffff; padding: 30px; border-radius: 12px; border: 1px solid #e1e4e8; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h2 style="color: #2da44e; margin-bottom: 20px;">✅ Система Printivo Активна!</h2>
                    <p style="color: #24292f; font-size: 16px; line-height: 1.6;">Это автоматическое уведомление от вашего нового помощника <b>NEXUS-Antigravity</b>.</p>
                    <p style="color: #24292f; font-size: 16px; line-height: 1.6;">Интеграция с <b>Google Drive</b> и <b>Gmail</b> прошла успешно. Мы готовы к началу работы по производству принтов.</p>
                    <hr style="border: 0; border-top: 1px solid #e1e4e8; margin: 25px 0;">
                    <p style="font-size: 14px; color: #57606a;">Получатель: <b>{email}</b></p>
                    <p style="font-size: 12px; color: #8c959f; text-align: center; margin-top: 30px;">
                        NEXUS AI Engine v4.1 | Printivo Automatization System 2026
                    </p>
                </div>
            </body>
        </html>
        """
        
        print(f"Отправка тестового письма на {email}...")
        if send_email(email, subject, body):
            print(f"🔥 УСПЕХ: Письмо успешно отправлено на {email}!")
        else:
            print(f"❌ ОШИБКА: Не удалось отправить письмо на {email}. Проверьте соединение.")
