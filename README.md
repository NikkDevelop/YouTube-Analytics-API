**YouTube Analytics & Content Tracker** is a Python automation tool that monitors a YouTube channel and synchronizes content performance metrics with Google Sheets.
<img width="1444" height="238" alt="image" src="https://github.com/user-attachments/assets/41f68f88-a8ec-474f-a9a6-26e933309ba7" />

> Uses the **Uploads Playlist** instead of search queries for maximum efficiency.

**Key Features**

- **Automatic detection** of new videos  
- **Hourly statistics updates**  
- **Shorts vs long-form classification**  
- **Incremental updates** (no data loss)  
- **Google Sheets synchronization**  
- **Scheduled execution + manual trigger**

**Video Classification Logic**

> **Shorts** — duration **≤ 60 seconds**  
> **Video** — duration **> 60 seconds**

Classification is based on **ISO 8601 duration parsing**.

**Data Collected**

Each video is stored with:

- **Publish date**
- **Video title**
- **Video type** (**Short / Video**)
- **Views**
- **Likes**
- **Comments**
- **Video ID** (**unique identifier**)

> **Video ID is the primary key** inside Google Sheets.

**Technical Details**

- **API:** YouTube Data API v3  
- **Optimized retrieval** via uploads playlist  
- **Batch updates** for Google Sheets  
- **Stable long-running execution**

**Technology Stack**

- **Python**
- **YouTube Data API v3**
- **Google Sheets API**
- **google-api-python-client**
- **gspread**
- **oauth2client**
- **isodate**
- **schedule**
- **python-dotenv**

**Configuration (.env)**

All configuration is stored securely:
  YOUTUBE_API_KEY=
  CHANNEL_ID=
  SERVICE_ACCOUNT_FILE=
  SPREADSHEET_ID=
  SHEET_NAME=  

**Execution Flow**

1. **Load configuration**
2. **Connect to YouTube API**
3. **Retrieve uploads playlist**
4. **Fetch latest videos & statistics**
5. **Compare with spreadsheet**
6. **Append or update rows**
7. **Repeat every hour**

**Intended Use**

This project is suitable for:

- **YouTube creators**
- **Analytics dashboards**
- **Automated reporting**
- **Long-term performance tracking**
