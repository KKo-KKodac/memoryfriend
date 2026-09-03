import json
import datetime
import requests
from bs4 import BeautifulSoup

def crawl_worldmemory():
    # 월드메모리 실제 자동견적 페이지 URL
    url = "http://www.worldmemory.co.kr/purchase/autoEstimate.do" 
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "http://www.worldmemory.co.kr/"
    }

    prices = {}

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 시세 테이블 행(tr) 파싱
        rows = soup.select("table tr")
        
        for row in rows:
            cols = row.select("td, th")
            texts = [c.get_text(strip=True) for c in cols]
            
            # 테이블 구조: [분류, 상품명, 가격, ...] 또는 [상품명, 가격, ...]
            if len(texts) >= 2:
                # 행의 텍스트들을 탐색하며 가격(숫자+원)이 들어있는 컬럼과 그 앞의 상품명을 짝지음
                for i in range(len(texts) - 1):
                    item_name = texts[i]
                    price_str = texts[i+1]
                    
                    # '원' 및 천단위 콤마(,) 제거
                    cleaned_price = price_str.replace(",", "").replace("원", "").strip()
                    
                    # 100원 이상의 정수 가격이고 의미있는 상품명인 경우 저장
                    if cleaned_price.isdigit():
                        price_num = int(cleaned_price)
                        if price_num >= 100 and len(item_name) >= 2 and not item_name.isdigit():
                            prices[item_name] = price_num
                            
    except Exception as e:
        print(f"크롤링 실행 중 오류 발생: {e}")

    # 한국 표준시 (KST) 시간 기록
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "updated_at": formatted_time,
        "count": len(prices),
        "prices": prices
    }

    # prices.json 파일에 저장
    with open("prices.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[{formatted_time}] 크롤링 완료 - 수집된 부품 수: {len(prices)}개")

if __name__ == "__main__":
    crawl_worldmemory()
