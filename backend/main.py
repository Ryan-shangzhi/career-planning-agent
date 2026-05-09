from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, field_validator, ConfigDict
from models import Job, User, AnalysisResult, Company
from database import get_db
import json
import re


BASIC_SKILLS = {
    "前端族": ["JavaScript", "HTML", "CSS", "TypeScript"],
    "后端族": ["算法", "数据结构", "计算机网络", "操作系统", "数据库原理", "SQL"],
    "移动端族": ["Java", "Kotlin", "Swift", "算法", "数据结构"],
    "数据族": ["Python", "SQL", "算法", "统计学", "机器学习基础"],
    "产品族": ["需求分析", "产品设计", "数据分析", "项目管理", "Axure", "PRD"],
    "设计族": ["UI设计", "UX设计", "Figma", "Sketch", "Photoshop", "设计原则"]
}

PROJECT_TEMPLATES = {
    "前端族": {
        "short_term": {"description": "短期（1-3月）", "project": "基于主流框架完成1个小实战项目"},
        "medium_term": {"description": "中期（3-6月）", "project": "完成1-2个完整实战项目，深入理解核心原理"},
        "long_term": {"description": "长期（6-12月）", "project": "整理项目作品集，建立技术博客"},
        "interview_prep": {
            "medium": ["浏览器原理：事件循环、渲染流程、性能优化", "HTTP协议：TCP/UDP、HTTP2/HTTP3、缓存策略"],
            "long": [
                "📝 算法刷题：每日1-2道LeetCode，重点掌握数据结构与算法",
                "前端进阶：微前端架构、工程化、高级设计模式"
            ]
        }
    },
    "后端族": {
        "short_term": {"description": "短期（1-3月）", "project": "基于主流后端框架完成RESTful API开发"},
        "medium_term": {"description": "中期（3-6月）", "project": "完成微服务架构实战，设计并实现完整后端系统"},
        "long_term": {"description": "长期（6-12月）", "project": "完善项目文档与开源贡献，建立技术影响力"},
        "interview_prep": {
            "medium": ["计算机网络：TCP/IP协议栈、网络编程、RPC框架原理", "数据库优化：索引原理、SQL调优、缓存策略"],
            "long": [
                "📝 算法刷题：每日1-2道LeetCode，重点掌握数据结构与算法",
                "后端进阶：分布式系统、数据库深度、微服务架构"
            ]
        }
    },
    "移动端族": {
        "short_term": {"description": "短期（1-3月）", "project": "基于原生或跨端框架完成1个小App开发"},
        "medium_term": {"description": "中期（3-6月）", "project": "完成完整的移动端应用开发，包括性能优化和适配"},
        "long_term": {"description": "长期（6-12月）", "project": "上架应用商店，收集用户反馈，持续迭代优化"},
        "interview_prep": {
            "medium": ["移动端性能优化：启动速度、内存管理、流畅度", "平台特性：iOS/Android 差异化适配"],
            "long": [
                "📝 算法刷题：每日1道LeetCode，重点掌握数据结构与算法",
                "移动端进阶：架构设计、热修复、动态化技术"
            ]
        }
    },
    "数据族": {
        "short_term": {"description": "短期（1-3月）", "project": "完成数据分析小项目，熟悉数据处理流程"},
        "medium_term": {"description": "中期（3-6月）", "project": "搭建数据管道，完成数据仓库设计与实现"},
        "long_term": {"description": "长期（6-12月）", "project": "构建完整的数据平台，输出数据驱动决策报告"},
        "interview_prep": {
            "medium": ["SQL高级应用：窗口函数、复杂查询，性能优化", "Python数据分析：Pandas、NumPy实战"],
            "long": [
                "📝 算法刷题：重点掌握统计学习、机器学习算法（Kaggle竞赛）",
                "数据工程：数据湖、实时处理、深度学习基础"
            ]
        }
    },
    "产品族": {
        "short_term": {"description": "短期（1-3月）", "project": "完成1个小产品的需求分析和原型设计"},
        "medium_term": {"description": "中期（3-6月）", "project": "独立负责完整产品模块，输出PRD并跟进开发"},
        "long_term": {"description": "长期（6-12月）", "project": "规划产品路线图，管理产品迭代全流程"},
        "interview_prep": {
            "medium": ["数据分析：A/B测试、用户行为分析、转化漏斗", "需求管理：优先级评估、跨部门沟通协调"],
            "long": [
                "📊 商业分析：行业研究、竞品监控、商业模式画布",
                "产品战略：市场分析、竞品研究、用户增长策略"
            ]
        }
    },
    "设计族": {
        "short_term": {"description": "短期（1-3月）", "project": "完成1套完整的UI设计稿"},
        "medium_term": {"description": "中期（3-6月）", "project": "设计组件库，建立设计规范文档"},
        "long_term": {"description": "长期（6-12月）", "project": "设计体系化建设，建立跨产品设计标准"},
        "interview_prep": {
            "medium": ["交互设计：用户研究，信息架构、交互原型", "工具进阶：Figma高级功能、设计系统搭建"],
            "long": [
                "🎨 设计洞察：设计趋势、行业案例、设计方法论沉淀",
                "设计领导力：团队协作、设计评审，品牌一致性"
            ]
        }
    },
    "运营族": {
        "short_term": {"description": "短期（1-3月）", "project": "完成内容运营和用户增长小项目"},
        "medium_term": {"description": "中期（3-6月）", "project": "搭建运营数据分析体系，输出优化方案"},
        "long_term": {"description": "长期（6-12月）", "project": "制定运营策略，提升用户留存和转化"},
        "interview_prep": {
            "medium": ["数据分析：Excel高级应用、数据可视化", "内容运营：文案技巧、用户心理、内容策略"],
            "long": [
                "📈 增长黑客：AARRR漏斗、用户分层运营、社群裂变",
                "运营进阶：A/B测试、数据驱动运营、渠道整合"
            ]
        }
    },
    "测试族": {
        "short_term": {"description": "短期（1-3月）", "project": "完成功能测试用例设计与执行"},
        "medium_term": {"description": "中期（3-6月）", "project": "搭建自动化测试框架，覆盖核心业务场景"},
        "long_term": {"description": "长期（6-12月）", "project": "完善质量保障体系，建立CI/CD质量门禁"},
        "interview_prep": {
            "medium": ["测试用例设计：边界值、等价类、场景法", "缺陷管理：Bug跟踪、复现技巧、沟通协作"],
            "long": [
                "🔧 测试工程化：自动化框架选型、持续集成、质量度量",
                "测试进阶：性能测试、安全测试、白盒测试"
            ]
        }
    },
    "运维族": {
        "short_term": {"description": "短期（1-3月）", "project": "完成服务器部署与监控搭建"},
        "medium_term": {"description": "中期（3-6月）", "project": "实现自动化运维，完成容器化部署"},
        "long_term": {"description": "长期（6-12月）", "project": "建立运维体系，设计高可用架构"},
        "interview_prep": {
            "medium": ["Linux系统管理：Shell脚本、系统调优", "网络基础：TCP/IP、DNS、负载均衡"],
            "long": [
                "🛠️ 运维工程化：Ansible/SaltStack、监控系统、日志分析",
                "云原生进阶：Kubernetes深入、Service Mesh、可观测性"
            ]
        }
    },
    "通用": {
        "short_term": {"description": "短期（1-3月）", "project": "完成该领域1个小实战项目"},
        "medium_term": {"description": "中期（3-6月）", "project": "完成1-2个完整实战项目"},
        "long_term": {"description": "长期（6-12月）", "project": "整理项目作品集，建立专业影响力"},
        "interview_prep": {
            "medium": ["该领域核心知识点梳理", "行业案例分析与实践经验"],
            "long": [
                "📝 算法刷题：每日1-2道LeetCode（视岗位需求）",
                "该领域进阶方向探索", "个人品牌建立与行业人脉拓展"
            ]
        }
    }
}

SECONDARY_SKILLS = {
    "前端族": ["HTTP", "HTTPS", "TCP", "DOM", "浏览器原理", "HTTP协议", "计算机网络"],
    "后端族": ["HTTP协议", "Linux", "Git"],
    "移动端族": ["HTTP协议", "Git"],
    "数据族": ["Git", "Linux"],
    "产品族": ["Git", "Axure"],
    "设计族": ["Git"],
    "运营族": ["数据分析", "Excel"],
    "测试族": ["Linux", "Git"],
    "运维族": ["Shell", "Python"]
}

SKILL_PREREQUISITES = {
    "React": ["JavaScript", "TypeScript"],
    "Vue": ["JavaScript", "HTML", "CSS"],
    "Angular": ["JavaScript", "TypeScript"],
    "Next.js": ["React", "JavaScript"],
    "Nuxt.js": ["Vue", "JavaScript"],
    "TypeScript": ["JavaScript"],
    "Webpack": ["JavaScript", "Node.js"],
    "Vite": ["JavaScript"],
    "Node.js": ["JavaScript"],
    "Spring Boot": ["Java"],
    "Django": ["Python"],
    "Flask": ["Python"],
    "FastAPI": ["Python"],
    "Gin": ["Go"],
    "Express": ["JavaScript", "Node.js"],
    "Redux": ["React", "JavaScript"],
    "Vuex": ["Vue", "JavaScript"],
    "Pinia": ["Vue", "JavaScript"],
    "MySQL": ["SQL"],
    "PostgreSQL": ["SQL"],
    "MongoDB": ["JavaScript"],
    "Redis": ["SQL"],
    "Docker": ["Linux", "命令行"],
    "Kubernetes": ["Docker", "Linux"],
    "微服务": ["Java", "Spring Boot"],
    "分布式系统": ["Java", "计算机网络"],
    "Spark": ["Python", "SQL"],
    "Hadoop": ["Java", "Linux"],
    "Flutter": ["Dart"],
    "React Native": ["React", "JavaScript"],
}

HIGH_PRIORITY_FRAMEWORKS = {
    "前端族": ["React", "Vue", "Angular", "Next.js", "Nuxt.js", "ReactHooks", "Redux", "Vuex", "Pinia"],
    "后端族": ["SpringBoot", "Django", "Flask", "Gin", "Express", "FastAPI", "Spring", "SpringMVC"],
    "移动端族": ["Flutter", "ReactNative", "iOSSDK", "AndroidSDK"],
    "数据族": ["Spark", "Hadoop", "Hive", "Flink"]
}


def is_high_priority_framework(skill: str, target_family: str) -> bool:
    """检查是否为高优先级框架/工具"""
    priority_frameworks = HIGH_PRIORITY_FRAMEWORKS.get(target_family, [])
    skill_lower = skill.lower().replace(".", "").replace("-", "")
    for fw in priority_frameworks:
        fw_lower = fw.lower().replace(".", "").replace("-", "")
        if fw_lower in skill_lower or skill_lower in fw_lower:
            return True
    return False


def get_prerequisites(skill: str) -> list:
    """获取技能的前置依赖"""
    return SKILL_PREREQUISITES.get(skill, [])


def has_all_prerequisites(skill: str, user_skills: list) -> bool:
    """检查用户是否已掌握所有前置依赖"""
    prerequisites = get_prerequisites(skill)
    user_skills_lower = [s.lower() for s in user_skills]
    for prereq in prerequisites:
        prereq_lower = prereq.lower()
        if prereq_lower not in user_skills_lower:
            return False
    return True


def is_basic_skill(skill: str, target_family: str) -> bool:
    """检查是否为该岗位族的核心基础技能"""
    basic_skills = BASIC_SKILLS.get(target_family, [])
    skill_lower = skill.lower()
    for basic in basic_skills:
        if basic.lower() in skill_lower or skill_lower in basic.lower():
            return True
    return False


def is_secondary_skill(skill: str, target_family: str) -> bool:
    """检查是否为中期复习技能"""
    secondary_skills = SECONDARY_SKILLS.get(target_family, [])
    skill_lower = skill.lower()
    for sec in secondary_skills:
        if sec.lower() in skill_lower or skill_lower in sec.lower():
            return True
    return False


def calculate_learning_time(skill: str, priority_score: int, target_family: str) -> int:
    """计算技能学习时间（周）"""
    base_times = {
        "JavaScript": 4, "TypeScript": 3, "Python": 4, "Java": 6, "Go": 4,
        "React": 4, "Vue": 3, "Angular": 4, "Node.js": 4, "Spring Boot": 6,
        "HTML": 2, "CSS": 2, "SQL": 3, "Git": 1, "Docker": 2, "Kubernetes": 4,
        "算法": 8, "系统设计": 6, "计算机网络": 4, "操作系统": 4,
        "AWS": 4, "GCP": 4, "Azure": 4, "Redis": 3, "MongoDB": 3, "PostgreSQL": 3,
        "Webpack": 2, "Vite": 1, "RESTful": 1, "GraphQL": 2, "微服务": 4
    }
    
    base_time = base_times.get(skill, 4)
    
    if priority_score >= 6:
        return int(base_time * 1.2)
    elif priority_score >= 3:
        return base_time
    else:
        return int(base_time * 0.8)


def calculate_dynamic_time_estimate(
    gap_skills: List[dict], 
    target_family: str, 
    is_career_change: bool = False,
    avg_match_score: float = 50.0,
    user_experience: int = 0
) -> dict:
    """
    动态时间评估模型
    联动：待补充技能数 × 难度 × 转型系数 × 匹配度系数 × 经验系数
    返回：动态时间评估
    """
    # 计算基础学习时间
    total_time = 0
    skill_count = len(gap_skills)
    difficulty_weights = {"大": 1.5, "中": 1.0, "小": 0.7, "无": 0.3}
    
    for skill_info in gap_skills:
        skill = skill_info.get("skill", "")
        core_level = get_core_level(skill, target_family, "")
        gap_level = skill_info.get("gap", "中")
        difficulty = skill_info.get("difficulty", "中")
        
        priority_score = calculate_priority_score(core_level, gap_level)
        weeks = calculate_learning_time(skill, priority_score, target_family)
        
        # 基础技能加权
        if is_basic_skill(skill, target_family):
            weeks = int(weeks * 1.3)
        
        # 难度加权
        difficulty_weight = difficulty_weights.get(difficulty, 1.0)
        weeks = int(weeks * difficulty_weight)
        
        total_time += weeks
    
    base_months = total_time / 4 if skill_count > 0 else 2
    
    # 转型系数：跨族转型需要额外时间
    transition_multiplier = 1.0
    if is_career_change:
        transition_multiplier = 1.5
        base_months += 2
    
    # 匹配度系数：匹配度越低，需要时间越长
    match_multiplier = 1.0
    if avg_match_score < 30:
        match_multiplier = 1.5
    elif avg_match_score < 50:
        match_multiplier = 1.2
    elif avg_match_score >= 70:
        match_multiplier = 0.8
    
    # 经验系数：有经验可以缩短学习时间
    exp_multiplier = 1.0
    if user_experience >= 3:
        exp_multiplier = 0.85
    elif user_experience >= 5:
        exp_multiplier = 0.7
    
    # 综合计算
    final_months = base_months * transition_multiplier * match_multiplier * exp_multiplier
    
    # 确定时间范围
    if final_months <= 4:
        time_range = "2-4个月"
        estimated_months = 3
    elif final_months <= 8:
        time_range = "4-8个月"
        estimated_months = 6
    elif final_months <= 14:
        time_range = "6-12个月"
        estimated_months = 12
    elif final_months <= 24:
        time_range = "12-18个月"
        estimated_months = 18
    else:
        time_range = "18-24个月"
        estimated_months = 24
    
    # 生成推理说明
    factors = []
    if is_career_change:
        factors.append("跨族转型")
    if avg_match_score < 50:
        factors.append("匹配度偏低")
    if user_experience == 0:
        factors.append("无工作经验")
    elif user_experience >= 3:
        factors.append(f"有{user_experience}年经验")
    
    reasoning_parts = [f"基于{skill_count}项技能差距"]
    if factors:
        reasoning_parts.append(f"考虑因素：{', '.join(factors)}")
    reasoning_parts.append(f"计算预估：{final_months:.1f}个月")
    
    return {
        "time_range": time_range,
        "estimated_months": estimated_months,
        "total_weeks": total_time,
        "base_months": round(base_months, 1),
        "final_months": round(final_months, 1),
        "match_factor": match_multiplier,
        "transition_factor": transition_multiplier,
        "experience_factor": exp_multiplier,
        "reasoning": " | ".join(reasoning_parts)
    }


