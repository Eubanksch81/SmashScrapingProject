from bs4 import BeautifulSoup
import requests

html_text = requests.get("https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords=Python&txtLocation=").text
# print(html_text)
soup = BeautifulSoup(html_text, 'html.parser')

jobs = soup.find_all("li", class_ = "clearfix job-bx wht-shd-bx")
# job = soup.find("li", class_ = "clearfix job-bx wht-shd-bx")
# print(job)

for job in jobs:
    company_name = job.find("h3", class_="joblist-comp-name").text.replace(' ', '')
    # print(company_name)

    skills = job.find("div", class_="srp-skills").text.replace(" ", "")
    # print(skills)

    published_date = job.find("span", class_="sim-posted").span.text
    # Because this element is a span within a span, need to get the inner span's text.
    # print(published_date)

    print(f'''
    Company Name: {company_name}
    Published Date: {published_date}
    ''')
