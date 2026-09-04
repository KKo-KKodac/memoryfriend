import datetime
import json
import re
import time
import requests
from bs4 import BeautifulSoup

# 세부 매핑 구조 (제공해주신 CPU 1세대~16세대 정확 반영)
URL_CONFIG = [
    # --- CPU (인텔 세대별 매핑) ---
    {
        "cat": "CPU",
        "sub": "INTEL",
        "detail": "1세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=31"
        ),
    },
    {
        "cat": "CPU",
        "sub": "INTEL",
        "detail": "2세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=993"
        ),
    },
    {
        "cat": "CPU",
        "sub": "INTEL",
        "detail": "3세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=1188"
        ),
    },
    {
        "cat": "CPU",
        "sub": "INTEL",
        "detail": "4세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=1684"
        ),
    },
    {
        "cat": "CPU",
        "sub": "INTEL",
        "detail": "6세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=3682"
        ),
    },
    {
        "cat": "CPU",
        "sub": "INTEL",
        "detail": "7세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=3838"
        ),
    },
    {
        "cat": "CPU",
        "sub": "INTEL",
        "detail": "8세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=3918"
        ),
    },
    {
        "cat": "CPU",
        "sub": "INTEL",
        "detail": "9세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=25"
        ),
    },
    {
        "cat": "CPU",
        "sub": "INTEL",
        "detail": "10세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4020"
        ),
    },
    {
        "cat": "CPU",
        "sub": "INTEL",
        "detail": "11세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4083"
        ),
    },
    {
        "cat": "CPU",
        "sub": "INTEL",
        "detail": "12세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4089"
        ),
    },
    {
        "cat": "CPU",
        "sub": "INTEL",
        "detail": "13세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4137"
        ),
    },
    {
        "cat": "CPU",
        "sub": "INTEL",
        "detail": "14세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4144"
        ),
    },
    {
        "cat": "CPU",
        "sub": "INTEL",
        "detail": "15세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4303"
        ),
    },
    {
        "cat": "CPU",
        "sub": "INTEL",
        "detail": "16세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4304"
        ),
    },
    # === CPU (AMD) ===
    {
        "category": "CPU",
        "sub": "AMD",
        "detail": "AMD(AM5)",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=4197"
        ),
    },
    # 아래 3개 URL은 모두 "AMD(AM4)" 태그를 동일하게 부여하여 하나의 중분류로 합침
    {
        "category": "CPU",
        "sub": "AMD",
        "detail": "AMD(AM4)",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=4072"
        ),
    },
    {
        "category": "CPU",
        "sub": "AMD",
        "detail": "AMD(AM4)",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=3945"
        ),
    },
    {
        "category": "CPU",
        "sub": "AMD",
        "detail": "AMD(AM4)",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=3943"
        ),
    },
    },
    },
    # --- 메인보드 ---
    {
        "cat": "메인보드",
        "sub": "INTEL",
        "detail": "LGA1700 (12~14세대)",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=4075"
        ),
    },
    {
        "cat": "메인보드",
        "sub": "INTEL",
        "detail": "LGA1200 (10~11세대)",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3808"
        ),
    },
    {
        "cat": "메인보드",
        "sub": "INTEL",
        "detail": "LGA1151v2 (8~9세대)",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3784"
        ),
    },
    {
        "cat": "메인보드",
        "sub": "INTEL",
        "detail": "LGA1151 (6~7세대)",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3775"
        ),
    },
    {
        "cat": "메인보드",
        "sub": "INTEL",
        "detail": "LGA1150 (4세대)",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3768"
        ),
    },
    {
        "cat": "메인보드",
        "sub": "AMD",
        "detail": "AM5 메인보드",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=4218"
        ),
    },
    {
        "cat": "메인보드",
        "sub": "AMD",
        "detail": "AM4 메인보드",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=4085"
        ),
    },
    # --- 메모리 ---
    {
        "cat": "메모리",
        "sub": "삼성/일반",
        "detail": "DDR5",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=966&ctgry_no3=4220"
        ),
    },
    {
        "cat": "메모리",
        "sub": "삼성/일반",
        "detail": "DDR4",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=966&ctgry_no3=967"
        ),
    },
    {
        "cat": "메모리",
        "sub": "삼성/일반",
        "detail": "DDR3",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=966&ctgry_no3=4221"
        ),
    },
    {
        "cat": "메모리",
        "sub": "노트북용",
        "detail": "노트북 메모리",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=57"
        ),
    },
    # --- 그래픽카드 ---
    {
        "cat": "그래픽카드",
        "sub": "NVIDIA",
        "detail": "RTX 40 시리즈",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=4305"
        ),
    },
    {
        "cat": "그래픽카드",
        "sub": "NVIDIA",
        "detail": "RTX 30 시리즈",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=4090"
        ),
    },
    {
        "cat": "그래픽카드",
        "sub": "NVIDIA",
        "detail": "RTX 20 / GTX 16 시리즈",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=4021"
        ),
    },
    {
        "cat": "그래픽카드",
        "sub": "NVIDIA",
        "detail": "GTX 10 시리즈",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=3932"
        ),
    },
    {
        "cat": "그래픽카드",
        "sub": "AMD",
        "detail": "라데온 시리즈",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=4026&ctgry_no3=4029"
        ),
    },
    # --- SSD / HDD ---
    {
        "cat": "SSD",
        "sub": "M.2",
        "detail": "NVMe / M.2 SSD",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=3866"
        ),
    },
    {
        "cat": "SSD",
        "sub": "SATA",
        "detail": "2.5인치 SATA SSD",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=4141"
        ),
    },
    {
        "cat": "HDD",
        "sub": "3.5인치",
        "detail": "데스크탑 HDD",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=7"
        ),
    },
    {
        "cat": "HDD",
        "sub": "2.5인치",
        "detail": "노트북 HDD",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=5"
        ),
    },
    # --- 파워 ---
    {
        "cat": "파워",
        "sub": "일반파워",
        "detail": "500W 이하",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=4273&ctgry_no2=4274"
        ),
    },
    {
        "cat": "파워",
        "sub": "일반파워",
        "detail": "600W~700W",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=4273&ctgry_no2=4275"
        ),
    },
    {
        "cat": "파워",
        "sub": "일반파워",
        "detail": "750W 이상",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=4273&ctgry_no2=4276"
        ),
    },
]


