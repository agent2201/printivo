import sys
import os

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libs.gmail import send_email

if __name__ == '__main__':
    # Force UTF-8
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Target list (excluding larichevaanya@gmail.com as requested)
    targets = ["yurarulev@gmail.com", "eugenetarget8@gmail.com"]
    subject = "🤖 NEXUS Printivo: Обновление Инфраструктуры Автоматизации"
    
    body_text = """
    Все 4 дублирующих процесса python.exe были принудительно завершены для исключения ошибок доступа к токену и дублирования ответов клиентам.
    Менеджер Сервиса: Создан оркестратор services/gmail-responder/service.py, который в реальном времени следит за работой автоответчика. Если основной скрипт упадет или зависнет, менеджер перезапустит его через 10 секунд.
    Автозагрузка (Persistence): Создан скрипт run_hidden.vbs и помещен в папку автозагрузки Windows (%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup). Теперь система будет запускаться автоматически при входе в Windows.
    Скрытый режим: Система работает полностью в фоновом режиме. Никаких лишних окон терминала на рабочем столе не появится.
    """
    
    html_body = f"""
    <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #f7f9fc; padding: 25px;">
            <div style="background-color: #ffffff; padding: 30px; border-radius: 12px; border: 1px solid #e1e7f0; max-width: 650px; margin: 0 auto; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
                <h2 style="color: #004d99; border-bottom: 2px solid #004d99; padding-bottom: 10px; margin-bottom: 25px;">🛠 NEXUS: Обновление Инфраструктуры</h2>
                
                <p style="color: #333; font-size: 16px; line-height: 1.6;">В рамках оптимизации проекта <b>Printivo</b> были внедрены следующие изменения:</p>
                
                <ul style="color: #444; font-size: 15px; line-height: 1.8; background-color: #f0f4f8; padding: 20px 40px; border-radius: 8px;">
                    <li><b>Оптимизация:</b> Удалено 4 дублирующих процесса для устранения ошибок токена.</li>
                    <li><b>Оркестратор:</b> Запущен <code>service.py</code> для контроля стабильности 24/7.</li>
                    <li><b>Автозагрузка:</b> Система добавлена в Startup через VBS-скрипт.</li>
                    <li><b>Скрытый режим:</b> Работа полностью переведена в фоновый режим (Invisible).</li>
                </ul>
                
                <div style="background-color: #fff4e5; border-left: 4px solid #ffcc00; padding: 15px; margin: 25px 0; color: #664d03;">
                    ⚠️ Статус: <b>Active / Monitoring</b>
                </div>
                
                <p style="font-size: 12px; color: #999; text-align: center; border-top: 1px solid #eee; padding-top: 15px;">
                    Сообщение сгенерировано NEXUS AI Engine v4.1
                </p>
            </div>
        </body>
    </html>
    """
    
    print("Запуск рассылки уведомлений об обновлении инфраструктуры...")
    
    for email in targets:
        print(f"Отправка на {email}...")
        if send_email(email, subject, html_body):
            print(f"✅ УСПЕХ: Уведомление доставлено на {email}.")
        else:
            print(f"❌ ОШИБКА: Не удалось отправить на {email}.")
