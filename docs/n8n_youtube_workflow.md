# 使用 n8n 自動生成圖片與音樂合成影片並上傳至 YouTube

此文件說明如何在 n8n 中設計一條龍流程，完成以下步驟：

1. 生成或取得圖片素材
2. 生成或取得背景音樂
3. 將圖片與音樂合成影片
4. 將影片上傳至 YouTube

## 範例流程概述

1. **觸發器**：可使用定時觸發 (Cron) 或 Webhook 觸發。
2. **圖片生成**：使用第三方 API (例如 Stable Diffusion、DALL·E) 生成圖片。
3. **音樂生成**：透過 AI 音樂 API (例如 Soundraw、AIVA)，或從資料庫/雲端儲存取得現成音樂。
4. **影片合成**：使用 n8n 的 [Execute Command] 節點呼叫 `ffmpeg` 將圖片與音樂合成影片。
5. **上傳 YouTube**：利用 n8n 的 [HTTP Request] 節點呼叫 YouTube Data API 進行影片上傳。
6. **錯誤處理與通知**：流程失敗時，可透過 Slack、Email 等方式通知。

## ffmpeg 合成影片指令範例

```bash
ffmpeg -loop 1 -i image.png -i music.mp3 -c:v libx264 -t 30 -pix_fmt yuv420p -c:a aac output.mp4
```

- `-loop 1`：將單張圖片循環使用。
- `-t 30`：設定影片長度（秒）。

## 上傳 YouTube

YouTube 上傳需要 OAuth 認證，流程如下：

1. 在 Google Cloud Console 建立專案並啟用 YouTube Data API v3。
2. 建立 OAuth 2.0 憑證並在 n8n 中設定認證資料。
3. 在 n8n 使用 [HTTP Request] 節點，向 `https://www.googleapis.com/upload/youtube/v3/videos` 發送 POST 請求上傳影片檔案。

## 範例工作流程 JSON

以下提供簡化範例，需依實際 API 與路徑調整：

```json
{
  "nodes": [
    {
      "parameters": {},
      "name": "Start",
      "type": "n8n-nodes-base.start",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "command": "ffmpeg -loop 1 -i image.png -i music.mp3 -c:v libx264 -t 30 -pix_fmt yuv420p -c:a aac output.mp4"
      },
      "name": "Execute Command",
      "type": "n8n-nodes-base.executeCommand",
      "typeVersion": 1,
      "position": [450, 300]
    },
    {
      "parameters": {
        "authentication": "oAuth2",
        "requestMethod": "POST",
        "url": "https://www.googleapis.com/upload/youtube/v3/videos",
        "jsonParameters": false,
        "options": {},
        "queryParameters": {
          "uploadType": "multipart",
          "part": "snippet,status"
        }
      },
      "name": "Upload YouTube",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [650, 300]
    }
  ],
  "connections": {
    "Start": {
      "main": [
        [
          {
            "node": "Execute Command",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Execute Command": {
      "main": [
        [
          {
            "node": "Upload YouTube",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

此範例僅示意流程，實際使用時請根據 API 需求及檔案路徑進行調整。

