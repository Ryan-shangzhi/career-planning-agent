"""
数据库初始化模块
优先从 jobs_data.json 加载爬虫数据，如果没有则使用内置数据
"""
import json
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Job, Company, SkillCategory

DATABASE_URL = "sqlite:///./career_planning.db"
JSON_PATH = os.path.join(os.path.dirname(__file__), 'jobs_data.json')

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def load_jobs_from_json():
    """从 JSON 文件加载爬虫数据"""
    if not os.path.exists(JSON_PATH):
        print(f"  未找到 {JSON_PATH}，使用内置数据")
        return []

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        raw_jobs = json.load(f)

    jobs = []
    for item in raw_jobs:
        # 解析薪资文本中的数字
        salary_min = item.get('salary_min')
        salary_max = item.get('salary_max')
        if salary_min is None:
            salary_min = 0
        if salary_max is None:
            salary_max = 0

        job = Job(
            title=item.get('title', ''),
            company_name=item.get('company_name', ''),
            industry=item.get('industry', ''),
            job_type=item.get('category', '') or item.get('job_type', ''),
            location=item.get('location', ''),
            salary_min=salary_min,
            salary_max=salary_max,
            experience_requirement=item.get('experience_requirement', ''),
            education_requirement=item.get('education_requirement', ''),
            description=item.get('description', ''),
            skills=item.get('skills', ''),
            source=item.get('source', ''),
            source_url=item.get('source_url', ''),
        )
        jobs.append(job)

    return jobs


def get_default_jobs():
    """内置默认职位数据（作为 fallback）"""
    return [
        Job(title="后端开发工程师", company_name="阿里巴巴", industry="互联网", job_type="技术",
            location="杭州", salary_min=25000, salary_max=50000, experience_requirement="1-3年",
            education_requirement="本科", description="负责服务端架构设计和开发，参与核心业务系统的设计与实现。",
            skills="Java,Spring Boot,MySQL,Redis,微服务,Docker,Kubernetes,消息队列,分布式系统,高并发,系统设计,性能优化",
            source="内置数据"),
        Job(title="高级前端工程师", company_name="京东", industry="电商", job_type="技术",
            location="北京", salary_min=25000, salary_max=45000, experience_requirement="3-5年",
            education_requirement="本科", description="负责核心业务开发、工程化建设、逐步提升开发、交付效率。",
            skills="JavaScript,React,Vue,TypeScript,Node.js,Webpack,微前端,性能优化,工程化,小程序开发",
            source="内置数据"),
        Job(title="前端开发工程师", company_name="阿里巴巴", industry="互联网", job_type="技术",
            location="杭州", salary_min=20000, salary_max=40000, experience_requirement="1-3年",
            education_requirement="本科", description="负责公司核心业务的前端开发，实现产品的页面交互及功能实现。",
            skills="JavaScript,HTML5,CSS3,React,Vue,TypeScript,Webpack,Node.js,ES6,性能优化,跨浏览器兼容,Git",
            source="内置数据"),
        Job(title="产品经理", company_name="字节跳动", industry="互联网", job_type="产品",
            location="北京", salary_min=20000, salary_max=40000, experience_requirement="1-3年",
            education_requirement="本科", description="负责产品规划和需求分析，收集整理产品需求，进行产品设计。",
            skills="需求分析,产品设计,PRD撰写,原型设计,Axure,Figma,数据分析,用户研究,竞品分析,项目管理,沟通协调,SQL",
            source="内置数据"),
        Job(title="UI设计师", company_name="哔哩哔哩", industry="互联网", job_type="设计",
            location="上海", salary_min=15000, salary_max=28000, experience_requirement="1-3年",
            education_requirement="本科", description="负责公司产品UI设计模块工作，基于产品需求与设计规范编写高质量设计方案。",
            skills="Figma,Photoshop,Illustrator,Sketch,UI设计,交互设计,设计规范,视觉设计,移动端设计,Web设计,图标设计,AE动效",
            source="内置数据"),
        Job(title="数据分析师", company_name="美团", industry="本地生活", job_type="数据",
            location="北京", salary_min=18000, salary_max=35000, experience_requirement="1-3年",
            education_requirement="本科", description="负责构建并优化企业核心业务数据指标体系，深入理解业务场景，开展专项数据分析工作。",
            skills="SQL,Python,Excel,Tableau,Power BI,数据分析,统计学,数据可视化,指标体系,数据清洗,假设检验,回归分析",
            source="内置数据"),
        Job(title="Go后端开发工程师", company_name="哔哩哔哩", industry="互联网", job_type="技术",
            location="上海", salary_min=25000, salary_max=45000, experience_requirement="1-3年",
            education_requirement="本科", description="负责B站核心业务后端开发，使用Go语言构建高并发、高可用系统。",
            skills="Go,Gin,gRPC,MySQL,Redis,Docker,Kubernetes,微服务,高并发,分布式系统,性能优化",
            source="内置数据"),
        Job(title="游戏策划", company_name="网易", industry="游戏", job_type="策划",
            location="杭州", salary_min=15000, salary_max=30000, experience_requirement="1-3年",
            education_requirement="本科", description="负责游戏系统设计、数值设计及关卡设计。",
            skills="游戏设计,数值策划,关卡设计,Excel,数据分析,文档撰写,玩家心理,系统设计,玩法设计,竞品分析",
            source="内置数据"),
    ]


