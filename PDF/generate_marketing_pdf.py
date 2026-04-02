import sys
sys.stdout.reconfigure(encoding='utf-8')

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# --- PATHS ---
ARTIFACTS_DIR = r"C:\Users\admin\.gemini\antigravity\brain\ac2e2167-cd2d-4f8b-b16c-a28564e0c314"
IMG_TITLE   = os.path.join(ARTIFACTS_DIR, "nexus_marketing_title_1774347089516.png")
IMG_ANALYSIS= os.path.join(ARTIFACTS_DIR, "nexus_ai_analysis_1774347106527.png")
IMG_CREATIVE= os.path.join(ARTIFACTS_DIR, "nexus_creative_factory_1774347215226.png")
OUTPUT_PATH = r"C:\Users\admin\Downloads\NEXUS\nexus-main\printivo\PDF\NEXUS_Marketing_AI_2026.pdf"

# --- BRAND COLORS ---
C_DARK   = HexColor("#0D0D1A")
C_TEAL   = HexColor("#00E5CC")
C_MAGENTA= HexColor("#FF2D78")
C_GOLD   = HexColor("#FFD700")
C_WHITE  = HexColor("#FFFFFF")
C_GRAY   = HexColor("#888888")
C_PANEL  = HexColor("#1A1A2E")

# --- CYRILLIC FONT SETUP ---
FONT_REG = "Arial"
FONT_BOLD = "Arial-Bold"

try:
    # Attempting to load standard Windows Arial font
    pdfmetrics.registerFont(TTFont('Arial', 'C:\\Windows\\Fonts\\arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:\\Windows\\Fonts\\arialbd.ttf'))
except:
    # If fail, fallback to standard but warn
    FONT_REG = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"
    print("Warning: Arial fonts not found, Cyrillic might be broken.")

W, H = A4