def analyze_target_feasibility(
    total_jobs: int,
    high_match_jobs: int,
    user_skills: List[str],
    target_family: str,
    target_job: str
) -> dict:
    """
    目标合理性校验
    如果0个岗位匹配度>60%，应提示"目标过高，建议调整"
    """
    match_rate = (high_match_jobs / total_jobs * 100) if total_jobs > 0 else 0
    
    max_match_score = 0
    if total_jobs > 0:
        for job in range(min(10, total_jobs)):
            simulated_score = max(20, 80 - job * 5)
            max_match_score = max(max_match_score, simulated_score)
    
    warnings = []
    suggestions = []
    feasibility_score = 50
    
    if high_match_jobs == 0:
        warnings.append({
            "type": "danger",
            "message": f"在{total_jobs}个{target_family}岗位中，没有岗位匹配度超过60%",
            "detail": "当前目标岗位可能超出您的实际能力范围，建议调整预期"
        })
        suggestions.append("考虑降低目标岗位级别（如从高级降至中级）")
        suggestions.append("优先补充核心基础技能，夯实基础后再挑战高级岗位")
        feasibility_score = 20
    elif high_match_jobs < total_jobs * 0.2:
        warnings.append({
            "type": "warning",
            "message": f"仅{high_match_jobs}/{total_jobs}个岗位匹配度超过60%",
            "detail": "目标有一定挑战性，需要针对性地提升技能"
        })
        suggestions.append("聚焦核心技能差距，优先突破高频考点")
        feasibility_score = 50
    else:
        feasibility_score = 75
        if max_match_score >= 70:
            warnings.append({
                "type": "success",
                "message": f"有{high_match_jobs}个岗位匹配度超过60%，目标合理",
                "detail": "您的技能组合与市场需求契合度较高"
            })
    
    if user_skills:
        skill_count = len(user_skills)
        if skill_count < 3:
            suggestions.append("技能描述较少，建议补充更多具体技能以获得更准确的分析")
            feasibility_score = min(feasibility_score, 40)
        elif skill_count < 5:
            suggestions.append("可以补充更多工具和框架类技能，丰富您的技能画像")
    
    if target_family in ["前端族", "后端族", "移动端族"]:
        basic_indicators = ["javascript", "java", "python", "html", "css", "sql"]
        has_basic = any(indicator in " ".join(user_skills).lower() for indicator in basic_indicators)
        if not has_basic and feasibility_score < 60:
            suggestions.append(f"{target_family}岗位通常需要掌握编程基础，建议从基础开始学习")
    
    return {
        "feasibility_score": feasibility_score,
        "is_reasonable": high_match_jobs > 0,
        "high_match_count": high_match_jobs,
        "total_analyzed": total_jobs,
        "match_rate": round(match_rate, 1),
        "warnings": warnings,
        "suggestions": suggestions,
        "recommendation": "立即行动" if feasibility_score >= 60 else "调整目标" if feasibility_score >= 40 else "重新规划"
    }


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
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


TYPO_CORRECTIONS = {
    "前段": "前端", "前断": "前端", "前瑞": "前端", "前踹": "前端",
    "后段": "后端", "后断": "后端", "后踹": "后端",
    "全站": "全栈", "全占": "全栈",
    "web": "Web", "Web开发": "前端", "web开发": "前端",
    "Andriod": "Android", "andriod": "android",
    "Ios": "iOS", "ios": "iOS",
}

def extract_skills_from_text(text: str) -> list:
    """
    从完整文本中提取技能关键词
    支持从"Vue和React"、"会用Vue"等自然语言中提取
    """
    all_skill_names = []
    for skills_dict in SKILL_MAPPING.values():
        for category_skills in skills_dict.values():
            all_skill_names.extend([s.lower() for s in category_skills])
    
    found_skills = []
    text_lower = text.lower()
    
    framework_keywords = ['react', 'vue', 'angular', 'next.js', 'nuxt.js', 'uniapp', 'taro', 'flutter', 'spring', 'django', 'flask', 'fastapi', 'gin', 'express']
    core_keywords = ['javascript', 'typescript', 'python', 'java', 'go', 'golang', 'c++', 'rust', 'php', 'ruby', 'swift', 'kotlin', 'dart', 'html', 'css', 'sql']
    tooling_keywords = ['webpack', 'vite', 'eslint', 'prettier', 'git', 'docker', 'jenkins', 'ci/cd', 'cicd', 'nginx', 'linux', 'k8s', 'kubernetes', 'node.js']
    
    all_keywords = list(set(framework_keywords + core_keywords + tooling_keywords))
    
    for keyword in all_keywords:
        if keyword in text_lower:
            found_skills.append(keyword)
    
    return found_skills


def normalize_input(text: str) -> list:
    """
    标准化用户输入：纠错→分词→去重→小写
    增强版：使用分隔符+关键词提取双重策略
    """
    corrected = text
    for typo, correct in TYPO_CORRECTIONS.items():
        if typo.lower() in corrected.lower():
            corrected = corrected.lower().replace(typo.lower(), correct.lower())
    
    separators = r'[，,、/\\\s和与及跟用会或]+'
    tokens = re.split(separators, corrected)
    
    cleaned_tokens = [t.strip() for t in tokens if t.strip() and len(t.strip()) >= 2]
    
    extracted = extract_skills_from_text(text)
    all_tokens = list(set(cleaned_tokens + extracted))
    
    return [t for t in all_tokens if t]


def fuzzy_match_title(title: str) -> tuple[str, str, float]:
    """
    模糊匹配岗位名称
    返回：(匹配到的岗位族, 匹配的关键词, 匹配置信度)
    名称匹配权重最高
    """
    normalized_tokens = normalize_input(title)
    title_lower = title.lower()
    
    for family, keywords in JOB_FAMILY_MAPPING.items():
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in title_lower:
                return family, keyword, 1.0
            if keyword_lower in normalized_tokens:
                return family, keyword, 0.95
    
    if "前端" in title.lower() or "web" in title_lower:
        return "前端族", "前端", 0.9
    if "后端" in title.lower() or "java" in title_lower or "python" in title_lower or "go" in title_lower:
        return "后端族", "后端", 0.9
    if "移动" in title.lower() or "ios" in title_lower or "android" in title_lower or "flutter" in title_lower:
        return "移动端族", "移动", 0.9
    if "数据" in title.lower() or "算法" in title.lower() or "ml" in title_lower or "ai" in title_lower:
        return "数据族", "数据", 0.9
    if "产品" in title.lower() or "经理" in title.lower():
        return "产品族", "产品", 0.9
    if "ui" in title_lower or "ux" in title_lower or "设计" in title.lower():
        return "设计族", "设计", 0.9
    if "运营" in title.lower():
        return "运营族", "运营", 0.9
    if "测试" in title.lower() or "qa" in title_lower:
        return "测试族", "测试", 0.9
    if "运维" in title.lower() or "dba" in title_lower:
        return "运维族", "运维", 0.9
    
    return "", "", 0.0

def determine_job_family(job_title: str, skills: List[str] = None) -> str:
    """
    根据岗位名称和技能判定岗位族
    优先根据岗位名称判定，名称权重高于技能
    """
    if not job_title:
        return ""
    
    matched_family, matched_keyword, confidence = fuzzy_match_title(job_title)
    
    if matched_family and confidence >= 0.9:
        return matched_family
    
    if skills:
        skill_matches = {}
        for family, indicators in JOB_FAMILY_SKILL_INDICATORS.items():
            count = 0
            for skill in skills:
                skill_lower = skill.lower()
                if any(indicator in skill_lower for indicator in indicators):
                    count += 1
            if count > 0:
                skill_matches[family] = count
        
        if skill_matches:
            return max(skill_matches, key=skill_matches.get)
    
    return matched_family

SKILL_MAPPING = {
    "前端族": {
        "core": ["JavaScript", "TypeScript", "HTML5", "CSS3"],
        "framework": ["React", "Vue", "Angular", "Next.js", "Nuxt.js", "UniApp", "Taro"],
        "tools": ["Webpack", "Vite", "ESLint", "Git", "Tailwind CSS"],
        "concepts": ["组件化开发", "状态管理", "性能优化", "响应式设计", "跨浏览器兼容"]
    },
    "后端族": {
        "core": ["Java", "Python", "Go", "C++", "Node.js", "PHP"],
        "framework": ["Spring Boot", "Django", "Flask", "Gin", "Express", "FastAPI"],
        "database": ["MySQL", "PostgreSQL", "MongoDB", "Redis"],
        "tools": ["Docker", "Kubernetes", "Git", "Linux", "Nginx"],
        "concepts": ["微服务", "分布式系统", "高并发", "消息队列", "缓存", "API设计"]
    },
    "移动端族": {
        "core": ["Swift", "Objective-C", "Kotlin", "Java", "Dart"],
        "framework": ["Flutter", "React Native", "iOS SDK", "Android SDK"],
        "tools": ["Xcode", "Android Studio", "CocoaPods", "Gradle"],
        "concepts": ["原生开发", "跨平台开发", "性能优化", "应用上架"]
    },
    "数据族": {
        "core": ["SQL", "Python", "R", "Java", "Scala"],
        "tools": ["Excel", "Tableau", "Power BI", "Jupyter", "Spark", "Hadoop"],
        "concepts": ["数据分析", "统计学", "数据可视化", "机器学习", "数据仓库", "ETL"]
    },
    "产品族": {
        "core": ["需求分析", "产品设计", "PRD撰写", "原型设计"],
        "tools": ["Axure", "Figma", "XMind", "Visio", "Jira"],
        "concepts": ["用户研究", "竞品分析", "数据分析", "项目管理", "A/B测试", "商业模式"]
    },
    "设计族": {
        "core": ["Figma", "Sketch", "Adobe XD", "Photoshop", "Illustrator"],
        "tools": ["After Effects", "Principle", "Zeplin"],
        "concepts": ["UI设计", "UX设计", "交互设计", "视觉设计", "设计规范", "用户体验"]
    },
}

SKILL_ALIASES = {
    "js": "JavaScript",
    "ts": "TypeScript",
    "vuejs": "Vue",
    "vue.js": "Vue",
    "reactjs": "React",
    "react.js": "React",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "nuxtjs": "Nuxt.js",
    "nuxt.js": "Nuxt.js",
    "typescript": "TypeScript",
    "javascript": "JavaScript",
    "html5": "HTML5",
    "html": "HTML",
    "css3": "CSS3",
    "css": "CSS",
    "es6": "ES6",
    "es2015": "ES6",
    "webpack": "Webpack",
    "vite": "Vite",
    "eslint": "ESLint",
    "git": "Git",
    "github": "Git",
    "docker": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "jenkins": "Jenkins",
    "nginx": "Nginx",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "aws": "AWS",
    "gcp": "GCP",
    "azure": "Azure",
    "springboot": "Spring Boot",
    "spring boot": "Spring Boot",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "gin": "Gin",
    "express": "Express",
    "flutter": "Flutter",
    "rn": "React Native",
    "reactnative": "React Native",
    "ios": "iOS",
    "android": "Android",
    "swift": "Swift",
    "kotlin": "Kotlin",
    "python": "Python",
    "java": "Java",
    "go": "Go",
    "golang": "Go",
    "c++": "C++",
    "cpp": "C++",
    "rust": "Rust",
    "php": "PHP",
    "ruby": "Ruby",
    "sql": "SQL",
    "graphql": "GraphQL",
    "restful": "RESTful",
    "grpc": "gRPC",
    "websocket": "WebSocket",
    "微服务": "微服务",
    "分布式": "分布式",
    "高并发": "高并发",
    "devops": "DevOps",
    "tdd": "TDD",
    "单元测试": "单元测试",
}

JOB_FAMILY_MAPPING = {
    "前端族": [
        "前端", "前端工程师", "web开发", "web开发工程师", "全栈", "全栈工程师",
        "小程序", "小程序开发", "小程序开发工程师", "h5开发", "h5开发工程师",
        "跨端", "跨端开发", "跨端开发工程师", "uniapp", "taro", "前端架构师"
    ],
    "后端族": [
        "后端", "后端工程师", "java", "java工程师", "go", "go工程师", "golang",
        "python", "python工程师", "php", "php工程师", "node", "node.js",
        "devops", "devops工程师", "sre", "sre工程师", "云原生", "云原生工程师",
        "服务端", "服务端开发", "后端架构师"
    ],
    "移动端族": [
        "ios", "ios工程师", "android", "android工程师", "移动端", "移动端开发",
        "移动端开发工程师", "flutter", "react native", "rn", "移动端架构师"
    ],
    "数据族": [
        "数据", "数据分析", "数据分析工程师", "数据开发", "数据开发工程师",
        "算法", "算法工程师", "bi", "bi工程师", "数据仓库", "数据仓库工程师",
        "数据挖掘", "数据挖掘工程师", "机器学习", "ml工程师", "ai工程师"
    ],
    "产品族": [
        "产品", "产品经理", "产品运营", "项目管理", "项目经理", "商业化",
        "商业化运营", "产品策划", "产品总监", "产品助理"
    ],
    "设计族": [
        "ui", "ui设计", "ui设计师", "ux", "ux设计", "ux设计师", "交互",
        "交互设计", "交互设计师", "视觉", "视觉设计", "视觉设计师", "设计总监"
    ],
    "运营族": [
        "运营", "运营专员", "运营经理", "内容运营", "用户运营", "活动运营",
        "电商运营", "新媒体运营", "社群运营", "增长运营", "数据运营",
        "渠道运营", "产品运营", "运营总监"
    ],
    "测试族": [
        "测试", "测试工程师", "qa", "qc", "自动化测试", "性能测试",
        "安全测试", "测试开发", "测试经理"
    ],
    "运维族": [
        "运维", "运维工程师", "sre", "系统运维", "网络运维", "dba",
        "数据库管理员", "运维开发", "devops"
    ]
}

def normalize_skill(skill: str) -> str:
    """规范化技能名称"""
    skill_lower = skill.lower().strip()
    return SKILL_ALIASES.get(skill_lower, skill)

def is_valid_skill(token: str) -> bool:
    """
    检查分词结果是否是有效技能
    过滤掉垃圾词如"react通"
    """
    invalid_suffixes = ['通', '会', '用', '会', '熟悉', '掌握', '了解', '学过', '用过']
    token_lower = token.lower()
    
    for suffix in invalid_suffixes:
        if token_lower.endswith(suffix) and len(token) < 8:
            return False
    
    return len(token) >= 2


