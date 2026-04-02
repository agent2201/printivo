import sys
import os
import base64

# Add libs to path
sys.path.append(os.getcwd())
from libs.gmail import send_email

if __name__ == '__main__':
    # Ensure UTF-8 output
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    target_email = "eugenetarget8@gmail.com"
    subject = "📸 Скриншот: Текущие квоты моделей (Вложенный файл)"
    
    file_path = r"C:\Users\admin\.gemini\antigravity\brain\d17ebf73-d4c9-44a4-bfb9-afbf26269e4b\media__1774369581350.png"
    
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        
    body = f"""
    <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f6fa; padding: 30px;">
            <div style="background-color: #ffffff; padding: 35px; border-radius: 12px; border: 1px solid #e1e4e8; max-width: 800px; margin: 0 auto; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
                <h2 style="color: #0366d6; margin-bottom: 25px; border-bottom: 2px solid #f4f6fa; padding-bottom: 10px;">📊 Статус: Доступные Модели (Скриншот)</h2>
                <p style="color: #24292e; font-size: 16px; line-height: 1.6;">Евгений, дублирую скриншот с текущими квотами (Он встроен прямо в это письмо).</p>
                
                <div style="margin: 20px 0; border: 1px solid #ccc; padding: 10px;">
                    <img src="data:image/png;base64,{encoded_string}" style="max-width: 100%; height: auto;" alt="Model Quota Screenshot">
                </div>
                
                <hr style="border: 0; border-top: 1px solid #eaecef; margin: 30px 0;">
                <p style="font-size: 14px; color: #586069; text-align: center;"><b>NEXUS Autonomous Agent v4.1</b></p>
            </div>
        </body>
    </html>
    """
    
    print(f"Повторная отправка скриншота (Inline + Attachment) на {target_email}...")
    if send_email(target_email, subject, body, file_path=file_path):
        print(f"✅ УСПЕХ: Письмо со скриншотом доставлено Евгению!")
    else:
        print(f"❌ ОШИБКА: Не удалось отправить письмо.")
