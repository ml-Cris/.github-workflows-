import requests
import pandas as pd
from datetime import datetime
import os
import time
import google.generativeai as genai

# 1. 設定 Gemini API (從 GitHub Secrets 讀取)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def get_gemini_sentiment(title):
    """使用 Gemini 分析情緒，回傳格式為: (情緒, 理由)"""
    try:
        prompt = f"""
        你是一位專業的金融輿情分析師。請分析這則證券商討論標題的情緒。
        請只從「正面」、「負面」、「中立」這三個詞中選擇一個作為情緒標籤。
        標題：{title}
        請依照此格式回傳：情緒標籤|簡短理由
        """
        response = model.generate_content(prompt)
        result = response.text.strip().split('|')
        
        sentiment = result[0] if len(result) > 0 else "中立"
        reason = result[1] if len(result) > 1 else "分析完成"
        return sentiment, reason
    except Exception as e:
        print(f"Gemini 分析錯誤: {e}")
        return "中立", "API 請求失敗"

def fetch_competitors():
    competitors = ["凱基證券", "國泰證券", "元大證券", "富邦證券", "永豐金證券"]
    all_new_data = []
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}

    for brand in competitors:
        print(f"正在分析品牌: {brand}...")
        url = f"https://www.dcard.tw/_api/search/posts?query={brand}&forum=stock&limit=10"
        
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                posts = res.json()
                for p in posts:
                    # 呼叫 Gemini 進行分析
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
                    print(f"  - {p['title'][:10]}... -> {sentiment}")
            time.sleep(2) # 避免 API 頻繁請求
        except Exception as e:
            print(f"抓取 {brand} 時發生錯誤: {e}")

    if all_new_data:
        df = pd.DataFrame(all_new_data)
        file_name = 'competitor_data.csv'
        # 如果檔案不存在則建立，存在則附加數據
        df.to_csv(file_name, mode='a', header=not os.path.exists(file_name), index=False, encoding='utf-8-sig')
        print(f"成功儲存數據！目前總篇數: {len(all_new_data)}")

if __name__ == "__main__":
    fetch_competitors()