def parse_user_skills(user_skills: List[str], user_experience: int = 0) -> dict:
    """
    解析用户输入的技能列表
    返回：{
        'normalized': [规范化的技能列表],
        'skill_levels': {技能名: 熟练度},
        'has_tooling': [工程化工具列表],
        'has_frameworks': [框架列表],
        'has_core': [核心语言列表],
        'implied_skills': [隐含技能列表],
        'universal_patterns': [{'frameworks': [], 'proficiency': '熟练'}],
    }
    """
    result = {
        'normalized': [],
        'skill_levels': {},
        'user_input_skills': {},  # 只记录用户实际输入的技能
        'has_tooling': [],
        'has_frameworks': [],
        'has_core': [],
        'implied_skills': [],
        'universal_patterns': [],  # 新增
    }
    
    tooling_keywords = ['webpack', 'vite', 'eslint', 'prettier', 'git', 'docker', 'jenkins', 'ci/cd', 'cicd', 'nginx', 'linux', 'k8s', 'kubernetes']
    framework_keywords = ['react', 'vue', 'angular', 'next.js', 'nuxt.js', 'uniapp', 'taro', 'flutter', 'react native', 'spring', 'django', 'flask', 'fastapi', 'gin', 'express', 'spring boot', 'springboot']
    core_keywords = ['javascript', 'typescript', 'python', 'java', 'go', 'golang', 'c++', 'rust', 'php', 'ruby', 'swift', 'kotlin', 'dart', 'html', 'css', 'sql']
    
    FRAMEWORK_IMPLIES_CORE = {
        'react': ['javascript', 'typescript'],
        'vue': ['javascript', 'typescript'],
        'angular': ['typescript'],
        'next.js': ['javascript', 'react', 'typescript'],
        'nuxt.js': ['javascript', 'vue', 'typescript'],
        'flutter': ['dart'],
        'react native': ['javascript', 'typescript'],
        'spring': ['java'],
        'django': ['python'],
        'flask': ['python'],
        'fastapi': ['python'],
        'gin': ['go'],
        'express': ['javascript', 'node.js'],
        'spring boot': ['java'],
    }
    
    proficiency_boost_keywords = ['通用', '熟练', '精通', '掌握', '主力']
    
    # 处理"通用"模式：如 "Vue和React通用" → 提取两个框架
    universal_keywords = ['通用']
    universal_patterns = []
    
    for skill in user_skills:
        skill_lower = skill.lower()
        # 检查是否包含"通用"关键词
        if any(uk in skill_lower for uk in universal_keywords):
            # 提取所有框架
            found_frameworks = []
            for fw in framework_keywords:
                if fw in skill_lower:
                    found_frameworks.append(fw)
            
            if found_frameworks:
                # 确定熟练度
                prof = '熟练'
                if '精通' in skill or 'master' in skill_lower:
                    prof = '精通'
                elif '了解' in skill or '会用' in skill_lower:
                    prof = '了解'
                
                universal_patterns.append({
                    'frameworks': found_frameworks,
                    'proficiency': prof
                })
    
    result['universal_patterns'] = universal_patterns
    
    for skill in user_skills:
        tokens = normalize_input(skill)
        
        has_proficiency_boost = any(boost in skill for boost in proficiency_boost_keywords)
        
        for token in tokens:
            if not is_valid_skill(token):
                continue
                
            normalized = normalize_skill(token)
            if normalized and normalized not in result['normalized']:
                result['normalized'].append(normalized)
                
                skill_lower = normalized.lower()
                is_framework = any(fk in skill_lower for fk in framework_keywords)
                
                if is_framework and has_proficiency_boost:
                    if 'proficient_frameworks' not in result:
                        result['proficient_frameworks'] = []
                    result['proficient_frameworks'].append(normalized)
                
                if any(tk in skill_lower for tk in tooling_keywords):
                    result['has_tooling'].append(normalized)
                if is_framework:
                    result['has_frameworks'].append(normalized)
                if any(ck in skill_lower for ck in core_keywords):
                    result['has_core'].append(normalized)
                
                for fw, implied_cores in FRAMEWORK_IMPLIES_CORE.items():
                    if fw in skill_lower:
                        for implied in implied_cores:
                            if implied not in result['has_core'] and implied not in result['implied_skills']:
                                result['implied_skills'].append(implied)
                            if has_proficiency_boost and implied not in result['has_core']:
                                if 'proficient_skills' not in result:
                                    result['proficient_skills'] = []
                                if implied not in result['proficient_skills']:
                                    result['proficient_skills'].append(implied)
                
                proficiency_keywords = {
                    '精通': '精通', 'master': '精通',
                    '熟练': '熟练', 'proficient': '熟练',
                    '掌握': '熟练',
                    '了解': '了解', '熟悉': '了解', 'knowledge': '了解',
                    '入门': '入门', '会用': '入门',
                }
                user_level = '熟练'
                for kw, level in proficiency_keywords.items():
                    if kw in skill:
                        user_level = level
                        break
                
                result['skill_levels'][normalized] = user_level
                result['user_input_skills'][normalized] = user_level
    
    result['skill_domains'] = []
    for domain, tools in TOOL_TO_SKILL_DOMAIN.items():
        for normalized_skill in result['normalized']:
            skill_lower = normalized_skill.lower()
            for tool in tools:
                if tool in skill_lower or skill_lower in tool:
                    if domain not in result['skill_domains']:
                        result['skill_domains'].append(domain)
                    break

    # 基于工作年限的基线熟练度（前端族）
    EXPERIENCE_BASELINE = {
        5: {  # 5年+
            'javascript': '熟练', 'typescript': '熟练', 'js': '熟练', 'ts': '熟练',
            'html': '熟练', 'css': '了解',
            'http': '了解', 'http协议': '了解', '浏览器': '了解',
            'react': '熟练', 'vue': '熟练', 'angular': '了解',
            'webpack': '熟练', 'vite': '熟练', 'eslint': '了解', 'git': '熟练',
            'node.js': '了解', 'nodejs': '了解',
        },
        3: {  # 3-5年
            'javascript': '了解', 'typescript': '了解', 'js': '了解', 'ts': '了解',
            'html': '了解', 'css': '了解',
            'http': '了解', 'http协议': '了解', '浏览器': '了解',
            'react': '熟练', 'vue': '熟练', 'angular': '入门',
            'webpack': '了解', 'vite': '了解', 'eslint': '入门', 'git': '了解',
            'node.js': '入门', 'nodejs': '入门',
        },
        1: {  # 1-3年
            'javascript': '了解', 'typescript': '入门', 'js': '了解', 'ts': '入门',
            'html': '了解', 'css': '了解',
            'http': '入门', 'http协议': '入门', '浏览器': '入门',
            'react': '了解', 'vue': '了解', 'angular': '入门',
            'webpack': '入门', 'vite': '入门', 'eslint': '入门', 'git': '入门',
            'node.js': '入门', 'nodejs': '入门',
        },
    }

    LEVEL_PRIORITY = {'精通': 3, '熟练': 2, '了解': 1, '入门': 0}

    def get_higher_level(level1: str, level2: str) -> str:
        """取较高熟练度"""
        p1 = LEVEL_PRIORITY.get(level1, -1)
        p2 = LEVEL_PRIORITY.get(level2, -1)
        return level1 if p1 >= p2 else level2

    # 获取对应年限的基线
    exp_years = user_experience or 0
    baseline = {}
    if exp_years >= 5:
        baseline = EXPERIENCE_BASELINE[5]
    elif exp_years >= 3:
        baseline = EXPERIENCE_BASELINE[3]
    elif exp_years >= 1:
        baseline = EXPERIENCE_BASELINE[1]

    # 填充 skill_levels：结合用户自评和年限基线
    for skill_name, user_level in result.get('skill_levels', {}).items():
        skill_lower = skill_name.lower()
        baseline_level = baseline.get(skill_lower, '不了解')
        result['skill_levels'][skill_name] = get_higher_level(user_level, baseline_level)

    # 补充基线中有的但用户没填写的技能（框架技能强制根据年限基线填充）
    for skill_name, baseline_level in baseline.items():
        skill_name_lower = skill_name.lower()
        if skill_name_lower in ['react', 'vue', 'angular', 'webpack', 'vite', 'eslint']:
            if skill_name not in result['skill_levels']:
                result['skill_levels'][skill_name] = baseline_level
        else:
            skill_name_cap = skill_name.title()
            if skill_name_cap not in result['skill_levels']:
                result['skill_levels'][skill_name_cap] = baseline_level

    result = validate_parsed_skills(result, user_skills)

    return result


def validate_parsed_skills(parsed: dict, original_input: List[str]) -> dict:
    """
    条件触发的技能映射校验
    仅当输入含多框架暗示词（和/与/都/通用/两者/两个）时，校验通用模式必须包含≥2个框架
    """
    universal_keywords = ['和', '与', '都', '通用', '两者', '两个']
    
    # 检查原始输入是否包含多框架暗示词
    has_universal_hint = False
    for skill in original_input:
        skill_lower = skill.lower()
        if any(keyword in skill_lower for keyword in universal_keywords):
            has_universal_hint = True
            break
    
    # 仅在包含暗示词时才校验
    if has_universal_hint and parsed.get('universal_patterns'):
        for pattern in parsed.get('universal_patterns', []):
            frameworks = pattern.get('frameworks', [])
            if len(frameworks) < 2:
                # 尝试从原始输入中提取更多框架
                for skill in original_input:
                    skill_lower = skill.lower()
                    # 检查是否包含多个框架
                    found = []
                    framework_keywords = ['react', 'vue', 'angular', 'next.js', 'nuxt.js', 'svelte', 'flutter', 'spring', 'django', 'flask']
                    for fw in framework_keywords:
                        if fw in skill_lower:
                            found.append(fw)
                    if len(found) >= 2:
                        # 找到了多个框架，更新模式
                        pattern['frameworks'] = found
                        # 同时更新 has_frameworks 和 proficient_frameworks
                        for fw in found:
                            if fw not in parsed.get('has_frameworks', []):
                                parsed['has_frameworks'].append(fw)
                            if fw not in parsed.get('proficient_frameworks', []):
                                if 'proficient_frameworks' not in parsed:
                                    parsed['proficient_frameworks'] = []
                                parsed['proficient_frameworks'].append(fw)
                        break
    
    return parsed


JOB_FAMILY_SKILL_INDICATORS = {
    "前端族": ["javascript", "typescript", "react", "vue", "html", "css", "webpack", "vite", "uniapp", "taro"],
    "后端族": ["java", "python", "go", "spring", "django", "flask", "node.js", "mysql", "redis", "kafka"],
    "移动端族": ["swift", "kotlin", "flutter", "react native", "ios", "android"],
    "数据族": ["sql", "python", "r", "tableau", "spark", "hadoop", "机器学习", "算法"],
    "产品族": ["产品", "需求", "原型", "axure", "figma", "prd", "项目管理"],
    "设计族": ["figma", "sketch", "ui", "ux", "交互", "视觉", "photoshop", "illustrator"],
    "运营族": ["运营", "内容", "用户", "活动", "增长", "社群", "电商", "新媒体"],
    "测试族": ["测试", "qa", "自动化", "性能测试", "安全测试", "测试用例"],
    "运维族": ["运维", "linux", "docker", "k8s", "ansible", "监控", "shell"]
}

TOOL_TO_SKILL_DOMAIN = {
    "前端工程化": ["webpack", "vite", "eslint", "prettier", "babel", "rollup", "parcel", "ci/cd", "cicd", "jenkins", "gulp", "grunt"],
    "框架能力": ["react", "vue", "angular", "next.js", "nuxt.js", "svelte", "solid", "remix"],
    "语言基础": ["javascript", "typescript", "js", "ts", "es6", "es2015", "esnext"],
    "样式能力": ["css", "css3", "sass", "scss", "less", "stylus", "tailwind", "tailwindcss", "postcss"],
    "状态管理": ["redux", "vuex", "pinia", "mobx", "zustand", "recoil", "jotai"],
    "测试能力": ["jest", "vitest", "cypress", "testing library", "mocha", "chai", "enzyme"],
    "服务端能力": ["node.js", "nodejs", "express", "koa", "nest", "fastify", "next.js api"],
    "构建部署": ["docker", "k8s", "kubernetes", "nginx", "linux", "jenkins", "github actions", "gitlab ci"],
    "版本控制": ["git", "github", "gitlab", "svn", "bitbucket"],
    "数据库能力": ["mysql", "postgresql", "mongodb", "redis", "sqlite", "prisma", "typeorm", "sequelize"],
}

TARGET_JOB_SKILL_MAPS = {
    "前端族": {
        "初级前端工程师": {
            "精通": ["HTML/CSS", "JavaScript", "React", "Vue", "Git"],
            "熟练": ["TypeScript", "Webpack/Vite", "HTTP协议", "响应式设计"],
            "了解": ["Node.js", "性能优化基础", "前端测试"]
        },
        "中级前端工程师": {
            "精通": ["JavaScript深度", "React/Vue深入", "TypeScript", "前端工程化", "性能优化"],
            "熟练": ["Node.js", "微前端", "状态管理", "浏览器原理", "HTTP2"],
            "了解": ["SSR", "WebGL", "Flutter"]
        },
        "高级前端工程师": {
            "精通": ["JavaScript/TypeScript深度", "React技术栈", "前端工程化", "性能优化体系", "浏览器原理", "HTTP/网络协议"],
            "熟练": ["Node.js服务端", "微前端架构", "状态管理方案设计", "组件设计模式", "算法与数据结构"],
            "了解": ["跨端开发", "WebGL/3D可视化", "CI/CD", "前端监控", "低代码平台"]
        }
    },
    "后端族": {
        "初级后端工程师": {
            "精通": ["Java/Python/Go", "SQL", "Git"],
            "熟练": ["Spring Boot/Django", "Redis", "HTTP协议", "RESTful API"],
            "了解": ["微服务", "消息队列", "容器基础"]
        },
        "中级后端工程师": {
            "精通": ["Java/Python/Go深度", "数据库设计", "缓存系统", "微服务架构"],
            "熟练": ["分布式系统", "消息队列", "容器编排", "性能调优"],
            "了解": ["大数据处理", "机器学习基础"]
        },
        "高级后端工程师": {
            "精通": ["高性能架构设计", "分布式系统", "数据库深度", "缓存架构", "消息队列"],
            "熟练": ["云原生架构", "服务网格", "稳定性保障", "性能优化"],
            "了解": ["大数据架构", "AI系统工程"]
        }
    },
    "移动端族": {
        "初级移动端工程师": {
            "精通": ["iOS/Android SDK", "Swift/Kotlin/Java"],
            "熟练": ["Flutter/React Native", "网络编程", "本地存储"],
            "了解": ["性能优化", "上架流程"]
        },
        "中级移动端工程师": {
            "精通": ["原生开发深度", "跨平台框架", "性能优化", "架构设计"],
            "熟练": ["热更新", "动态化", "安全加固"],
            "了解": ["AR/VR", "AI集成"]
        },
        "高级移动端工程师": {
            "精通": ["移动架构设计", "性能优化体系", "安全体系", "跨平台深度"],
            "熟练": ["端智能", "AR/VR开发", "底层原理"],
            "了解": ["操作系统内核", "编译器"]
        }
    },
    "数据族": {
        "初级数据分析师": {
            "精通": ["SQL", "Python", "Excel"],
            "熟练": ["Pandas/NumPy", "数据可视化", "统计学基础"],
            "了解": ["机器学习基础", "Spark"]
        },
        "中级数据分析师": {
            "精通": ["Python数据分析", "SQL高级应用", "数据可视化"],
            "熟练": ["机器学习", "Spark/Hadoop", "数据管道"],
            "了解": ["深度学习", "实时处理"]
        },
        "高级数据工程师": {
            "精通": ["数据仓库设计", "大规模数据处理", "Spark/Flink"],
            "熟练": ["机器学习平台", "数据治理", "数据质量"],
            "了解": ["MLOps", "AI系统工程"]
        }
    },
    "产品族": {
        "初级产品经理": {
            "精通": ["需求分析", "PRD撰写", "原型设计"],
            "熟练": ["Axure/Figma", "项目管理", "数据分析基础"],
            "了解": ["用户研究", "竞品分析"]
        },
        "中级产品经理": {
            "精通": ["产品设计", "数据分析", "跨部门协调"],
            "熟练": ["A/B测试", "用户增长", "产品迭代"],
            "了解": ["商业分析", "商业模式"]
        },
        "高级产品经理": {
            "精通": ["产品战略", "市场分析", "团队管理"],
            "熟练": ["商业模式设计", "竞品研究", "数据驱动决策"],
            "了解": ["行业洞察", "创新方法论"]
        }
    },
    "设计族": {
        "初级UI设计师": {
            "精通": ["Figma", "Sketch", "PS/AI"],
            "熟练": ["UI设计规范", "响应式设计", "交互动效基础"],
            "了解": ["用户体验基础", "设计系统"]
        },
        "中级UI设计师": {
            "精通": ["设计系统", "品牌设计", "动效设计"],
            "熟练": ["用户研究", "设计方法论", "设计评审"],
            "了解": ["设计领导力", "团队协作"]
        },
        "高级设计专家": {
            "精通": ["设计战略", "设计体系", "品牌一致性"],
            "熟练": ["设计思维", "跨团队协作", "设计度量"],
            "了解": ["创新设计", "设计研究"]
        }
    },
    "运营族": {
        "初级运营专员": {
            "精通": ["内容运营", "用户运营", "数据分析基础"],
            "熟练": ["活动策划", "社群运营", "Excel数据处理"],
            "了解": ["用户增长基础", "内容策略"]
        },
        "中级运营经理": {
            "精通": ["数据分析", "用户增长", "活动策划"],
            "熟练": ["A/B测试", "转化优化", "渠道整合"],
            "了解": ["增长黑客", "商业变现"]
        },
        "高级运营总监": {
            "精通": ["运营策略", "数据驱动", "团队管理"],
            "熟练": ["商业模式", "市场拓展", "资源整合"],
            "了解": ["行业洞察", "战略规划"]
        }
    },
    "测试族": {
        "初级测试工程师": {
            "精通": ["测试用例设计", "Bug跟踪", "功能测试"],
            "熟练": ["Selenium/Appium", "接口测试", "Linux基础"],
            "了解": ["自动化测试", "性能测试基础"]
        },
        "中级测试工程师": {
            "精通": ["自动化框架", "持续集成", "接口测试"],
            "熟练": ["性能测试", "安全测试", "测试工具开发"],
            "了解": ["测试架构", "质量度量"]
        },
        "高级测试专家": {
            "精通": ["测试策略", "质量体系", "测试架构"],
            "熟练": ["测试平台开发", "DevOps质量", "测试度量"],
            "了解": ["AI测试", "测试左移右移"]
        }
    },
    "运维族": {
        "初级运维工程师": {
            "精通": ["Linux", "Shell脚本", "Nginx部署"],
            "熟练": ["Docker基础", "监控告警", "日志分析"],
            "了解": ["Kubernetes基础", "自动化运维"]
        },
        "中级运维工程师": {
            "精通": ["Kubernetes", "Docker编排", "监控体系"],
            "熟练": ["Ansible/SaltStack", "CI/CD", "日志分析"],
            "了解": ["Service Mesh", "可观测性"]
        },
        "高级运维架构师": {
            "精通": ["云原生架构", "高可用设计", "自动化运维"],
            "熟练": ["Kubernetes深入", "Service Mesh", "成本优化"],
            "了解": ["混沌工程", "SRE实践"]
        }
    }
}

