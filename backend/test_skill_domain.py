#!/usr/bin/env python3
"""
测试技能领域映射：前端工程化
"""

import json
import urllib.request

API_URL = "http://localhost:8000/api/analyze"

test_payload = {
    "target_job": "中级前端工程师",
    "current_job": "前端开发工程师",
    "user_skills": ["Webpack/Vite、CI/CD，Vue和React通用"],
    "user_experience": 2,
    "target_company": ""
}

print("=" * 80)
print("技能领域映射测试：中级前端工程师")
print("=" * 80)

print(f"\n📥 请求:")
print(f"  目标岗位: {test_payload['target_job']}")
print(f"  用户技能: {test_payload['user_skills']}")

data = json.dumps(test_payload).encode('utf-8')
req = urllib.request.Request(API_URL, data=data, headers={'Content-Type': 'application/json'})

with urllib.request.urlopen(req, timeout=30) as response:
    result = json.loads(response.read().decode('utf-8'))

gap_skills = result.get('gapAnalysis', {}).get('skills', [])

print(f"\n📋 差距分析表:")
print("-" * 80)
print(f"{'技能':<20} {'目标级别':<8} {'用户级别':<10} {'差距':<6} {'状态'}")
print("-" * 80)

for skill_info in gap_skills:
    skill = skill_info.get('skill', 'N/A')
    required = skill_info.get('requiredLevel', 'N/A')
    user = skill_info.get('userLevel', 'N/A')
    gap = skill_info.get('gap', 'N/A')
    
    status = "✅" if gap in ["无", "小"] else "❌"
    
    # 高亮前端工程化
    highlight = " ◀" if "工程化" in skill else ""
    
    print(f"{skill:<20} {required:<8} {user:<10} {gap:<6} {status}{highlight}")

print("-" * 80)

# 检查前端工程化
print("\n🔍 前端工程化技能检查:")
for skill_info in gap_skills:
    skill = skill_info.get('skill', '')
    if '工程化' in skill:
        user_level = skill_info.get('userLevel', 'N/A')
        gap = skill_info.get('gap', 'N/A')
        status = "✅ 正确识别!" if user_level == "熟练" else f"❌ 用户级别={user_level}"
        print(f"  {skill}: 用户级别={user_level}, 差距={gap} {status}")
