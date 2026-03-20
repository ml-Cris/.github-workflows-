from curl_cffi import requests
import pandas as pd
from datetime import datetime
import os
import time
import google.generativeai as genai

# 1. Gemini 設定
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def get_gemini_sentiment(title):
    try:
        prompt = f"分析金融標題情緒（正面、負面、中立）。只回傳：情緒|理由。標題：{title}"
        response = model.generate_content(prompt)
        res = response.text.strip().split('|')
        return (res[0], res[1]) if len(res) > 1 else (res[0], "OK")
    except:
        return "中立", "分析失敗"

def fetch_competitors():
    competitors = ["凱基證券", "國泰證券", "元大證券", "富邦證券", "永豐金證券"]
    all_new_data = []
    
    # 使用 curl_cffi 模擬 Chrome 
    for brand in competitors:
        print(f"正在分析品牌: {brand}...")
        url = f"https://www.dcard.tw/_api/search/posts?query={brand}&forum=stock&limit=5"
        
        try:
            # impersonate 參數是繞過 403 的關鍵
            res = requests.get(url, impersonate="chrome120")
            if res.status_code == 200:
                posts = res.json()
                print(f"  - 找到 {len(posts)} 篇")
                for p in posts:
                    s, r = get_gemini_sentiment(p['title'])
                    all_new_data.append({
                        "collect_date": datetime.now().strftime("%Y-%m-%d"),
                        "brand": brand,
                        "title": p['title'],
                        "likeCount": p['likeCount'],
                        "sentiment": s,
                        "reason": r
                    })
            else:
                print(f"  - 抓取失敗，狀態碼: {res.status_code}")
        except Exception as e:
            print(f"  - 發生錯誤: {e}")
        time.sleep(2)

    # --- 修正存檔邏輯：確保檔案一定會產生 ---
    file_name = 'competitor_data.csv'
    
    if all_new_data:
        df = pd.DataFrame(all_new_data)
        # 如果是第一次執行，寫入標頭；之後則用附加(a)模式
        header = not os.path.exists(file_name)
        df.to_csv(file_name, mode='a', index=False, header=header, encoding='utf-8-sig')
        print(f"成功存入 {len(all_new_data)} 筆數據。")
    else:
        # 如果真的沒抓到資料，至少生出一個有欄位名稱的檔案，防止 Actions 噴錯
        if not os.path.exists(file_name):
            empty_df = pd.DataFrame(columns=["collect_date","brand","title","likeCount","sentiment","reason"])
            empty_df.to_csv(file_name, index=False, encoding='utf-8-sig')
            print("建立初始空白檔案。")

if __name__ == "__main__":
    fetch_competitors()