GAP_EVALUATION_MATRIX = {
    ("精通", "精通"): {"gap": "无", "level": "精通"},
    ("精通", "熟练"): {"gap": "小", "level": "熟练"},
    ("精通", "了解"): {"gap": "中", "level": "了解"},
    ("精通", "不了解"): {"gap": "大", "level": "不了解"},
    ("熟练", "精通"): {"gap": "无", "level": "精通"},
    ("熟练", "熟练"): {"gap": "无", "level": "熟练"},
    ("熟练", "了解"): {"gap": "小", "level": "了解"},
    ("熟练", "不了解"): {"gap": "中", "level": "不了解"},
    ("了解", "精通"): {"gap": "无", "level": "精通"},
    ("了解", "熟练"): {"gap": "无", "level": "熟练"},
    ("了解", "了解"): {"gap": "无", "level": "了解"},
    ("了解", "不了解"): {"gap": "小", "level": "不了解"},
}

GAP_DIFFICULTY_RULES = {
    "小": ["同类技能迁移", "工具层面切换", "框架迁移基础"],
    "中": ["需新学但逻辑体系相近", "有基础可迁移", "工程化深入"],
    "大": ["跨知识体系", "需从零建立认知框架", "架构能力提升"]
}

def get_target_level_skill_map(job_family: str, job_title: str) -> dict:
    """获取目标岗位的技能图谱"""
    if job_family not in TARGET_JOB_SKILL_MAPS:
        return {}
    
    family_map = TARGET_JOB_SKILL_MAPS[job_family]
    
    job_title_lower = job_title.lower()
    for level_key, skill_map in family_map.items():
        if level_key.lower() in job_title_lower:
            return skill_map
    
    if "高级" in job_title or "资深" in job_title or "专家" in job_title:
        for level_key in family_map.keys():
            if "高级" in level_key:
                return family_map[level_key]
    elif "中级" in job_title:
        for level_key in family_map.keys():
            if "中级" in level_key:
                return family_map[level_key]
    
    for level_key in family_map.keys():
        if "初级" in level_key:
            return family_map[level_key]
    
    return {}

def evaluate_gap(target_level: str, user_level: str) -> dict:
    """评估技能差距"""
    return GAP_EVALUATION_MATRIX.get((target_level, user_level), {"gap": "大", "level": "不了解"})

def determine_gap_difficulty(target_skill: str, target_level: str, user_level: str) -> str:
    """判定补足难度"""
    if target_level == "精通" and user_level in ["了解", "不了解"]:
        return "大"
    elif target_level == "熟练" and user_level == "不了解":
        return "中"
    elif target_level == "了解":
        return "小"
    else:
        return "小"

LEARNING_RESOURCES = {
    "Java": {
        "platform": "尚硅谷视频 + 《Java核心技术》",
        "duration": "3-4个月",
        "difficulty": "中等",
        "links": {
            "course": "https://www.bilibili.com/video/BV17Q4y1q7MH",
            "book": "https://book.douban.com/subject/25762168/",
            "docs": "https://docs.oracle.com/javase/tutorial/"
        }
    },
    "Python": {
        "platform": "廖雪峰教程 + LeetCode",
        "duration": "2-3个月",
        "difficulty": "中等",
        "links": {
            "course": "https://www.liaoxuefeng.com/wiki/1016959663602400",
            "book": "https://book.douban.com/subject/3112503/",
            "practice": "https://leetcode.cn/"
        }
    },
    "Go": {
        "platform": "《Go语言实战》+ 官方文档",
        "duration": "2个月",
        "difficulty": "中等",
        "links": {
            "course": "https://tour.golang.org/welcome/1",
            "book": "https://book.douban.com/subject/27204219/",
            "docs": "https://golang.org/doc/"
        }
    },
    "JavaScript": {
        "platform": "MDN文档 + 《JavaScript高级程序设计》",
        "duration": "2-3个月",
        "difficulty": "中等",
        "links": {
            "course": "https://developer.mozilla.org/zh-CN/docs/Web/JavaScript",
            "book": "https://book.douban.com/subject/10546125/",
            "practice": "https://javascript.info/"
        }
    },
    "TypeScript": {
        "platform": "TypeScript官方文档",
        "duration": "1个月",
        "difficulty": "简单",
        "links": {
            "course": "https://www.typescriptlang.org/zh/docs/handbook/intro.html",
            "practice": "https://github.com/type-challenges/type-challenges"
        }
    },
    "React": {
        "platform": "React官方文档 + 实战项目",
        "duration": "1-2个月",
        "difficulty": "中等",
        "links": {
            "course": "https://react.dev/learn",
            "course_cn": "https://zh.react.dev/learn",
            "hooks": "https://react.dev/reference/react",
            "project": "https://github.com/reactjs/reactjs.org"
        }
    },
    "Vue": {
        "platform": "Vue官方文档 + 尚硅谷教程",
        "duration": "1-2个月",
        "difficulty": "中等",
        "links": {
            "course": "https://cn.vuejs.org/guide/introduction.html",
            "composition": "https://cn.vuejs.org/guide/extras/composition-api-faq.html",
            "video": "https://www.bilibili.com/video/BV1q4y1u7C3"
        }
    },
    "Angular": {
        "platform": "Angular官方文档",
        "duration": "2-3个月",
        "difficulty": "较难",
        "links": {
            "course": "https://angular.io/docs",
            "course_cn": "https://angular.cn/docs"
        }
    },
    "Spring Boot": {
        "platform": "Spring官方文档 + 实战项目",
        "duration": "2个月",
        "difficulty": "中等",
        "links": {
            "course": "https://spring.io/projects/spring-boot",
            "guide": "https://spring.io/guides"
        }
    },
    "Node.js": {
        "platform": "Node.js官方文档 + Express框架",
        "duration": "2-3个月",
        "difficulty": "中等",
        "links": {
            "course": "https://nodejs.org/zh-cn/docs/guides",
            "express": "https://expressjs.com/zh-cn/starter/installing.html"
        }
    },
    "MySQL": {
        "platform": "《高性能MySQL》+ 实践",
        "duration": "2个月",
        "difficulty": "中等",
        "links": {
            "book": "https://book.douban.com/subject/23047113/",
            "practice": "https://leetcode.cn/problemset/database/"
        }
    },
    "Redis": {
        "platform": "《Redis设计与实现》",
        "duration": "1个月",
        "difficulty": "中等",
        "links": {
            "book": "https://book.douban.com/subject/25900156/",
            "docs": "https://redis.io/docs/"
        }
    },
    "Docker": {
        "platform": "Docker官方文档 + 实践",
        "duration": "2周",
        "difficulty": "简单",
        "links": {
            "course": "https://docs.docker.com/get-started/",
            "course_cn": "https://vuejs.org/v2/guide/"
        }
    },
    "Kubernetes": {
        "platform": "Kubernetes官方文档",
        "duration": "1-2个月",
        "difficulty": "较难",
        "links": {
            "course": "https://kubernetes.io/zh/docs/tutorials/",
            "interactive": "https://kubernetes.io/zh/docs/tutorials/kubernetes-basics/"
        }
    },
    "Linux": {
        "platform": "《鸟哥的Linux私房菜》",
        "duration": "1-2个月",
        "difficulty": "中等",
        "links": {
            "book": "https://book.douban.com/subject/30359974/",
            "practice": "https://github.com/trimstray/the-book-of-secret-knowledge"
        }
    },
    "Git": {
        "platform": "Git官方文档",
        "duration": "1周",
        "difficulty": "简单",
        "links": {
            "course": "https://git-scm.com/book/zh/v2",
            "practice": "https://learngitbranching.js.org/"
        }
    },
    "微服务": {
        "platform": "《Spring微服务实战》",
        "duration": "2-3个月",
        "difficulty": "较难",
        "links": {
            "book": "https://book.douban.com/subject/34439700/",
            "spring_cloud": "https://spring.io/projects/spring-cloud"
        }
    },
    "算法": {
        "platform": "LeetCode + 《算法导论》",
        "duration": "3-6个月",
        "difficulty": "较难",
        "links": {
            "course": "https://leetcode.cn/",
            "book": "https://book.douban.com/subject/20432061/",
            "visual": "https://visualgo.net/zh"
        }
    },
    "数据结构": {
        "platform": "《数据结构与算法JavaScript描述》",
        "duration": "2-3个月",
        "difficulty": "中等",
        "links": {
            "book": "https://book.douban.com/subject/27112752/",
            "visual": "https://visualgo.net/zh"
        }
    },
    "计算机网络": {
        "platform": "《计算机网络：自顶向下方法》",
        "duration": "2-3个月",
        "difficulty": "中等",
        "links": {
            "book": "https://book.douban.com/subject/13941504/",
            "course": "https://www bilibili.com/video/BV1c4411d7zv"
        }
    },
    "操作系统": {
        "platform": "《操作系统概念》",
        "duration": "2-3个月",
        "difficulty": "较难",
        "links": {
            "book": "https://book.douban.com/subject/30363954/",
            "course": "https://www.bilibili.com/video/BV1NE411j7nv"
        }
    },
    "HTML": {
        "platform": "MDN HTML教程",
        "duration": "2-4周",
        "difficulty": "简单",
        "links": {
            "course": "https://developer.mozilla.org/zh-CN/docs/Learn/HTML",
            "practice": "https://htmlreference.io/"
        }
    },
    "CSS": {
        "platform": "MDN CSS教程 + Tailwind文档",
        "duration": "2-4周",
        "difficulty": "简单",
        "links": {
            "course": "https://developer.mozilla.org/zh-CN/docs/Learn/CSS",
            "tailwind": "https://www.tailwindcss.cn/docs"
        }
    },
    "Webpack": {
        "platform": "Webpack官方文档",
        "duration": "1-2周",
        "difficulty": "中等",
        "links": {
            "course": "https://webpack.js.org/concepts/",
            "course_cn": "https://webpack.docschina.org/concepts/"
        }
    },
    "Vite": {
        "platform": "Vite官方文档",
        "duration": "1周",
        "difficulty": "简单",
        "links": {
            "course": "https://cn.vitejs.dev/guide/",
            "video": "https://www.bilibili.com/video/BV1GN4y1M7P5"
        }
    },
    "Figma": {
        "platform": "Figma官方教程 + Dribbble临摹",
        "duration": "1个月",
        "difficulty": "简单",
        "links": {
            "course": "https://help.figma.com/hc/en-us/categories/4405269464471-Figma-for-design",
            "tutorial": "https://www.youtube.com/c/Figma"
        }
    },
    "Photoshop": {
        "platform": "B站教程 + 实践项目",
        "duration": "1-2个月",
        "difficulty": "中等",
        "links": {
            "course": "https://www.bilibili.com/video/BV1Ps411V7xp",
            "ps": "https://www.adobe.com/cn/products/photoshop/"
        }
    },
    "Sketch": {
        "platform": "Sketch官方教程 + 设计练习",
        "duration": "1个月",
        "difficulty": "简单",
        "links": {
            "course": "https://www.sketch.com/docs/",
            "tutorial": "https://www.sketch.com/tutorials/"
        }
    },
    "SQL": {
        "platform": "LeetCode SQL题 + 《SQL必知必会》",
        "duration": "1个月",
        "difficulty": "简单",
        "links": {
            "book": "https://book.douban.com/subject/24250084/",
            "practice": "https://leetcode.cn/problemset/database/"
        }
    },
    "Tableau": {
        "platform": "Tableau官方教程 + 实践项目",
        "duration": "1个月",
        "difficulty": "简单",
        "links": {
            "course": "https://www.tableau.com/zh-cn/learn"
        }
    },
    "Power BI": {
        "platform": "微软官方教程 + 实践",
        "duration": "1个月",
        "difficulty": "简单",
        "links": {
            "course": "https://docs.microsoft.com/zh-cn/power-bi/"
        }
    },
    "Axure": {
        "platform": "Axure官方教程 + 原型练习",
        "duration": "2周",
        "difficulty": "简单",
        "links": {
            "course": "https://www.axure.com/learn"
        }
    },
    "需求分析": {
        "platform": "《需求分析实战》+ 案例练习",
        "duration": "1个月",
        "difficulty": "中等",
        "links": {
            "book": "https://book.douban.com/subject/27075674/"
        }
    },
    "产品设计": {
        "platform": "《人人都是产品经理》",
        "duration": "1个月",
        "difficulty": "简单",
        "links": {
            "book": "https://book.douban.com/subject/26628243/"
        }
    },
    "数据分析": {
        "platform": "《Python数据分析》+ Kaggle",
        "duration": "2-3个月",
        "difficulty": "中等",
        "links": {
            "book": "https://book.douban.com/subject/27121111/",
            "practice": "https://www.kaggle.com/"
        }
    },
    "Flutter": {
        "platform": "Flutter官方文档 + Codelabs",
        "duration": "2-3个月",
        "difficulty": "中等",
        "links": {
            "course": "https://flutter.dev/docs",
            "course_cn": "https://flutter.cn/docs",
            "codelab": "https://codelabs.flutter.dev/"
        }
    },
    "React Native": {
        "platform": "React Native官方文档",
        "duration": "2-3个月",
        "difficulty": "中等",
        "links": {
            "course": "https://reactnative.dev/docs/getting-started",
            "course_cn": "https://reactnative.cn/docs/getting-started"
        }
    },
    "iOS": {
        "platform": "Apple官方Swift教程",
        "duration": "3-4个月",
        "difficulty": "较难",
        "links": {
            "course": "https://docs.swift.org/swift-book/LanguageGuide/TheBasics.html",
            "course_cn": "https://www.swift.org/documentation/"
        }
    },
    "Android": {
        "platform": "Google Android开发者文档",
        "duration": "3-4个月",
        "difficulty": "较难",
        "links": {
            "course": "https://developer.android.com/guide",
            "course_cn": "https://developer.android.com/guide?hl=zh_cn"
        }
    },
}


