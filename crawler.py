import json
import re
from datetime import datetime, timezone, timedelta
import bs4
import requests

# 한국 표준시 (KST) 설정
KST = timezone(timedelta(hours=9))

URL_CONFIG = [
    # === CPU (INTEL) ===
    {"category": "CPU", "sub": "INTEL", "detail": "16세대", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=4241"},
    {"category": "CPU", "sub": "INTEL", "detail": "15세대", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=4240"},
    {"category": "CPU", "sub": "INTEL", "detail": "14세대", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=4233"},
    {"category": "CPU", "sub": "INTEL", "detail": "13세대", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=4195"},
    {"category": "CPU", "sub": "INTEL", "detail": "12세대", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=4156"},
    {"category": "CPU", "sub": "INTEL", "detail": "11세대", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=4106"},
    {"category": "CPU", "sub": "INTEL", "detail": "10세대", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=4071"},
    {"category": "CPU", "sub": "INTEL", "detail": "9세대", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=4013"},
    {"category": "CPU", "sub": "INTEL", "detail": "8세대", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=3973"},
    {"category": "CPU", "sub": "INTEL", "detail": "7세대", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=3941"},
    {"category": "CPU", "sub": "INTEL", "detail": "6세대", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=3940"},
    {"category": "CPU", "sub": "INTEL", "detail": "4세대", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=3939"},
    {"category": "CPU", "sub": "INTEL", "detail": "3세대", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=3938"},
    {"category": "CPU", "sub": "INTEL", "detail": "2세대", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=3937"},
    {"category": "CPU", "sub": "INTEL", "detail": "1세대", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=3936"},

    # === CPU (AMD) ===
    {"category": "CPU", "sub": "AMD", "detail": "AMD(AM5)", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=4197"},
    {"category": "CPU", "sub": "AMD", "detail": "AMD(AM4)", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=4072"},
    {"category": "CPU", "sub": "AMD", "detail": "AMD(AM4)", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=3945"},
    {"category": "CPU", "sub": "AMD", "detail": "AMD(AM4)", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=24&ctgry_no3=3943"},

    # === 메인보드 ===
    {"category": "메인보드", "sub": "INTEL", "detail": "소켓1851/1700", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=25&ctgry_no3=4157"},
    {"category": "메인보드", "sub": "INTEL", "detail": "소켓1200", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=25&ctgry_no3=4073"},
    {"category": "메인보드", "sub": "INTEL", "detail": "소켓1151v2/1151", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=25&ctgry_no3=3975"},
    {"category": "메인보드", "sub": "INTEL", "detail": "소켓1150/1155", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=25&ctgry_no3=3947"},
    {"category": "메인보드", "sub": "AMD", "detail": "AM5/AM4", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=25&ctgry_no3=3949"},

    # === 메모리 ===
    {"category": "메모리", "sub": "RAM", "detail": "DDR5", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=26&ctgry_no3=4158"},
    {"category": "메모리", "sub": "RAM", "detail": "DDR4", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=26&ctgry_no3=3950"},
    {"category": "메모리", "sub": "RAM", "detail": "DDR3", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=26&ctgry_no3=3951"},

    # === SSD ===
    {"category": "SSD", "sub": "SSD", "detail": "M.2(NVMe)", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=29&ctgry_no3=4015"},
    {"category": "SSD", "sub": "SSD", "detail": "SATA 2.5인치", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=29&ctgry_no3=3958"},

    # === HDD ===
    {"category": "HDD", "sub": "HDD", "detail": "3.5인치(PC용)", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=28&ctgry_no3=3955"},

    # === 그래픽카드 ===
    {"category": "그래픽카드", "sub": "NVIDIA", "detail": "RTX 40시리즈", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=27&ctgry_no3=4218"},
    {"category": "그래픽카드", "sub": "NVIDIA", "detail": "RTX 30시리즈", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=27&ctgry_no3=4108"},
    {"category": "그래픽카드", "sub": "NVIDIA", "detail": "RTX 20시리즈", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=27&ctgry_no3=3980"},
    {"category": "그래픽카드", "sub": "NVIDIA", "detail": "GTX 16/10/900시리즈", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=27&ctgry_no3=3953"},

    # === 파워 ===
    {"category": "파워", "sub": "POWER", "detail": "ATX 파워", "url": "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=30&ctgry_no3=3961"},
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
            response.encoding = "utf-8"

            soup = bs4.BeautifulSoup(response.text, "html.parser")
            
            # 테이블 행(tr) 탐색
            rows = soup.find_all("tr")

            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    name = clean_text(cols[0].text)
                    price_text = clean_text(cols[1].text)
                    price = parse_price(price_text)

                    # 헤더 행 및 불필요 항목 통과
                    if name and price > 0 and "품명" not in name and "상품명" not in name:
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
