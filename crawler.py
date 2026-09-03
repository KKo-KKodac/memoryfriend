import json
import re
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# 크롤링 대상 월드메모리 URL 목록
URLS = [
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=966&ctgry_no3=4220",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=966&ctgry_no3=967",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=966&ctgry_no3=4221",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4083",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=31",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=993",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=1684",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=3682",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=3838",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=3918",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=25",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4020",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4089",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4137",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4144",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4303",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4304",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3784",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3775",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3768",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3808",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=4075",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=4145",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=3901",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=3902",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=4085",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=4146",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=4218",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=3701",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=3932",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=4021",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=4090",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=4305",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=4026&ctgry_no3=4029",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=4026&ctgry_no3=4139",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=4199",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=57",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=3866",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=4141",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=3608",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=7",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=3943",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=3945",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=30",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=4072",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=4138",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=4197",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=651",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=5",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=1208",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=4273&ctgry_no2=4274",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=4273&ctgry_no2=4275",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=4273&ctgry_no2=4276",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=4273&ctgry_no2=4280",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=4277&ctgry_no2=4278",
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=4277&ctgry_no2=4279"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def clean_price(text):
    """숫자 외 문자 제거 및 정수 변환"""
    numbers = re.sub(r"[^\d]", "", text)
    return int(numbers) if numbers else 0

def fetch_all_prices():
    price_dict = {}
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 월드메모리 크롤링 시작...")

    for idx, url in enumerate(URLS):
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                
                # 월드메모리 가격 테이블 행 추출
                rows = soup.select("table.tb_list tbody tr") or soup.select("table tbody tr")
                for row in rows:
                    cols = row.select("td")
                    if len(cols) >= 2:
                        name = cols[0].text.strip()
                        price_text = cols[1].text.strip()
                        price = clean_price(price_text)
                        
                        if name and price > 0:
                            price_dict[name] = price
            time.sleep(0.3)  # 과도한 요청 방지
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    result_data = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "count": len(price_dict),
        "prices": price_dict
    }

    # JSON 파일로 저장
    with open("prices.json", "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=4)

    print(f"총 {len(price_dict)}개 부품 시세 수집 완료 및 prices.json 저장 완료!")

if __name__ == "__main__":
    fetch_all_prices()