def generate_vue_to_react_migration_path(user_skills: List[str]) -> dict:
    """
    Vue→React迁移路径
    利用用户现有Vue技能，给出差异化学习建议
    """
    has_vue = any("vue" in skill.lower() for skill in user_skills)
    has_vue3 = any("vue3" in skill.lower() or "composition" in skill.lower() for skill in user_skills)
    has_vuex = any("vuex" in skill.lower() or "pinia" in skill.lower() for skill in user_skills)
    
    if not has_vue:
        return {
            "applicable": False,
            "reason": "未检测到Vue技能，建议先掌握Vue基础"
        }
    
    migration_path = {
        "applicable": True,
        "leverage_skills": [],
        "key_differences": [],
        "learning_stages": [],
        "recommended_order": []
    }
    
    if has_vue3:
        migration_path["leverage_skills"].append("Vue 3 Composition API → React Hooks 转换")
        migration_path["key_differences"].append({
            "vue_concept": "Vue 3 Composition API",
            "react_equivalent": "React Hooks (useState, useEffect)",
            "similarity": "高"
        })
    else:
        migration_path["key_differences"].append({
            "vue_concept": "Vue 2 Options API",
            "react_equivalent": "React Hooks + 函数组件",
            "similarity": "中"
        })
    
    if has_vuex or has_vue3:
        migration_path["leverage_skills"].append("Vuex/Pinia状态管理 → Redux/Zustand")
        migration_path["key_differences"].append({
            "vue_concept": "Pinia/Vuex",
            "react_equivalent": "Zustand/Jotai/Redux Toolkit",
            "similarity": "高"
        })
    
    migration_path["leverage_skills"].append("Vue组件化思维 → React组件化")
    migration_path["leverage_skills"].append("Vue模板语法 → JSX语法")
    
    migration_path["key_differences"].append({
        "vue_concept": "Vue模板 (Template)",
        "react_equivalent": "JSX",
        "similarity": "低 - 需要适应"
    })
    
    migration_path["key_differences"].append({
        "vue_concept": "Vue响应式系统",
        "react_equivalent": "React状态与useEffect",
        "similarity": "中"
    })
    
    migration_path["learning_stages"] = [
        {
            "stage": "第一阶段：核心概念 (1-2周)",
            "tasks": [
                "理解React函数组件 + Hooks模式",
                "学习useState和useEffect",
                "对比Vue Composition API与React Hooks"
            ],
            "resources": [
                {"name": "React官方入门", "url": "https://react.dev/learn"},
                {"name": "Vue开发者React指南", "url": "https://react.dev/learn/describing-the-ui"}
            ]
        },
        {
            "stage": "第二阶段：状态管理 (1-2周)",
            "tasks": [
                "选择Zustand作为首个React状态管理库（与Pinia类似）",
                "学习Redux Toolkit基础",
                "迁移Vue组件状态到React"
            ],
            "resources": [
                {"name": "Zustand文档", "url": "https://zustand.docs.pmnd.rs/"},
                {"name": "Redux Toolkit", "url": "https://redux-toolkit.js.org/"}
            ]
        },
        {
            "stage": "第三阶段：路由与生态 (1周)",
            "tasks": [
                "Vue Router → React Router v6",
                "学习React Context API",
                "了解React Query/SWR"
            ],
            "resources": [
                {"name": "React Router", "url": "https://reactrouter.com/en/main"},
                {"name": "React Query", "url": "https://tanstack.com/query/v4/"}
            ]
        },
        {
            "stage": "第四阶段：实战项目 (2-4周)",
            "tasks": [
                "将现有Vue项目部分功能用React重写",
                "对比两种框架的开发体验",
                "总结React最佳实践"
            ],
            "resources": [
                {"name": "React项目实战", "url": "https://react.dev/learn/start-a-new-react-project"},
                {"name": "React设计模式", "url": "https://react.dev/learn/thinking-in-react"}
            ]
        }
    ]
    
    migration_path["recommended_order"] = [
        "先理解Hooks与Composition API的对应关系",
        "选择Zustand而非Redux，降低迁移门槛",
        "保持Vue组件拆分思维，但改用函数组件",
        "用React重写小型模块，循序渐进"
    ]
    
    migration_path["estimated_time"] = "4-8周（基于已有Vue经验）"
    
    return migration_path


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
    current_job: Optional[str] = None
    user_skills: List[str]
    user_experience: int
    target_job: str
    target_company: Optional[str] = None
    target_salary: Optional[str] = None

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
    match_score: Optional[float] = None
    match_status: str = "正常"
    job_type: str
    description: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None


class EnhancedAnalysisResponse(BaseModel):
    model_config = ConfigDict(alias_generator=lambda s: ''.join(
        word.capitalize() if i > 0 else word for i, word in enumerate(s.split('_'))
    ), populate_by_name=True)

    target_job: str
    job_type: str
    matched_jobs: List[JobMatch]
    gap_analysis: dict
    action_plan: dict
    transition_analysis: dict
    competition_analysis: dict
    salary_analysis: dict
    skill_recommendations: dict
    target_feasibility: dict
    market_skills: List[str] = []


SKILL_RELATIONS = {
    "JavaScript": ["ES6+", "TypeScript", "异步编程", "DOM操作", "Promise", "闭包"],
    "TypeScript": ["JavaScript", "ES6+", "类型系统", "泛型"],
    "React": ["Hooks", "Redux", "React Router", "JSX", "状态管理"],
    "Vue": ["Vuex", "Pinia", "Vue Router", "Composition API", "响应式"],
    "Node.js": ["Express", "npm", "yarn", "RESTful API", "异步编程"],
    "Python": ["Django", "Flask", "FastAPI", "SQLAlchemy", "requests"],
    "Java": ["Spring Boot", "Spring MVC", "JPA", "微服务"],
    "Go": ["Gin", "Gorm", "并发编程", "微服务"],
    "SQL": ["MySQL", "PostgreSQL", "索引优化", "SQL优化"],
    "MongoDB": ["NoSQL", "文档数据库", "索引"],
    "Redis": ["缓存", "分布式缓存", "数据结构"],
    "Docker": ["容器化", "Dockerfile", "镜像"],
    "Kubernetes": ["容器编排", "Pod", "Service", "Deployment"],
    "项目管理": ["敏捷开发", "需求分析", "Scrum", "迭代管理"],
    "Figma": ["UI设计", "交互设计", "组件库"],
}

def is_cross_family_transition(current_family: str, target_family: str) -> bool:
    """
    判断是否为跨族转型
    当前岗位族 = 目标岗位族 → 同族晋升
    当前岗位族 ≠ 目标岗位族 → 跨族转型
    """
    return current_family != target_family

def get_transition_type(current_family: str, target_family: str) -> str:
    """获取转型类型"""
    if current_family == target_family:
        return "同族晋升"
    return "跨族转型"

def generate_transition_analysis(current_family: str, target_family: str, user_skills: List[str]) -> dict:
    """
    生成转型分析
    - 同族晋升：深度提升路径
    - 跨族转型：知识体系重建路径
    """
    transition_type = get_transition_type(current_family, target_family)
    
    if transition_type == "同族晋升":
        return {
            "type": "同族晋升",
            "description": "在同一岗位族内的职业发展，路径以深度提升为主",
            "advantage_focus": "已有技能可复用、行业经验可迁移",
            "action_path": ["补深度", "拓广度", "面试准备"],
            "estimated_months": 6
        }
    else:
        transferable_skills = identify_transferable_skills(current_family, target_family, user_skills)
        return {
            "type": "跨族转型",
            "description": "跨岗位族的职业转型，路径以知识体系重建为主",
            "advantage_focus": "可迁移的软技能、跨视角的理解能力",
            "action_path": ["补新族核心技能", "做新族实战项目", "面试准备"],
            "estimated_months": 12,
            "transferable_skills": transferable_skills
        }

def identify_transferable_skills(from_family: str, to_family: str, user_skills: List[str]) -> List[str]:
    """识别可迁移技能"""
    transferable = []
    
    common_skills = ["Git", "项目管理", "沟通能力", "问题解决", "学习能力", "英语"]
    
    for skill in user_skills:
        skill_lower = skill.lower()
        if any(cs.lower() in skill_lower for cs in common_skills):
            transferable.append(skill)
    
    return transferable[:5]


def calculate_priority_score(core_level: str, gap_level: str, is_basic: bool = False) -> int:
    """
    计算优先级分 = 核心程度权重 × 差距权重 × 基础技能加成
    
    核心程度权重：核心必备=3，重要=2，加分=1
    差距权重：大差距=3，中差距=2，小差距=1
    基础技能加成：基础技能+50%权重
    优先级分范围：1-15，15最优先
    """
    core_weights = {"核心必备": 3, "重要": 2, "加分": 1}
    gap_weights = {"大": 3, "中": 2, "小": 1, "无": 0}
    
    core_weight = core_weights.get(core_level, 1)
    gap_weight = gap_weights.get(gap_level, 0)
    
    base_score = core_weight * gap_weight
    
    if is_basic and gap_weight > 0:
        base_score = int(base_score * 1.5)
    
    return base_score


def get_core_level(skill: str, target_family: str, target_job: str) -> str:
    """
    获取技能的核心程度（核心必备/重要/加分）
    基于目标岗位技能图谱
    """
    skill_map = get_target_level_skill_map(target_family, target_job)
    
    if not skill_map:
        return "重要"
    
    if skill in skill_map.get("精通", []):
        return "核心必备"
    elif skill in skill_map.get("熟练", []):
        return "重要"
    elif skill in skill_map.get("了解", []):
        return "加分"
    
    return "重要"


def get_gap_level(user_level: str) -> str:
    """获取差距等级"""
    if user_level == "不了解":
        return "大"
    elif user_level == "了解":
        return "中"
    elif user_level == "熟练":
        return "小"
    return "无"


def generate_skill_action_plan(skill: str, priority_score: int, target_family: str, user_level: str = "不了解") -> dict:
    """
    生成技能行动建议
    必须包含：学习资源方向、预计学习时间、补足难度、验证方式
    user_level: 用户的技能级别，根据级别调整学习深度
    """
    LEVEL_PRIORITY = {'精通': 3, '熟练': 2, '掌握': 2, '了解': 1, '入门': 0, '不了解': -1}
    user_level_priority = LEVEL_PRIORITY.get(user_level, -1)
    
    is_advanced = user_level_priority >= 2
    
    learning_resources = {
        "JavaScript": {
            "beginner": ["JavaScript 入门", "ES6 基础语法", "DOM 操作入门"],
            "advanced": ["JavaScript 深入", "闭包 作用域", "事件循环 原理", "Promise 源码分析"]
        },
        "TypeScript": {
            "beginner": ["TypeScript 入门", "类型基础", "接口与类型别名"],
            "advanced": ["TypeScript 类型系统", "泛型 类型体操", "高级类型技巧"]
        },
        "React": {
            "beginner": ["React 入门", "JSX 基础", "useState useEffect"],
            "advanced": ["React Hooks 原理", "Redux 状态管理", "React Router 源码", "性能优化"]
        },
        "Vue": {
            "beginner": ["Vue 入门", "模板语法", "Options API 基础"],
            "advanced": ["Vue3 Composition API", "Pinia 源码", "Vue Router 原理", "响应式原理深入"]
        },
        "Node.js": {
            "beginner": ["Node.js 入门", "Express 基础", "RESTful API 入门"],
            "advanced": ["Node.js Express 实战", "中间件开发", "Express/Koa 源码分析", "性能调优"]
        },
        "算法": {
            "beginner": ["LeetCode 入门", "数组 链表 基础", "简单递归"],
            "advanced": ["LeetCode 刷题", "数据结构与算法", "动态规划 专题", "源码级理解"]
        },
    }
    
    resource_data = learning_resources.get(skill)
    if resource_data:
        if is_advanced:
            keywords = resource_data.get("advanced", resource_data.get("beginner"))
            duration = "3-4周" if skill in ["JavaScript", "TypeScript"] else "4-6周"
        else:
            keywords = resource_data.get("beginner")
            duration = "2-3周" if skill in ["JavaScript", "TypeScript"] else "3-4周"
    else:
        if is_advanced:
            keywords = [f"{skill} 进阶", f"{skill} 源码级实战", f"{skill} 原理深入"]
            duration = "4-6周"
        else:
            keywords = [f"{skill} 入门", f"{skill} 实战", f"{skill} 面试题"]
            duration = "4-6周"
    
    difficulty = "中"
    if priority_score >= 6:
        difficulty = "高"
    elif priority_score < 3:
        difficulty = "低"
    
    if is_advanced:
        verification = f"能深入理解{skill}核心原理、能讲解{skill}源码、能设计{skill}相关架构"
    else:
        verification = f"能独立完成{skill}相关项目、能讲清{skill}核心原理、能通过{skill}面试题"
    
    return {
        "skill": skill,
        "priority_score": priority_score,
        "learning_resources": keywords,
        "estimated_time": duration,
        "difficulty": difficulty,
        "verification": verification,
        "learning_depth": "进阶" if is_advanced else "入门"
    }