def crawl_worldmemory():
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }

  items = []
  prices_map = {}

  for cfg in URL_CONFIG:
    try:
      response = requests.get(cfg["url"], headers=headers, timeout=10)
      response.encoding = "utf-8"
      soup = BeautifulSoup(response.text, "html.parser")

      rows = soup.select("table tr")
      for row in rows:
        cols = row.select("td, th")
        texts = [c.get_text(strip=True) for c in cols]

        if len(texts) >= 3:
          item_name = texts[1]
          price_str = texts[2]
          cleaned_price = re.sub(r"[^\d]", "", price_str)

          if cleaned_price.isdigit():
            price_num = int(cleaned_price)
            if price_num > 0 and len(item_name) > 1:
              items.append({
                  "category": cfg["cat"],
                  "sub": cfg["sub"],
                  "detail": cfg["detail"],
                  "name": item_name,
                  "price": price_num,
              })
              prices_map[item_name] = price_num
      time.sleep(0.05)
    except Exception as e:
      print(f"Error crawling {cfg['url']}: {e}")

  now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
  formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")

  data = {
      "updated_at": formatted_time,
      "count": len(items),
      "items": items,
      "prices": prices_map,
  }

  with open("prices.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

  print(f"[{formatted_time}] 완료 - 총 {len(items)}개 정밀 매핑 완료!")


if __name__ == "__main__":
  crawl_worldmemory()
