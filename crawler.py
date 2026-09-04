from datetime import datetime, timedelta, timezone
import json
import re
import bs4
import requests

# 한국 표준시 (KST) 설정
KST = timezone(timedelta(hours=9))

URL_CONFIG = [
    # === CPU (INTEL) ===
    {
        "category": "CPU",
        "sub": "INTEL",
        "detail": "16세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=4241"
        ),
    },
    {
        "category": "CPU",
        "sub": "INTEL",
        "detail": "15세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=4240"
        ),
    },
    {
        "category": "CPU",
        "sub": "INTEL",
        "detail": "14세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=4233"
        ),
    },
    {
        "category": "CPU",
        "sub": "INTEL",
        "detail": "13세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=4195"
        ),
    },
    {
        "category": "CPU",
        "sub": "INTEL",
        "detail": "12세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=4156"
        ),
    },
    {
        "category": "CPU",
        "sub": "INTEL",
        "detail": "11세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=4106"
        ),
    },
    {
        "category": "CPU",
        "sub": "INTEL",
        "detail": "10세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=4071"
        ),
    },
    {
        "category": "CPU",
        "sub": "INTEL",
        "detail": "9세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=4013"
        ),
    },
    {
        "category": "CPU",
        "sub": "INTEL",
        "detail": "8세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=3973"
        ),
    },
    {
        "category": "CPU",
        "sub": "INTEL",
        "detail": "7세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=3941"
        ),
    },
    {
        "category": "CPU",
        "sub": "INTEL",
        "detail": "6세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=3940"
        ),
    },
    {
        "category": "CPU",
        "sub": "INTEL",
        "detail": "4세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=3939"
        ),
    },
    {
        "category": "CPU",
        "sub": "INTEL",
        "detail": "3세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=3938"
        ),
    },
    {
        "category": "CPU",
        "sub": "INTEL",
        "detail": "2세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=3937"
        ),
    },
    {
        "category": "CPU",
        "sub": "INTEL",
        "detail": "1세대",
        "url": (
            "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=3936"
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
]


def clean_text(text):
  if not text:
    return ""
  return re.sub(r"\s+", " ", text).strip()


def parse_price(price_str):
  if not price_str:
    return 0
  num = re.sub(r"[^\d]", "", price_str)
  return int(num) if num else 0


def fetch_prices():
  all_items = []
  prices_map = {}

  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }

  for config in URL_CONFIG:
    category = config["category"]
    sub = config["sub"]
    detail = config["detail"]
    url = config["url"]

    try:
      response = requests.get(url, headers=headers, timeout=15)
      response.raise_for_encoding()
      response.encoding = "utf-8"

      soup = bs4.BeautifulSoup(response.text, "html.parser")
      rows = soup.select("table.tb_type01 tbody tr, table tbody tr")

      for row in rows:
        cols = row.select("td")
        if len(cols) >= 2:
          name = clean_text(cols[0].text)
          price_text = clean_text(cols[1].text)
          price = parse_price(price_text)

          if name and price > 0:
            item = {
                "category": category,
                "sub": sub,
                "detail": detail,
                "name": name,
                "price": price,
            }
            all_items.append(item)
            prices_map[name] = price

    except Exception as e:
      print(f"Error fetching {url}: {e}")

  now_str = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")

  result = {
      "updated_at": now_str,
      "count": len(all_items),
      "items": all_items,
      "prices": prices_map,
  }

  with open("prices.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

  print(f"Successfully saved {len(all_items)} items to prices.json")


if __name__ == "__main__":
  fetch_prices()
