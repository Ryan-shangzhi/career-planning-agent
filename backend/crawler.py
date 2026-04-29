import requests
from bs4 import BeautifulSoup
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}

def parse_salary(salary_text):
    """解析薪资范围"""
    if not salary_text:
        return None, None
    match = re.search(r'(\d+)[kK]-(\d+)[kK]', salary_text)
    if match:
        return int(match.group(1)) * 1000, int(match.group(2)) * 1000
    return None, None

def parse_experience(exp_text):
    """解析经验要求"""
    if not exp_text:
        return ""
    return exp_text.strip()

def parse_education(edu_text):
    """解析学历要求"""
    if not edu_text:
        return ""
    return edu_text.strip()

def crawl_boss(keyword, city="北京", page=1):
    """爬取Boss直聘职位数据"""
    jobs = []
    try:
        url = f"https://www.zhipin.com/web/geek/job?query={keyword}&city={city}&page={page}"
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return jobs
        
        soup = BeautifulSoup(response.text, 'html.parser')
        job_cards = soup.find_all('div', class_='job-card')
        
        for card in job_cards:
            job = {}
            
            title_tag = card.find('span', class_='job-name')
            job['title'] = title_tag.get_text().strip() if title_tag else ""
            
            company_tag = card.find('span', class_='company-name')
            job['company_name'] = company_tag.get_text().strip() if company_tag else ""
            
            salary_tag = card.find('span', class_='salary')
            salary_text = salary_tag.get_text().strip() if salary_tag else ""
            job['salary_min'], job['salary_max'] = parse_salary(salary_text)
            
            info_tags = card.find_all('span', class_='tag')
            if info_tags:
                job['experience_requirement'] = parse_experience(info_tags[0].get_text() if len(info_tags) > 0 else "")
                job['education_requirement'] = parse_education(info_tags[1].get_text() if len(info_tags) > 1 else "")
            
            desc_tag = card.find('div', class_='job-desc')
            job['description'] = desc_tag.get_text().strip() if desc_tag else ""
            
            tag_list = card.find('div', class_='job-tags')
            if tag_list:
                tags = [t.get_text().strip() for t in tag_list.find_all('span')]
                job['skills'] = ",".join(tags)
            
            job['source'] = "Boss直聘"
            job['source_url'] = url
            job['industry'] = keyword
            
            jobs.append(job)
    except Exception as e:
        print(f"爬取Boss直聘失败: {e}")
    
    return jobs

def crawl_lagou(keyword, city="北京", page=1):
    """爬取拉勾网职位数据"""
    jobs = []
    try:
        url = f"https://www.lagou.com/jobs/list_{keyword}?city={city}&pageNo={page}"
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return jobs
        
        soup = BeautifulSoup(response.text, 'html.parser')
        job_list = soup.find('ul', class_='position-list')
        if not job_list:
            return jobs
        
        for item in job_list.find_all('li'):
            job = {}
            
            title_tag = item.find('h3')
            job['title'] = title_tag.get_text().strip() if title_tag else ""
            
            company_tag = item.find('div', class_='company-name')
            job['company_name'] = company_tag.get_text().strip() if company_tag else ""
            
            salary_tag = item.find('span', class_='salary')
            salary_text = salary_tag.get_text().strip() if salary_tag else ""
            job['salary_min'], job['salary_max'] = parse_salary(salary_text)
            
            info_tags = item.find_all('span', class_='position-label')
            if info_tags:
                job['experience_requirement'] = parse_experience(info_tags[0].get_text() if len(info_tags) > 0 else "")
                job['education_requirement'] = parse_education(info_tags[1].get_text() if len(info_tags) > 1 else "")
            
            job['source'] = "拉勾网"
            job['source_url'] = url
            job['industry'] = keyword
            
            jobs.append(job)
    except Exception as e:
        print(f"爬取拉勾网失败: {e}")
    
    return jobs

def crawl_jobs(keyword, city="北京", pages=1):
    """综合爬取多个招聘网站"""
    all_jobs = []
    for page in range(1, pages + 1):
        boss_jobs = crawl_boss(keyword, city, page)
        lagou_jobs = crawl_lagou(keyword, city, page)
        all_jobs.extend(boss_jobs)
        all_jobs.extend(lagou_jobs)
    
    return all_jobs
