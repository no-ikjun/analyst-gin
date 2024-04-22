import requests
from bs4 import BeautifulSoup
import os

# 기본 URL 설정
base_url = "https://finance.naver.com/research/company_list.naver"

# User-Agent 설정
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# 페이지에서 리포트 링크를 찾기
list_page_response = requests.get(base_url, headers=headers)
list_page_response.raise_for_status()
soup = BeautifulSoup(list_page_response.text, 'html.parser')

# 'company_read.naver?nid=' 링크 추출
nid_links = soup.find_all('a', href=lambda href: href and "company_read.naver?nid=" in href, limit=5)

# 각 링크에 대해 PDF 파일 다운로드
for link in nid_links:
    report_url = f"https://finance.naver.com/research/{link['href']}"  # 슬래시 누락 오류 수정
    report_page_response = requests.get(report_url, headers=headers)
    report_page_response.raise_for_status()
    report_soup = BeautifulSoup(report_page_response.text, 'html.parser')

    pdf_link_tag = report_soup.find('a', class_='con_link')
    if pdf_link_tag:
        pdf_url = pdf_link_tag['href']
        pdf_response = requests.get(pdf_url)
        pdf_response.raise_for_status()

        pdf_file_name = pdf_url.split('/')[-1]
        save_path = os.path.join(os.getcwd(), pdf_file_name)

        with open(save_path, 'wb') as file:
            file.write(pdf_response.content)

        print(f'PDF 파일이 성공적으로 다운로드 되었습니다: {save_path}')
    else:
        print(f'PDF 링크를 찾을 수 없습니다: {report_url}')
