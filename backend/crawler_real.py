"""
真实招聘数据爬虫 - 使用 Playwright 模拟浏览器
支持：登链社区、Boss直聘、智联招聘
数据保存为 JSON，启动时加载到 SQLite
"""
import json
import re
import os
import time
import random
from playwright.sync_api import sync_playwright

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'jobs_data.json')

# ============ 工具函数 ============

def random_sleep(min_s=20, max_s=30):
    """随机等待，防止被封 IP"""
    wait = random.uniform(min_s, max_s)
    print(f"    ⏳ 等待 {wait:.1f}s 防封 IP...")
    time.sleep(wait)


def parse_salary(text):
    """解析薪资文本，返回 (min, max) 元组，单位：元/月"""
    if not text or text == '面议':
        return None, None
    text = text.strip()
    # 50K以上
    if re.match(r'^(\d+)\s*[kK]以上', text):
        val = int(re.match(r'(\d+)', text).group(1)) * 1000
        return val, val * 2
    # 20~50k, 10~20K
    match = re.search(r'(\d+)\s*[~\-～]\s*(\d+)\s*[kK]', text)
    if match:
        return int(match.group(1)) * 1000, int(match.group(2)) * 1000
    # 单个 50K
    match = re.search(r'(\d+)\s*[kK]', text)
    if match:
        val = int(match.group(1)) * 1000
        return val, int(val * 1.5)
    return None, None


def parse_experience(text):
    """解析经验要求"""
    if not text:
        return ""
    if '不限' in text or '应届' in text:
        return "经验不限"
    match = re.search(r'(\d+)\s*[~\-～]\s*(\d+)\s*年', text)
    if match:
        return f"{match.group(1)}-{match.group(2)}年"
    match = re.search(r'(\d+)\s*年', text)
    if match:
        return f"{match.group(1)}年以上"
    return text.strip()


def close_popups(page):
    """关闭常见弹窗（登录框、广告、Cookie 提示等）"""
    popup_selectors = [
        '.modal-dialog .close, .modal .close',
        '[class*="close-btn"], [class*="closeBtn"]',
        '[class*="popup"] [class*="close"]',
        '[class*="dialog"] [class*="close"]',
        '[class*="mask"] [class*="close"]',
        '.btn-close, .close-button',
        '[aria-label="Close"], [aria-label="关闭"]',
        'button:has-text("关闭"), button:has-text("我知道了"), button:has-text("暂不")',
        'button:has-text("以后再说"), button:has-text("不需要"), button:has-text("取消")',
        'button:has-text("Close"), button:has-text("No thanks")',
        '#close, .close-icon, .icon-close',
        '[class*="login"] [class*="close"]',
        '[class*="banner"] [class*="close"]',
        '[class*="toast"] [class*="close"]',
    ]
    for selector in popup_selectors:
        try:
            els = page.query_selector_all(selector)
            for el in els:
                if el.is_visible():
                    el.click()
                    print(f"    🔘 关闭了弹窗: {selector}")
                    time.sleep(0.5)
        except:
            pass


# ============ 登链社区爬虫 ============

