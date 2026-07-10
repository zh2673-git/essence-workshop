"""
本质工坊 · 文章内容后处理（v2.0 平台约束版）

v2.0：只保留与平台硬性约束相关的后处理。
内容编排（图片均匀分布、GIF前置、图片数量限制）已移除，由内容框架层决定。
"""

import re


def _limit_references(md_content, max_refs=5):
    """限制参考文献数量（超限的替换为行内备注），防止HTML总字符超20000上限。"""
    ref_section_pattern = re.compile(
        r'^(#{1,3}\s+(?:参考文献|参考资料|References?))\s*$',
        re.MULTILINE
    )
    match = ref_section_pattern.search(md_content)
    if not match:
        return md_content

    section_start = match.start()
    before_section = md_content[:section_start]
    section_header = match.group(0)
    after_header = md_content[match.end():]

    next_heading = re.search(r'^#{1,3}\s+', after_header, re.MULTILINE)
    if next_heading:
        ref_body = after_header[:next_heading.start()]
        after_section = after_header[next_heading.start():]
    else:
        ref_body = after_header
        after_section = ""

    ref_lines = ref_body.split('\n')
    kept = []
    removed_refs = {}
    count = 0
    for line in ref_lines:
        stripped = line.strip()
        if not stripped:
            kept.append(line)
            continue
        ref_match = re.match(r'^\[(\d+)\]\s*(.+)', stripped)
        if ref_match:
            count += 1
            if count <= max_refs:
                kept.append(line)
            else:
                desc = ref_match.group(2).strip()
                desc = re.sub(r'^\d+\.\s*', '', desc)
                short_desc = desc[:20] + ('…' if len(desc) > 20 else '')
                removed_refs[int(ref_match.group(1))] = short_desc
        elif re.match(r'^[\-\*\d]+[.\s]', stripped):
            count += 1
            if count <= max_refs:
                kept.append(line)
            else:
                short_desc = stripped[:20] + ('…' if len(stripped) > 20 else '')
                removed_refs[count] = short_desc
        else:
            kept.append(line)

    new_ref_body = '\n'.join(kept)

    def replace_overflow_citation(m):
        num = int(m.group(1))
        if num in removed_refs:
            return f"（见{removed_refs[num]}）"
        elif num > max_refs:
            return ""
        return m.group(0)

    before_section = re.sub(r'\[(\d+)\]', replace_overflow_citation, before_section)

    return before_section + section_header + '\n' + new_ref_body + '\n' + after_section
