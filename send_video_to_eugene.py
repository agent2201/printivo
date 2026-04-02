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
    video_path = r"C:\Users\admin\Downloads\NEXUS\nexus-main\printivo\INBOX\Comp 1_22_VP9_alpha.webm"
    
    subject = "📹 Ваш видео-файл с прозрачностью (Web/VP9) | NEXUS-Printivo"
    body = f"""
    <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #f0f7ff; padding: 30px;">
            <div style="background-color: #ffffff; padding: 35px; border-radius: 12px; border: 1px solid #cce3ff; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
                <h2 style="color: #0066cc; margin-bottom: 25px; border-bottom: 2px solid #f0f7ff; padding-bottom: 10px;">📦 Готовый файл для веба</h2>
                <p style="color: #333; font-size: 16px; line-height: 1.6;">Евгений, видео переконвертировано в формат <b>WebM (VP9)</b> с сохранением альфа-канала (прозрачности).</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-left: 4px solid #0066cc; margin: 20px 0;">
                    <b>Параметры файла:</b><br>
                    • Формат: <b>WebM / VP9</b><br>
                    • Вес: <b>0.24 MB</b> (сжатие ~1500x)<br>
                    • Особенности: <b>Сохранена прозрачность</b>
                </div>
                
                <p style="color: #333; font-size: 14px;">Файл прикреплен к этому письму.</p>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 14px; color: #666; text-align: center;">NEXUS AI v4.1 | Automated Delivery System</p>
            </div>
        </body>
    </html>
    """
    
    print(f"Отправка файла {os.path.basename(video_path)} на {target_email}...")
    if send_email(target_email, subject, body, file_path=video_path):
        print(f"✅ УСПЕХ: Файл доставлен Евгению!")
    else:
        print(f"❌ ОШИБКА: Не удалось отправить письмо.")
