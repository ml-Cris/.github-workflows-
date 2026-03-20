from curl_cffi import requests  # 替換掉原本的 import requests
import pandas as pd
from datetime import datetime
import os
import time
import google.generativeai as genai

# ... (Gemini 設定不變) ...

def fetch_competitors():
    competitors = ["凱基證券", "國泰證券", "元大證券", "富邦證券", "永豐金證券"]
    all_new_data = []

    # 使用 curl_cffi 模擬 Chrome 瀏覽器
    for brand in competitors:
        print(f"正在分析: {brand}...")
        url = f"https://www.dcard.tw/_api/search/posts?query={brand}&forum=stock&limit=10"
        
        try:
            # 關鍵修改：impersonate="chrome" 會模擬真實 Chrome 的 TLS 指紋
            res = requests.get(url, impersonate="chrome")
            
            if res.status_code == 200:
                posts = res.json()
                print(f"  - 成功抓取 {len(posts)} 篇內容")
                for p in posts:
                    sentiment, reason = get_gemini_sentiment(p['title'])
                    all_new_data.append({
                        "collect_date": datetime.now().strftime("%Y-%m-%d"),
                        "brand": brand,
                        "title": p['title'],
                        "likeCount": p['likeCount'],
                        "commentCount": p['commentCount'],
                        "sentiment": sentiment,
                        "reason": reason
                    })
            else:
                print(f"  - 抓取失敗，代碼: {res.status_code}")
            
            time.sleep(3) # 稍微增加延遲
        except Exception as e:
            print(f"錯誤: {e}")

    # ... (後續存檔邏輯不變) ...
