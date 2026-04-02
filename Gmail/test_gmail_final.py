import sys
from libs.gmail import send_email

if __name__ == '__main__':
    # Ensure UTF-8 output
    sys.stdout.reconfigure(encoding='utf-8')
    
    target_email = "yurarulev@gmail.com"
    subject = "🚀 NEXUS Printivo: Почтовый сервис активирован"
    body = """
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #ddd;">
                <h2 style="color: #4CAF50;">✅ Поздравляем! Соединение установлено.</h2>
                <p>Ваша система <b>NEXUS Printivo</b> теперь имеет собственный "Голос".</p>
                <p>Это автоматическое уведомление подтверждает, что все <b>Google API</b> (Drive + Gmail) настроены корректно.</p>
                <hr>
                <p style="font-size: 0.9em; color: #666;">Тестовое письмо отправлено на: <b>yurarulev@gmail.com</b></p>
                <p style="font-size: 0.7em; color: #999;">NEXUS-Antigravity AI Engine 2026 | Advanced Agentic Coding</p>
            </div>
        </body>
    </html>
    """
    
    print(f"Отправка тестового письма на {target_email}...")
    if send_email(target_email, subject, body):
        print("🔥 УСПЕХ: Письмо успешно отправлено! Проверьте папку 'Входящие' или 'Спам'.")
    else:
        print("❌ ОШИБКА: Не удалось отправить письмо. Проверьте логи.")
