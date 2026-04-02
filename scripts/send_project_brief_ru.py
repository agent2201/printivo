import sys
import os

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Ensure UTF-8 output for CLI
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from libs.nexus_mailer import send_templated_email

def send_project_brief():
    # Recipient list
    recipients = ["eugenetarget8@gmail.com", "yurarulev@gmail.com"]
    
    subject = "NEXUS Printivo: Autonomous Layout & Marketing Engine"
    title = "NEXUS Printivo"
    
    # User's provided Russian description
    message_body = """
    <b>Автономная система верстки и маркетинга для полиграфического бизнеса.</b><br><br>
    NEXUS Printivo — это специализированная система автоматизации, ориентированная на локальные решения и предназначенная для устранения разрыва между интернет-магазинами на базе WooCommerce и локальными процессами дизайна и производства.<br><br>
    
    <b>Основные характеристики:</b><br>
    • <b>Инфраструктура с приоритетом локальных ресурсов</b>: использует MinIO для постоянного хранения данных и безопасного управления локальными активами.<br>
    • <b>Автоматизированный загрузчик</b>: Пользовательский плагин для WordPress/WooCommerce, обеспечивающий бесперебойную прямую передачу файлов через туннели Nginx/Ngrok.<br>
    • <b>Автоматизация маркетинга</b>: Интегрированные инструменты Google API для автоматических рассылок в Gmail и уведомлений о кампаниях на основе ИИ.<br>
    • <b>Генерация PDF-файлов</b>: Динамический генератор маркетинговых презентаций с высококачественными макетами и поддержкой шрифтов.<br>
    • <b>Туннельное соединение</b>: надежное и безопасное соединение между удаленными и локальными сетями с использованием Ngrok и Cloudflared.<br><br>
    
    <b>Технологический стек:</b><br>
    • <b>Основной движок</b>: Python, PowerShell<br>
    • <b>Интерфейс</b>: PHP (WordPress/WooCommerce)<br>
    • <b>Data Engine</b>: MinIO — высокопроизводительное хранилище данных<br>
    • <b>Сеть</b>: Docker-контейнеризированный Nginx с туннелями Ngrok/Cloudflare.<br>
    • <b>Автоматизация</b>: интеграция API Google Cloud Workspace (Gmail, Drive)<br><br>
    
    Разработано на основе архитектуры NEXUS — версия 2026 года.
    """
    
    print(f"🚀 Initializing bulk delivery for NEXUS Project Brief...")
    
    for email in recipients:
        print(f"Sending to {email}...")
        success = send_templated_email(
            to=email,
            subject=subject,
            title=title,
            recipient_name="Team",
            message_body=message_body,
            cta_text="View on GitHub",
            cta_link="https://github.com/agent2201/printivo"
        )
        if success:
            print(f"✅ Success: Brief delivered to {email}")
        else:
            print(f"❌ Error: Failed to delivery to {email}")

if __name__ == "__main__":
    send_project_brief()
