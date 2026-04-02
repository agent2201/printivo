import os
import sys

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libs.gmail import send_email

if __name__ == '__main__':
    # Ensure UTF-8 output
    sys.stdout.reconfigure(encoding='utf-8')
    
    targets = ["yurarulev@gmail.com", "eugenetarget8@gmail.com", "larichevaanya@gmail.com"]
    subject = "🚀 NEXUS Marketing Strategy: Эра Автономного Роста"
    pdf_path = r"C:\Users\admin\Downloads\NEXUS\nexus-main\printivo\PDF\NEXUS_Marketing_AI_2026.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Error: Missing PDF at {pdf_path}")
        sys.exit(1)

    for email in targets:
        body = f"""
        <html>
            <body style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #0d0d1a; color: #ffffff; padding: 40px;">
                <div style="background-color: #1a1a2e; padding: 40px; border-radius: 20px; border: 1px solid #00e5cc; max-width: 650px; margin: 0 auto; box-shadow: 0 10px 30px rgba(0,229,204,0.1);">
                    <h1 style="color: #00e5cc; margin-top: 0; font-size: 28px; letter-spacing: 1px;">Команда Printivo, привет! 👋</h1>
                    
                    <p style="font-size: 18px; line-height: 1.6; color: #e0e0e0;">
                        Пока мы настраивали автоответчики и базу данных, я заглянул в наше будущее... 
                    </p>
                    
                    <div style="background-color: #0d0d1a; border-radius: 12px; padding: 25px; margin: 30px 0; border-left: 5px solid #ff2d78;">
                        <h3 style="color: #ff2d78; margin-top: 0;">Что это за файл?</h3>
                        <p style="font-size: 15px; color: #cccccc; margin-bottom: 0;">
                            Это — <b>NEXUS Strategy 2026</b>. Внутри я описал, как наш проект будет сам находить клиентов, генерировать для них рекламу и захватывать рынок полиграфии, пока мы занимаемся качеством печати.
                        </p>
                    </div>

                    <p style="font-size: 16px; color: #ffffff;">
                        <b>Внутри PDF вы найдете:</b>
                        <ul style="color: #00e5cc;">
                            <li>Как я шпионю за конкурентами 🔎</li>
                            <li>Сколько мы заработаем на Google Ads 💰</li>
                            <li>Как выглядят наши будущие креативы 🎨</li>
                        </ul>
                    </p>

                    <p style="font-size: 15px; color: #888888; margin-top: 30px;">
                        Это только начало. Проект <b>Printivo</b> теперь — это не просто сервер, это цифровая экосистема с интеллектом.
                    </p>
                    
                    <div style="text-align: center; margin-top: 40px; border-top: 1px solid #333; padding-top: 30px;">
                        <span style="color: #00e5cc; font-weight: bold; font-size: 12px; text-transform: uppercase; letter-spacing: 2px;">
                            NEXUS AI | Advanced Agentic Engine
                        </span>
                    </div>
                </div>
            </body>
        </html>
        """
        
        print(f"Отправка презентации на {email}...")
        if send_email(email, subject, body, pdf_path):
            print(f"✨ ГОТОВО: Презентация доставлена {email}!")
        else:
            print(f"❌ ОШИБКА: Не удалось отправить на {email}.")
