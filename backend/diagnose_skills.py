#!/usr/bin/env python3
"""
技能匹配诊断脚本
验证用户输入的技能如何被处理和匹配
"""

import sys
sys.path.insert(0, '/workspace/backend')

from main import normalize_input, parse_user_skills, SKILL_ALIASES

# 测试用例
test_inputs = [
    "Webpack/Vite、CI/CD，Vue和React通用",
    "JavaScript, React, TypeScript, Webpack, Vite, CI/CD",
    "会Vue和React",
    "Vue React Angular",
    "html css javascript",
]

print("=" * 60)
print("技能匹配诊断报告")
print("=" * 60)

for user_input in test_inputs:
    print(f"\n📥 用户输入: \"{user_input}\"")
    print("-" * 60)
    
    # 步骤1: 分词
    tokens = normalize_input(user_input)
    print(f"【步骤1 - 分词结果】")
    print(f"  分词后: {tokens}")
    print(f"  关键词数量: {len(tokens)}")
    
    # 步骤2: 解析技能
    parsed = parse_user_skills([user_input])
    print(f"\n【步骤2 - 技能解析】")
    print(f"  normalized (规范化技能): {parsed['normalized']}")
    print(f"  has_tooling (工具类): {parsed['has_tooling']}")
    print(f"  has_frameworks (框架类): {parsed['has_frameworks']}")
    print(f"  has_core (核心语言): {parsed['has_core']}")
    
    # 步骤3: 模拟匹配
    target_skills = ["JavaScript", "React", "Vue", "Webpack", "Vite", "TypeScript", "CSS", "HTML"]
    print(f"\n【步骤3 - 目标技能匹配测试】")
    print(f"  目标技能列表: {target_skills}")
    
    user_normalized = set(s.lower() for s in parsed['normalized'])
    user_has_tooling = set(s.lower() for s in parsed['has_tooling'])
    user_has_frameworks = set(s.lower() for s in parsed['has_frameworks'])
    
    for skill in target_skills:
        skill_lower = skill.lower()
        
        # 检查匹配逻辑
        has_skill = skill_lower in user_normalized
        knows_tooling = skill_lower in user_has_tooling
        knows_framework = skill_lower in user_has_frameworks
        
        # 确定用户等级
        if has_skill:
            user_level = "熟练"
        elif knows_tooling:
            user_level = "熟练"
        elif knows_framework:
            user_level = "了解"
        else:
            user_level = "不了解"
        
        match_status = "✅" if user_level != "不了解" else "❌"
        print(f"  {match_status} {skill:12} → {user_level}")

print("\n" + "=" * 60)
print("问题诊断")
print("=" * 60)

print("""
【问题1】"Vue和React通用" 会被拆成什么？
→ 答案: normalize_input() 使用 r'[，,、/\\\s]+' 分词
   "Vue和React通用" → ['vue和react通用']
   ❌ 问题: "和" 不是分隔符，导致整个字符串被当成一个关键词

【问题2】匹配逻辑
→ 答案: 是分词后逐个匹配
   但分词不完善，"Vue和React" 会被当作一个词

【问题3】"Vue和React通用" 能识别几个技能？
→ 答案: 0个
   因为 'vue和react通用' 不在 normalized/skills 里

【问题4】匹配失败时的默认值
→ 答案: user_level = "不了解"
   导致所有未匹配的技能差距都显示"大"

【问题5】"了解"是解析的还是预设的？
→ 答案: 是代码预设的默认值
   - has_skill = True → "熟练"
   - knows_tooling = True → "熟练"  
   - knows_framework = True → "了解"
   - 其他 → "不了解"
""")

print("=" * 60)
print("修复建议")
print("=" * 60)
print("""
1. 扩展分隔符: r'[，,、/\\\s和与及跟用会]+'
2. 增加关键词提取: 从完整文本中用正则提取技能关键词
3. 改进匹配: 支持 "Vue和React" 这种连续技能写法
""")
