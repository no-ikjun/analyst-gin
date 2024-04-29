from google.colab import drive
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

# Google Drive를 마운트
drive.mount('/content/drive')

# 저장할 경로 설정
drive_path = '/content/drive/My Drive/report'  # My Drive 내의 report 폴더 사용

# 날짜 형식을 변환하는 함수
def parse_date(date_str):
    return datetime.strptime(date_str, "%y.%m.%d")

# 시작 날짜와 종료 날짜
min_date = parse_date("24.04.08")
max_date = parse_date("24.04.29")

# 페이지 시작
page = 1

# User-Agent 설정
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

while True:
    formatted_url = f"https://finance.naver.com/research/company_list.naver?searchType=itemCode&itemName=%BB%EF%BC%BA%C0%FC%C0%DA&itemCode=005930&page={page}"
    response = requests.get(formatted_url, headers=headers)
    if response.status_code != 200:
        break
    soup = BeautifulSoup(response.text, 'html.parser')
    nid_links = soup.find_all('a', href=lambda href: href and "company_read.naver?nid=" in href)
    
    if not nid_links:
        break

    for link in nid_links:
        parent_row = link.find_parent('tr')
        date_tags = parent_row.find_all('td', class_='date')
        research_date = parse_date(date_tags[0].text.strip())

        if research_date > max_date:
            continue
        elif research_date < min_date:
            exit()

        securities_firm = parent_row.find_all('td', class_=False)
        firm_name = securities_firm[2].text.strip()

        report_url = f"https://finance.naver.com/research/{link['href']}"
        report_page_response = requests.get(report_url, headers=headers)
        if report_page_response.status_code != 200:
            continue
        report_soup = BeautifulSoup(report_page_response.text, 'html.parser')

        pdf_link_tag = report_soup.find('a', class_='con_link')
        if pdf_link_tag:
            pdf_url = pdf_link_tag['href']
            pdf_response = requests.get(pdf_url)
            if pdf_response.status_code != 200:
                continue

            os.makedirs(drive_path, exist_ok=True)
            pdf_file_name = research_date.strftime("%Y.%m.%d") + "_" + firm_name + "_" + pdf_url.split("/")[-1]
            save_path = os.path.join(drive_path, pdf_file_name)

            with open(save_path, 'wb') as file:
                file.write(pdf_response.content)

            print(f'PDF 파일이 성공적으로 다운로드 되었습니다: {save_path}')
        else:
            print(f'PDF 링크를 찾을 수 없습니다: {report_url}')
    
    page += 1
