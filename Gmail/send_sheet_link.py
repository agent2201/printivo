import sys
from libs.gmail import send_email

if __name__ == '__main__':
    # Ensure UTF-8 output
    sys.stdout.reconfigure(encoding='utf-8')
    
    targets = ["yurarulev@gmail.com", "eugenetarget8@gmail.com", "larichevaanya@gmail.com"]
    sheet_url = "https://docs.google.com/spreadsheets/d/1GgNcg0cmhH73u0PRjS81Y8fvN9Dp8Me2BRA_aah_kss"
    subject = "📊 Общая база заказов --PRINTIVO активирована"
    
    for email in targets:
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
                <div style="background-color: #ffffff; padding: 30px; border-radius: 8px; border: 1px solid #ddd; max-width: 650px; margin: 0 auto;">
                    <h2 style="color: #4CAF50;">✅ База заказов запущена!</h2>
                    <p>Ваша система <b>Printivo</b> теперь подключена к общей облачной таблице.</p>
                    <p>Это ваш основной реестр для контроля производства в реальном времени.</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{sheet_url}" style="background-color: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Открыть таблицу PRINTIVO (Google Таблицы)</a>
                    </div>
                    <p style="font-size: 0.9em; color: #666;">Здесь вы сможете видеть все входящие заказы, их статусы, размеры и качество исполнения (DPI).</p>
                    <hr>
                    <p style="font-size: 0.7em; color: #999; text-align: center;">NEXUS-Antigravity AI | Advanced Order Management v4.1</p>
                </div>
            </body>
        </html>
        """
        
        print(f"Отправка ссылки на таблицу для {email}...")
        if send_email(email, subject, body):
            print(f"🔥 УСПЕХ: Ссылка на таблицу доставлена на {email}!")
        else:
            print(f"❌ ОШИБКА: Не удалось отправить письмо на {email}.")
