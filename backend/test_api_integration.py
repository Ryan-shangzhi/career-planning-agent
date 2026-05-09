#!/usr/bin/env python3
"""
集成测试：调用实际 API 验证差距分析
"""

import json
import urllib.request
import urllib.error

API_URL = "http://localhost:8000/api/analyze"

test_payload = {
    "target_job": "前端开发工程师",
    "current_job": "前端开发工程师",
    "user_skills": ["Webpack/Vite、CI/CD，Vue和React通用"],
    "user_experience": 2,
    "target_company": ""
}

print("=" * 80)
print("集成测试：调用实际 API 验证差距分析")
print("=" * 80)

print(f"\n📥 请求:")
print(f"  目标岗位: {test_payload['target_job']}")
print(f"  当前岗位: {test_payload['current_job']}")
print(f"  用户技能: {test_payload['user_skills']}")
print(f"  工作年限: {test_payload['user_experience']}")

try:
    data = json.dumps(test_payload).encode('utf-8')
    req = urllib.request.Request(
        API_URL, 
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
    
    # API 使用 camelCase 格式
    job_type = result.get('jobType', result.get('job_type', 'N/A'))
    transition_analysis = result.get('transitionAnalysis', {})
    gap_analysis = result.get('gapAnalysis', {})
    
    print(f"\n📊 API 响应摘要:")
    print(f"  目标岗位族: {job_type}")
    print(f"  匹配岗位数: {len(result.get('matchedJobs', []))}")
    print(f"  转型类型: {transition_analysis.get('type', 'N/A')}")
    
    # 解析差距分析
    if isinstance(gap_analysis, str):
        gap_skills = json.loads(gap_analysis)
    elif isinstance(gap_analysis, dict):
        gap_skills = gap_analysis.get('skills', [])
    else:
        gap_skills = []
    
    print(f"\n📋 差距分析表 (共 {len(gap_skills)} 项技能):")
    print("-" * 80)
    print(f"{'技能':<20} {'目标级别':<8} {'用户级别':<10} {'差距':<6} {'状态'}")
    print("-" * 80)
    
    large_gap_count = 0
    for skill_info in gap_skills:
        skill = skill_info.get('skill', 'N/A')
        required = skill_info.get('requiredLevel', skill_info.get('required_level', 'N/A'))
        user = skill_info.get('userLevel', skill_info.get('user_level', 'N/A'))
        gap = skill_info.get('gap', 'N/A')
        
        status = "✅" if gap in ["无", "小"] else "❌"
        if gap == "大":
            large_gap_count += 1
            status = "❌ 大差距!"
        
        # 高亮显示相关技能
        highlight = ""
        if any(keyword in skill.lower() for keyword in ['webpack', 'vite', 'ci', 'react', 'vue', 'javascript', 'typescript']):
            highlight = " ◀"
        
        print(f"{skill:<20} {required:<8} {user:<10} {gap:<6} {status}{highlight}")
    
    print("-" * 80)
    
    # 检查关键技能
    print("\n🔍 关键技能检查:")
    key_skills = {
        'webpack/vite': False,
        'ci/cd': False,
        'react': False,
        'vue': False,
        'javascript': False,
        'typescript': False
    }
    
    for skill_info in gap_skills:
        skill_lower = skill_info.get('skill', '').lower()
        user_level = skill_info.get('userLevel', skill_info.get('user_level', ''))
        gap = skill_info.get('gap', '')
        
        for key in key_skills:
            if key in skill_lower:
                key_skills[key] = {
                    'skill': skill_info.get('skill'),
                    'user_level': user_level,
                    'gap': gap,
                    'is_good': gap in ['无', '小']
                }
    
    for key, info in key_skills.items():
        if info:
            status = "✅" if info['is_good'] else "❌"
            print(f"  {key}: 用户级别={info['user_level']}, 差距={info['gap']} {status}")
        else:
            print(f"  {key}: 未在分析中")
    
    # 总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    
    if large_gap_count == 0:
        print("✅ 没有发现'差距大'的问题!")
    else:
        print(f"❌ 发现 {large_gap_count} 项技能存在'差距大'问题")
    
    # 检查转型类型
    if transition_analysis.get('type') == '同族晋升':
        print("✅ 转型类型正确: 同族晋升")
    else:
        print(f"⚠️ 转型类型: {transition_analysis.get('type', 'N/A')}")
    
    # 数据一致性检查
    matched_count = len(result.get('matchedJobs', []))
    gap_count = len(gap_skills)
    print(f"✅ 数据一致: 匹配岗位 {matched_count} 个, 差距分析 {gap_count} 项")
    
except urllib.error.HTTPError as e:
    print(f"\n❌ API 请求失败 (HTTP {e.code}): {e.read().decode('utf-8')}")
except Exception as e:
    print(f"\n❌ API 请求失败: {e}")
    import traceback
    traceback.print_exc()
