import os
import time
import schedule
import gspread
import isodate
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
CHANNEL_ID = os.getenv('CHANNEL_ID')
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
SHEET_NAME = os.getenv('SHEET_NAME')

if not YOUTUBE_API_KEY:
    print("Ошибка: Не найден YOUTUBE_API_KEY в файле .env")
    exit()

COL_DATE = 1
COL_TITLE = 2
COL_TYPE = 3
COL_VIEWS = 4
COL_LIKES = 5
COL_COMMENTS = 6
COL_VIDEO_ID = 11

def get_youtube_service():
    return build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def get_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    return sheet

def get_video_type(duration_iso):
    """Определяет тип видео (Shorts/Video) по длительности."""
    try:
        dur = isodate.parse_duration(duration_iso)
        if dur.total_seconds() <= 60:
            return "Short"
        return "Video"
    except:
        return "Video"

def job():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Запуск проверки YouTube...")
    
    try:
        youtube = get_youtube_service()
        sheet = get_google_sheet()
        
        channel_response = youtube.channels().list(
            id=CHANNEL_ID,
            part='contentDetails'
        ).execute()
        
        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        playlist_response = youtube.playlistItems().list(
            playlistId=uploads_playlist_id,
            part='snippet',
            maxResults=10
        ).execute()
        
        video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_response['items']]
        
        stats_response = youtube.videos().list(
            id=','.join(video_ids),
            part='statistics,snippet,contentDetails'
        ).execute()
        
        api_videos = {}
        for item in stats_response['items']:
            vid = item['id']
            stats = item['statistics']
            snippet = item['snippet']
            
            video_type = get_video_type(item['contentDetails']['duration'])
            published_at = datetime.strptime(snippet['publishedAt'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M")
            
            api_videos[vid] = {
                'date': published_at,
                'title': snippet['title'],
                'type': video_type,
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'comments': int(stats.get('commentCount', 0)),
                'id': vid
            }

        existing_ids_list = sheet.col_values(COL_VIDEO_ID)
        
        existing_map = {vid: i+1 for i, vid in enumerate(existing_ids_list) if vid}

        new_rows = []
        updates = []
        
        for vid in reversed(video_ids):
            if vid not in api_videos: continue
            
            data = api_videos[vid]
            
            if vid in existing_map:
                row_num = existing_map[vid]
                
                updates.append({
                    'range': gspread.utils.rowcol_to_a1(row_num, COL_VIEWS),
                    'values': [[data['views']]]
                })
                updates.append({
                    'range': gspread.utils.rowcol_to_a1(row_num, COL_LIKES),
                    'values': [[data['likes']]]
                })
                updates.append({
                    'range': gspread.utils.rowcol_to_a1(row_num, COL_COMMENTS),
                    'values': [[data['comments']]]
                })
                print(f"   Обновление: {data['title'][:30]}... (Views: {data['views']})")
                
            else:
                row = [
                    data['date'],
                    data['title'],
                    data['type'],
                    data['views'],
                    data['likes'],
                    data['comments'],
                    "", "", "", "",
                    data['id']
                ]
                new_rows.append(row)
                print(f"   Новое видео: {data['title'][:30]}...")

        if new_rows:
            sheet.append_rows(new_rows)
            print(f"Добавлено новых строк: {len(new_rows)}")
            
        if updates:
            sheet.batch_update(updates)
            print(f"Обновлено полей статистики: {len(updates)}")
            
        if not new_rows and not updates:
            print("💤 Нет изменений.")

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    print("Бот запущен. Ожидание расписания...")
    
    job()
    
    schedule.every(1).hours.do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(60)