"""
本质工坊 · 文章内容编排后处理

属于内容框架层：对 Markdown 正文进行内容编排层面的预处理，
包括图片均匀分布、GIF 前置、参考文献限量、图片数量限制等。
这些操作关注内容组织结构，与具体输出形式无关。
"""

import re


def _distribute_images_evenly(md_content):
    """将图片均匀分布到各章节标题下方，每章节最多一张图。

    逻辑：
    1. 按章节（## 标题）分组，收集所有图片
    2. 按章节在文章中的位置比例，等间距分配图片
    3. 每个章节最多放一张图，放在标题下方第一个空行后
    4. 如果图片数 > 章节数，多余的图放在最长的无图章节中
    """
    lines = md_content.split('\n')
    total_lines = len(lines)

    # 收集章节标题行索引（仅 ## 二级标题）
    heading_indices = []
    for i, line in enumerate(lines):
        if re.match(r'^##\s+', line.strip()):
            heading_indices.append(i)

    # 收集图片行索引和内容
    img_indices = []
    img_contents = []
    for i, line in enumerate(lines):
        if re.match(r'^!\[.*?\]\(.*?\)', line.strip()):
            img_indices.append(i)
            img_contents.append(line)

    if not heading_indices or not img_indices:
        return md_content

    num_imgs = len(img_contents)
    num_headings = len(heading_indices)

    # 计算每个章节的行范围（从标题到下一个标题或文末）
    section_ranges = []
    for si, h_idx in enumerate(heading_indices):
        start = h_idx
        end = heading_indices[si + 1] if si + 1 < num_headings else total_lines
        section_ranges.append((start, end))

    # 等间距分配：在章节中均匀选取目标位置
    # 例如 8 张图 6 个章节 → 每章节 1 张，多出 2 张放最长章节
    target_sections = []
    if num_imgs <= num_headings:
        # 图片少于等于章节数：等间距选章节
        step = num_headings / num_imgs
        for k in range(num_imgs):
            target_sections.append(int(k * step))
    else:
        # 图片多于章节数：每章节至少一张，多出的放最长章节
        for k in range(num_headings):
            target_sections.append(k)
        remaining = num_imgs - num_headings
        # 按章节长度排序，最长的多放
        sections_by_len = sorted(range(num_headings),
                                  key=lambda s: section_ranges[s][1] - section_ranges[s][0],
                                  reverse=True)
        for k in range(remaining):
            target_sections.append(sections_by_len[k])

    target_sections.sort()

    # 先移除所有原始图片行
    result_lines = list(lines)
    for idx in sorted(img_indices, reverse=True):
        result_lines[idx] = None

    # 在目标章节标题下方插入图片
    insertions = {}  # heading_index -> [img_line, ...]
    for img_idx_in_list, section_idx in enumerate(target_sections):
        if img_idx_in_list >= num_imgs:
            break
        h_idx = heading_indices[section_idx]
        insertions.setdefault(h_idx, []).append(img_contents[img_idx_in_list])

    final_lines = []
    for i, line in enumerate(result_lines):
        if line is not None:
            final_lines.append(line)
        # 在标题行后插入分配的图片
        if i in insertions:
            for img_line in insertions[i]:
                final_lines.append(img_line)

    return '\n'.join(final_lines)


def _prioritize_gifs(md_content, min_text_gap=8):
    lines = md_content.split('\n')
    total_lines = len(lines)
    threshold = int(total_lines * 0.3)

    gif_lines = []
    gif_indices = []
    png_indices = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r'^!\[.*?\]\(.*?\.gif\)', stripped, re.IGNORECASE):
            gif_lines.append(line)
            gif_indices.append(i)
        elif re.match(r'^!\[.*?\]\(.*?\)', stripped):
            png_indices.append(i)

    if not gif_lines:
        return md_content

    need_move = [idx for idx in gif_indices if idx > threshold]
    if not need_move:
        return md_content

    first_heading = None
    for i, line in enumerate(lines):
        if re.match(r'^#{1,3}\s+', line.strip()):
            first_heading = i
            break

    best_pos = None
    if first_heading is not None:
        search_start = first_heading + 2
    else:
        search_start = min(5, threshold)

    for pos in range(search_start, threshold + 1):
        if png_indices and min(abs(pos - pi) for pi in png_indices) < min_text_gap:
            continue
        nearby_text = sum(1 for j in range(max(0, pos - min_text_gap), min(len(lines), pos + min_text_gap))
                          if lines[j].strip() and not re.match(r'^!\[.*?\]\(.*?\)', lines[j].strip()))
        if nearby_text >= min_text_gap:
            best_pos = pos
            break

    if best_pos is None:
        best_pos = search_start

    for idx in sorted(need_move, reverse=True):
        lines[idx] = None

    result = []
    inserted = False
    for i, line in enumerate(lines):
        if line is not None:
            result.append(line)
        if not inserted and i >= best_pos:
            for gl in gif_lines:
                result.append(gl)
            inserted = True

    return '\n'.join(result)


def _limit_references(md_content, min_refs=3, max_refs=5):
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

    # ── 解析参考文献列表，构建编号→简要描述的映射 ──
    ref_lines = ref_body.split('\n')
    kept = []
    removed_refs = {}  # {编号: 简要描述}
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
                # 超限参考文献：提取简要描述（作者+书名/文章名，截取前20字）
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

    if count < min_refs:
        return md_content

    new_ref_body = '\n'.join(kept)

    # ── 处理正文中超限的引用标记 [N] ──
    # 将 [6], [7] 等替换为行内备注，如（见亚里士多德《形而上学》…）
    def replace_overflow_citation(m):
        num = int(m.group(1))
        if num in removed_refs:
            return f"（见{removed_refs[num]}）"
        elif num > max_refs:
            # 编号不在参考文献列表中（可能被合并），直接删除标记
            return ""
        return m.group(0)  # 保留范围内的引用

    before_section = re.sub(r'\[(\d+)\]', replace_overflow_citation, before_section)

    return before_section + section_header + '\n' + new_ref_body + '\n' + after_section


def _limit_images(md_content, max_png=6, max_gif=1):
    lines = md_content.split('\n')
    png_count = 0
    gif_count = 0
    result = []

    for line in lines:
        stripped = line.strip()
        img_match = re.match(r'^!\[.*?\]\(.*?(\.\w+)\)', stripped)
        if img_match:
            ext = img_match.group(1).lower()
            if ext == '.gif':
                if gif_count < max_gif:
                    gif_count += 1
                    result.append(line)
            elif ext == '.png':
                if png_count < max_png:
                    png_count += 1
                    result.append(line)
            else:
                if png_count < max_png:
                    png_count += 1
                    result.append(line)
        else:
            result.append(line)

    return '\n'.join(result)
