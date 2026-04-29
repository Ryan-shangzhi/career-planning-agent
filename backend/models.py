from sqlalchemy import Column, Integer, String, Text, DECIMAL, BOOLEAN, TIMESTAMP, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    industry = Column(String(50))
    company_type = Column(String(50))
    description = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.now)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"))
    company_name = Column(String(100))
    industry = Column(String(50))
    job_type = Column(String(50))
    location = Column(String(100))
    salary_min = Column(DECIMAL(10, 2))
    salary_max = Column(DECIMAL(10, 2))
    experience_requirement = Column(String(50))
    education_requirement = Column(String(50))
    description = Column(Text)
    skills = Column(Text)
    tags = Column(Text)
    source = Column(String(50))
    source_url = Column(String(500))
    created_at = Column(TIMESTAMP, default=datetime.now)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    
    company = relationship("Company")

class JobSkill(Base):
    __tablename__ = "job_skills"
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    skill_name = Column(String(100))
    proficiency_level = Column(String(20))
    is_required = Column(BOOLEAN, default=True)
    
    job = relationship("Job")

class SkillCategory(Base):
    __tablename__ = "skill_categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)

class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey("skill_categories.id"))
    description = Column(Text)
    
    category = relationship("SkillCategory")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)
    current_job = Column(String(100))
    experience_years = Column(Integer)
    skills = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.now)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    target_job_id = Column(Integer, ForeignKey("jobs.id"))
    target_job_title = Column(String(100))
    gap_analysis = Column(JSON)
    action_plan = Column(JSON)
    created_at = Column(TIMESTAMP, default=datetime.now)
    
    user = relationship("User")
    job = relationship("Job")
