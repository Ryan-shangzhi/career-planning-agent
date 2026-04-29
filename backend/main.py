from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, field_validator, ConfigDict
from models import Job, User, AnalysisResult, Company
from database import get_db
from crawler_real import crawl_learnblockchain, crawl_liepin
import json
import re


def to_camel_case(data):
    """递归将 dict 的 key 从 snake_case 转为 camelCase"""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            # 将 snake_case 转为 camelCase
            camel_key = ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(key.split('_')))
            result[camel_key] = to_camel_case(value)
        return result
    elif isinstance(data, list):
        return [to_camel_case(item) for item in data]
    return data

app = FastAPI(title="职业规划顾问 API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

JOB_TYPE_MAPPING = {
    "后端": ["后端", "服务端", "java开发", "python开发", "golang", "go开发", "架构师"],
    "前端": ["前端", "web开发", "h5开发", "小程序开发", "移动端开发"],
    "设计": ["UI设计", "UX设计", "视觉设计", "交互设计", "平面设计", "设计师"],
    "美术": ["3D美术", "2D美术", "场景美术", "角色美术", "原画", "特效", "动画", "建模"],
    "产品": ["产品经理", "产品策划", "产品运营", "产品总监"],
    "数据": ["数据分析", "数据挖掘", "数据工程师", "算法", "机器学习"],
    "运营": ["运营", "市场", "推广", "增长"],
    "策划": ["游戏策划", "数值策划", "关卡策划", "系统策划"],
    "测试": ["测试", "QA", "质量"],
    "运维": ["运维", "devops", "sre", "基础设施"],
}

SKILL_MAPPING = {
    "后端": {
        "core": ["Java", "Python", "Go", "C++", "Node.js"],
        "framework": ["Spring Boot", "Django", "Flask", "Gin", "Express"],
        "database": ["MySQL", "PostgreSQL", "MongoDB", "Redis"],
        "tools": ["Docker", "Kubernetes", "Git", "Linux", "Nginx"],
        "concepts": ["微服务", "分布式系统", "高并发", "消息队列", "缓存", "API设计"]
    },
    "前端": {
        "core": ["JavaScript", "TypeScript", "HTML5", "CSS3"],
        "framework": ["React", "Vue", "Angular", "Next.js", "Nuxt.js"],
        "tools": ["Webpack", "Vite", "ESLint", "Git"],
        "concepts": ["组件化开发", "状态管理", "性能优化", "响应式设计", "跨浏览器兼容"]
    },
    "设计": {
        "core": ["Figma", "Sketch", "Adobe XD"],
        "tools": ["Photoshop", "Illustrator", "After Effects"],
        "concepts": ["UI设计", "UX设计", "交互设计", "视觉设计", "设计规范", "用户体验"]
    },
    "美术": {
        "core": ["3DMax", "Maya", "Blender", "ZBrush"],
        "tools": ["Substance Painter", "Photoshop", "Marvelous Designer"],
        "engine": ["UE4", "UE5", "Unity3D"],
        "concepts": ["PBR流程", "场景设计", "角色建模", "贴图绘制", "灯光烘焙", "LOD优化"]
    },
    "产品": {
        "core": ["需求分析", "产品设计", "PRD撰写", "原型设计"],
        "tools": ["Axure", "Figma", "XMind", "Visio"],
        "concepts": ["用户研究", "竞品分析", "数据分析", "项目管理", "A/B测试", "商业模式"]
    },
    "数据": {
        "core": ["SQL", "Python", "R"],
        "tools": ["Excel", "Tableau", "Power BI", "Jupyter"],
        "concepts": ["数据分析", "统计学", "数据可视化", "机器学习", "A/B测试", "指标体系"]
    },
    "运营": {
        "core": ["用户运营", "内容运营", "活动策划"],
        "tools": ["Excel", "数据分析", "文案写作"],
        "concepts": ["用户增长", "转化率优化", "社群运营", "数据分析"]
    },
    "策划": {
        "core": ["游戏设计", "数值策划", "关卡设计", "系统设计"],
        "tools": ["Excel", "Unity3D", "UE4"],
        "concepts": ["玩家心理", "玩法设计", "经济系统", "文档撰写"]
    },
    "测试": {
        "core": ["Python", "Java", "自动化测试"],
        "tools": ["Selenium", "JMeter", "Postman", "Jenkins"],
        "concepts": ["测试用例设计", "性能测试", "接口测试", "持续集成"]
    },
    "运维": {
        "core": ["Linux", "Docker", "Kubernetes"],
        "tools": ["Ansible", "Terraform", "Prometheus", "Grafana"],
        "concepts": ["CI/CD", "监控告警", "自动化运维", "云原生"]
    }
}

LEARNING_RESOURCES = {
    "Java": {"platform": "尚硅谷视频 + 《Java核心技术》", "duration": "3-4个月", "difficulty": "中等"},
    "Python": {"platform": "廖雪峰教程 + LeetCode", "duration": "2-3个月", "difficulty": "中等"},
    "Go": {"platform": "《Go语言实战》+ 官方文档", "duration": "2个月", "difficulty": "中等"},
    "JavaScript": {"platform": "MDN文档 + 《JavaScript高级程序设计》", "duration": "2-3个月", "difficulty": "中等"},
    "TypeScript": {"platform": "TypeScript官方文档", "duration": "1个月", "difficulty": "简单"},
    "React": {"platform": "React官方文档 + 实战项目", "duration": "1-2个月", "difficulty": "中等"},
    "Vue": {"platform": "Vue官方文档 + 尚硅谷教程", "duration": "1-2个月", "difficulty": "中等"},
    "Spring Boot": {"platform": "Spring官方文档 + 实战项目", "duration": "2个月", "difficulty": "中等"},
    "MySQL": {"platform": "《高性能MySQL》+ 实践", "duration": "2个月", "difficulty": "中等"},
    "Redis": {"platform": "《Redis设计与实现》", "duration": "1个月", "difficulty": "中等"},
    "Docker": {"platform": "Docker官方文档 + 实践", "duration": "2周", "difficulty": "简单"},
    "Kubernetes": {"platform": "Kubernetes官方文档", "duration": "1-2个月", "difficulty": "较难"},
    "Linux": {"platform": "《鸟哥的Linux私房菜》", "duration": "1-2个月", "difficulty": "中等"},
    "微服务": {"platform": "《Spring微服务实战》", "duration": "2-3个月", "difficulty": "较难"},
    "Figma": {"platform": "Figma官方教程 + Dribbble临摹", "duration": "1个月", "difficulty": "简单"},
    "Photoshop": {"platform": "B站教程 + 实践项目", "duration": "1-2个月", "difficulty": "中等"},
    "Sketch": {"platform": "Sketch官方教程 + 设计练习", "duration": "1个月", "difficulty": "简单"},
    "3DMax": {"platform": "AboutCG/翼狐网教程 + 项目实践", "duration": "2-3个月", "difficulty": "中等"},
    "Maya": {"platform": "Autodesk官方教程 + AboutCG", "duration": "3-4个月", "difficulty": "较难"},
    "Blender": {"platform": "Blender官方教程 + Blender Guru", "duration": "1-2个月", "difficulty": "中等"},
    "ZBrush": {"platform": "ZBrush官方教程 + 翼狐网", "duration": "2-3个月", "difficulty": "较难"},
    "Substance Painter": {"platform": "Substance官方教程 + ArtStation学习", "duration": "1-2个月", "difficulty": "中等"},
    "UE4": {"platform": "Unreal官方教程 + B站实战项目", "duration": "2-3个月", "difficulty": "较难"},
    "UE5": {"platform": "Unreal官方教程 + B站实战项目", "duration": "2-3个月", "difficulty": "较难"},
    "Unity3D": {"platform": "Unity官方教程 + B站实战项目", "duration": "2-3个月", "difficulty": "中等"},
    "SQL": {"platform": "LeetCode SQL题 + 《SQL必知必会》", "duration": "1个月", "difficulty": "简单"},
    "Tableau": {"platform": "Tableau官方教程 + 实践项目", "duration": "1个月", "difficulty": "简单"},
    "Power BI": {"platform": "微软官方教程 + 实践", "duration": "1个月", "difficulty": "简单"},
    "Axure": {"platform": "Axure官方教程 + 原型练习", "duration": "2周", "difficulty": "简单"},
    "需求分析": {"platform": "《需求分析实战》+ 案例练习", "duration": "1个月", "difficulty": "中等"},
    "产品设计": {"platform": "《人人都是产品经理》", "duration": "1个月", "difficulty": "简单"},
    "数据分析": {"platform": "《Python数据分析》+ Kaggle", "duration": "2-3个月", "difficulty": "中等"},
    "场景设计": {"platform": "《游戏场景设计》+ ArtStation参考", "duration": "2-3个月", "difficulty": "中等"},
    "PBR流程": {"platform": "Substance官方PBR教程", "duration": "1个月", "difficulty": "中等"},
    "游戏设计": {"platform": "《游戏设计艺术》+ 分析优秀游戏", "duration": "2-3个月", "difficulty": "中等"},
    "数值策划": {"platform": "《游戏数值设计》+ Excel实践", "duration": "1-2个月", "difficulty": "中等"},
}


class JobCreate(BaseModel):
    title: str
    company_name: str
    industry: Optional[str] = None
    job_type: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    experience_requirement: Optional[str] = None
    education_requirement: Optional[str] = None
    description: Optional[str] = None
    skills: Optional[str] = None
    tags: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None


class UserCreate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    current_job: Optional[str] = None
    experience_years: Optional[int] = None
    skills: Optional[str] = None


class AnalysisRequest(BaseModel):
    user_id: Optional[int] = None
    user_skills: List[str]
    user_experience: int
    target_job: str
    target_company: Optional[str] = None

    @field_validator('user_skills')
    @classmethod
    def validate_skills(cls, v):
        if not v or all(not s.strip() for s in v):
            raise ValueError('至少需要填写一项技能')
        return [s.strip() for s in v if s.strip()]

    @field_validator('target_job')
    @classmethod
    def validate_target_job(cls, v):
        if not v or not v.strip():
            raise ValueError('目标岗位不能为空')
        return v.strip()

    @field_validator('user_experience')
    @classmethod
    def validate_experience(cls, v):
        if v < 0:
            raise ValueError('工作经验年限不能为负数')
        return v


class JobMatch(BaseModel):
    model_config = ConfigDict(alias_generator=lambda s: ''.join(
        word.capitalize() if i > 0 else word for i, word in enumerate(s.split('_'))
    ), populate_by_name=True)

    id: int
    title: str
    company_name: str
    location: Optional[str]
    salary_range: str
    experience_requirement: Optional[str]
    education_requirement: Optional[str]
    skills: List[str]
    match_score: float
    job_type: str


class EnhancedAnalysisResponse(BaseModel):
    model_config = ConfigDict(alias_generator=lambda s: ''.join(
        word.capitalize() if i > 0 else word for i, word in enumerate(s.split('_'))
    ), populate_by_name=True)

    target_job: str
    job_type: str
    matched_jobs: List[JobMatch]
    gap_analysis: dict
    action_plan: dict
    competition_analysis: dict
    salary_analysis: dict
    skill_recommendations: dict


def get_job_type(title: str) -> str:
    title_lower = title.lower()
    for job_type, keywords in JOB_TYPE_MAPPING.items():
        for keyword in keywords:
            if keyword.lower() in title_lower:
                return job_type
    return "其他"


def get_relevant_skills(job_type: str) -> List[str]:
    skills = []
    if job_type in SKILL_MAPPING:
        for category, skill_list in SKILL_MAPPING[job_type].items():
            skills.extend(skill_list)
    return skills


@app.get("/")
def read_root():
    return {"message": "职业规划顾问 API"}


class JobSearchRequest(BaseModel):
    keyword: Optional[str] = None
    city: Optional[str] = None
    limit: int = 20


@app.get("/api/jobs", response_model=List[dict])
def get_jobs(
    keyword: Optional[str] = None,
    city: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(Job)
    if keyword:
        query = query.filter(Job.title.like(f"%{keyword}%") | Job.skills.like(f"%{keyword}%"))
    if city:
        query = query.filter(Job.location.like(f"%{city}%"))
    
    jobs = query.limit(limit).all()
    
    result = []
    for job in jobs:
        result.append({
            "id": job.id,
            "title": job.title,
            "company_name": job.company_name,
            "industry": job.industry,
            "location": job.location,
            "salary_min": float(job.salary_min) if job.salary_min else None,
            "salary_max": float(job.salary_max) if job.salary_max else None,
            "experience_requirement": job.experience_requirement,
            "education_requirement": job.education_requirement,
            "description": job.description,
            "skills": job.skills,
            "source": job.source,
            "created_at": job.created_at.isoformat()
        })
    
    return to_camel_case(result)


@app.post("/api/jobs/search", response_model=List[dict])
def search_jobs(request: JobSearchRequest, db: Session = Depends(get_db)):
    query = db.query(Job)
    if request.keyword:
        query = query.filter(Job.title.like(f"%{request.keyword}%") | Job.skills.like(f"%{request.keyword}%"))
    if request.city:
        query = query.filter(Job.location.like(f"%{request.city}%"))
    
    jobs = query.limit(request.limit).all()
    
    result = []
    for job in jobs:
        result.append({
            "id": job.id,
            "title": job.title,
            "company_name": job.company_name,
            "industry": job.industry,
            "location": job.location,
            "salary_min": float(job.salary_min) if job.salary_min else None,
            "salary_max": float(job.salary_max) if job.salary_max else None,
            "experience_requirement": job.experience_requirement,
            "education_requirement": job.education_requirement,
            "description": job.description,
            "skills": job.skills,
            "source": job.source,
            "created_at": job.created_at.isoformat()
        })
    
    return result


@app.get("/api/jobs/{job_id}", response_model=dict)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    return {
        "id": job.id,
        "title": job.title,
        "company_name": job.company_name,
        "industry": job.industry,
        "location": job.location,
        "salary_min": float(job.salary_min) if job.salary_min else None,
        "salary_max": float(job.salary_max) if job.salary_max else None,
        "experience_requirement": job.experience_requirement,
        "education_requirement": job.education_requirement,
        "description": job.description,
        "skills": job.skills,
        "source": job.source,
        "source_url": job.source_url,
        "created_at": job.created_at.isoformat()
    }


@app.post("/api/jobs")
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    db_job = Job(
        title=job.title,
        company_name=job.company_name,
        industry=job.industry,
        job_type=job.job_type,
        location=job.location,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        experience_requirement=job.experience_requirement,
        education_requirement=job.education_requirement,
        description=job.description,
        skills=job.skills,
        tags=job.tags,
        source=job.source,
        source_url=job.source_url
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    return {"id": db_job.id, "message": "职位创建成功"}


@app.delete("/api/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    db.delete(job)
    db.commit()
    
    return {"message": "职位删除成功"}


class CrawlRequest(BaseModel):
    keyword: str
    city: str = "北京"
    pages: int = 1


@app.post("/api/crawl")
def crawl_and_save_jobs(request: CrawlRequest, db: Session = Depends(get_db)):
    """使用 Playwright 爬取真实招聘数据（较慢，约 30s-2min）"""
    from playwright.sync_api import sync_playwright
    
    all_jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            locale='zh-CN',
        )
        page = context.new_page()
        
        # 爬取登链社区
        try:
            lb_jobs = crawl_learnblockchain(page, max_pages=request.pages)
            all_jobs.extend(lb_jobs)
        except Exception as e:
            pass
        
        # 爬取猎聘
        try:
            liepin_jobs = crawl_liepin(page, keyword=request.keyword, city=request.city, max_pages=request.pages)
            all_jobs.extend(liepin_jobs)
        except Exception as e:
            pass
        
        browser.close()
    
    # 保存到数据库
    saved_count = 0
    for job_data in all_jobs:
        existing_job = db.query(Job).filter(
            Job.title == job_data.get('title', ''),
            Job.source_url == job_data.get('source_url', '')
        ).first()
        
        if not existing_job:
            db_job = Job(
                title=job_data.get('title', ''),
                company_name=job_data.get('company_name', ''),
                industry=job_data.get('industry', ''),
                job_type=job_data.get('category', '') or job_data.get('job_type', ''),
                location=job_data.get('location', ''),
                salary_min=job_data.get('salary_min') or 0,
                salary_max=job_data.get('salary_max') or 0,
                experience_requirement=job_data.get('experience_requirement', ''),
                education_requirement=job_data.get('education_requirement', ''),
                description=job_data.get('description', ''),
                skills=job_data.get('skills', ''),
                source=job_data.get('source', ''),
                source_url=job_data.get('source_url', ''),
            )
            db.add(db_job)
            saved_count += 1
    
    db.commit()
    
    return {"message": f"爬取完成：共 {len(all_jobs)} 条，新增 {saved_count} 条", "total": len(all_jobs), "new": saved_count}


@app.post("/api/users", response_model=dict)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if user.email:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="邮箱已存在")
    
    db_user = User(
        name=user.name,
        email=user.email,
        current_job=user.current_job,
        experience_years=user.experience_years,
        skills=user.skills
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"id": db_user.id, "message": "用户创建成功"}


@app.get("/api/users/{user_id}", response_model=dict)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "current_job": user.current_job,
        "experience_years": user.experience_years,
        "skills": user.skills,
        "created_at": user.created_at.isoformat()
    }


def parse_experience(exp_str: str) -> tuple:
    if not exp_str:
        return (0, 0)
    match = re.search(r'(\d+)-(\d+)', exp_str)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    match = re.search(r'(\d+)', exp_str)
    if match:
        return (int(match.group(1)), int(match.group(1)))
    return (0, 0)


def calculate_match_score(job: Job, user_skills: List[str], user_experience: int, job_type: str = "其他") -> float:
    score = 0.0
    skill_match_weight = 50
    exp_match_weight = 30
    salary_match_weight = 20
    
    if job.skills:
        job_skills = [s.strip().lower() for s in job.skills.split(",")]
        user_skills_lower = [s.lower() for s in user_skills]
        
        matched = 0
        for s in job_skills:
            if s in user_skills_lower:
                matched += 1
            else:
                # 检查是否有部分匹配，但是不同类别的技能不能过度匹配
                for us in user_skills_lower:
                    if us in s:
                        matched += 0.5
        
        if job_skills:
            score += (matched / len(job_skills)) * skill_match_weight
    
    min_exp, max_exp = parse_experience(job.experience_requirement)
    job_title_lower = job.title.lower()
    is_senior_job = any(kw in job_title_lower for kw in ["高级", "资深", "专家", "senior", "expert"])
    
    # 根据经验给分
    if min_exp <= user_experience <= max_exp:
        score += exp_match_weight
    elif user_experience > max_exp:
        # 超出经验上限
        if is_senior_job:
            # 高级岗位，用户经验超出是好事，给高分
            score += exp_match_weight * 0.9
        else:
            # 普通岗位，用户经验超出，可以胜任但可能overqualified
            score += exp_match_weight * 0.6
    elif user_experience >= min_exp * 0.5:
        score += exp_match_weight * 0.5
    else:
        score += exp_match_weight * 0.2
    
    # 薪资匹配：根据用户经验调整期望
    if job.salary_min and job.salary_max:
        # 高级岗位薪资通常更高，对资深用户更有吸引力
        if is_senior_job and user_experience >= 5:
            score += salary_match_weight * 1.2
        else:
            score += salary_match_weight
    
    return round(score, 1)


def filter_jobs_by_experience(jobs: List[Job], user_experience: int) -> List[Job]:
    """根据用户经验过滤和排序岗位"""
    filtered = []
    for job in jobs:
        min_exp, max_exp = parse_experience(job.experience_requirement)
        # 完全匹配经验范围
        if min_exp <= user_experience <= max_exp:
            filtered.append((100, job))
        # 经验超出上限（推荐高级岗位）
        elif user_experience > max_exp:
            # 检查是否包含高级关键词
            job_title = job.title.lower()
            is_senior = any(kw in job_title for kw in ["高级", "资深", "专家", "senior", "expert"])
            if is_senior:
                filtered.append((90, job))
            else:
                filtered.append((70, job))
        # 经验不足但有潜力
        elif user_experience >= min_exp * 0.5:
            filtered.append((50, job))
        # 经验差距太大
        else:
            filtered.append((20, job))
    
    # 按匹配分数排序
    filtered.sort(key=lambda x: x[0], reverse=True)
    # 返回排序后的岗位列表
    return [job for (score, job) in filtered]


def extract_common_skills(jobs: List[Job]) -> List[tuple]:
    """从 job.skills 字段和 JD 描述文本中提取技能关键词"""
    skill_count = {}
    # 常见技能关键词列表（用于从 JD 文本中提取）
    tech_keywords = [
        "JavaScript", "TypeScript", "React", "Vue", "Angular", "Node.js", "Next.js", "Nuxt.js",
        "HTML5", "CSS3", "Sass", "Less", "Tailwind", "Webpack", "Vite", "ES6",
        "Java", "Python", "Go", "C++", "Rust", "PHP", "Ruby", "Swift", "Kotlin",
        "Spring Boot", "Django", "Flask", "Express", "Gin", "FastAPI",
        "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "ClickHouse",
        "Docker", "Kubernetes", "Jenkins", "CI/CD", "Git",
        "AWS", "Azure", "GCP", "Linux", "Nginx",
        "微服务", "分布式", "高并发", "消息队列", "Kafka", "RabbitMQ",
        "机器学习", "深度学习", "NLP", "数据分析", "数据挖掘",
        "Figma", "Sketch", "Photoshop", "Illustrator", "UI设计", "UX设计",
        "产品经理", "项目管理", "Scrum", "Agile",
        "Solidity", "Web3", "区块链", "智能合约", "DeFi",
        "Flutter", "React Native", "iOS", "Android", "小程序",
        "GraphQL", "RESTful", "gRPC", "WebSocket",
        "TDD", "单元测试", "性能优化", "SEO",
    ]

    for job in jobs:
        # 1. 从 skills 字段提取
        if job.skills:
            for skill in job.skills.split(","):
                skill = skill.strip()
                if skill:
                    skill_count[skill] = skill_count.get(skill, 0) + 1

        # 2. 从 JD 描述文本中提取
        if job.description:
            desc = job.description
            for keyword in tech_keywords:
                if keyword.lower() in desc.lower():
                    skill_count[keyword] = skill_count.get(keyword, 0) + 1

    sorted_skills = sorted(skill_count.items(), key=lambda x: x[1], reverse=True)
    return sorted_skills


def analyze_salary_range(jobs: List[Job]) -> dict:
    salaries = []
    for job in jobs:
        if job.salary_min and job.salary_max:
            salaries.append((job.salary_min, job.salary_max))
    
    if not salaries:
        return {"min": 0, "max": 0, "avg": 0, "median": 0}
    
    min_salary = min(s[0] for s in salaries)
    max_salary = max(s[1] for s in salaries)
    avg_salary = sum((s[0] + s[1]) / 2 for s in salaries) / len(salaries)
    
    sorted_salaries = sorted(salaries, key=lambda x: x[0])
    mid = len(sorted_salaries) // 2
    median_salary = (sorted_salaries[mid][0] + sorted_salaries[mid][1]) / 2
    
    return {
        "min": int(min_salary),
        "max": int(max_salary),
        "avg": int(avg_salary),
        "median": int(median_salary)
    }


def generate_skill_recommendations(missing_skills: List[str], job_type: str) -> dict:
    relevant_skills = set(get_relevant_skills(job_type))
    
    recommendations = []
    for skill in missing_skills[:5]:
        if skill in relevant_skills or job_type == "其他":
            resource = LEARNING_RESOURCES.get(skill, {
                "platform": f"搜索'{skill}教程'或相关书籍",
                "duration": "1-2个月",
                "difficulty": "中等"
            })
            recommendations.append({
                "skill": skill,
                "platform": resource["platform"],
                "duration": resource["duration"],
                "difficulty": resource["difficulty"]
            })
    
    if not recommendations:
        for skill in relevant_skills:
            if skill in missing_skills:
                resource = LEARNING_RESOURCES.get(skill, {
                    "platform": f"搜索'{skill}教程'或相关书籍",
                    "duration": "1-2个月",
                    "difficulty": "中等"
                })
                recommendations.append({
                    "skill": skill,
                    "platform": resource["platform"],
                    "duration": resource["duration"],
                    "difficulty": resource["difficulty"]
                })
                if len(recommendations) >= 5:
                    break
    
    return {"recommendations": recommendations}


@app.post("/api/analyze", response_model=EnhancedAnalysisResponse)
def analyze_career(request: AnalysisRequest, db: Session = Depends(get_db)):
    target_job = request.target_job
    user_skills = [s.strip().lower() for s in request.user_skills]
    user_experience = request.user_experience
    
    target_job_type = get_job_type(target_job)
    
    all_jobs = db.query(Job).all()
    
    same_type_jobs = [job for job in all_jobs if get_job_type(job.title) == target_job_type]
    
    # 搜索匹配的岗位（宽松匹配：岗位标题包含目标关键词，或目标关键词包含岗位核心词）
    matched_jobs_query = []
    target_lower = target_job.lower()
    for job in same_type_jobs:
        job_title_lower = job.title.lower()
        # 双向匹配：目标职位包含岗位标题核心词，或岗位标题包含目标职位核心词
        if target_lower in job_title_lower:
            matched_jobs_query.append(job)
        else:
            # 检查核心关键词是否匹配
            target_keywords = target_lower.replace("开发", "").replace("工程师", "").replace("师", "").split()
            job_keywords = job_title_lower.replace("开发", "").replace("工程师", "").replace("师", "").split()
            # 如果核心关键词有交集，也加入匹配
            for tk in target_keywords:
                for jk in job_keywords:
                    if tk in jk or jk in tk:
                        matched_jobs_query.append(job)
                        break
    
    # 去重
    matched_jobs_query = list(set(matched_jobs_query))
    
    # 如果匹配结果太少，使用同类型所有岗位
    if len(matched_jobs_query) < 3:
        matched_jobs_query = same_type_jobs
    
    # 如果用户经验丰富，优先推荐高级岗位
    if user_experience >= 5:
        senior_jobs = [job for job in matched_jobs_query if any(kw in job.title.lower() for kw in ["高级", "资深", "专家", "senior", "expert"])]
        if senior_jobs:
            # 高级岗位排在前面
            matched_jobs_query = senior_jobs + [j for j in matched_jobs_query if j not in senior_jobs]
    
    if request.target_company:
        company_jobs = [job for job in all_jobs if request.target_company.lower() in job.company_name.lower()]
        matched_jobs_query = list(set(matched_jobs_query) | set(company_jobs))
    
    # ==== 问题1修复：经验匹配逻辑 ====
    filtered_jobs = filter_jobs_by_experience(matched_jobs_query, user_experience)
    
    matched_jobs = []
    for job in filtered_jobs[:10]:
        match_score = calculate_match_score(job, user_skills, user_experience, target_job_type)
        salary_range = f"{int(job.salary_min/1000)}K-{int(job.salary_max/1000)}K" if job.salary_min and job.salary_max else "面议"
        matched_jobs.append(JobMatch(
            id=job.id,
            title=job.title,
            company_name=job.company_name,
            location=job.location,
            salary_range=salary_range,
            experience_requirement=job.experience_requirement,
            education_requirement=job.education_requirement,
            skills=job.skills.split(",") if job.skills else [],
            match_score=match_score,
            job_type=get_job_type(job.title)
        ))
    
    matched_jobs.sort(key=lambda x: x.match_score, reverse=True)
    
    # ==== 问题2和3修复：技能来源和差距分析 ====
    all_skills = extract_common_skills(same_type_jobs)
    relevant_skills = set(get_relevant_skills(target_job_type))
    
    # 分析用户现有技能的类型
    user_skill_types = set()
    for skill in user_skills:
        skill_lower = skill.lower()
        # 前端技能识别
        if any(frontend_kw in skill_lower for frontend_kw in ["javascript", "react", "vue", "css", "html", "typescript", "webpack", "vite", "es6"]):
            user_skill_types.add("前端")
        # 后端技能识别
        if any(backend_kw in skill_lower for backend_kw in ["java", "python", "go", "spring", "mysql", "node.js", "nodejs", "express", "django", "flask", "gin", "grpc", "redis", "kafka", "分布式", "微服务", "api", "restful"]):
            user_skill_types.add("后端")
        # 数据技能识别
        if any(data_kw in skill_lower for data_kw in ["sql", "数据分析", "tableau", "power bi", "excel", "python"]):
            user_skill_types.add("数据")
        # 产品技能识别
        if any(pm_kw in skill_lower for pm_kw in ["产品", "需求", "原型", "axure", "figma"]):
            user_skill_types.add("产品")
        # 运营技能识别
        if any(ops_kw in skill_lower for ops_kw in ["运营", "增长", "用户"]):
            user_skill_types.add("运营")
        # 测试技能识别
        if any(test_kw in skill_lower for test_kw in ["测试", "qa", "selenium", "自动化"]):
            user_skill_types.add("测试")
        # 运维技能识别
        if any(devops_kw in skill_lower for devops_kw in ["docker", "kubernetes", "linux", "运维", "devops", "ci/cd"]):
            user_skill_types.add("运维")
    
    # 检查是否是转型
    is_transition = len(user_skill_types) > 0 and target_job_type not in user_skill_types
    
    gap_analysis_skills = []
    missing_skills = []
    transferable_skills = []
    
    for skill, count in all_skills[:15]:
        skill_lower = skill.lower()
        has_skill = any(skill_lower == us.lower() for us in user_skills)
        # 检查是否可以从其他技能迁移过来
        is_transferable = False
        if not has_skill:
            for us in user_skills:
                us_lower = us.lower()
                # 项目管理可以迁移到任何需要项目管理的岗位
                if "项目管理" in skill and "项目管理" in us:
                    is_transferable = True
                # 分布式系统是通用后端技能
                if "分布式系统" in skill and "分布式" in us_lower:
                    is_transferable = True
                # Node.js开发者可以迁移到后端开发
                if skill_lower in ["node.js", "nodejs"] and "node" in us_lower:
                    is_transferable = True
                # Docker/K8s是通用运维技能
                if skill_lower in ["docker", "kubernetes"] and us_lower in ["docker", "kubernetes", "devops"]:
                    is_transferable = True
                # Redis/消息队列是通用后端技能
                if skill_lower in ["redis", "kafka", "消息队列"] and ("分布式" in us_lower or "微服务" in us_lower):
                    is_transferable = True
        
        if skill in relevant_skills or target_job_type == "其他":
            if has_skill:
                gap_analysis_skills.append({
                    "skill": skill,
                    "required": True,
                    "user_has": True,
                    "gap": "达标",
                    "frequency": count
                })
            else:
                gap_type = "缺口"
                if is_transferable:
                    gap_type = "可迁移"
                    transferable_skills.append(skill)
                gap_analysis_skills.append({
                    "skill": skill,
                    "required": True,
                    "user_has": False,
                    "gap": gap_type,
                    "frequency": count
                })
                missing_skills.append(skill)
    
    exp_requirements = [parse_experience(job.experience_requirement) for job in same_type_jobs if job.experience_requirement]
    avg_min_exp = 0
    avg_max_exp = 0
    if exp_requirements:
        avg_min_exp = sum(e[0] for e in exp_requirements) / len(exp_requirements)
        avg_max_exp = sum(e[1] for e in exp_requirements) / len(exp_requirements)
        exp_required = f"{int(avg_min_exp)}-{int(avg_max_exp)}年"
    else:
        exp_required = "不限"
    
    edu_requirements = [job.education_requirement for job in same_type_jobs if job.education_requirement]
    common_edu = max(set(edu_requirements), key=edu_requirements.count) if edu_requirements else "不限"
    
    salary_analysis = analyze_salary_range(same_type_jobs)
    
    # ==== 问题3修复：转型逻辑和行动计划 ====
    action_plan = {
        "short_term": [],
        "medium_term": [],
        "long_term": []
    }
    
    # 根据是否是转型定制不同的计划
    if is_transition:
        action_plan["short_term"].append(f"🚀 你正在进行{', '.join(user_skill_types)} → {target_job_type}的转型！")
        if transferable_skills:
            action_plan["short_term"].append(f"✅ 可复用技能：{', '.join(transferable_skills[:3])}")
    
    for skill in missing_skills[:3]:
        if skill in ["java", "go", "spring"]:
            action_plan["short_term"].append(f"📚 核心学习：{skill}，通过系统课程快速入门，预计1-3个月掌握基础")
        else:
            action_plan["short_term"].append(f"📚 学习 {skill}，建议通过系统课程或书籍学习，每天1-2小时，预计1-2个月掌握基础")
    
    if missing_skills:
        action_plan["short_term"].append(f"🎯 重点关注核心技能：{', '.join(missing_skills[:3])}，这些技能在相关岗位中出现频率最高")
    
    if user_experience < avg_min_exp:
        exp_gap = int(avg_min_exp - user_experience)
        action_plan["medium_term"].append(f"💼 积累 {exp_gap} 年相关工作经验，可通过实习、兼职或项目经验补充")
    elif user_experience > avg_max_exp:
        action_plan["medium_term"].append(f"👑 你的经验超出一般标准，更适合目标高级/资深岗位！")
    
    if missing_skills:
        action_plan["medium_term"].append(f"🎯 完成2-3个实战项目，重点应用{', '.join(missing_skills[:3])}技能")
        action_plan["medium_term"].append("📝 整理项目作品集，建立技术博客或设计作品展示")
    
    if request.target_company:
        action_plan["medium_term"].append(f"🔍 研究 {request.target_company} 的技术栈和团队文化，针对性准备")
    
    action_plan["long_term"].append("📋 优化简历，突出项目经验和技能匹配度")
    action_plan["long_term"].append("📚 准备面试题，包括专业技能和行为面试")
    action_plan["long_term"].append("🎯 制定投递策略：先投递匹配度70%以上的岗位，积累面试经验后再投递心仪公司")
    
    # ==== 问题1修复：根据经验设定合适的薪资目标 ====
    if user_experience >= 10:
        action_plan["long_term"].append("💰 目标薪资范围：40K-80K")
    elif user_experience >= 5:
        action_plan["long_term"].append("💰 目标薪资范围：30K-60K")
    else:
        action_plan["long_term"].append(f"💰 目标薪资范围：{int(salary_analysis['avg']/1000)}K-{int(salary_analysis['max']/1000)}K")
    
    total_jobs = len(same_type_jobs)
    high_match_jobs = len([j for j in matched_jobs if j.match_score >= 50])
    
    # ==== 问题3修复：竞争分析加入转型信息 ====
    if total_jobs > 5:
        supply_demand = f"该类型岗位需求稳定，共找到{total_jobs}个相关岗位"
    elif total_jobs > 2:
        supply_demand = f"该类型岗位相对稀缺，共找到{total_jobs}个相关岗位"
    else:
        supply_demand = f"该类型岗位较少，建议扩大搜索范围"
    
    competitor_profile = f"通常要求{common_edu}学历，{exp_required}经验，掌握{len(all_skills[:5])}项核心技能"
    
    matched_skill_count = len([s for s in gap_analysis_skills if s["gap"] == "达标"])
    total_required_skills = len(gap_analysis_skills)
    
    if is_transition:
        user_advantage = f"🎯 转型场景：{', '.join(user_skill_types)} → {target_job_type}，具备可迁移技能，潜力巨大"
    elif matched_skill_count / max(total_required_skills, 1) >= 0.7:
        user_advantage = f"✅ 技能匹配度高（{matched_skill_count}/{total_required_skills}），具备较强竞争力"
    elif matched_skill_count / max(total_required_skills, 1) >= 0.4:
        user_advantage = f"💪 部分技能匹配（{matched_skill_count}/{total_required_skills}），有一定基础"
    else:
        user_advantage = "🚀 学习能力强，有转型决心"
    
    if is_transition:
        user_disadvantage = f"⚠️ 转型挑战：需要补充{len(missing_skills)}项核心技能"
        if transferable_skills:
            user_disadvantage += f"，但{len(transferable_skills)}项技能可以迁移"
    elif missing_skills:
        user_disadvantage = f"❌ 缺乏{len(missing_skills)}项核心技能：{', '.join(missing_skills[:3])}"
        if user_experience < avg_min_exp:
            user_disadvantage += f"；经验不足（需要{exp_required}）"
    else:
        user_disadvantage = "💡 经验可能不足，需要更多项目历练"
    
    competition_analysis = {
        "supply_demand": supply_demand,
        "competitor_profile": competitor_profile,
        "user_advantage": user_advantage,
        "user_disadvantage": user_disadvantage,
        "market_insight": f"分析了{total_jobs}个{target_job_type}类岗位，{high_match_jobs}个岗位匹配度超过50%"
    }
    
    skill_recommendations = generate_skill_recommendations(missing_skills, target_job_type)
    
    if request.user_id:
        analysis_result = AnalysisResult(
            user_id=request.user_id,
            target_job_title=target_job,
            gap_analysis=json.dumps(gap_analysis_skills),
            action_plan=json.dumps(action_plan)
        )
        db.add(analysis_result)
        db.commit()
    
    response_data = EnhancedAnalysisResponse(
        target_job=target_job,
        job_type=target_job_type,
        matched_jobs=matched_jobs[:5],
        gap_analysis={
            "skills": gap_analysis_skills,
            "experience": {
                "required": exp_required,
                "user": user_experience,
                "gap": max(0, int(avg_min_exp - user_experience)) if user_experience < avg_min_exp else 0
            },
            "education": {
                "required": common_edu,
                "market_trend": f"在{total_jobs}个岗位中，{edu_requirements.count(common_edu)}个要求{common_edu}学历"
            }
        },
        action_plan=action_plan,
        competition_analysis=competition_analysis,
        salary_analysis=salary_analysis,
        skill_recommendations=skill_recommendations
    )
    # 转换为 camelCase（包括嵌套 dict）
    return to_camel_case(response_data.model_dump())


@app.get("/api/companies", response_model=List[dict])
def get_companies(
    name: Optional[str] = None,
    industry: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Company)
    if name:
        query = query.filter(Company.name.like(f"%{name}%"))
    if industry:
        query = query.filter(Company.industry.like(f"%{industry}%"))
    
    companies = query.all()
    
    return to_camel_case([{
        "id": c.id,
        "name": c.name,
        "industry": c.industry,
        "company_type": c.company_type,
        "description": c.description
    } for c in companies])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
