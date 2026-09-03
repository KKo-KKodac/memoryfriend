import json
import datetime
import requests
from bs4 import BeautifulSoup

def crawl_worldmemory():
    # 월드메모리 매입 시세 페이지 URL (또는 시세 목록 API/URL)
    url = "http://www.worldmemory.co.kr/purchase/priceList.do" 
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    prices = {}

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8' # 한글 깨짐 방지
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 월드메모리 시세 테이블 및 행(tr) 파싱
        rows = soup.select("table tr")
        
        for row in rows:
            cols = row.select("td, th")
            # 텍스트 추출
            texts = [c.get_text(strip=True) for c in cols]
            
            # 행 데이터 조건 검사 (상품명과 가격이 포함된 행 찾기)
            if len(texts) >= 2:
                # 테이블의 각 열 구조 분석
                # 보통 [분류/세대, 상품명, 가격] 형태임
                for i in range(len(texts) - 1):
                    item_name = texts[i]
                    price_str = texts[i+1]
                    
                    # '원' 또는 숫자가 들어간 가격 형태 추출
                    cleaned_price = price_str.replace(",", "").replace("원", "").strip()
                    
                    if cleaned_price.isdigit() and int(cleaned_price) > 0 and len(item_name) > 1:
                        # 숫자와 의미있는 상품명일 경우 추가
                        prices[item_name] = int(cleaned_price)
                        
    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")

    # 현재 KST (한국 표준시) 시간 생성
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

    print(f"[{formatted_time}] 크롤링 완료! 총 {len(prices)}개 부품 수집됨.")

if __name__ == "__main__":
    crawl_worldmemory()
