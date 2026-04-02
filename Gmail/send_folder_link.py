import sys
from libs.gmail import send_email

if __name__ == '__main__':
    # Ensure UTF-8 output
    sys.stdout.reconfigure(encoding='utf-8')
    
    targets = ["yurarulev@gmail.com", "eugenetarget8@gmail.com", "larichevaanya@gmail.com"]
    folder_url = "https://drive.google.com/drive/folders/1RFqidlNi93olbNxx1ENIcxXfD8eqAMPQ"
    subject = "📁 Доступ к облачной папке проекта --PRINTIVO"
    
    for email in targets:
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
                <div style="background-color: #ffffff; padding: 30px; border-radius: 8px; border: 1px solid #ddd; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #4CAF50;">✅ Общий доступ открыт</h2>
                    <p>Вас приветствует система автоматизации <b>Printivo</b>.</p>
                    <p>Вам предоставлен доступ к главной облачной папке проекта <b>--PRINTIVO</b> на Google Drive.</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{folder_url}" style="background-color: #4CAF50; color: white; padding: 15px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Открыть папку на Google Диск</a>
                    </div>
                    <p style="font-size: 0.9em; color: #666;">В этой папке будут храниться все макеты и результаты вашего производства.</p>
                    <hr>
                    <p style="font-size: 0.7em; color: #999; text-align: center;">NEXUS-Antigravity AI | Printivos Automatiztion v4.1</p>
                </div>
            </body>
        </html>
        """
        
        print(f"Отправка ссылки на папку для {email}...")
        if send_email(email, subject, body):
            print(f"🔥 УСПЕХ: Ссылка успешно доставлена на {email}!")
        else:
            print(f"❌ ОШИБКА: Не удалось отправить письмо на {email}.")
