import sys
import os

# Add libs to path
sys.path.append(os.getcwd())
from libs.gmail import send_email

if __name__ == '__main__':
    # Ensure UTF-8 output
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    target_email = "eugenetarget8@gmail.com"
    subject = "📊 Скриншот: Текущие квоты моделей (NEXUS AI)"
    
    body = """
    <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f6fa; padding: 30px;">
            <div style="background-color: #ffffff; padding: 35px; border-radius: 12px; border: 1px solid #e1e4e8; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
                <h2 style="color: #0366d6; margin-bottom: 25px; border-bottom: 2px solid #f4f6fa; padding-bottom: 10px;">📊 Статус: Доступные Модели (QUOTA)</h2>
                <p style="color: #24292e; font-size: 16px; line-height: 1.6;">Евгений, пересылаю скриншот с текущими данными по лимитам моделей (Gemini, Claude, GPT-OSS).</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-left: 4px solid #0366d6; margin: 20px 0;">
                    <b>Детали:</b><br>
                    • Файл: <i>Снимок окна настроек (Settings - Models)</i><br>
                    • Статус: Отправлено по запросу пользователя.
                </div>
                
                <hr style="border: 0; border-top: 1px solid #eaecef; margin: 30px 0;">
                <p style="font-size: 14px; color: #586069; text-align: center;"><b>NEXUS Autonomous Agent v4.1</b></p>
            </div>
        </body>
    </html>
    """
    
    file_path = r"C:\Users\admin\.gemini\antigravity\brain\d17ebf73-d4c9-44a4-bfb9-afbf26269e4b\media__1774369581350.png"
    
    print(f"Отправка файла со скриншотом на {target_email}...")
    if send_email(target_email, subject, body, file_path=file_path):
        print(f"✅ УСПЕХ: Фрагмент доставлен Евгению!")
    else:
        print(f"❌ ОШИБКА: Не удалось отправить письмо.")
