import sys
from libs.gmail import send_email

if __name__ == '__main__':
    # Ensure UTF-8 output
    sys.stdout.reconfigure(encoding='utf-8')
    
    targets = ["yurarulev@gmail.com", "eugenetarget8@gmail.com", "larichevaanya@gmail.com"]
    subject = "🤖 Новая функция: Активирован Интеллектуальный Автоответчик Printivo"
    
    for email in targets:
        body = f"""
        <html>
            <body style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #f0f7ff; padding: 30px;">
                <div style="background-color: #ffffff; padding: 35px; border-radius: 12px; border: 1px solid #cce3ff; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
                    <h2 style="color: #0066cc; margin-bottom: 25px; border-bottom: 2px solid #f0f7ff; padding-bottom: 10px;">🛡 Обновление системы: NEXUS Guard</h2>
                    <p style="color: #333; font-size: 16px; line-height: 1.6;">Мы рады сообщить вам, что ваш проект <b>Printivo</b> теперь оснащен функцией <b>Интеллектуальный Автоответчик</b>.</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-left: 4px solid #0066cc; margin: 20px 0;">
                        <b>Как это работает?</b><br>
                        Теперь при получении любого письма от вас или вашей команды, система мгновенно высылает подтверждение о получении. Это гарантирует, что ни один файл из <b>INBOX</b> не останется незамеченным.
                    </div>
                    
                    <p style="color: #333; font-size: 16px;">Система мониторинга теперь работает в режиме реального времени (интервал: 10 секунд).</p>
                    
                    <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0;">
                    <p style="font-size: 14px; color: #666; text-align: center;">Статус: <b>Active / Running</b> | NEXUS AI v4.1</p>
                </div>
            </body>
        </html>
        """
        
        print(f"Отправка оповещения о новой функции для {email}...")
        if send_email(email, subject, body):
            print(f"🔥 УСПЕХ: Оповещение об автоответчике доставлено на {email}!")
        else:
            print(f"❌ ОШИБКА: Не удалось отправить письмо на {email}.")
