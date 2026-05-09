"""
JD技能标签入库脚本
使用 extract_skills_from_text() 从 JD 描述中抽取技能标签并写入数据库
"""
import sys
sys.path.insert(0, '/workspace/backend')

from database import get_db, engine
from models import Job, Base
from main import extract_skills_from_text
from sqlalchemy.orm import Session


def extract_skills_for_all_jobs():
    """为所有 JD 抽取技能标签并更新数据库"""
    db = next(get_db())

    jobs = db.query(Job).all()
    print(f"找到 {len(jobs)} 条岗位记录")

    updated_count = 0
    empty_skills_count = 0

    for job in jobs:
        # 从描述和标题中提取技能
        skills = []

        if job.description:
            desc_skills = extract_skills_from_text(job.description)
            skills.extend(desc_skills)

        if job.title:
            title_skills = extract_skills_from_text(job.title)
            skills.extend(title_skills)

        # 去重
        skills = list(set(skills))

        # 写入数据库（逗号分隔）
        if skills:
            job.skills = ",".join(skills)
            updated_count += 1
        else:
            empty_skills_count += 1
            print(f"  警告: {job.title} (ID={job.id}) 未提取到技能标签")

    db.commit()
    print(f"\n完成! 更新了 {updated_count} 条岗位的技能标签")
    print(f"未能提取技能标签的岗位: {empty_skills_count} 条")

    # 显示示例
    print("\n=== 示例 ===")
    sample_jobs = db.query(Job).filter(Job.skills != None, Job.skills != "").limit(5).all()
    for job in sample_jobs:
        print(f"{job.title}: {job.skills[:80]}...")


def regenerate_skills_for_job_family(job_family_keywords: list = None):
    """
    重新为特定岗位族生成技能标签
    job_family_keywords: 如 ["前端", "web开发", "全栈"]
    """
    db = next(get_db())

    query = db.query(Job)
    if job_family_keywords:
        conditions = [Job.title.like(f"%{kw}%") for kw in job_family_keywords]
        from sqlalchemy import or_
        query = query.filter(or_(*conditions))

    jobs = query.all()
    print(f"找到 {len(jobs)} 条符合条件的岗位")

    for job in jobs:
        skills = []
        if job.description:
            skills = extract_skills_from_text(job.description)
        if job.title and not skills:
            skills = extract_skills_from_text(job.title)

        skills = list(set(skills))
        job.skills = ",".join(skills) if skills else None

    db.commit()
    print("更新完成!")


if __name__ == "__main__":
    print("=" * 60)
    print("JD技能标签入库脚本")
    print("=" * 60)
    print()

    # 选项1: 为所有岗位抽取技能标签
    print("[1] 为所有岗位抽取技能标签")
    print("[2] 只为前端岗位抽取技能标签 (推荐)")
    print("[3] 显示当前技能标签统计")
    choice = input("请选择 (1/2/3): ").strip()

    if choice == "1":
        extract_skills_for_all_jobs()
    elif choice == "2":
        regenerate_skills_for_job_family(["前端", "web开发", "全栈", "web3", "小程序"])
    elif choice == "3":
        db = next(get_db())
        total = db.query(Job).count()
        with_skills = db.query(Job).filter(
            Job.skills != None,
            Job.skills != ""
        ).count()
        print(f"总岗位数: {total}")
        print(f"有技能标签的岗位: {with_skills}")
        print(f"无技能标签的岗位: {total - with_skills}")
    else:
        print("无效选择")
