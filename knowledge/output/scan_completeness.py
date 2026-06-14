#!/usr/bin/env python3
"""扫描知识图谱，按skill工作流程C的标准检查完整性"""
import json, os, re

BASE = r'c:\Users\LX\.trae-cn\skills\essence-workshop\knowledge\output'
GRAPH_PATH = os.path.join(BASE, 'knowledge-graph.json')

with open(GRAPH_PATH, 'r', encoding='utf-8') as f:
    graph = json.load(f)

results = {'complete': [], 'incomplete': [], 'pending': []}

for name, node in graph['nodes'].items():
    if node.get('type') == 'project':
        continue
    
    html_file = node.get('html_file', '')
    if not html_file:
        results['pending'].append(name)
        continue
    
    # 读取HTML检查完整性
    full_path = os.path.join(BASE, html_file.replace('output/', ''))
    if not os.path.exists(full_path):
        results['pending'].append(name)
        continue
    
    with open(full_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 检查7个维度的完整性
    issues = []
    
    # 检查是否有占位符内容
    placeholder_patterns = [
        '内容待补充', '内容待完善', '待补充', '待完善',
        '详细拆解内容待补充', '历史溯源内容待完善',
        '现实矛盾内容待完善', '应用场景内容待完善',
        '思维延伸内容待完善', '知识网络内容待完善',
        '验证理解内容待完善'
    ]
    
    for pattern in placeholder_patterns:
        if pattern in html:
            issues.append(f'含占位符: {pattern}')
            break
    
    # 检查定义锚点是否有生活锚点
    if '生活锚点' not in html and '体验锚点' not in html and '可观察现象' not in html:
        issues.append('定义锚点缺少生活锚点/体验锚点')
    
    # 检查历史溯源是否有具体故事
    if '历史溯源' in html:
        # 找历史溯源section的内容
        has_story = any(kw in html for kw in ['年', '世纪', '发现', '发明', '提出', '古人', '数学家', '物理学家', '科学家'])
        if not has_story:
            issues.append('历史溯源缺少具体故事')
    
    # 检查现实矛盾是否有困境时刻
    if '困境时刻' not in html and '困境' not in html:
        issues.append('现实矛盾缺少困境时刻')
    
    # 检查验证理解是否有3题以上
    quiz_count = html.count('quiz-item')
    if quiz_count < 3:
        issues.append(f'验证理解题目不足({quiz_count}题)')
    
    # 检查SVG图示
    if '<svg' not in html:
        issues.append('缺少SVG图示')
    
    if issues:
        results['incomplete'].append({
            'name': name,
            'phase': node.get('phase', '?'),
            'grade': node.get('grade', '?'),
            'domain': node.get('domain', '?'),
            'issues': issues
        })
    else:
        results['complete'].append(name)

# 按学段/年级排序不完整的
results['incomplete'].sort(key=lambda x: (
    {'小学': 0, '初中': 1, '高中': 2}.get(x['phase'], 9),
    x['grade'] if isinstance(x['grade'], int) else 99,
    x['domain'],
    x['name']
))

print(f"=== 知识图谱增量更新扫描报告 ===")
print(f"完整: {len(results['complete'])}个")
print(f"不完整: {len(results['incomplete'])}个")
print(f"待生成: {len(results['pending'])}个")
print()

if results['complete']:
    print(f"--- 完整知识点 ({len(results['complete'])}) ---")
    for n in results['complete']:
        print(f"  ✓ {n}")
    print()

print(f"--- 不完整知识点 ({len(results['incomplete'])}) ---")
for item in results['incomplete']:
    print(f"  ✗ {item['phase']} {item['grade']}年级 {item['domain']} - {item['name']}")
    for issue in item['issues']:
        print(f"      · {issue}")

print()
print(f"建议更新顺序：先补充不完整的{len(results['incomplete'])}个，按学段从低到高")