def make_pdf():
    c = canvas.Canvas(OUTPUT_PATH, pagesize=A4)

    # ===================== PAGE 1: TITLE =====================
    # Background
    c.setFillColor(C_DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Hero image
    if os.path.exists(IMG_TITLE):
        c.drawImage(IMG_TITLE, 0, H*0.38, width=W, height=H*0.62, preserveAspectRatio=True, mask='auto')

    # Gradient overlay strip
    c.setFillColor(C_DARK)
    c.rect(0, 0, W, H*0.45, fill=1, stroke=0)

    # Brand accent line
    c.setStrokeColor(C_TEAL)
    c.setLineWidth(3)
    c.line(20*mm, H*0.48, W - 20*mm, H*0.48)

    # Title text
    c.setFillColor(C_WHITE)
    c.setFont(FONT_BOLD, 32)
    c.drawCentredString(W/2, H*0.42, "NEXUS: MARKETING AI ENGINE")

    c.setFillColor(C_TEAL)
    c.setFont(FONT_BOLD, 16)
    c.drawCentredString(W/2, H*0.37, "Intelligent Advertising Automation for PRINTIVO 2026")

    c.setFillColor(C_GRAY)
    c.setFont(FONT_REG, 11)
    c.drawCentredString(W/2, H*0.31, "AI-powered campaigns · Google Ads · Meta Ads · Creative Factory · Analytics")

    # Footer
    c.setFillColor(C_MAGENTA)
    c.rect(0, 0, W, 8*mm, fill=1, stroke=0)
    c.setFillColor(C_WHITE)
    c.setFont(FONT_BOLD, 9)
    c.drawCentredString(W/2, 3*mm, "NEXUS — Advanced Agentic AI Engine  |  Printivo Production System  |  2026")

    c.showPage()

    # ===================== PAGE 2: ABILITIES =====================
    c.setFillColor(C_DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    if os.path.exists(IMG_ANALYSIS):
        c.drawImage(IMG_ANALYSIS, 0, H*0.5, width=W, height=H*0.5, preserveAspectRatio=True, mask='auto')

    # Overlay
    c.setFillColor(C_DARK)
    c.rect(0, 0, W, H*0.52, fill=1, stroke=0)

    # Section header
    c.setFillColor(C_TEAL)
    c.setFont(FONT_BOLD, 10)
    c.drawString(20*mm, H*0.95, "01  //  ВОЗМОЖНОСТИ")
    c.setFillColor(C_WHITE)
    c.setFont(FONT_BOLD, 22)
    c.drawString(20*mm, H*0.9, "AI-Анализ рынка и конкурентов")

    abilities = [
        ("🔎  Парсинг рынка", "Автоматический сбор семантики по нишам: наклейки, баннеры, полиграфия."),
        ("📊  Тепловые карты спроса", "Анализ трафика по городу и временным слотам (пиковые часы заказов)."),
        ("🎯  Таргетинг аудитории", "AI строит портрет покупателя по данным сайта и поведению клиентов."),
        ("🏆  Анализ конкурентов", "Сканирование рекламных объявлений конкурентов для выявления слабых мест."),
    ]

    y = H*0.46
    for title, desc in abilities:
        c.setFillColor(C_PANEL)
        c.roundRect(18*mm, y, W - 36*mm, 22*mm, 4, fill=1, stroke=0)
        c.setFillColor(C_TEAL)
        c.setFont(FONT_BOLD, 11)
        c.drawString(24*mm, y + 14*mm, title)
        c.setFillColor(C_GRAY)
        c.setFont(FONT_REG, 9)
        c.drawString(24*mm, y + 6*mm, desc)
        y -= 26*mm

    # Footer
    c.setFillColor(C_MAGENTA)
    c.rect(0, 0, W, 8*mm, fill=1, stroke=0)
    c.setFillColor(C_WHITE)
    c.setFont(FONT_BOLD, 9)
    c.drawCentredString(W/2, 3*mm, "NEXUS — Advanced Agentic AI Engine  |  Printivo Production System  |  2026")

    c.showPage()

    # ===================== PAGE 3: ADS AUTOMATION =====================
    c.setFillColor(C_DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    c.setFillColor(C_MAGENTA)
    c.setFont(FONT_BOLD, 10)
    c.drawString(20*mm, H*0.95, "02  //  РЕКЛАМНЫЕ КАМПАНИИ")
    c.setFillColor(C_WHITE)
    c.setFont(FONT_BOLD, 22)
    c.drawString(20*mm, H*0.9, "Управление Google Ads и Meta Ads")

    platforms = [
        ("Google Search Ads", "Ключевые слова с высокой конверсией, A/B тестирование заголовков", C_TEAL),
        ("Google Display", "Баннеры для ретаргетинга посетителей сайта", C_GOLD),
        ("Meta Ads (FB/IG)", "Таргетинг по интересам: бизнес, дизайн, офисы", C_MAGENTA),
        ("YouTube Pre-Roll", "Видео-кейсы производства Printivo (AI + FFmpeg)", HexColor("#8A2BE2")),
    ]

    y = H*0.82
    for platform, desc, color in platforms:
        c.setFillColor(color)
        c.rect(18*mm, y, 4*mm, 16*mm, fill=1, stroke=0)
        c.setFillColor(C_PANEL)
        c.rect(24*mm, y, W - 44*mm, 16*mm, fill=1, stroke=0)
        c.setFillColor(C_WHITE)
        c.setFont(FONT_BOLD, 12)
        c.drawString(28*mm, y + 9*mm, platform)
        c.setFillColor(C_GRAY)
        c.setFont(FONT_REG, 9)
        c.drawString(28*mm, y + 3*mm, desc)
        y -= 22*mm

    # ROI Table
    c.setFillColor(C_WHITE)
    c.setFont(FONT_BOLD, 14)
    c.drawString(20*mm, y - 5*mm, "Прогнозируемый KPI (прогноз данных):")

    y -= 18*mm
    headers = ["Канал", "CTR", "CPC (руб)", "ROAS"]
    rows    = [
        ["Google Search", "4.5%", "12-28", "350%"],
        ["Google Display", "0.9%", "4-8",  "180%"],
        ["Meta Ads",       "2.1%", "8-15", "280%"],
    ]
    col_w = (W - 40*mm) / 4

    # Header row
    c.setFillColor(C_TEAL)
    c.rect(18*mm, y, W-36*mm, 10*mm, fill=1, stroke=0)
    c.setFillColor(C_DARK)
    c.setFont(FONT_BOLD, 10)
    for i, h in enumerate(headers):
        c.drawString(20*mm + i*col_w + 2*mm, y + 3*mm, h)

    for row in rows:
        y -= 10*mm
        c.setFillColor(C_PANEL)
        c.rect(18*mm, y, W-36*mm, 10*mm, fill=1, stroke=0)
        c.setFillColor(C_WHITE)
        c.setFont(FONT_REG, 9)
        for i, cell in enumerate(row):
            c.drawString(20*mm + i*col_w + 2*mm, y + 3*mm, cell)

    # Footer
    c.setFillColor(C_MAGENTA)
    c.rect(0, 0, W, 8*mm, fill=1, stroke=0)
    c.setFillColor(C_WHITE)
    c.setFont(FONT_BOLD, 9)
    c.drawCentredString(W/2, 3*mm, "NEXUS — Advanced Agentic AI Engine  |  Printivo Production System  |  2026")

    c.showPage()

    # ===================== PAGE 4: CREATIVE FACTORY =====================
    c.setFillColor(C_DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    if os.path.exists(IMG_CREATIVE):
        c.drawImage(IMG_CREATIVE, 0, H*0.45, width=W, height=H*0.55, preserveAspectRatio=True, mask='auto')

    c.setFillColor(C_DARK)
    c.rect(0, 0, W, H*0.48, fill=1, stroke=0)

    c.setFillColor(C_GOLD)
    c.setFont(FONT_BOLD, 10)
    c.drawString(20*mm, H*0.95, "03  //  CREATIVE FACTORY")
    c.setFillColor(C_WHITE)
    c.setFont(FONT_BOLD, 22)
    c.drawString(20*mm, H*0.9, "AI-Генерация Креативов")

    creatives = [
        ("Баннеры (300+ форматов)",  "Авто-адаптация под Google, VK, Telegram, OZON"),
        ("HTML5 Лендинги",           "Генерация посадочных страниц под продукт"),
        ("Видео-ролики 15с",         "Промо из фото товаров Printivo (AI + FFmpeg)"),
        ("UGC-стиль контент",        "Фото продукта в интерьерах / на улице"),
    ]

    y = H*0.44
    for i, (title, desc) in enumerate(creatives):
        c.setFillColor(C_TEAL if i % 2 == 0 else C_MAGENTA)
        c.circle(22*mm, y + 7*mm, 3*mm, fill=1, stroke=0)
        c.setFillColor(C_WHITE)
        c.setFont(FONT_BOLD, 11)
        c.drawString(28*mm, y + 10*mm, title)
        c.setFillColor(C_GRAY)
        c.setFont(FONT_REG, 9)
        c.drawString(28*mm, y + 3*mm, desc)
        y -= 22*mm

    # Footer
    c.setFillColor(C_MAGENTA)
    c.rect(0, 0, W, 8*mm, fill=1, stroke=0)
    c.setFillColor(C_WHITE)
    c.setFont(FONT_BOLD, 9)
    c.drawCentredString(W/2, 3*mm, "NEXUS — Advanced Agentic AI Engine  |  Printivo Production System  |  2026")

    c.showPage()

    # ===================== PAGE 5: ANALYTICS + CTA =====================
    c.setFillColor(C_DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    c.setFillColor(C_WHITE)
    c.setFont(FONT_BOLD, 10)
    c.drawString(20*mm, H*0.95, "04  //  СКВОЗНАЯ АНАЛИТИКА И ROI")
    c.setFillColor(C_WHITE)
    c.setFont(FONT_BOLD, 22)
    c.drawString(20*mm, H*0.9, "От клика до заказа")

    # Flow visualization
    steps = ["Клик", "Лендинг", "Заказ", "Проверка", "Печать"]
    colors_flow = [C_TEAL, C_GOLD, C_MAGENTA, C_TEAL, C_GOLD]
    x = 18*mm
    y_flow = H*0.78
    box_w = (W - 36*mm) / 5 - 4*mm

    for i, (step, col) in enumerate(zip(steps, colors_flow)):
        c.setFillColor(col)
        c.roundRect(x, y_flow, box_w, 22*mm, 4, fill=1, stroke=0)
        c.setFillColor(C_DARK)
        c.setFont(FONT_BOLD, 8)
        c.drawCentredString(x + box_w/2, y_flow + 10*mm, step)
        if i < 4:
            c.setFillColor(C_WHITE)
            c.setFont(FONT_BOLD, 14)
            c.drawString(x + box_w + 1*mm, y_flow + 9*mm, "→")
        x += box_w + 5*mm

    # Analytics metrics
    metrics = [
        ("Сквозная конверсия", "полный путь от клика до оплаты"),
        ("A/B тест в авто-режиме", "AI выбирает лучший рекламный вариант"),
        ("Авто-ставки (Smart Bidding)", "управление бюджетом в реальном времени"),
        ("Когортный анализ", "LTV, повторные заказы, сезонность"),
    ]

    y = H*0.65
    for title, desc in metrics:
        c.setFillColor(C_PANEL)
        c.roundRect(18*mm, y, W - 36*mm, 18*mm, 4, fill=1, stroke=0)
        c.setFillColor(C_TEAL)
        c.setFont(FONT_BOLD, 10)
        c.drawString(24*mm, y + 10*mm, f"✓  {title}")
        c.setFillColor(C_GRAY)
        c.setFont(FONT_REG, 9)
        c.drawString(24*mm, y + 4*mm, desc)
        y -= 23*mm

    # CTA Block
    c.setFillColor(C_MAGENTA)
    c.roundRect(18*mm, 22*mm, W - 36*mm, 30*mm, 6, fill=1, stroke=0)
    c.setFillColor(C_WHITE)
    c.setFont(FONT_BOLD, 16)
    c.drawCentredString(W/2, 42*mm, "Готовы запустить Рекламный Автопилот?")
    c.setFont(FONT_REG, 11)
    c.drawCentredString(W/2, 34*mm, "NEXUS подключится к вашему рекламному кабинету за 1 рабочий день.")
    c.drawCentredString(W/2, 27*mm, "Google Ads API  •  Meta Business API  •  Яндекс.Директ  •  VK Ads")

    # Footer
    c.setFillColor(C_DARK)
    c.rect(0, 0, W, 8*mm, fill=1, stroke=0)
    c.setFillColor(C_TEAL)
    c.setFont(FONT_BOLD, 9)
    c.drawCentredString(W/2, 3*mm, "NEXUS — Advanced Agentic AI Engine  |  Printivo Production System  |  2026")

    c.showPage()
    c.save()
    print(f"PDF saved: {OUTPUT_PATH}")

if __name__ == '__main__':
    make_pdf()
    print("Done! NEXUS_Marketing_AI_2026.pdf is ready.")
