from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Job, Company, SkillCategory

DATABASE_URL = "sqlite:///./career_planning.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
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
            print("公司数据初始化完成")
        
        db.query(Job).delete()
        db.commit()
        
        jobs = [
            Job(
                title="后端开发工程师",
                company_name="阿里巴巴",
                industry="互联网",
                job_type="技术",
                location="杭州",
                salary_min=25000,
                salary_max=50000,
                experience_requirement="1-3年",
                education_requirement="本科",
                description="负责服务端架构设计和开发，参与核心业务系统的设计与实现。负责高并发、高可用系统的开发与优化，保证系统稳定性和性能。",
                skills="Java,Spring Boot,MySQL,Redis,微服务,Docker,Kubernetes,消息队列,分布式系统,高并发,系统设计,性能优化",
                source="Boss直聘"
            ),
            Job(
                title="高级后端工程师",
                company_name="腾讯",
                industry="互联网",
                job_type="技术",
                location="深圳",
                salary_min=35000,
                salary_max=60000,
                experience_requirement="3-5年",
                education_requirement="本科",
                description="负责核心业务系统架构设计，主导技术方案评审，解决复杂技术问题。参与微服务架构演进，保障系统高可用和高性能。",
                skills="Java,Go,Spring Cloud,MySQL,Redis,Kafka,Docker,Kubernetes,分布式系统,高并发,架构设计,性能调优",
                source="拉勾网"
            ),
            Job(
                title="Java后端开发工程师",
                company_name="字节跳动",
                industry="互联网",
                job_type="技术",
                location="北京",
                salary_min=25000,
                salary_max=45000,
                experience_requirement="1-3年",
                education_requirement="本科",
                description="负责抖音/今日头条核心业务后端开发，参与高并发系统设计与实现，优化系统性能和稳定性。",
                skills="Java,Spring Boot,MySQL,Redis,消息队列,微服务,分布式系统,高并发,性能优化,系统设计",
                source="Boss直聘"
            ),
            Job(
                title="Go后端开发工程师",
                company_name="哔哩哔哩",
                industry="互联网",
                job_type="技术",
                location="上海",
                salary_min=25000,
                salary_max=45000,
                experience_requirement="1-3年",
                education_requirement="本科",
                description="负责B站核心业务后端开发，使用Go语言构建高并发、高可用系统，参与微服务架构设计。",
                skills="Go,Gin,gRPC,MySQL,Redis,Docker,Kubernetes,微服务,高并发,分布式系统,性能优化",
                source="Boss直聘"
            ),
            Job(
                title="Python后端开发工程师",
                company_name="美团",
                industry="本地生活",
                job_type="技术",
                location="北京",
                salary_min=22000,
                salary_max=40000,
                experience_requirement="1-3年",
                education_requirement="本科",
                description="负责美团核心业务后端开发，使用Python/Django构建高可用系统，参与系统架构设计和性能优化。",
                skills="Python,Django,Flask,MySQL,Redis,Docker,消息队列,RESTful API,微服务,性能优化",
                source="Boss直聘"
            ),
            Job(
                title="前端开发工程师",
                company_name="阿里巴巴",
                industry="互联网",
                job_type="技术",
                location="杭州",
                salary_min=20000,
                salary_max=40000,
                experience_requirement="1-3年",
                education_requirement="本科",
                description="负责公司核心业务的前端开发，实现产品的页面交互及功能实现。与程序开发人员紧密合作，制作前端及后端程序接口标准。",
                skills="JavaScript,HTML5,CSS3,React,Vue,TypeScript,Webpack,Node.js,ES6,性能优化,跨浏览器兼容,Git",
                source="Boss直聘"
            ),
            Job(
                title="高级前端工程师",
                company_name="京东",
                industry="电商",
                job_type="技术",
                location="北京",
                salary_min=25000,
                salary_max=45000,
                experience_requirement="3-5年",
                education_requirement="本科",
                description="负责核心业务开发、工程化建设、逐步提升开发、交付效率，并保证产品工程质量。",
                skills="JavaScript,React,Vue,TypeScript,Node.js,Webpack,微前端,性能优化,工程化,小程序开发",
                source="Boss直聘"
            ),
            Job(
                title="3D场景美术师",
                company_name="网易",
                industry="游戏",
                job_type="美术",
                location="杭州",
                salary_min=18000,
                salary_max=35000,
                experience_requirement="1-3年",
                education_requirement="本科",
                description="负责游戏3D场景设计与制作，包括建筑、自然环境等场景资产。负责游戏中场景模型制作。",
                skills="3DMax,Maya,Blender,Substance Painter,UE4,UE5,Unity3D,场景设计,手绘贴图,PBR流程,ZBrush,Photoshop",
                source="Boss直聘"
            ),
            Job(
                title="高级3D场景美术师",
                company_name="米哈游",
                industry="游戏",
                job_type="美术",
                location="上海",
                salary_min=25000,
                salary_max=45000,
                experience_requirement="3-5年",
                education_requirement="本科",
                description="独立负责游戏中场景物件、功能性道具、装饰元素等3D资产的全流程制作。",
                skills="3DMax,Maya,ZBrush,Substance Painter,UE4,UE5,PBR流程,LOD优化,高模雕刻,贴图绘制,场景氛围,灯光烘焙",
                source="Boss直聘"
            ),
            Job(
                title="产品经理",
                company_name="字节跳动",
                industry="互联网",
                job_type="产品",
                location="北京",
                salary_min=20000,
                salary_max=40000,
                experience_requirement="1-3年",
                education_requirement="本科",
                description="负责产品规划和需求分析，收集整理产品需求，进行产品设计。",
                skills="需求分析,产品设计,PRD撰写,原型设计,Axure,Figma,数据分析,用户研究,竞品分析,项目管理,沟通协调,SQL",
                source="Boss直聘"
            ),
            Job(
                title="高级产品经理",
                company_name="腾讯",
                industry="互联网",
                job_type="产品",
                location="深圳",
                salary_min=30000,
                salary_max=55000,
                experience_requirement="3-5年",
                education_requirement="本科",
                description="负责产品的全生命周期管理，包括需求分析、产品设计、项目实施和运营优化。",
                skills="产品规划,商业模式,需求分析,数据分析,SQL,用户研究,A/B测试,项目管理,跨部门协作,商业洞察,PRD撰写,原型设计",
                source="拉勾网"
            ),
            Job(
                title="数据分析师",
                company_name="美团",
                industry="本地生活",
                job_type="数据",
                location="北京",
                salary_min=18000,
                salary_max=35000,
                experience_requirement="1-3年",
                education_requirement="本科",
                description="负责构建并优化企业核心业务数据指标体系，深入理解业务场景，开展专项数据分析工作。",
                skills="SQL,Python,Excel,Tableau,Power BI,数据分析,统计学,数据可视化,指标体系,数据清洗,假设检验,回归分析",
                source="Boss直聘"
            ),
            Job(
                title="高级数据分析师",
                company_name="拼多多",
                industry="电商",
                job_type="数据",
                location="上海",
                salary_min=25000,
                salary_max=45000,
                experience_requirement="3-5年",
                education_requirement="本科",
                description="负责数据驱动的业务优化项目，与产品、运营、市场等团队深度协作。",
                skills="SQL,Python,R,Tableau,Power BI,机器学习,数据建模,A/B测试,统计分析,数据挖掘,指标体系,业务洞察",
                source="拉勾网"
            ),
            Job(
                title="UI设计师",
                company_name="哔哩哔哩",
                industry="互联网",
                job_type="设计",
                location="上海",
                salary_min=15000,
                salary_max=28000,
                experience_requirement="1-3年",
                education_requirement="本科",
                description="负责公司产品UI设计模块工作，基于产品需求与设计规范编写高质量设计方案。",
                skills="Figma,Photoshop,Illustrator,Sketch,UI设计,交互设计,设计规范,视觉设计,移动端设计,Web设计,图标设计,AE动效",
                source="Boss直聘"
            ),
            Job(
                title="高级UI设计师",
                company_name="快手",
                industry="短视频",
                job_type="设计",
                location="北京",
                salary_min=22000,
                salary_max=40000,
                experience_requirement="3-5年",
                education_requirement="本科",
                description="负责Web端、移动端及多端产品的整体UI视觉设计，确保界面美观、一致且符合用户体验原则。",
                skills="Figma,Photoshop,Illustrator,AE,交互设计,视觉设计,设计规范,用户体验,动效设计,组件库,设计系统,用户研究",
                source="Boss直聘"
            ),
            Job(
                title="游戏策划",
                company_name="网易",
                industry="游戏",
                job_type="策划",
                location="杭州",
                salary_min=15000,
                salary_max=30000,
                experience_requirement="1-3年",
                education_requirement="本科",
                description="负责游戏系统设计、数值设计及关卡设计。根据游戏设定，设计游戏玩法和系统功能。",
                skills="游戏设计,数值策划,关卡设计,Excel,数据分析,文档撰写,玩家心理,系统设计,玩法设计,竞品分析",
                source="Boss直聘"
            ),
        ]
        db.add_all(jobs)
        db.commit()
        print(f"职位数据初始化完成，共{len(jobs)}条")
        
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
            print("技能分类数据初始化完成")
            
    finally:
        db.close()

if __name__ == "__main__":
    init_data()
    print("所有数据初始化完成!")
