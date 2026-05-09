#!/usr/bin/env python3
"""
技能匹配修复验证
验证用户输入"Vue和React通用"后，JavaScript应该显示"了解"或"熟练"
"""

import sys
sys.path.insert(0, '/workspace/backend')

from main import normalize_input, parse_user_skills, is_valid_skill

user_input = "Vue和React通用"
target_skills = ["JavaScript", "React", "Vue", "Webpack", "Vite", "TypeScript", "CSS", "HTML"]

print("=" * 70)
print("技能匹配修复验证")
print("=" * 70)

print(f"\n📥 用户输入: \"{user_input}\"")

print("\n" + "-" * 70)
print("【验证1】is_valid_skill() - 垃圾词过滤")
print("-" * 70)

test_tokens = ['vue', 'react通', '会vue', '熟悉react', 'react', 'vue和react通用', 'webpack']
for token in test_tokens:
    is_valid = is_valid_skill(token)
    print(f"  is_valid_skill('{token}') = {is_valid}")

print("\n" + "-" * 70)
print("【验证2】parse_user_skills() - 含隐含技能")
print("-" * 70)

parsed = parse_user_skills([user_input])
print(f"normalized (规范化): {parsed['normalized']}")
print(f"has_tooling (工具类): {parsed['has_tooling']}")
print(f"has_frameworks (框架类): {parsed['has_frameworks']}")
print(f"has_core (核心语言): {parsed['has_core']}")
print(f"implied_skills (隐含技能): {parsed['implied_skills']}")

print("\n" + "-" * 70)
print("【验证3】技能匹配 - 与目标技能对比")
print("-" * 70)

user_normalized = set(s.lower() for s in parsed['normalized'])
user_has_tooling = set(s.lower() for s in parsed['has_tooling'])
user_has_frameworks = set(s.lower() for s in parsed['has_frameworks'])
user_implied_skills = set(s.lower() for s in parsed['implied_skills'])

print(f"\n隐含技能集合: {user_implied_skills}")

print("\n目标技能匹配结果:")
for skill in target_skills:
    skill_lower = skill.lower()
    
    has_skill = skill_lower in user_normalized
    knows_tooling = skill_lower in user_has_tooling
    knows_framework = skill_lower in user_has_frameworks
    knows_implied = skill_lower in user_implied_skills
    
    if has_skill:
        user_level = "熟练"
        reason = "直接输入"
    elif knows_implied:
        user_level = "了解"
        reason = f"隐含推断({skill_lower}←框架)"
    elif knows_tooling:
        user_level = "熟练"
        reason = "工具类"
    elif knows_framework:
        user_level = "了解"
        reason = "框架类"
    else:
        user_level = "不了解"
        reason = "未识别"
    
    status = "✅" if user_level != "不了解" else "❌"
    print(f"  {status} {skill:12} → {user_level:4} ({reason})")

print("\n" + "=" * 70)
print("【修复总结】")
print("=" * 70)

javascript_level = "不了解"
for skill in target_skills:
    if skill.lower() == "javascript":
        skill_lower = skill.lower()
        if skill_lower in user_normalized:
            javascript_level = "熟练"
        elif skill_lower in user_implied_skills:
            javascript_level = "了解"
        break

print(f"\nJavaScript 最终判定: {javascript_level}")
print(f"预期结果: 了解或熟练")
print(f"验证: {'✅ 通过' if javascript_level in ['了解', '熟练'] else '❌ 未通过'}")
