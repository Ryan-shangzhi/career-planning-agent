#!/usr/bin/env python3
"""
技能匹配过程详细追踪
"""

import sys
sys.path.insert(0, '/workspace/backend')

from main import normalize_input, parse_user_skills, extract_skills_from_text

user_input = "Webpack/Vite、CI/CD，Vue和React通用"
target_skills = ["JavaScript", "React", "Vue", "Webpack", "Vite", "TypeScript", "CSS", "HTML"]

print("=" * 70)
print("技能匹配详细追踪报告")
print("=" * 70)

print(f"\n📥 用户输入: \"{user_input}\"")

print("\n" + "-" * 70)
print("【步骤1】normalize_input() - 分词处理")
print("-" * 70)

tokens = normalize_input(user_input)
print(f"分词结果: {tokens}")
print(f"共 {len(tokens)} 个词")

print("\n" + "-" * 70)
print("【步骤2】extract_skills_from_text() - 关键词提取")
print("-" * 70)

extracted = extract_skills_from_text(user_input)
print(f"从完整文本中提取到: {extracted}")
print(f"共 {len(extracted)} 个技能")

print("\n" + "-" * 70)
print("【步骤3】parse_user_skills() - 技能分类")
print("-" * 70)

parsed = parse_user_skills([user_input])
print(f"normalized (规范化): {parsed['normalized']}")
print(f"has_tooling (工具类): {parsed['has_tooling']}")
print(f"has_frameworks (框架类): {parsed['has_frameworks']}")
print(f"has_core (核心语言): {parsed['has_core']}")

print("\n" + "-" * 70)
print("【步骤4】技能匹配 - 与目标技能对比")
print("-" * 70)

user_normalized = set(s.lower() for s in parsed['normalized'])
user_has_tooling = set(s.lower() for s in parsed['has_tooling'])
user_has_frameworks = set(s.lower() for s in parsed['has_frameworks'])

print(f"\n用户输入的normalized集合: {user_normalized}")
print(f"用户输入的has_tooling集合: {user_has_tooling}")
print(f"用户输入的has_frameworks集合: {user_has_frameworks}")

print("\n" + "-" * 70)
print("【步骤5】每个目标技能的匹配过程")
print("-" * 70)

for skill in target_skills:
    skill_lower = skill.lower()
    
    print(f"\n▶ 检查技能: {skill}")
    
    # 步骤5.1: 检查 normalized
    step1_match = skill_lower in user_normalized
    print(f"   [1] 'normalized' 匹配: {skill_lower} in {user_normalized}")
    print(f"       结果: {'✅ True' if step1_match else '❌ False'}")
    
    # 步骤5.2: 检查 has_tooling
    step2_match = skill_lower in user_has_tooling
    print(f"   [2] 'has_tooling' 匹配: {skill_lower} in {user_has_tooling}")
    print(f"       结果: {'✅ True' if step2_match else '❌ False'}")
    
    # 步骤5.3: 检查 has_frameworks
    step3_match = skill_lower in user_has_frameworks
    print(f"   [3] 'has_frameworks' 匹配: {skill_lower} in {user_has_frameworks}")
    print(f"       结果: {'✅ True' if step3_match else '❌ False'}")
    
    # 最终判定
    if step1_match:
        user_level = "熟练"
        reason = "命中 normalized"
    elif step2_match:
        user_level = "熟练"
        reason = "命中 has_tooling"
    elif step3_match:
        user_level = "了解"
        reason = "命中 has_frameworks"
    else:
        user_level = "不了解"
        reason = "全部未命中，使用默认值"
    
    print(f"\n   🎯 最终判定: {user_level}")
    print(f"   📝 原因: {reason}")

print("\n" + "=" * 70)
print("【总结】")
print("=" * 70)

matched = []
unmatched = []
for skill in target_skills:
    skill_lower = skill.lower()
    if skill_lower in user_normalized or skill_lower in user_has_tooling or skill_lower in user_has_frameworks:
        matched.append(skill)
    else:
        unmatched.append(skill)

print(f"\n✅ 识别到的技能 ({len(matched)}): {matched}")
print(f"❌ 未识别的技能 ({len(unmatched)}): {unmatched}")

print(f"\n⚠️ 问题诊断:")
print(f"   - 'vue' 不在 normalized 中 (因为分词结果是 'vue和react通用')")
print(f"   - 'vue' 不在 has_tooling 中")
print(f"   - 'vue' 不在 has_frameworks 中 (因为 'vue和react通用' != 'vue')")
print(f"   - 所以 Vue 被判定为'不了解'")
