import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

# 날짜 형식을 변환해 비교 가능하게 하기 위한 함수
def parse_date(date_str):
    return datetime.strptime(date_str, "%y.%m.%d")

# 시작 날짜와 종료 날짜 설정
min_date = parse_date("24.04.08")
max_date = parse_date("24.04.29")

# 페이지 값 설정
page = 1


# 기본 URL 설정 - 예시 : 삼성전자
base_url = "https://finance.naver.com/research/company_list.naver?searchType=itemCode&itemName=%BB%EF%BC%BA%C0%FC%C0%DA&itemCode=005930&page=" + str(page)

# User-Agent 설정
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# 반복 시작
while True:    
    formatted_url = base_url.format(page=page)
    # 페이지에서 리포트 링크를 찾기
    list_page_response = requests.get(formatted_url, headers=headers)
    list_page_response.raise_for_status()
    soup = BeautifulSoup(list_page_response.text, 'html.parser')

    # 'company_read.naver?nid=' 링크 추출
    nid_links = soup.find_all('a', href=lambda href: href and "company_read.naver?nid=" in href)
    
    if not nid_links:
        break  # 링크가 없다면 루프 종료

    for link in nid_links:
        parent_row = link.find_parent('tr')
        
        # 날짜 값 추출
        date_tags = parent_row.find_all('td', class_='date')
        research_date = parse_date(date_tags[0].text.strip())

        print(research_date)
        print(max_date)

        # 날짜 범위 체크
        if research_date > max_date:
            continue
        elif research_date < min_date:
            exit()

        # 증권사 값
        securities_firm = parent_row.find_all('td', class_=False)
        firm_name = securities_firm[2].text.strip()

        print(firm_name)

        report_url = f"https://finance.naver.com/research/{link['href']}"
        report_page_response = requests.get(report_url, headers=headers)
        report_page_response.raise_for_status()
        report_soup = BeautifulSoup(report_page_response.text, 'html.parser')

        pdf_link_tag = report_soup.find('a', class_='con_link')
        if pdf_link_tag:
            pdf_url = pdf_link_tag['href']
            pdf_response = requests.get(pdf_url)
            pdf_response.raise_for_status()

            pdf_file_name = research_date.strftime("%Y.%m.%d") + "_" + firm_name + "_" + pdf_url.split("/")[-1]
            save_path = os.path.join(os.getcwd(), pdf_file_name)

            with open(save_path, 'wb') as file:
                file.write(pdf_response.content)

            print(f'PDF 파일이 성공적으로 다운로드 되었습니다: {save_path}')
        else:
            print(f'PDF 링크를 찾을 수 없습니다: {report_url}')

    # 다음 페이지로 이동
    page += 1