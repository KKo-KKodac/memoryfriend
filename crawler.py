import datetime
import json
import re
import time
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
    "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=4277&ctgry_no2=4279",
]


def crawl_worldmemory():
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }

  prices = {}

  for idx, url in enumerate(URLS):
    try:
      response = requests.get(url, headers=headers, timeout=10)
      response.encoding = "utf-8"
      soup = BeautifulSoup(response.text, "html.parser")

      # 월드메모리 가격 테이블 행 파싱
      rows = soup.select("table tr")

      for row in rows:
        cols = row.select("td, th")
        texts = [c.get_text(strip=True) for c in cols]

        # 보통 [분류, 상품명, 가격] 형태 (3개 컬럼)
        if len(texts) >= 3:
          item_name = texts[1]  # 상품명
          price_str = texts[2]  # 가격

          # 숫자만 추출
          cleaned_price = re.sub(r"[^\d]", "", price_str)

          # 가격이 존재하고 유효한 상품인 경우
          if cleaned_price.isdigit():
            price_num = int(cleaned_price)
            if price_num > 0 and len(item_name) > 1:
              prices[item_name] = price_num

      # 서버 과부하 방지 (0.1초 대기)
      time.sleep(0.1)

    except Exception as e:
      print(f"Error crawling URL index {idx}: {e}")

  # KST (한국 표준시) 시간
  now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
  formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")

  data = {"updated_at": formatted_time, "count": len(prices), "prices": prices}

  # prices.json 파일에 저장
  with open("prices.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

  print(f"[{formatted_time}] 크롤링 성공 - 총 {len(prices)}개 품목 수집 완료!")


if __name__ == "__main__":
  crawl_worldmemory()
