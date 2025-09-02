from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# 크롬 옵션
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 디버깅시 주석
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

base_url = "http://medi.qia.go.kr/searchMedicine?csSignature=pEwDBK30q42YqSM%2Faec2jw%3D%3D&searchDivision=detail&page={}"
all_data = []

for page in range(1, 2):  # 일단 1페이지만 테스트
    print(f"===== {page} 페이지 크롤링 중 =====")
    driver.get(base_url.format(page))
    time.sleep(2)

    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

    for i in range(len(rows)):
        try:
            # 리스트 다시 로드
            driver.get(base_url.format(page))
            time.sleep(2)
            rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

            link = rows[i].find_element(By.CSS_SELECTOR, "td.al_l a")
            href = link.get_attribute("href")

            # 상대경로 → 절대경로 변환
            if href.startswith("http"):
                detail_url = href
            else:
                detail_url = "http://medi.qia.go.kr" + href
            print("👉 상세페이지 URL:", detail_url)

            driver.get(detail_url)

            # 상세페이지 로딩 대기
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
            )

            # 제품명
            name = driver.find_element(By.CSS_SELECTOR, "div.drug_header h1 strong").text.strip()

            # 기본정보 테이블
            basic_info = {}
            rows_info = driver.find_elements(By.CSS_SELECTOR, "table.s-dr_table tr")
            for r in rows_info:
                ths = r.find_elements(By.TAG_NAME, "th")
                tds = r.find_elements(By.TAG_NAME, "td")
                if ths and tds:
                    key = ths[0].text.strip()
                    value = tds[0].text.strip()
                    basic_info[key] = value

            # 원료약품 및 분량
            ingredients = []
            ing_rows = driver.find_elements(By.CSS_SELECTOR, "div.scroll_02 table.tb_base tbody tr")
            for ing in ing_rows:
                cols = [c.text.strip() for c in ing.find_elements(By.TAG_NAME, "td")]
                if cols:
                    ingredients.append(cols)

            # 📌 효능효과, 용법용량, 주의사항, 성상 가져오기
            extra_fields = ["효능효과", "용법용량", "주의사항"]
            extra_info = {}

            for field in extra_fields:
                try:
                    title_elem = driver.find_element(By.XPATH, f"//h2[contains(text(), '{field}')]")
                    # 다음 형제 div 또는 table 찾기
                    sibling = title_elem.find_element(By.XPATH, "following-sibling::*[1]")
                    extra_info[field] = sibling.text.strip()
                except:
                    extra_info[field] = "없음"

            all_data.append({
                "제품명": name,
                "기본정보": basic_info,
                "원료약품 및 분량": ingredients,
                **extra_info
            })

            print(f"✔ {name} 크롤링 완료")

        except Exception as e:
            print("❌ 에러 발생:", e)

driver.quit()

print("\n===== 최종 결과 =====")
for item in all_data:
    print(item)
    
import csv

# CSV 파일 저장
with open("medicine_data.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)

    # 헤더
    header = ["제품명", "기본정보", "원료약품 및 분량", "효능효과", "용법용량", "주의사항", "성상"]
    writer.writerow(header)

    # 데이터
    for item in all_data:
        writer.writerow([
            item.get("제품명", ""),
            str(item.get("기본정보", "")),
            str(item.get("원료약품 및 분량", "")),
            item.get("효능효과", ""),
            item.get("용법용량", ""),
            item.get("주의사항", ""),
            item.get("성상", "")
        ])

