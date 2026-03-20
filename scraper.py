import requests
import pandas as pd
from datetime import datetime
import os
import time
import google.generativeai as genai

# 設定 Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def get_gemini_sentiment(title):
    try:
        prompt = f"分析情緒。標題：{title}。請回傳：情緒標籤|簡短理由 (情緒標籤僅限正面、負面、中立)"
        response = model.generate_content(prompt)
        result = response.text.strip().split('|')
        return (result[0], result[1]) if len(result) > 1 else (result[0], "分析完成")
    except:
        return "中立", "API請求失敗"

def fetch_competitors():
    competitors = ["凱基證券", "國泰證券", "元大證券", "富邦證券", "永豐金證券"]
    all_new_data = []
    # 模擬更真實的瀏覽器
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': 'https://www.dcard.tw/f/stock'
    }

    for brand in competitors:
        print(f"正在分析: {brand}...")
        url = f"https://www.dcard.tw/_api/search/posts?query={brand}&forum=stock&limit=5"
        res = requests.get(url, headers=headers)
        
        if res.status_code == 200:
            posts = res.json()
            print(f"  - 找到 {len(posts)} 篇討論")
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
        time.sleep(2)

    # --- 修正後的存檔邏輯 ---
    file_name = 'competitor_data.csv'
    if all_new_data:
        df = pd.DataFrame(all_new_data)
        df.to_csv(file_name, mode='a', header=not os.path.exists(file_name), index=False, encoding='utf-8-sig')
        print(f"成功存入 {len(all_new_data)} 筆資料。")
    else:
        # 如果真的沒抓到，先建立一個空標頭檔，讓 GitHub Action 不會找不到檔案
        if not os.path.exists(file_name):
            df_empty = pd.DataFrame(columns=["collect_date","brand","title","likeCount","commentCount","sentiment","reason"])
            df_empty.to_csv(file_name, index=False, encoding='utf-8-sig')
        print("警告：本次未抓到任何新資料。")

if __name__ == "__main__":
    fetch_competitors()
