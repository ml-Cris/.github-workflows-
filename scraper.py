import requests
import pandas as pd
from datetime import datetime
import os
import time
import openai  # 記得在 requirements.txt 加上 openai

# 設定 OpenAI API Key (稍後會教你如何安全地設定在 GitHub)
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_sentiment(text):
    """使用 AI 判斷情緒"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # 使用最便宜且快速的模型
            messages=[
                {"role": "system", "content": "你是一位專業的金融輿情分析師。請分析評論情緒，僅回傳 JSON 格式：{'label': '正面/負面/中立', 'reason': '一句話簡述原因'}"},
                {"role": "user", "content": f"分析這則證券商評論：{text}"}
            ],
            response_format={ "type": "json_object" }
        )
        # 解析 AI 回傳的結果
        import json
        result = json.loads(response.choices[0].message.content)
        return result.get('label', '中立'), result.get('reason', '')
    except Exception as e:
        print(f"AI 分析失敗: {e}")
        return "分析失敗", str(e)

def fetch_competitors():
    competitors = ["凱基證券", "國泰證券", "元大證券", "富邦證券", "永豐金證券"]
    all_new_data = []
    headers = {'User-Agent': 'Mozilla/5.0'}

    for brand in competitors:
        print(f"正在抓取並分析: {brand}...")
        url = f"https://www.dcard.tw/_api/search/posts?query={brand}&forum=stock&limit=5" # 測試時先抓 5 筆省錢
        
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                posts = res.json()
                for p in posts:
                    # --- 加入 AI 情緒分析 ---
                    sentiment_label, sentiment_reason = get_sentiment(p['title'])
                    
                    all_new_data.append({
                        "collect_date": datetime.now().strftime("%Y-%m-%d"),
                        "brand": brand,
                        "title": p['title'],
                        "likeCount": p['likeCount'],
                        "commentCount": p['commentCount'],
                        "sentiment": sentiment_label,      # AI 標籤
                        "sentiment_reason": sentiment_reason, # AI 理由
                        "topics": ",".join(p.get('topics', []))
                    })
                    print(f"  - 標題: {p['title'][:15]}... -> [{sentiment_label}]")
                    time.sleep(0.5) # 稍微停頓
            
            time.sleep(2)
        except Exception as e:
            print(f"發生錯誤: {e}")

    if all_new_data:
        df = pd.DataFrame(all_new_data)
        file_name = 'competitor_data.csv'
        if not os.path.isfile(file_name):
            df.to_csv(file_name, index=False, encoding='utf-8-sig')
        else:
            df.to_csv(file_name, mode='a', header=False, index=False, encoding='utf-8-sig')
        print(f"成功儲存 {len(all_new_data)} 筆數據（含 AI 情緒標籤）！")

if __name__ == "__main__":
    fetch_competitors()