def crawl_learnblockchain(page, max_pages=5):
    """爬取登链社区招聘页 - 已验证可用"""
    all_jobs = []

    for pg in range(1, max_pages + 1):
        url = f'https://learnblockchain.cn/jobs/recruit?categorySlug=0&filter=0&page={pg}'
        print(f"  📄 第 {pg} 页: {url}")

        page.goto(url, wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(3000)
        close_popups(page)

        # 等待职位列表加载
        try:
            page.wait_for_selector('.stream-list-item', timeout=10000)
        except:
            print(f"    ⚠️ 未找到职位列表，可能没有更多数据")
            break

        items = page.query_selector_all('section.stream-list-item')
        page_jobs = []

        for item in items:
            try:
                # 标题和链接
                title_el = item.query_selector('h2.title a')
                if not title_el:
                    continue
                full_title = title_el.inner_text().strip()
                href = title_el.get_attribute('href') or ''
                if not full_title or len(full_title) < 2:
                    continue

                # 从标题提取 [城市 /类型]（可能有多个前缀）
                location = ""
                job_type = ""
                clean_title = full_title
                while True:
                    title_match = re.match(r'\[([^\]]+)\]\s*', clean_title)
                    if not title_match:
                        break
                    loc_type = title_match.group(1)
                    parts = [p.strip() for p in loc_type.split('/')]
                    if not location and len(parts) >= 1:
                        location = parts[0]
                    if not job_type and len(parts) >= 2:
                        job_type = parts[1]
                    clean_title = clean_title[title_match.end():].strip()

                # 薪资
                salary_text = ""
                salary_el = item.query_selector('.text-gold')
                if salary_el:
                    salary_text = salary_el.inner_text().strip()
                salary_min, salary_max = parse_salary(salary_text)

                # 标签信息：开发 / 1~3年 / 本科
                tags_text = ""
                li_els = item.query_selector_all('ul.author li')
                for li in li_els:
                    t = li.inner_text().strip()
                    if 'k' in t.lower() or 'K' in t or '薪资' in t:
                        continue
                    if '天前' in t or '小时' in t:
                        continue
                    if t:
                        tags_text = t
                        break

                experience = ""
                education = ""
                category = ""
                if tags_text:
                    parts = [p.strip() for p in tags_text.split('/')]
                    for part in parts:
                        if '年' in part:
                            experience = parse_experience(part)
                        elif any(kw in part for kw in ['本科', '硕士', '大专', '博士', '不限', '高中']):
                            education = part
                        else:
                            category = part

                job = {
                    'title': clean_title,
                    'source_url': href if href.startswith('http') else f'https://learnblockchain.cn{href}',
                    'salary_min': salary_min,
                    'salary_max': salary_max,
                    'salary_text': salary_text,
                    'location': location,
                    'job_type': job_type,
                    'category': category,
                    'experience_requirement': experience,
                    'education_requirement': education,
                    'company_name': '',
                    'industry': 'Web3/区块链',
                    'description': '',
                    'skills': '',
                    'source': '登链社区',
                }
                page_jobs.append(job)
            except Exception as e:
                print(f"    ⚠️ 解析出错: {e}")
                continue

        print(f"    ✅ 第 {pg} 页: {len(page_jobs)} 条职位")
        all_jobs.extend(page_jobs)

        if len(page_jobs) == 0 or pg >= max_pages:
            break
        random_sleep(20, 30)

    return all_jobs


# ============ 猎聘爬虫 ============

def crawl_liepin(page, keyword, city, max_pages=3):
    """爬取猎聘 - 已验证可用，使用混淆 class 名"""
    all_jobs = []
    city_map = {
        '北京': '010', '上海': '020', '广州': '030', '深圳': '040',
        '杭州': '080', '成都': '090', '南京': '100', '武汉': '110',
        '西安': '120', '苏州': '070', '天津': '050', '重庆': '060',
    }
    city_code = city_map.get(city, '')

    for pg in range(1, max_pages + 1):
        if city_code:
            url = f'https://www.liepin.com/zhaopin/?key={keyword}&city={city_code}&currentPage={pg}'
        else:
            url = f'https://www.liepin.com/zhaopin/?key={keyword}&currentPage={pg}'
        print(f"  📄 第 {pg} 页: {url}")

        try:
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            page.wait_for_timeout(8000)  # 猎聘是 CSR，需要等 JS 渲染
            close_popups(page)

            # 使用 JS evaluate 提取数据（class 名是混淆的）
            job_cards = page.evaluate('''() => {
                const cards = document.querySelectorAll('[class*="job-card-pc-container"]');
                const results = [];
                for (const card of cards) {
                    const text = card.innerText || '';
                    const lines = text.split('\\n').map(l => l.trim()).filter(Boolean);
                    
                    // 标题通常是第一个非空行
                    let title = lines[0] || '';
                    // 去掉"广告"标记
                    title = title.replace(/广告/g, '').trim();
                    
                    // 薪资：匹配 9-14k, 17-27k·16薪 等
                    const salaryMatch = text.match(/(\\d+[\\-~]\\d+[kK](?:·\\d+薪)?)|(\\d+[kK]以上)|(面议)/);
                    const salary = salaryMatch ? salaryMatch[0] : '';
                    
                    // 地点：匹配 【城市-区域】
                    const areaMatch = text.match(/【([^】]+)】/);
                    const area = areaMatch ? areaMatch[1] : '';
                    
                    // 经验：匹配 X-Y年
                    const expMatch = text.match(/(\\d+[\\-~]\\d+年|\\d+年以上|经验不限|应届生)/);
                    const experience = expMatch ? expMatch[0] : '';
                    
                    // 学历
                    const eduMatch = text.match(/(本科|硕士|大专|博士|不限|高中|学历不限)/);
                    const education = eduMatch ? eduMatch[0] : '';
                    
                    // 公司名：在经验/学历后面
                    let company = '';
                    const expIdx = text.indexOf(experience);
                    if (expIdx > -1) {
                        const afterExp = text.substring(expIdx + experience.length).split('\\n').filter(Boolean);
                        // 公司名通常是下一个有意义的行
                        for (const line of afterExp) {
                            if (line.length > 2 && !line.match(/^\\d/) && !line.includes('在线') && !line.includes('广告') && !line.includes('聊一聊')) {
                                company = line;
                                break;
                            }
                        }
                    }
                    
                    // 链接
                    const linkEl = card.querySelector('a[href*="/job/"]');
                    const href = linkEl ? linkEl.href : '';
                    
                    results.push({
                        title, salary, area, experience, education, company, href,
                    });
                }
                return results;
            }''')

            page_jobs = []
            for card in job_cards:
                if not card['title'] or len(card['title']) < 2:
                    continue
                s_min, s_max = parse_salary(card['salary'])
                job = {
                    'title': card['title'],
                    'source_url': card['href'],
                    'salary_min': s_min,
                    'salary_max': s_max,
                    'salary_text': card['salary'],
                    'location': card['area'] or city,
                    'job_type': '全职',
                    'category': '',
                    'experience_requirement': parse_experience(card['experience']),
                    'education_requirement': card['education'],
                    'company_name': card['company'],
                    'industry': '',
                    'description': '',
                    'skills': '',
                    'source': '猎聘',
                }
                page_jobs.append(job)

            print(f"    ✅ 第 {pg} 页: {len(page_jobs)} 条职位")
            all_jobs.extend(page_jobs)

            if len(page_jobs) == 0 or pg >= max_pages:
                break
            random_sleep(20, 30)

        except Exception as e:
            print(f"    ❌ 第 {pg} 页出错: {e}")
            break

    return all_jobs


# ============ 智联招聘爬虫 ============

def crawl_zhaopin(page, keyword, city, max_pages=3):
    """爬取智联招聘"""
    all_jobs = []

    for pg in range(1, max_pages + 1):
        url = f'https://www.zhaopin.com/sou/jl{city}/kw{keyword}/p{pg}/'
        print(f"  📄 第 {pg} 页: {url}")

        try:
            page.goto(url, wait_until='domcontentloaded', timeout=20000)
            page.wait_for_timeout(5000)
            close_popups(page)

            body_text = page.inner_text('body')
            if '验证' in body_text or '安全' in body_text:
                print(f"    ⚠️ 智联触发安全验证，等待...")
                page.wait_for_timeout(30000)
                close_popups(page)

            job_cards = page.evaluate('''() => {
                const cards = document.querySelectorAll('.joblist-box__item, .positionlist .item, [class*="jobcard"], [class*="job-card"], .jobcard');
                const results = [];
                for (const card of cards) {
                    const titleEl = card.querySelector('.iteminfo__jobname a, .jobname a, a[class*="jobname"], a[class*="title"]');
                    const salaryEl = card.querySelector('.iteminfo__salary, .salary, [class*="salary"]');
                    const companyEl = card.querySelector('.iteminfo__comp a, .company a, [class*="company"] a');
                    const areaEl = card.querySelector('.iteminfo__addr, [class*="addr"], [class*="area"]');
                    const tags = card.querySelectorAll('.iteminfo__tag li, [class*="tag"] li, [class*="tag"]');
                    const descEl = card.querySelector('.iteminfo__desc, [class*="desc"]');
                    
                    results.push({
                        title: titleEl ? titleEl.innerText.trim() : '',
                        href: titleEl ? titleEl.href : '',
                        salary: salaryEl ? salaryEl.innerText.trim() : '',
                        company: companyEl ? companyEl.innerText.trim() : '',
                        area: areaEl ? areaEl.innerText.trim() : '',
                        tags: [...tags].map(t => t.innerText.trim()).filter(Boolean),
                        desc: descEl ? descEl.innerText.trim() : '',
                    });
                }
                return results;
            }''')

            page_jobs = []
            for card in job_cards:
                if not card['title'] or len(card['title']) < 2:
                    continue
                experience = ""
                education = ""
                skills = []
                for tag in card['tags']:
                    if '年' in tag:
                        experience = parse_experience(tag)
                    elif any(kw in tag for kw in ['本科', '硕士', '大专', '博士', '不限', '高中']):
                        education = tag
                    else:
                        skills.append(tag)

                job = {
                    'title': card['title'],
                    'source_url': card['href'],
                    'salary_min': None,
                    'salary_max': None,
                    'salary_text': card['salary'],
                    'location': card['area'] or city,
                    'job_type': '',
                    'category': '',
                    'experience_requirement': experience,
                    'education_requirement': education,
                    'company_name': card['company'],
                    'industry': '',
                    'description': card['desc'],
                    'skills': ','.join(skills),
                    'source': '智联招聘',
                }
                s_min, s_max = parse_salary(card['salary'])
                job['salary_min'] = s_min
                job['salary_max'] = s_max
                page_jobs.append(job)

            print(f"    ✅ 第 {pg} 页: {len(page_jobs)} 条职位")
            all_jobs.extend(page_jobs)

            if len(page_jobs) == 0 or pg >= max_pages:
                break
            random_sleep(30, 60)

        except Exception as e:
            print(f"    ❌ 第 {pg} 页出错: {e}")
            break

    return all_jobs


# ============ 主函数 ============

def main():
    print("=" * 60)
    print("  真实招聘数据爬虫 - Playwright")
    print("=" * 60)

    all_jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN',
        )
        page = context.new_page()

        # 1. 登链社区（已验证可用）
        print("\n【1/3】爬取登链社区...")
        lb_jobs = crawl_learnblockchain(page, max_pages=5)
        print(f"  📊 登链社区共 {len(lb_jobs)} 条")
        all_jobs.extend(lb_jobs)

        if len(lb_jobs) > 0:
            random_sleep(30, 45)

        # 2. 猎聘（已验证可用）
        print("\n【2/3】爬取猎聘...")
        liepin_jobs = crawl_liepin(page, keyword='前端开发', city='北京', max_pages=2)
        print(f"  📊 猎聘共 {len(liepin_jobs)} 条")
        all_jobs.extend(liepin_jobs)

        if len(liepin_jobs) > 0:
            random_sleep(30, 45)

        # 3. 智联招聘（可能触发反爬，超时则跳过）
        print("\n【3/3】爬取智联招聘...")
        try:
            zhaopin_jobs = crawl_zhaopin(page, keyword='前端开发', city='北京', max_pages=1)
            print(f"  📊 智联招聘共 {len(zhaopin_jobs)} 条")
            all_jobs.extend(zhaopin_jobs)
        except Exception as e:
            print(f"  ⚠️ 智联招聘爬取失败: {e}")

        browser.close()

    # 保存 JSON
    print(f"\n{'=' * 60}")
    print(f"  总计爬取: {len(all_jobs)} 条职位数据")
    print(f"{'=' * 60}")

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_jobs, f, ensure_ascii=False, indent=2)
    print(f"  💾 数据已保存到: {OUTPUT_PATH}")

    # 数据预览
    print(f"\n📋 数据预览（前5条）：")
    for i, job in enumerate(all_jobs[:5]):
        print(f"\n  [{i+1}] {job['title']}")
        print(f"      来源: {job['source']} | 薪资: {job['salary_text']} | 地点: {job['location']}")
        print(f"      经验: {job['experience_requirement']} | 学历: {job['education_requirement']}")

    # 统计
    sources = {}
    for job in all_jobs:
        src = job['source']
        sources[src] = sources.get(src, 0) + 1
    print(f"\n📊 来源统计:")
    for src, count in sources.items():
        print(f"  {src}: {count} 条")


if __name__ == '__main__':
    main()
