import sys
import os
from googleapiclient.discovery import build

# Add libs to path
sys.path.append(os.getcwd())
from libs.gmail import get_google_creds

if __name__ == '__main__':
    # Ensure UTF-8 output
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    try:
        creds = get_google_creds()
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Get about info to check storage
        about = drive_service.about().get(fields="storageQuota, user").execute()
        
        user = about.get('user', {})
        quota = about.get('storageQuota', {})
        
        total_bytes = int(quota.get('limit', 0))
        used_bytes = int(quota.get('usage', 0))
        
        total_gb = total_bytes / (1024**3)
        used_gb = used_bytes / (1024**3)
        
        print(f"--- ИНФОРМАЦИЯ ОБ АККАУНТЕ GOOGLE ---")
        print(f"Пользователь: {user.get('displayName')} ({user.get('emailAddress')})")
        print(f"Всего места: {total_gb:.2f} GB")
        print(f"Использовано: {used_gb:.2f} GB ({(used_bytes/total_bytes*100):.1f}%)")
        
        if total_gb == 15.0:
            print("Тариф: Бесплатный (15 GB)")
        elif total_gb > 15.0:
            print(f"Тариф: Платный / Workspace / Google One ({total_gb:.0f} GB)")
        else:
            print(f"Тариф: Не определен (Лимит: {total_gb:.2f} GB)")
            
    except Exception as e:
        print(f"Ошибка при получении данных о тарифе: {e}")
