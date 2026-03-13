import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import os

# [중요] 깃허브 보안 설정에서 가져오도록 수정된 부분
# 로컬에서 테스트할 때는 환경 변수가 없으면 에러가 날 수 있으니 
# 아래 "본인의_API_키" 부분에 키를 잠시 넣어서 테스트 후, 깃허브 올릴 땐 지우셔도 됩니다.
API_KEY = os.environ.get("AIzaSyClZT14IcaJW0RWxgHL-iQFYdwGFnGjXXE") 

if not API_KEY:
    print("❌ 에러: GEMINI_API_KEY를 찾을 수 없습니다. Settings -> Secrets를 확인하세요.")
    # 로컬 테스트용 (깃허브 올릴 땐 이 줄을 지우거나 주석처리하세요)
    # API_KEY = "여기에_실제_키를_넣으면_내_컴퓨터에서도_돌아갑니다"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')

def get_google_news_nike():
    # 24시간 내 나이키 뉴스 검색
    query = urllib.parse.quote("Nike Shoes when:1d")
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.content, "xml")
        return soup.find_all("item")
    except Exception as e:
        print(f"📡 접속 에러: {e}")
        return []

def summarize_with_gemini(title):
    try:
        prompt = f"다음 나이키 뉴스를 한국어로 아주 짧고 간결하게 1줄로 요약해줘.\n제목: {title}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return "요약 정보를 가져오지 못했습니다."

def save_to_html(news_list):
    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>나이키 뉴스 리포트</title>
        <style>
            body {{ font-family: 'Malgun Gothic', sans-serif; background-color: #f8f9fa; padding: 20px; line-height: 1.6; }}
            .container {{ max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
            h1 {{ text-align: center; color: #111; font-size: 28px; border-bottom: 3px solid #111; padding-bottom: 10px; }}
            .news-item {{ border-bottom: 1px solid #eee; padding: 20px 0; }}
            .news-item:last-child {{ border-bottom: none; }}
            .title {{ font-size: 19px; font-weight: bold; color: #000; text-decoration: none; display: block; margin-bottom: 8px; }}
            .title:hover {{ color: #ff5000; }}
            .summary {{ color: #444; background: #f0f0f0; padding: 10px; border-left: 4px solid #111; font-size: 15px; }}
            .info {{ font-size: 13px; color: #888; margin-top: 10px; }}
            .update-time {{ text-align: right; font-size: 13px; color: #666; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>👟 NIKE NEWS DAILY</h1>
            <p class="update-time">마지막 업데이트: {time.strftime('%Y-%m-%d %H:%M:%S')} (KST)</p>
    """
    
    for news in news_list:
        html_content += f"""
            <div class="news-item">
                <a href="{news['link']}" target="_blank" class="title">{news['title']}</a>
                <div class="summary">💡 {news['summary']}</div>
                <p class="info">출처: {news['source']} | 날짜: {news['date']}</p>
            </div>
        """
        
    html_content += """
        </div>
    </body>
    </html>
    """
    
    # 깃허브 서버에서 파일이 생성됩니다.
    with open("nike_news.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("📂 nike_news.html 파일 생성 완료")

def run_once():
    print(f"🚀 뉴스 수집을 시작합니다...")
    items = get_google_news_nike()
    
    if not items:
        print("❌ 새로운 뉴스가 없습니다.")
        return

    news_data = []
    for item in items[:10]:
        title = item.title.text
        summary = summarize_with_gemini(title)
        news_data.append({
            'title': title,
            'link': item.link.text,
            'source': item.source.text,
            'date': item.pubDate.text,
            'summary': summary
        })
    
    save_to_html(news_data)

if __name__ == "__main__":
    run_once()