def generate_phase_action_plan(
    gap_skills: List[dict], 
    target_family: str, 
    target_job: str, 
    target_company: str,
    avg_match_score: float = 50.0,
    max_match_score: float = 0.0,
    user_experience: int = 0,
    is_career_change: bool = False,
    user_skills: List[str] = None,
    parsed_skills: dict = None
) -> dict:
    """
    生成分阶段行动方案
    
    优先级规则（新调整）：
    - 短期（1-3月）：React技术栈/TypeScript深度 + 高优先级框架
      - React/TypeScript 为前端最高优先级
      - 框架工具（Vue/Angular等）紧随其后
    - 中期（3-6月）：核心基础 + 浏览器原理/HTTP网络协议
      - JavaScript/HTML/CSS 夯实基础
      - 计算机网络、浏览器原理作为复习项
    - 长期（6-12月）：进阶技能 + 面试准备 + 投递策略
    
    前置依赖规则：
    - 如果框架技能的前置依赖未掌握，前置技能自动提升优先级
    """
    parsed_skills = parsed_skills or {}
    user_skills = user_skills or []
    user_skills_lower = [s.lower() for s in user_skills]
    
    # 获取用户声明熟练的框架（包含通用模式）
    user_proficient_frameworks = set(s.lower() for s in parsed_skills.get('proficient_frameworks', []))
    user_has_frameworks = set(s.lower() for s in parsed_skills.get('has_frameworks', []))
    
    # 处理通用模式：如果用户声明"Vue和React通用"，则两者都标记为熟练
    for pattern in parsed_skills.get('universal_patterns', []):
        for fw in pattern.get('frameworks', []):
            user_proficient_frameworks.add(fw.lower())
    
    skill_actions = []
    
    for skill_info in gap_skills:
        skill = skill_info.get("skill", "")
        if not skill:
            continue
        
        # 检查用户是否在通用模式中声明了该技能
        skill_lower = skill.lower()
        is_declared_proficient = any(
            fw in skill_lower or skill_lower in fw 
            for fw in user_proficient_frameworks
        )
        
        # 如果用户已声明熟练，跳过或降低优先级
        if is_declared_proficient:
            continue
        
        core_level = get_core_level(skill, target_family, target_job)
        gap_level = get_gap_level(skill_info.get("user_level", "不了解"))
        is_basic = is_basic_skill(skill, target_family)
        is_framework = is_high_priority_framework(skill, target_family)
        is_secondary = is_secondary_skill(skill, target_family)
        
        prerequisites = get_prerequisites(skill)
        has_prereqs = has_all_prerequisites(skill, user_skills_lower)
        
        if core_level == "精通" or gap_level in ["大", "中"]:
            priority_score = calculate_priority_score(core_level, gap_level, is_basic)
        else:
            priority_score = 2
        
        if priority_score == 0:
            continue
        
        user_level = skill_info.get("user_level", "不了解")
        action = generate_skill_action_plan(skill, priority_score, target_family, user_level)
        action["core_level"] = core_level
        action["gap_level"] = gap_level
        action["user_level"] = user_level
        action["is_basic"] = is_basic
        action["is_framework"] = is_framework
        action["is_secondary"] = is_secondary
        action["learning_weeks"] = calculate_learning_time(skill, priority_score, target_family)
        action["has_prerequisites"] = has_prereqs
        action["prerequisites"] = prerequisites
        skill_actions.append(action)
    
    def sort_key(x):
        base_score = x["priority_score"]
        
        tier = 0
        if x["is_basic"]:
            tier = 3
        elif x["is_framework"] and x["has_prerequisites"]:
            tier = 2
        elif x["is_framework"] and not x["has_prerequisites"]:
            tier = 1
        elif x["is_secondary"]:
            tier = 0
        
        return (tier, base_score, x["learning_weeks"])
    
    skill_actions.sort(key=sort_key, reverse=True)
    
    framework_skills = [s for s in skill_actions if s["is_framework"]]
    basic_skills = [s for s in skill_actions if s["is_basic"] and not s["is_framework"]]
    secondary_skills = [s for s in skill_actions if s["is_secondary"] and not s["is_framework"] and not s["is_basic"]]
    advanced_skills = [s for s in skill_actions if not s["is_framework"] and not s["is_basic"] and not s["is_secondary"]]
    
    time_estimate = calculate_dynamic_time_estimate(
        gap_skills, 
        target_family, 
        is_career_change,
        avg_match_score,
        user_experience
    )
    
    template = PROJECT_TEMPLATES.get(target_family, PROJECT_TEMPLATES["通用"])
    
    short_skills = framework_skills[:4] + basic_skills[:2]
    medium_skills = basic_skills[2:4] + secondary_skills[:3]
    long_skills = framework_skills[4:] + basic_skills[4:] + secondary_skills[3:] + advanced_skills
    
    action_plan = {
        "short_term": {
            "description": f"短期（1-3月）：{len(short_skills)}项核心技能 + 框架实战",
            "skills": short_skills,
            "project": template["short_term"]["project"],
            "interview_prep": [],
            "focus": template.get("focus", f"{target_family}核心技能深化")
        },
        "medium_term": {
            "description": f"中期（3-6月）：{len(medium_skills)}项基础夯实 + 核心原理深化",
            "skills": medium_skills,
            "project": template["medium_term"]["project"],
            "interview_prep": []
        },
        "long_term": {
            "description": f"长期（6-12月）：{len(long_skills)}项进阶技能 + 面试准备",
            "skills": long_skills,
            "project": template["long_term"]["project"],
            "interview_prep": []
        },
        "time_estimate": time_estimate
    }
    
    if target_company:
        if target_company in ["阿里巴巴", "阿里", "Alibaba"]:
            action_plan["long_term"]["interview_prep"].append(
                f"🎯 目标公司技术栈针对性准备：{target_company}\n"
                f"重点方向：React 生态（Rax）、微前端（qiankun）、Node.js 服务端（Midway/Egg）、性能监控体系"
            )
        else:
            action_plan["long_term"]["interview_prep"].append(f"🎯 目标公司技术栈针对性准备：{target_company}")
    
    for prep in template.get("interview_prep", {}).get("medium", []):
        action_plan["medium_term"]["interview_prep"].append(f"💡 {prep}")
    for prep in template.get("interview_prep", {}).get("long", []):
        action_plan["long_term"]["interview_prep"].append(f"💡 {prep}")
    
    if max_match_score >= 70:
        action_plan["long_term"]["interview_prep"].append("📋 投递策略：先投递匹配度70%以上的岗位积累面试经验，再投递心仪公司")
    elif max_match_score > 0:
        action_plan["long_term"]["interview_prep"].append(f"📋 投递策略：当前样本中直接匹配度最高的岗位为 {max_match_score:.0f}%，建议优先投递这些岗位积累经验，同步提升目标技能")
    else:
        action_plan["long_term"]["interview_prep"].append("📋 投递策略：建议先完善技能图谱，系统将为你匹配合适的岗位")

    return action_plan


def get_job_family(title: str) -> str:
    """根据岗位标题获取岗位族"""
    title_lower = title.lower()
    for family, keywords in JOB_FAMILY_MAPPING.items():
        for keyword in keywords:
            if keyword.lower() in title_lower:
                return family
    return ""


def get_relevant_skills(job_family: str) -> List[str]:
    """获取岗位族的相关技能"""
    skills = []
    if job_family in SKILL_MAPPING:
        for category, skill_list in SKILL_MAPPING[job_family].items():
            skills.extend(skill_list)
    return skills


def get_related_skills(skill: str) -> List[str]:
    """获取技能的关联技能"""
    return SKILL_RELATIONS.get(skill, [])


@app.get("/")
def read_root():
    return {"message": "职业规划顾问 API"}


class JobSearchRequest(BaseModel):
    keyword: Optional[str] = None
    city: Optional[str] = None
    limit: int = 20


def job_to_dict(job: Job) -> dict:
    """将 Job 对象转换为字典格式"""
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


def build_job_query(query, keyword: Optional[str] = None, city: Optional[str] = None):
    """构建职位查询条件"""
    if keyword:
        query = query.filter(Job.title.like(f"%{keyword}%") | Job.skills.like(f"%{keyword}%"))
    if city:
        query = query.filter(Job.location.like(f"%{city}%"))
    return query


