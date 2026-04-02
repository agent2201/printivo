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
    subject = "⚠️ Архитектурный Отчет NEXUS: Блокировка HEVC (H.265) + Alpha"
    
    body = """
    <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f6fa; padding: 30px;">
            <div style="background-color: #ffffff; padding: 35px; border-radius: 12px; border: 1px solid #e1e4e8; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
                <h2 style="color: #d73a49; margin-bottom: 25px; border-bottom: 2px solid #f4f6fa; padding-bottom: 10px;">🛡 Техническое ограничение среды (Windows)</h2>
                <p style="color: #24292e; font-size: 16px; line-height: 1.6;">Евгений, создание HEVC с альфа-каналом стандартными средствами FFmpeg на платформе Windows <b>невозможно</b>.</p>
                
                <div style="background-color: #ffeef0; padding: 20px; border-left: 4px solid #d73a49; margin: 20px 0;">
                    <b>Техническая блокировка (NEXUS Zero-Guessing Validation):</b><br>
                    • <b>libx265 (CPU)</b>: Официальные билды для Windows (включая Gyan/BtbN) компилируются БЕЗ поддержки альфа-слоя <i>(Loaded libx265 does not support alpha layer encoding)</i>.<br>
                    • <b>NVENC / Media Foundation</b>: Аппаратные кодеки на Windows не поддерживают <i>yuva420p10le</i> и принудительно сбрасывают прозрачность в непрозрачный формат (bgra/nv12).<br>
                    • <b>HEVC + Alpha (hvc1)</b> — это закрытый архитектурный стандарт Apple.
                </div>
                
                <p style="color: #24292e; font-size: 16px; font-weight: bold;">Возможные решения:</p>
                <ol style="color: #24292e; font-size: 15px; line-height: 1.5; padding-left: 20px;">
                    <li><b>Компиляция macOS:</b> Вы можете переконвертировать этот исходник на базе macOS в Terminal через встроенный нативный кодек:<br><code style="background:#f6f8fa; padding:2px 5px; border-radius:3px;">ffmpeg -i input.mov -c:v hevc_videotoolbox -alpha_quality 0.75 -tag:v hvc1 output.mov</code></li>
                    <li style="margin-top:10px;"><b>Использовать WebM (VP9):</b> Файл <i>Comp 1_22_VP9_alpha.webm</i> (отправленный в предыдущем сообщении) уже имеет прозрачность и вес 244 КБ. Начиная с Safari 14+ (macOS/iOS), <b>браузер поддерживает WebM-контейнер и прозрачность</b>. Для современного парка устройств Apple VP9 более чем достаточно.</li>
                </ol>
                
                <hr style="border: 0; border-top: 1px solid #eaecef; margin: 30px 0;">
                <p style="font-size: 14px; color: #586069; text-align: center;">Анализ и проверка логики завершена | <b>NEXUS Autonomous Agent v4.1</b></p>
            </div>
        </body>
    </html>
    """
    
    print(f"Отправка технического ответа на {target_email}...")
    if send_email(target_email, subject, body):
        print(f"✅ УСПЕХ: Ответ доставлен Евгению!")
    else:
        print(f"❌ ОШИБКА: Не удалось отправить письмо.")
