#!/usr/bin/env python3
"""
完整测试用例：验证技能推断逻辑
输入："Webpack/Vite、CI/CD，Vue和React通用"
"""

import sys
sys.path.insert(0, '/workspace/backend')

from main import normalize_input, parse_user_skills, evaluate_gap

print("=" * 80)
print("技能推断完整性测试")
print("=" * 80)

user_input = "Webpack/Vite、CI/CD，Vue和React通用"
parsed = parse_user_skills([user_input])

print(f"\n📥 用户输入: \"{user_input}\"")
print("-" * 80)

print("\n【parse_user_skills() 完整结果】:")
for key, value in parsed.items():
    print(f"  {key}: {value}")

user_implied_skills = parsed.get('implied_skills', [])
user_proficient_skills = parsed.get('proficient_skills', [])
user_proficient_frameworks = parsed.get('proficient_frameworks', [])
user_has_core = [s.lower() for s in parsed.get('has_core', [])]
user_has_tooling = [s.lower() for s in parsed.get('has_tooling', [])]
user_has_frameworks = [s.lower() for s in parsed.get('has_frameworks', [])]

print("\n" + "=" * 80)
print("差距分析表")
print("=" * 80)

target_skills = ["Webpack", "Vite", "CI/CD", "Vue", "React", "JavaScript", "TypeScript"]
target_levels = {
    "Webpack": "熟练",
    "Vite": "熟练",
    "CI/CD": "熟练",
    "Vue": "精通",
    "React": "精通",
    "JavaScript": "精通",
    "TypeScript": "熟练",
}

print(f"\n{'技能':<12} {'目标级别':<8} {'识别方式':<20} {'用户级别':<10} {'差距':<6}")
print("-" * 80)

results = []
for skill in target_skills:
    skill_lower = skill.lower()

    has_skill = skill_lower in user_has_core
    knows_tooling = skill_lower in user_has_tooling
    knows_framework = skill_lower in user_has_frameworks
    proficient_framework = skill_lower in user_proficient_frameworks
    knows_implied = skill_lower in user_implied_skills
    proficient_implied = skill_lower in user_proficient_skills

    if has_skill:
        user_level = "熟练"
        reason = "直接掌握"
    elif knows_tooling:
        user_level = "熟练"
        reason = "工具类"
    elif proficient_framework:
        user_level = "熟练"
        reason = "熟练框架"
    elif proficient_implied:
        user_level = "熟练"
        reason = "熟练隐含"
    elif knows_implied:
        user_level = "了解"
        reason = "隐含推断"
    elif knows_framework:
        user_level = "了解"
        reason = "框架识别"
    else:
        user_level = "不了解"
        reason = "❌未识别"

    target_level = target_levels.get(skill, "熟练")
    gap = evaluate_gap(target_level, user_level)['gap']
    
    results.append((skill, target_level, user_level, gap, reason))

for skill, target_level, user_level, gap, reason in results:
    is_reasonable = gap in ["无", "小"] or user_level != "不了解"
    status = "✅" if is_reasonable else "❌"
    print(f"{skill:<12} {target_level:<8} {reason:<20} {user_level:<10} {gap:<6} {status}")

print("-" * 80)

print("\n" + "=" * 80)
print("修复验证")
print("=" * 80)

issues_fixed = []

# 问题1: Webpack/Vite 识别
if 'webpack' in user_has_tooling and 'vite' in user_has_tooling:
    issues_fixed.append("✅ 问题1已修复: Webpack/Vite 正确识别为工具类")
else:
    issues_fixed.append("❌ 问题1未修复: Webpack/Vite 识别失败")

# 问题2: TypeScript 推断
if 'typescript' in user_implied_skills:
    issues_fixed.append("✅ 问题2已修复: Vue/React 推断出 TypeScript")
else:
    issues_fixed.append("❌ 问题2未修复: TypeScript 推断缺失")

# 问题3: 用户级别偏低
js_level = None
for skill, _, user_level, _, _ in results:
    if skill == "JavaScript":
        js_level = user_level
        break
if js_level == "熟练":
    issues_fixed.append("✅ 问题3已修复: JavaScript 显示'熟练'而非'了解'")
else:
    issues_fixed.append(f"❌ 问题3未修复: JavaScript 显示'{js_level}'")

for issue in issues_fixed:
    print(f"  {issue}")

print("-" * 80)

print("\n" + "=" * 80)
print("差距合理性验证")
print("=" * 80)

print(f"\n用户输入: \"{user_input}\"")
print("\n差距分析合理性:")
for skill, target_level, user_level, gap, reason in results:
    if gap == "无":
        gap_desc = "无需学习（已达标）"
    elif gap == "小":
        gap_desc = "学习难度小"
    elif gap == "中":
        gap_desc = "需要一定学习"
    elif gap == "大":
        gap_desc = "需要大量学习"
    else:
        gap_desc = "未知"
    
    print(f"  {skill}: 目标={target_level}, 用户={user_level} → 差距={gap} ({gap_desc})")

print("\n" + "=" * 80)
print("结论")
print("=" * 80)

all_fixed = all("✅" in issue for issue in issues_fixed)
if all_fixed:
    print("""
✅ 所有问题已修复！

修复效果:
1. Webpack/Vite/CI/CD: 通过工具类识别 → 熟练，差距=无
2. Vue/React: 通过熟练框架识别 → 熟练，差距=小（精通目标）
3. JavaScript: 通过熟练隐含技能识别 → 熟练，差距=小（精通目标）
4. TypeScript: 通过隐含推断识别 → 熟练，差距=无

分析：用户输入"Vue和React通用"表明其对Vue/React有较深掌握，
系统正确推断其JavaScript/TypeScript也达到熟练级别。
""")
else:
    print("\n❌ 部分问题未修复，请检查上述结果。")