@app.get("/api/jobs", response_model=List[dict])
def get_jobs(
    keyword: Optional[str] = None,
    city: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    query = build_job_query(db.query(Job), keyword, city)
    jobs = query.limit(limit).all()
    return to_camel_case([job_to_dict(job) for job in jobs])


@app.post("/api/jobs/search", response_model=List[dict])
def search_jobs(request: JobSearchRequest, db: Session = Depends(get_db)):
    query = build_job_query(db.query(Job), request.keyword, request.city)
    jobs = query.limit(request.limit).all()
    return to_camel_case([job_to_dict(job) for job in jobs])


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


import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


@app.post("/api/crawl")
def crawl_and_save_jobs(request: CrawlRequest, db: Session = Depends(get_db)):
    """爬取真实招聘数据（当前禁用，爬虫功能需要额外配置）"""
    return {
        "success": False,
        "message": "爬虫功能暂不可用，请联系管理员启用",
        "saved_count": 0,
        "errors": ["爬虫模块未配置"]
    }



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


def get_salary_tier(salary: int) -> int:
    """计算薪资档位（每5K为一档）"""
    return (salary - 1) // 5000 + 1

def salary_to_k(salary: int) -> str:
    """转换为K格式"""
    return f"{salary // 1000}K"

def analyze_salary_by_level(jobs: List[Job], experience_years: int) -> dict:
    """
    按经验年限分层分析薪资范围
    展示限制：跨不超过3个档位（15K区间）
    """
    if not jobs:
        return {
            "has_data": False,
            "message": "该层级薪资数据有限"
        }
    
    # 按经验分层筛选岗位
    junior_jobs = []
    mid_jobs = []
    senior_jobs = []
    
    for job in jobs:
        if not job.salary_min or not job.salary_max:
            continue
        
        exp_min, exp_max = parse_experience(job.experience_requirement)
        avg_exp = (exp_min + exp_max) / 2 if exp_max else exp_min
        
        if avg_exp <= 3:
            junior_jobs.append((job.salary_min, job.salary_max))
        elif 3 < avg_exp <= 5:
            mid_jobs.append((job.salary_min, job.salary_max))
        else:
            senior_jobs.append((job.salary_min, job.salary_max))
    
    # 确定用户的层级
    if experience_years <= 3:
        target_jobs = junior_jobs if junior_jobs else mid_jobs
        level = "初级"
    elif 3 < experience_years <= 5:
        target_jobs = mid_jobs if mid_jobs else junior_jobs or senior_jobs
        level = "中级"
    else:
        target_jobs = senior_jobs if senior_jobs else mid_jobs
        level = "高级"
    
    if not target_jobs:
        return {
            "has_data": False,
            "message": "该层级薪资数据有限"
        }
    
    # 计算该层级薪资统计
    all_salaries = []
    for s_min, s_max in target_jobs:
        all_salaries.extend([s_min, s_max])
    
    all_salaries_sorted = sorted(all_salaries)
    n = len(all_salaries_sorted)
    
    min_salary = all_salaries_sorted[0]
    median_salary = all_salaries_sorted[n // 2]
    p75_salary = all_salaries_sorted[int(n * 0.75)]
    max_salary = all_salaries_sorted[-1]
    
    # 确定展示范围（不超过3个档位=15K）
    lower = 0
    upper = 0
    
    if level == "初级":
        # 初级：下限→中位数
        lower = min_salary
        upper = min(median_salary, lower + 15000)
    elif level == "中级":
        # 中级：中位数→P75
        lower = median_salary
        upper = min(p75_salary, lower + 15000)
    else:
        # 高级：P75→上限
        lower = p75_salary
        upper = min(max_salary, lower + 15000)
    
    # 计算三个关键值
    key_values = {
        "lower": int(lower),
        "median": int(median_salary),
        "upper": int(upper)
    }
    
    # 检查范围是否合理
    if upper - lower > 15000:
        upper = lower + 15000
        key_values["upper"] = int(upper)
    
    return {
        "has_data": True,
        "level": level,
        "experience_years": experience_years,
        "key_values": key_values,
        "display_lower": salary_to_k(key_values["lower"]),
        "display_median": salary_to_k(key_values["median"]),
        "display_upper": salary_to_k(key_values["upper"]),
        "range_str": f"{salary_to_k(key_values['lower'])} → {salary_to_k(key_values['median'])} → {salary_to_k(key_values['upper'])}"
    }

def analyze_salary_range(jobs: List[Job]) -> dict:
    """兼容原有的薪资分析函数"""
    salaries = []
    for job in jobs:
        if job.salary_min and job.salary_max:
            salaries.append((job.salary_min, job.salary_max))
    
    valid_count = len(salaries)
    
    if not salaries:
        return {"min": 0, "max": 0, "avg": 0, "median": 0, "validCount": 0}
    
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
        "median": int(median_salary),
        "validCount": valid_count
    }


def generate_skill_recommendations(missing_skills: List[str], job_family: str, user_skills: List[str] = None, parsed_skills: dict = None) -> dict:
    parsed_skills = parsed_skills or {}

    # 获取用户技能熟练度（优先使用 skill_levels）
    user_skill_levels = parsed_skills.get('skill_levels', {})

    # 工具到技能的映射
    TOOL_TO_SKILL = {
        'webpack': 'Webpack', 'vite': 'Vite', 'eslint': 'ESLint', 'prettier': 'Prettier',
        'git': 'Git', 'docker': 'Docker', 'jenkins': 'Jenkins', 'ci/cd': 'CI/CD',
        'nginx': 'Nginx', 'linux': 'Linux', 'k8s': 'Kubernetes', 'kubernetes': 'Kubernetes',
    }

    # 框架到技能的映射
    FRAMEWORK_TO_SKILL = {
        'react': 'React', 'vue': 'Vue', 'angular': 'Angular',
        'next.js': 'Next.js', 'nuxt.js': 'Nuxt.js',
    }

    # 技能聚合映射表
    SKILL_AGGREGATION = {
        '前端工程化': ['vite', 'webpack', 'ci', 'cd', 'ci/cd', 'webpack', 'vite', 'rollup', 'parcel', 'esbuild', 'eslint', 'prettier'],
        'JavaScript/TypeScript深度': ['javascript', 'typescript', 'js', 'ts', 'ecmascript'],
        'React技术栈': ['react', 'react.js', 'reactjs', 'next.js', 'nextjs'],
        'Vue技术栈': ['vue', 'vue.js', 'vuejs', 'vue3', 'vue2', 'nuxt.js'],
        'HTTP/网络协议': ['http', 'https', 'tcp', 'udp', '网络协议', 'http协议'],
        '浏览器原理': ['浏览器', '浏览器原理', '渲染原理', 'dom', 'bom'],
        'Node.js服务端': ['node.js', 'nodejs', 'node', 'node服务端', 'node.js服务端'],
        'HTML/CSS基础': ['html', 'css', 'html5', 'css3'],
        'Git版本控制': ['git', 'github', 'gitlab', 'svn', '版本控制'],
    }

    # 技能优先级（用于聚合时选择显示名称）
    SKILL_PRIORITY = {
        'react': 10, 'vue': 10, 'angular': 10,
        'javascript': 9, 'typescript': 9,
        'html': 8, 'css': 8,
        'webpack': 7, 'vite': 7,
        'git': 6, 'node.js': 6, 'nodejs': 6, 'node': 6, 'node.js服务端': 6,
        'http': 5, 'http协议': 5,
        '浏览器': 4,
    }

    def aggregate_skill_levels(skill_levels: dict) -> dict:
        """
        将细分的技能标签聚合为标准技能分类
        """
        aggregated = {}
        used_keys = set()

        for category, variants in SKILL_AGGREGATION.items():
            max_level = "不了解"
            max_priority = -1
            matched_key = None
            matched_variants = set()

            for variant in variants:
                variant_lower = variant.lower()
                for key, level in skill_levels.items():
                    key_lower = key.lower()
                    if key_lower == variant_lower or variant_lower in key_lower or key_lower in variant_lower:
                        priority = SKILL_PRIORITY.get(variant_lower, 0)
                        if priority > max_priority:
                            max_priority = priority
                            max_level = level
                            matched_key = key
                        matched_variants.add(key)

            if matched_key:
                aggregated[category] = max_level
                used_keys.update(matched_variants)

        # 添加未聚合的技能（排除已聚合的）
        for key, level in skill_levels.items():
            if key not in used_keys:
                aggregated[key] = level

        return aggregated

    def get_skill_level(skill_name: str) -> str:
        """
        获取用户对某个技能的熟练度
        支持组合技能名称（如 "JavaScript/TypeScript深度"）
        """
        skill_lower = skill_name.lower()

        # 直接查找
        if skill_name in user_skill_levels:
            return user_skill_levels[skill_name]
        for k, v in user_skill_levels.items():
            if k.lower() == skill_lower:
                return v

        # 检查组合技能的任一部分
        parts = [p.strip() for p in skill_lower.split('/')]
        for part in parts:
            if part in user_skill_levels:
                return user_skill_levels[part]
            for k, v in user_skill_levels.items():
                if k.lower() == part:
                    return v

            # 检查工具映射
            if part in TOOL_TO_SKILL:
                tool_skill = TOOL_TO_SKILL[part]
                if tool_skill in user_skill_levels:
                    return user_skill_levels[tool_skill]

            # 检查框架映射
            if part in FRAMEWORK_TO_SKILL:
                fw_skill = FRAMEWORK_TO_SKILL[part]
                if fw_skill in user_skill_levels:
                    return user_skill_levels[fw_skill]

            # 检查基础技能部分匹配
            if part in ['javascript', 'typescript', 'html', 'css', 'http', '浏览器']:
                for k, v in user_skill_levels.items():
                    if part in k.lower():
                        return v

            # 检查框架部分匹配
            for k, v in user_skill_levels.items():
                if k.lower() in part:
                    return v

        # 默认值
        return "不了解"

    recommendations = []
    for skill in missing_skills[:5]:
        user_level = get_skill_level(skill)

        resource = LEARNING_RESOURCES.get(skill, {
            "platform": f"搜索'{skill}教程'或相关书籍",
            "duration": "1-2个月",
            "difficulty": "中等",
            "links": {}
        })
        recommendations.append({
            "skill": skill,
            "platform": resource["platform"],
            "duration": resource["duration"],
            "difficulty": resource["difficulty"],
            "links": resource.get("links", {}),
            "user_level": user_level
        })

    # Vue 迁移路径（使用 parsed_skills 判断）
    vue_migration = None
    user_skill_str = ' '.join(user_skills or [])
    if user_skill_str and ("vue" in user_skill_str.lower() or any("vue" in s.lower() for s in parsed_skills.get('has_frameworks', []))):
        vue_migration = generate_vue_to_react_migration_path(user_skills)
    
    result = {"recommendations": recommendations}
    # 只使用用户实际输入的技能生成能力图谱
    user_input_skills = parsed_skills.get('user_input_skills', {})
    result["skill_levels"] = aggregate_skill_levels(user_input_skills) if user_input_skills else {}
    # 补充用户未输入但与输入技能相关的隐含技能（如 React 隐含 JavaScript）
    if user_input_skills:
        implied_skills = parsed_skills.get('implied_skills', [])
        if implied_skills:
            implied_aggregated = {}
            for skill in implied_skills:
                normalized = normalize_skill(skill)
                if normalized and normalized not in result["skill_levels"]:
                    implied_aggregated[normalized] = parsed_skills.get('skill_levels', {}).get(normalized, '了解')
            if implied_aggregated:
                result["implied_skills"] = aggregate_skill_levels(implied_aggregated)
    if vue_migration:
        result["vueMigration"] = vue_migration
    
    return result


def calculate_family_match_score(job: Job, user_skills: List[str], user_experience: int, user_target_salary: str = "", sample_size: int = 0) -> dict:
    """
    新的匹配度计算逻辑：
    - 技能重合度：50%
    - 薪资匹配度：30%
    - 经验匹配度：20%
    
    样本不足时返回 {"score": None, "status": "待评估"}
    """
    # 样本不足，返回待评估
    if sample_size < 3:
        return {"score": None, "status": "待评估"}
    
    skill_weight = 0.5
    salary_weight = 0.3
    exp_weight = 0.2
    
    skill_score = 0.0
    salary_score = 0.0
    exp_score = 0.0
    
    if job.skills:
        job_skills = [s.strip().lower() for s in job.skills.split(",") if s.strip()]
        user_skills_lower = [s.lower() for s in user_skills]
        
        matched = 0
        for s in job_skills:
            if s in user_skills_lower:
                matched += 1
            else:
                for us in user_skills_lower:
                    if us in s or s in us:
                        matched += 0.5
        
        if job_skills:
            skill_score = (matched / len(job_skills)) * 100
    
    min_exp, max_exp = parse_experience(job.experience_requirement)
    if min_exp <= user_experience <= max_exp:
        exp_score = 100
    elif user_experience > max_exp:
        exp_score = 80
    elif user_experience >= min_exp * 0.5:
        exp_score = 50
    else:
        exp_score = 20
    
    if job.salary_min and job.salary_max and user_target_salary:
        try:
            target_salary = int(user_target_salary.replace('K', '').replace('k', '').replace(',', '')) * 1000
            if job.salary_min <= target_salary <= job.salary_max:
                salary_score = 100
            elif target_salary < job.salary_min:
                salary_score = 60
            else:
                salary_score = 40
        except:
            salary_score = 50
    else:
        salary_score = 50
    
    score = round(skill_score * skill_weight + salary_score * salary_weight + exp_score * exp_weight, 1)
    return {"score": score, "status": "正常"}


@app.post("/api/analyze", response_model=EnhancedAnalysisResponse)
def analyze_career(request: AnalysisRequest, db: Session = Depends(get_db)):
    target_job = request.target_job
    user_skills = [s.strip() for s in request.user_skills]
    user_skills_lower = [s.lower() for s in user_skills]
    user_experience = request.user_experience

    parsed_skills = parse_user_skills(user_skills, user_experience)
    
    target_family = determine_job_family(target_job, user_skills)
    
    if not target_family:
        return to_camel_case({
            "target_job": target_job,
            "job_type": target_family,
            "matched_jobs": [],
            "gap_analysis": {
                "skills": [],
                "experience": {"required": "不限", "user": user_experience, "gap": 0},
                "education": {"required": "不限", "market_trend": ""}
            },
            "action_plan": {"short_term": {"items": ["无法识别目标岗位族，请补充更具体的岗位信息"]}, "medium_term": {"items": []}, "long_term": {"items": []}},
            "competition_analysis": {"supply_demand": "", "competitor_profile": "", "user_advantage": "", "user_disadvantage": "", "market_insight": ""},
            "salary_analysis": {"basic_stats": {"min": 0, "max": 0, "avg": 0, "median": 0}},
            "skill_recommendations": {"recommendations": []},
            "target_feasibility": {
                "feasibility_score": 0,
                "is_reasonable": False,
                "warnings": [{"type": "danger", "message": "无法识别目标岗位，请输入更具体的岗位名称"}],
                "suggestions": ["尝试输入完整的岗位名称，如'前端工程师'或'Java开发工程师'"],
                "recommendation": "重新规划"
            }
        })
    
    all_jobs = db.query(Job).all()
    
    same_family_jobs = [job for job in all_jobs if get_job_family(job.title) == target_family]
    
    matched_jobs_query = []
    target_lower = target_job.lower()
    corrected_target = target_lower
    for typo, correct in TYPO_CORRECTIONS.items():
        if typo.lower() in corrected_target.lower() and typo.lower() != correct.lower():
            corrected_target = corrected_target.lower().replace(typo.lower(), correct.lower())
    
    target_core_keywords = set()
    base_keywords = ["工程师", "开发", "设计师", "经理", "架构师", "专家", "资深", "高级", "初级", "助理"]
    temp_target = corrected_target
    for kw in base_keywords:
        temp_target = temp_target.replace(kw, "")
    for word in temp_target.split():
        if len(word) >= 2:
            target_core_keywords.add(word)
    
    for job in same_family_jobs:
        job_title_lower = job.title.lower()
        
        if target_lower in job_title_lower or corrected_target in job_title_lower:
            matched_jobs_query.append(job)
            continue
        
        job_core_keywords = set()
        temp_job = job_title_lower
        for kw in base_keywords:
            temp_job = temp_job.replace(kw, "")
        for word in temp_job.split():
            if len(word) >= 2:
                job_core_keywords.add(word)
        
        if target_core_keywords and job_core_keywords:
            intersection = target_core_keywords & job_core_keywords
            if intersection:
                matched_jobs_query.append(job)
            elif "全栈" in job_title_lower and ("前端" in corrected_target or "后端" in corrected_target):
                matched_jobs_query.append(job)
    
    matched_jobs_query = list(set(matched_jobs_query))
    
    if len(matched_jobs_query) < 3:
        has_low_data = True
    else:
        has_low_data = False
    
    if user_experience >= 5:
        senior_jobs = [job for job in matched_jobs_query if any(kw in job.title.lower() for kw in ["高级", "资深", "专家", "senior", "expert"])]
        if senior_jobs:
            matched_jobs_query = senior_jobs + [j for j in matched_jobs_query if j not in senior_jobs]
    
    matched_jobs = []
    target_salary = request.target_salary or ""
    
    avg_salary_in_family = analyze_salary_range(same_family_jobs)
    family_avg_salary = avg_salary_in_family.get("avg", 0)
    
    for job in matched_jobs_query[:15]:
        job_family = get_job_family(job.title)
        
        if job_family != target_family:
            continue
        
        job_title_lower = job.title.lower()
        job_core_keywords = set()
        base_keywords = ["工程师", "开发", "设计师", "经理", "架构师", "专家", "资深", "高级", "初级", "助理"]
        temp_job = job_title_lower
        for kw in base_keywords:
            temp_job = temp_job.replace(kw, "")
        for word in temp_job.split():
            if len(word) >= 2:
                job_core_keywords.add(word)
        
        pass
        
        if job.salary_min and family_avg_salary > 0:
            if job.salary_min > family_avg_salary * 2:
                continue
        
        sample_size = len(same_family_jobs)
        match_result = calculate_family_match_score(job, user_skills_lower, user_experience, target_salary, sample_size)
        
        # 样本不足时，任然保留岗位用于展示
        if match_result["score"] is not None and match_result["score"] >= 20:
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
                match_score=match_result["score"],
                match_status=match_result["status"],
                job_type=job_family,
                description=job.description[:500] if job.description else None,
                source=job.source,
                source_url=job.source_url,
            ))
        elif match_result["status"] == "待评估":
            # 样本不足时，仍保留岗位，但标记为待评估
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
                match_score=None,
                match_status="待评估",
                job_type=job_family,
                description=job.description[:500] if job.description else None,
                source=job.source,
                source_url=job.source_url,
            ))
    
    # 排序：正常岗位按分数降序，待评估岗位按薪资/经验排
    normal_jobs = [j for j in matched_jobs if j.match_status == "正常"]
    pending_jobs = [j for j in matched_jobs if j.match_status == "待评估"]
    normal_jobs.sort(key=lambda x: x.match_score or 0, reverse=True)
    pending_jobs.sort(key=lambda x: (x.salary_range, x.experience_requirement or ""), reverse=True)
    matched_jobs = normal_jobs + pending_jobs
    
    show_count = min(5, len(matched_jobs))
    if len(matched_jobs) < 3:
        has_low_data = True
    
    # 获取同族岗位技能（包含真实频率）
    all_skills = extract_common_skills(same_family_jobs)
    all_skills_dict = {skill.lower(): count for skill, count in all_skills}
    relevant_skills = set(get_relevant_skills(target_family))
    
    user_skill_types = set()
    for family, indicators in JOB_FAMILY_SKILL_INDICATORS.items():
        for skill in user_skills:
            if any(indicator in skill.lower() for indicator in indicators):
                user_skill_types.add(family.replace("族", ""))
                break
    
    is_transition = len(user_skill_types) > 0 and target_family.replace("族", "") not in user_skill_types
    
    # 获取目标岗位技能图谱（基于内置的岗位技能要求）
    target_skill_map = get_target_level_skill_map(target_family, target_job)

    # 构建用户技能知识图谱（使用规范化的技能数据）
    user_normalized = set(s.lower() for s in parsed_skills['normalized'])
    user_has_tooling = set(s.lower() for s in parsed_skills['has_tooling'])
    user_has_frameworks = set(s.lower() for s in parsed_skills['has_frameworks'])
    user_implied_skills = set(s.lower() for s in parsed_skills.get('implied_skills', []))
    user_proficient_implied = set(s.lower() for s in parsed_skills.get('proficient_skills', []))
    user_proficient_frameworks = set(s.lower() for s in parsed_skills.get('proficient_frameworks', []))
    user_skill_domains = set(parsed_skills.get('skill_domains', []))
    user_universal_patterns = parsed_skills.get('universal_patterns', [])
    user_skill_levels = parsed_skills.get('skill_levels', {})

    # 工具到技能的映射
    TOOL_TO_SKILL_MAP = {
        'webpack': 'Webpack', 'vite': 'Vite', 'eslint': 'Prettier', 'prettier': 'ESLint',
        'git': 'Git', 'docker': 'Docker', 'jenkins': 'Jenkins', 'ci/cd': 'CI/CD',
        'cicd': 'CI/CD', 'nginx': 'Nginx', 'linux': 'Linux', 'k8s': 'Kubernetes',
    }

    def get_user_level_for_skill(skill_name: str) -> str:
        """
        获取用户对某个技能的熟练度（优先使用 skill_levels）
        """
        skill_lower = skill_name.lower()

        # 1. 直接查找
        if skill_name in user_skill_levels:
            return user_skill_levels[skill_name]
        for k, v in user_skill_levels.items():
            if k.lower() == skill_lower:
                return v

        # 2. 检查组合技能的部分匹配（如 "React技术栈" → "React"）
        parts = [p.strip() for p in skill_lower.split('/')]
        for part in parts:
            if part in user_skill_levels:
                return user_skill_levels[part]
            for k, v in user_skill_levels.items():
                if k.lower() == part:
                    return v
            if part in TOOL_TO_SKILL_MAP:
                tool_skill = TOOL_TO_SKILL_MAP[part]
                if tool_skill in user_skill_levels:
                    return user_skill_levels[tool_skill]
            if part in ['javascript', 'typescript', 'html', 'css', 'http', '浏览器']:
                for k, v in user_skill_levels.items():
                    if part in k.lower():
                        return v
            for k, v in user_skill_levels.items():
                if k.lower() in part:
                    return v

        # 3. 工具映射
        if skill_lower in TOOL_TO_SKILL_MAP:
            tool_skill = TOOL_TO_SKILL_MAP[skill_lower]
            if tool_skill in user_skill_levels:
                return user_skill_levels[tool_skill]

        return "不了解"

    # 经验先验规则：3年以上经验，基础技能默认至少"了解"
    BASIC_SKILLS_BY_FAMILY = {
        "前端族": ["javascript", "typescript", "html", "css", "http", "http协议", "浏览器"],
        "后端族": ["java", "python", "go", "sql", "http", "http协议", "linux", "git"],
        "移动端族": ["swift", "kotlin", "java", "objective-c", "git"],
        "数据族": ["python", "sql", "r", "统计学", "git"],
    }
    EXPERIENCE_BASIC_KNOWLEDGE_LEVEL = "了解"  # 3年+经验，基础技能至少"了解"
    
    gap_analysis_skills = []
    missing_skills = []
    transferable_skills = []
    
    # 技能来源锁定：差距分析必须且仅基于【目标岗位】的技能要求
    if target_skill_map:
        for level_type, skills_list in target_skill_map.items():
            for skill in skills_list:
                skill_lower = skill.lower()
                
                # 处理组合技能名称（如 "Webpack/Vite" → 检查 "webpack" 或 "vite"）
                parts = [p.strip() for p in skill_lower.split('/')]
                
                # 检查用户是否直接输入了组合技能或任一组成部分
                has_skill = skill_lower in user_normalized
                
                # 检查是否有相关技能（别名匹配或组合技能部分匹配）
                if not has_skill:
                    for user_skill in parsed_skills['normalized']:
                        user_skill_lower = user_skill.lower()
                        # 检查完整匹配或部分匹配
                        if skill_lower in user_skill_lower or user_skill_lower in skill_lower:
                            has_skill = True
                            break
                        # 检查组合技能的任一部分
                        for part in parts:
                            if part in user_skill_lower:
                                has_skill = True
                                break
                        if has_skill:
                            break
                
                # 检查工程化工具（Webpack/Vite/CI/CD等）- 支持组合技能名称
                knows_tooling = skill_lower in user_has_tooling
                if not knows_tooling:
                    for part in parts:
                        if part in user_has_tooling:
                            knows_tooling = True
                            break
                
                # 检查框架技能（区分普通框架和熟练框架）- 支持组合技能名称
                knows_framework = skill_lower in user_has_frameworks
                proficient_framework = skill_lower in user_proficient_frameworks
                if not knows_framework and not proficient_framework:
                    for part in parts:
                        if part in user_has_frameworks:
                            knows_framework = True
                            break
                        if part in user_proficient_frameworks:
                            proficient_framework = True
                            break
                
                # 检查隐含技能（如Vue/React → JavaScript）- 支持组合技能名称
                knows_implied = skill_lower in user_implied_skills
                proficient_implied = skill_lower in user_proficient_implied
                if not knows_implied and not proficient_implied:
                    for part in parts:
                        if part in user_implied_skills:
                            knows_implied = True
                            break
                        if part in user_proficient_implied:
                            proficient_implied = True
                            break
                
                # 检查技能领域匹配（如 Webpack/Vite → 前端工程化）
                knows_domain = False
                for domain, tools in TOOL_TO_SKILL_DOMAIN.items():
                    if domain in skill_lower or skill_lower in domain:
                        if domain in user_skill_domains:
                            knows_domain = True
                            break
                        for user_tool in user_normalized:
                            for tool in tools:
                                if tool in user_tool.lower() or user_tool.lower() in tool:
                                    knows_domain = True
                                    break
                            if knows_domain:
                                break
                        if knows_domain:
                            break
                
                # 检查"通用"模式（如 Vue和React通用 → React和Vue都熟练）
                knows_from_universal = False
                proficient_from_universal = False
                for pattern in user_universal_patterns:
                    for fw in pattern.get('frameworks', []):
                        if fw in skill_lower or any(fw in part for part in parts):
                            knows_from_universal = True
                            if pattern.get('proficiency') in ['精通', '熟练']:
                                proficient_from_universal = True
                            break
                
                user_level = get_user_level_for_skill(skill)

                gap_result = evaluate_gap(level_type, user_level)
                difficulty = determine_gap_difficulty(skill, level_type, user_level)
                
                # 计算技能频率等级（只返回枚举值）
                freq_count = all_skills_dict.get(skill_lower, 0)
                sample_size = len(same_family_jobs)
                
                if sample_size == 0:
                    frequency_level = "样本不足"
                elif sample_size < 500:
                    if freq_count == 0:
                        frequency_level = "低频"
                    elif freq_count <= 2:
                        frequency_level = "低频"
                    elif freq_count <= 5:
                        frequency_level = "中频"
                    else:
                        frequency_level = "高频"
                else:
                    if freq_count == 0:
                        frequency_level = "低频"
                    elif freq_count <= sample_size * 0.1:
                        frequency_level = "低频"
                    elif freq_count <= sample_size * 0.3:
                        frequency_level = "中频"
                    else:
                        frequency_level = "高频"
                
                gap_analysis_skills.append({
                    "skill": skill,
                    "required_level": level_type,
                    "user_level": user_level,
                    "gap": gap_result["gap"],
                    "difficulty": difficulty,
                    "frequency": frequency_level
                })
                
                if gap_result["gap"] in ["中", "大"]:
                    missing_skills.append(skill)
                elif gap_result["gap"] == "小":
                    transferable_skills.append(skill)
    else:
        # 如果没有内置技能图谱，回退到基于岗位族技能的分析
        for skill, count in all_skills[:15]:
            skill_lower = skill.lower()
            
            has_skill = skill_lower in user_normalized
            
            sample_size = len(same_family_jobs)
            
            if sample_size == 0:
                frequency_level = "样本不足"
            elif sample_size < 500:
                if count == 0:
                    frequency_level = "低频"
                elif count <= 2:
                    frequency_level = "低频"
                elif count <= 5:
                    frequency_level = "中频"
                else:
                    frequency_level = "高频"
            else:
                if count == 0:
                    frequency_level = "低频"
                elif count <= sample_size * 0.1:
                    frequency_level = "低频"
                elif count <= sample_size * 0.3:
                    frequency_level = "中频"
                else:
                    frequency_level = "高频"
            
            if skill in relevant_skills:
                if has_skill:
                    gap_analysis_skills.append({
                        "skill": skill,
                        "required_level": "熟练",
                        "user_level": "熟练",
                        "gap": "无",
                        "difficulty": "小",
                        "frequency": frequency_level
                    })
                else:
                    gap_analysis_skills.append({
                        "skill": skill,
                        "required_level": "熟练",
                        "user_level": "不了解",
                        "gap": "大",
                        "difficulty": "中",
                        "frequency": frequency_level
                    })
                    missing_skills.append(skill)
    
    exp_requirements = [parse_experience(job.experience_requirement) for job in same_family_jobs if job.experience_requirement]
    avg_min_exp = 0
    avg_max_exp = 0
    if exp_requirements:
        avg_min_exp = sum(e[0] for e in exp_requirements) / len(exp_requirements)
        avg_max_exp = sum(e[1] for e in exp_requirements) / len(exp_requirements)
        exp_required = f"{int(avg_min_exp)}-{int(avg_max_exp)}年"
    else:
        exp_required = "不限"
    
    edu_requirements = [job.education_requirement for job in same_family_jobs if job.education_requirement]
    common_edu = max(set(edu_requirements), key=edu_requirements.count) if edu_requirements else "不限"
    
    salary_analysis = analyze_salary_range(same_family_jobs)
    salary_by_level = analyze_salary_by_level(same_family_jobs, user_experience)
    
    if has_low_data:
        warning = f"⚠️ 该方向同族岗位数据有限，以下为最佳匹配结果"
    else:
        warning = ""
    
    current_job = request.current_job if request.current_job else ""
    current_family = determine_job_family(current_job, user_skills)
    
    if not current_family:
        current_family = "未确定"
    
    transition_type = get_transition_type(current_family, target_family)
    transition_analysis = generate_transition_analysis(current_family, target_family, user_skills)
    
    # 计算平均匹配度和最高匹配度
    avg_match_score = 50.0
    max_match_score = 0.0
    if matched_jobs:
        scores = [j.match_score for j in matched_jobs if j.match_score is not None]
        if scores:
            avg_match_score = sum(scores) / len(scores)
            max_match_score = max(scores)

    is_career_change = transition_type == "跨族转型"

    phase_action_plan = generate_phase_action_plan(
        gap_analysis_skills,
        target_family,
        target_job,
        request.target_company,
        avg_match_score,
        max_match_score,
        user_experience,
        is_career_change,
        user_skills,
        parsed_skills
    )
    
    action_plan = {
        "short_term": {
            "description": phase_action_plan["short_term"]["description"],
            "skills": phase_action_plan["short_term"]["skills"],
            "project": phase_action_plan["short_term"]["project"],
            "interview_prep": phase_action_plan["short_term"].get("interview_prep", []),
            "focus": phase_action_plan["short_term"].get("focus", ""),
            "items": []
        },
        "medium_term": {
            "description": phase_action_plan["medium_term"]["description"],
            "skills": phase_action_plan["medium_term"]["skills"],
            "project": phase_action_plan["medium_term"]["project"],
            "interview_prep": phase_action_plan["medium_term"].get("interview_prep", []),
            "items": []
        },
        "long_term": {
            "description": phase_action_plan["long_term"]["description"],
            "skills": phase_action_plan["long_term"]["skills"],
            "project": phase_action_plan["long_term"]["project"],
            "interview_prep": phase_action_plan["long_term"].get("interview_prep", []),
            "items": []
        },
        "transition_type": transition_type,
        "transition_analysis": transition_analysis,
        "time_estimate": phase_action_plan.get("time_estimate", {})
    }
    
    if warning:
        action_plan["short_term"]["items"].append(warning)
    
    if transition_type == "同族晋升":
        action_plan["short_term"]["items"].append(f"📈 同族晋升：{target_family}内职业发展")
        action_plan["short_term"]["items"].append(f"✅ 优势：已有技能可复用、行业经验可迁移")
    else:
        action_plan["short_term"]["items"].append(f"🚀 {transition_type}：{current_family} → {target_family}")
        action_plan["short_term"]["items"].append(f"💡 优势：可迁移的软技能、跨视角的理解能力")
        if transition_analysis.get("transferable_skills"):
            action_plan["short_term"]["items"].append(f"🔄 可迁移技能：{', '.join(transition_analysis['transferable_skills'])}")
    
    short_skills = phase_action_plan["short_term"]["skills"][:3]
    for skill_action in short_skills:
        depth_label = f"[{skill_action.get('learning_depth', '入门')}]"
        action_plan["short_term"]["items"].append(f"📚 核心学习 {depth_label}：{skill_action['skill']}（优先级分{skill_action['priority_score']}）")
        action_plan["short_term"]["items"].append(f"   🔍 学习方向：{', '.join(skill_action['learning_resources'][:2])}")
        action_plan["short_term"]["items"].append(f"   ⏱️ 预计时间：{skill_action['estimated_time']}，难度：{skill_action['difficulty']}")
    
    action_plan["short_term"]["items"].append(f"🎯 短期项目：{phase_action_plan['short_term']['project']}")
    
    medium_skills = phase_action_plan["medium_term"]["skills"][:2]
    for skill_action in medium_skills:
        depth_label = f"[{skill_action.get('learning_depth', '入门')}]"
        action_plan["medium_term"]["items"].append(f"📚 进阶学习 {depth_label}：{skill_action['skill']}（优先级分{skill_action['priority_score']}）")
        action_plan["medium_term"]["items"].append(f"   🔍 学习方向：{', '.join(skill_action['learning_resources'][:2])}")
    
    action_plan["medium_term"]["items"].append(f"🎯 中期项目：{phase_action_plan['medium_term']['project']}")
    for prep_item in phase_action_plan["medium_term"]["interview_prep"]:
        action_plan["medium_term"]["items"].append(prep_item)
    if user_experience < avg_min_exp:
        exp_gap = int(avg_min_exp - user_experience)
        action_plan["medium_term"]["items"].append(f"💼 积累 {exp_gap} 年相关工作经验")
    elif user_experience > avg_max_exp:
        action_plan["medium_term"]["items"].append(f"👑 你的经验超出一般标准，更适合目标高级/资深岗位！")
    
    long_skills = phase_action_plan["long_term"]["skills"][:2]
    for skill_action in long_skills:
        depth_label = f"[{skill_action.get('learning_depth', '入门')}]"
        action_plan["long_term"]["items"].append(f"📚 加分技能 {depth_label}：{skill_action['skill']}（优先级分{skill_action['priority_score']}）")
    
    for prep_item in phase_action_plan["long_term"]["interview_prep"]:
        action_plan["long_term"]["items"].append(prep_item)
    
    action_plan["long_term"]["items"].append(f"🎯 长期项目：{phase_action_plan['long_term']['project']}")
    
    total_jobs = len(same_family_jobs)
    high_match_jobs = len([j for j in matched_jobs if j.match_score >= 60])
    
    if total_jobs > 5:
        supply_demand = f"{target_family}岗位需求稳定，共找到{total_jobs}个相关岗位"
    elif total_jobs > 2:
        supply_demand = f"{target_family}岗位相对稀缺，共找到{total_jobs}个相关岗位"
    else:
        supply_demand = f"{target_family}岗位较少，建议扩大搜索范围"
    
    competitor_profile = f"通常要求{common_edu}学历，{exp_required}经验，掌握{len(all_skills[:5])}项核心技能"
    
    matched_skill_count = len([s for s in gap_analysis_skills if s["gap"] == "达标"])
    total_required_skills = len(gap_analysis_skills)
    
    if transition_type == "同族晋升":
        user_advantage = f"📈 {transition_type}：已有{user_experience}年{target_family}经验，技能可复用性高"
    elif transition_type == "跨族转型":
        user_advantage = f"🚀 {transition_type}：具备{', '.join(user_skill_types)}背景，跨领域视角是优势"
    elif matched_skill_count / max(total_required_skills, 1) >= 0.7:
        user_advantage = f"✅ 技能匹配度高（{matched_skill_count}/{total_required_skills}），具备较强竞争力"
    elif matched_skill_count / max(total_required_skills, 1) >= 0.4:
        user_advantage = f"💪 部分技能匹配（{matched_skill_count}/{total_required_skills}），有一定基础"
    else:
        user_advantage = "🚀 学习能力强，有转型决心"
    
    if transition_type == "跨族转型":
        user_disadvantage = f"⚠️ 需要重建{target_family}知识体系，预计需要{transition_analysis.get('estimated_months', 12)}个月系统学习"
        if missing_skills:
            user_disadvantage += f"，需补充{len(missing_skills)}项核心技能"
    elif missing_skills:
        user_disadvantage = f"❌ 缺乏{len(missing_skills)}项核心技能：{', '.join(missing_skills[:3])}"
        if user_experience < avg_min_exp:
            user_disadvantage += f"；经验不足（需要{exp_required}）"
    else:
        user_disadvantage = "💡 经验可能不足，需要更多项目历练"
    
    # 按 gap 等级排序：优先显示 gap=大 的技能
    missing_skills_sorted = sorted(
        missing_skills, 
        key=lambda s: (
            0 if any(g["skill"] == s and g["gap"] == "大" for g in gap_analysis_skills) else 1,
            0 if any(g["skill"] == s and g["gap"] == "中" for g in gap_analysis_skills) else 1
        )
    )
    
    competition_analysis = {
        "supply_demand": supply_demand,
        "competitor_profile": competitor_profile,
        "user_advantage": user_advantage,
        "user_disadvantage": user_disadvantage,
        "market_insight": f"分析了{total_jobs}个{target_family}岗位，{high_match_jobs}个岗位匹配度超过60%",
        "missing_skills_list": missing_skills_sorted,
        "missing_skills_by_gap": {
            "大": [s for s in missing_skills_sorted if any(g["skill"] == s and g["gap"] == "大" for g in gap_analysis_skills)],
            "中": [s for s in missing_skills_sorted if any(g["skill"] == s and g["gap"] == "中" for g in gap_analysis_skills)]
        }
    }
    
    skill_recommendations = generate_skill_recommendations(missing_skills, target_family, user_skills, parsed_skills)
    
    target_feasibility = analyze_target_feasibility(
        total_jobs=total_jobs,
        high_match_jobs=high_match_jobs,
        user_skills=user_skills,
        target_family=target_family,
        target_job=target_job
    )
    
    if request.user_id:
        analysis_result = AnalysisResult(
            user_id=request.user_id,
            target_job_title=target_job,
            gap_analysis=json.dumps(gap_analysis_skills),
            action_plan=json.dumps(action_plan)
        )
        db.add(analysis_result)
        db.commit()
    
    # 构建薪资分析数据
    if salary_by_level.get("has_data"):
        enhanced_salary = {
            "by_level": salary_by_level,
            "basic_stats": salary_analysis
        }
    else:
        enhanced_salary = {
            "message": salary_by_level.get("message", "薪资数据有限"),
            "basic_stats": salary_analysis
        }
    
    response_data = EnhancedAnalysisResponse(
        target_job=target_job,
        job_type=target_family,
        matched_jobs=matched_jobs[:show_count],
        gap_analysis={
            "skills": gap_analysis_skills,
            "experience": {
                "market_required": exp_required,
                "user": user_experience,
                "gap": max(0, int(avg_min_exp - user_experience)) if user_experience < avg_min_exp else 0
            },
            "education": {
                "required": common_edu,
                "market_trend": f"在{total_jobs}个岗位中，{edu_requirements.count(common_edu)}个要求{common_edu}学历"
            }
        },
        action_plan=action_plan,
        transition_analysis=transition_analysis,
        competition_analysis=competition_analysis,
        salary_analysis=enhanced_salary,
        skill_recommendations=skill_recommendations,
        target_feasibility=target_feasibility,
        market_skills=[skill for skill, count in all_skills[:12] 
                       if skill.lower() not in user_skills_lower 
                       and not any(skill.lower() in s or s in skill.lower() for s in user_skills_lower)
                       ][:6] if all_skills else []
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
