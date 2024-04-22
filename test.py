import requests
from bs4 import BeautifulSoup
import os

# 웹 페이지 URL
url = "https://finance.naver.com/research/company_read.naver?nid=72925"

# 웹 페이지를 요청하고 HTML을 파싱
response = requests.get(url)
response.raise_for_status()  # HTTP 요청 에러 체크
soup = BeautifulSoup(response.text, 'html.parser')

# PDF 링크 찾기
# 두 번째 <a> 태그 내에서 PDF 링크를 찾음
pdf_link_tag = soup.find('a', class_='con_link', href=True)
if pdf_link_tag:
    pdf_url = pdf_link_tag['href']

    # PDF 파일 요청 및 저장
    pdf_response = requests.get(pdf_url)
    pdf_response.raise_for_status()

    # PDF 파일 이름 생성
    pdf_file_name = pdf_url.split('/')[-1]

    # PDF 파일 저장 경로 설정
    save_path = os.path.join(os.getcwd(), pdf_file_name)

    # PDF 파일 로컬에 저장
    with open(save_path, 'wb') as file:
        file.write(pdf_response.content)

    print(f'PDF 파일이 성공적으로 다운로드 되었습니다: {save_path}')
else:
    print('PDF 링크를 찾을 수 없습니다.')