def init_data():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 初始化公司数据
        if not db.query(Company).first():
            companies = [
                Company(name="阿里巴巴", industry="互联网", company_type="互联网大厂"),
                Company(name="腾讯", industry="互联网", company_type="互联网大厂"),
                Company(name="字节跳动", industry="互联网", company_type="互联网大厂"),
                Company(name="百度", industry="互联网", company_type="互联网大厂"),
                Company(name="京东", industry="电商", company_type="互联网大厂"),
                Company(name="美团", industry="本地生活", company_type="互联网大厂"),
                Company(name="华为", industry="通信", company_type="科技公司"),
                Company(name="小米", industry="消费电子", company_type="科技公司"),
                Company(name="网易", industry="游戏", company_type="游戏大厂"),
                Company(name="米哈游", industry="游戏", company_type="游戏公司"),
                Company(name="完美世界", industry="游戏", company_type="游戏公司"),
                Company(name="莉莉丝", industry="游戏", company_type="游戏公司"),
                Company(name="哔哩哔哩", industry="互联网", company_type="互联网公司"),
                Company(name="拼多多", industry="电商", company_type="互联网大厂"),
                Company(name="快手", industry="短视频", company_type="互联网大厂"),
            ]
            db.add_all(companies)
            db.commit()
            print("  公司数据初始化完成")

        # 初始化技能分类
        if not db.query(SkillCategory).first():
            categories = [
                SkillCategory(name="编程语言", description="编程相关技能"),
                SkillCategory(name="框架/库", description="开发框架和库"),
                SkillCategory(name="数据库", description="数据库技术"),
                SkillCategory(name="工具", description="开发工具"),
                SkillCategory(name="软技能", description="沟通协作等软技能"),
                SkillCategory(name="3D软件", description="3D建模和渲染软件"),
                SkillCategory(name="2D软件", description="2D设计和绘画软件"),
                SkillCategory(name="游戏引擎", description="游戏开发引擎"),
                SkillCategory(name="设计能力", description="设计相关能力"),
                SkillCategory(name="分析能力", description="数据分析相关能力"),
            ]
            db.add_all(categories)
            db.commit()
            print("  技能分类数据初始化完成")

        # 加载职位数据：优先 JSON，fallback 内置
        db.query(Job).delete()
        db.commit()

        json_jobs = load_jobs_from_json()
        if json_jobs:
            db.add_all(json_jobs)
            db.commit()
            print(f"  从 JSON 加载了 {len(json_jobs)} 条真实职位数据")
        else:
            default_jobs = get_default_jobs()
            db.add_all(default_jobs)
            db.commit()
            print(f"  使用了 {len(default_jobs)} 条内置职位数据")

    finally:
        db.close()


if __name__ == "__main__":
    init_data()
    print("所有数据初始化完成!")
