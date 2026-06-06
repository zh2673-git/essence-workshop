import re

TEMPLATE_SCHEMA = {
    "title": {
        "required": ["title"],
        "limits": {"title": 15, "subtitle": 30},
    },
    "stat": {
        "required": ["value", "label"],
        "limits": {"value": 10, "label": 20, "sublabel": 30},
    },
    "bullet": {
        "required": ["title", "items"],
        "limits": {"title": 15, "items": 5, "item_len": 20},
    },
    "chart": {
        "required": ["title", "data"],
        "limits": {"title": 15, "data": 6, "label_len": 6},
    },
    "quote": {
        "required": ["text"],
        "limits": {"text": 120, "source": 20},
    },
    "timeline": {
        "required": ["title", "events"],
        "limits": {
            "title": 15,
            "events": 6,
            "year_len": 6,
            "ev_title_len": 15,
            "ev_desc_len": 30,
        },
    },
    "focus": {
        "required": ["keyword"],
        "limits": {"keyword": 8, "explanation": 60, "callout": 20},
    },
    "steps": {
        "required": ["title", "steps"],
        "limits": {"title": 15, "steps": 5, "step_title_len": 15, "step_desc_len": 30},
    },
    "qa": {
        "required": ["question", "answer"],
        "limits": {"question": 40, "answer": 50},
    },
    "compare": {
        "required": ["title", "left", "right"],
        "limits": {"title": 15, "items_per_col": 4, "item_len": 10, "label_len": 6},
    },
    "summary": {
        "required": ["title", "items"],
        "limits": {"title": 15, "items": 4, "item_len": 18},
    },
    "feature": {
        "required": ["title", "features"],
        "limits": {"title": 15, "features": 4, "keyword_len": 10, "desc_len": 40},
    },
    "grid": {
        "required": ["title", "cards"],
        "limits": {"title": 15, "cards": 6, "card_title_len": 10, "card_desc_len": 30},
    },
    "line_chart": {
        "required": ["title", "labels", "datasets"],
        "limits": {"title": 15, "labels": 8, "datasets": 3, "name_len": 8},
    },
}

VALID_TYPES = set(TEMPLATE_SCHEMA.keys())

_TYPE_HINT_RE = re.compile(r'^\s*<!--\s*type\s*:\s*(\w+)\s*-->\s*$')


def detect_type_hint(line):
    m = _TYPE_HINT_RE.match(line)
    if m and m.group(1) in VALID_TYPES:
        return m.group(1)
    return None


def truncate(text, max_len):
    if not text:
        return text
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len]


def parse_template_sections(markdown):
    sections = []
    lines = markdown.split("\n")
    current = {"type_hint": None, "heading": "", "content": []}
    pending_type_hint = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        type_hint = detect_type_hint(stripped)
        if type_hint:
            pending_type_hint = type_hint
            continue

        h_match = re.match(r"^(#{1,4})\s+(.+)", stripped)
        if h_match:
            level = len(h_match.group(1))
            if level >= 3 and current["type_hint"] in ("compare",):
                current["content"].append(("heading3", h_match.group(2).strip()))
                continue
            if current["heading"] or current["content"]:
                sections.append(current)
            current = {
                "type_hint": pending_type_hint,
                "heading": h_match.group(2).strip(),
                "content": [],
            }
            pending_type_hint = None
            continue

        if stripped == "---":
            if current["heading"] or current["content"]:
                sections.append(current)
            current = {"type_hint": None, "heading": "", "content": []}
            pending_type_hint = None
            continue

        if not current["heading"] and not current["content"] and pending_type_hint:
            current["type_hint"] = pending_type_hint
            pending_type_hint = None

        if stripped.startswith("> "):
            current["content"].append(("quote", stripped[2:].strip()))
        elif stripped.startswith("- ") or stripped.startswith("* "):
            current["content"].append(("bullet", stripped[2:].strip()))
        elif re.match(r"^\d+[.、)]\s*", stripped):
            text = re.sub(r"^\d+[.、)]\s*", "", stripped)
            current["content"].append(("step", text.strip()))
        else:
            current["content"].append(("text", stripped))

    if current["heading"] or current["content"]:
        sections.append(current)

    return sections


def _parse_title(section):
    heading = section["heading"]
    texts = [c[1] for c in section["content"] if c[0] == "text"]
    limits = TEMPLATE_SCHEMA["title"]["limits"]
    return {
        "type": "title",
        "title": truncate(heading, limits["title"]),
        "subtitle": truncate(texts[0], limits["subtitle"]) if texts else "",
        "duration": 5,
    }


def _parse_stat(section):
    heading = section["heading"]
    all_text = heading + " " + " ".join(c[1] for c in section["content"])
    limits = TEMPLATE_SCHEMA["stat"]["limits"]
    num_match = re.search(r"(\d+[.%万亿]?万?亿?)", all_text)
    value = num_match.group(1) if num_match else "100%"
    label_text = all_text.replace(value, "").strip().strip("，。的")
    return {
        "type": "stat",
        "value": truncate(value, limits["value"]),
        "label": truncate(label_text or heading, limits["label"]),
        "sublabel": truncate(
            " ".join(c[1] for c in section["content"] if c[0] == "text"),
            limits["sublabel"],
        ),
        "duration": 6,
    }


def _parse_bullet(section):
    heading = section["heading"]
    limits = TEMPLATE_SCHEMA["bullet"]["limits"]
    items = []
    for c in section["content"]:
        if c[0] == "bullet":
            items.append(truncate(c[1], limits["item_len"]))
        elif c[0] == "quote":
            items.append(truncate(c[1], limits["item_len"]))
        elif c[0] == "text" and items:
            items[-1] += truncate(c[1], limits["item_len"])
    return {
        "type": "bullet",
        "title": truncate(heading, limits["title"]),
        "items": items[: limits["items"]],
        "duration": max(8, len(items) * 4),
    }


def _parse_chart(section):
    heading = section["heading"]
    limits = TEMPLATE_SCHEMA["chart"]["limits"]
    data = []
    for c in section["content"]:
        if c[0] == "bullet":
            parts = c[1].split(":")
            if len(parts) >= 2:
                label = truncate(parts[0].strip(), limits["label_len"])
                try:
                    value = int(parts[1].strip())
                except ValueError:
                    value = len(parts[1].strip())
                data.append({"label": label, "value": value})
            else:
                num_match = re.search(r"(\d+)", c[1])
                label = truncate(
                    re.sub(r"\d+", "", c[1]).strip(), limits["label_len"]
                )
                value = int(num_match.group(1)) if num_match else len(data) * 10 + 10
                data.append({"label": label or f"项目{len(data)+1}", "value": value})
    if not data:
        for i, c in enumerate(section["content"][:5]):
            data.append(
                {"label": truncate(c[1], limits["label_len"]), "value": 10 + i * 5}
            )
    return {
        "type": "chart",
        "title": truncate(heading, limits["title"]),
        "chartType": "bar",
        "data": data[: limits["data"]],
        "duration": 8,
    }


def _parse_quote(section):
    limits = TEMPLATE_SCHEMA["quote"]["limits"]
    quote_text = " ".join(c[1] for c in section["content"] if c[0] == "quote")
    if not quote_text:
        quote_text = " ".join(c[1] for c in section["content"])
    source = ""
    for c in section["content"]:
        if c[0] == "text" and c[1].startswith("——"):
            source = c[1].lstrip("——").strip()
            break
    if not source:
        source = section["heading"]
    return {
        "type": "quote",
        "text": truncate(quote_text, limits["text"]),
        "source": truncate(source, limits["source"]),
        "duration": 6,
    }


def _parse_timeline(section):
    heading = section["heading"]
    limits = TEMPLATE_SCHEMA["timeline"]["limits"]
    events = []
    for c in section["content"]:
        if c[0] == "bullet":
            parts = [p.strip() for p in c[1].split("|")]
            if len(parts) >= 3:
                events.append(
                    {
                        "year": truncate(parts[0], limits["year_len"]),
                        "title": truncate(parts[1], limits["ev_title_len"]),
                        "desc": truncate(parts[2], limits["ev_desc_len"]),
                    }
                )
            elif len(parts) == 2:
                year_match = re.search(r"(\d{2,4})\s*年?", parts[0])
                events.append(
                    {
                        "year": truncate(parts[0], limits["year_len"]),
                        "title": truncate(parts[1], limits["ev_title_len"]),
                        "desc": "",
                    }
                )
            else:
                year_match = re.search(r"(\d{2,4})\s*年?", c[1])
                events.append(
                    {
                        "year": truncate(
                            year_match.group(1) if year_match else "", limits["year_len"]
                        ),
                        "title": truncate(c[1], limits["ev_title_len"]),
                        "desc": "",
                    }
                )
    if not events:
        for i, c in enumerate(section["content"][:6]):
            events.append(
                {
                    "year": str(i + 1),
                    "title": truncate(c[1], limits["ev_title_len"]),
                    "desc": "",
                }
            )
    return {
        "type": "timeline",
        "title": truncate(heading, limits["title"]),
        "events": events[: limits["events"]],
        "duration": max(8, len(events) * 3),
    }


def _parse_focus(section):
    heading = section["heading"]
    texts = [c[1] for c in section["content"] if c[0] == "text"]
    limits = TEMPLATE_SCHEMA["focus"]["limits"]
    keyword = heading if heading else (texts[0][:8] if texts else "关键词")
    explanation = " ".join(texts) if texts else heading
    return {
        "type": "focus",
        "keyword": truncate(keyword, limits["keyword"]),
        "explanation": truncate(explanation, limits["explanation"]),
        "callout": truncate(explanation, limits["callout"])
        if len(explanation) > limits["callout"]
        else "",
        "duration": 6,
    }


def _parse_steps(section):
    heading = section["heading"]
    limits = TEMPLATE_SCHEMA["steps"]["limits"]
    steps = []
    for c in section["content"]:
        if c[0] == "step":
            parts = c[1].split("：", 1)
            if len(parts) >= 2:
                steps.append(
                    {
                        "title": truncate(parts[0], limits["step_title_len"]),
                        "desc": truncate(parts[1], limits["step_desc_len"]),
                    }
                )
            else:
                parts = c[1].split(":", 1)
                if len(parts) >= 2:
                    steps.append(
                        {
                            "title": truncate(parts[0], limits["step_title_len"]),
                            "desc": truncate(parts[1], limits["step_desc_len"]),
                        }
                    )
                else:
                    steps.append(
                        {
                            "title": truncate(c[1], limits["step_title_len"]),
                            "desc": "",
                        }
                    )
        elif c[0] == "text" and steps:
            steps[-1]["desc"] += truncate(" " + c[1], limits["step_desc_len"])
    return {
        "type": "steps",
        "title": truncate(heading or "步骤", limits["title"]),
        "steps": steps[: limits["steps"]],
        "duration": max(8, len(steps) * 4),
    }


def _parse_qa(section):
    heading = section["heading"]
    texts = [c[1] for c in section["content"] if c[0] == "text"]
    limits = TEMPLATE_SCHEMA["qa"]["limits"]
    all_text = " ".join(texts)
    qa_match = re.match(r"^(.{2,15})[？?](.{2,})$", all_text)
    if qa_match:
        question = qa_match.group(1) + "？"
        answer = qa_match.group(2)
    else:
        question = heading if "？" in heading or "?" in heading else heading + "？"
        answer = all_text
    return {
        "type": "qa",
        "question": truncate(question, limits["question"]),
        "answer": truncate(answer, limits["answer"]),
        "duration": 8,
    }


def _parse_compare(section):
    heading = section["heading"]
    limits = TEMPLATE_SCHEMA["compare"]["limits"]
    left_label = "A"
    right_label = "B"
    left_items = []
    right_items = []
    current_side = None
    for c in section["content"]:
        if c[0] == "heading3":
            label = truncate(c[1].strip(), limits["label_len"])
            if current_side is None:
                left_label = label
                current_side = "left"
            else:
                right_label = label
                current_side = "right"
            continue
        if c[0] == "text":
            h3_match = re.match(r"^#{1,3}\s+(.+)", c[1])
            if h3_match:
                label = truncate(h3_match.group(1).strip(), limits["label_len"])
                if current_side is None:
                    left_label = label
                    current_side = "left"
                else:
                    right_label = label
                    current_side = "right"
            continue
        if c[0] == "bullet":
            item = truncate(c[1], limits["item_len"])
            if current_side == "right":
                right_items.append(item)
            else:
                left_items.append(item)
                current_side = "left"
    if not right_items and left_items:
        mid = max(1, len(left_items) // 2)
        right_items = left_items[mid:]
        left_items = left_items[:mid]
    if not left_items:
        left_items = ["—"]
    if not right_items:
        right_items = ["—"]
    return {
        "type": "compare",
        "title": truncate(heading or "对比", limits["title"]),
        "leftTitle": left_label,
        "rightTitle": right_label,
        "left": left_items[: limits["items_per_col"]],
        "right": right_items[: limits["items_per_col"]],
        "duration": max(8, (len(left_items) + len(right_items)) * 3),
    }


def _parse_summary(section):
    heading = section["heading"]
    limits = TEMPLATE_SCHEMA["summary"]["limits"]
    items = []
    for c in section["content"]:
        if c[0] == "bullet":
            items.append(truncate(c[1], limits["item_len"]))
        elif c[0] == "quote":
            items.append(truncate(c[1], limits["item_len"]))
    return {
        "type": "summary",
        "title": truncate(heading or "总结", limits["title"]),
        "items": items[: limits["items"]],
        "duration": 10,
    }


def _parse_feature(section):
    heading = section["heading"]
    limits = TEMPLATE_SCHEMA["feature"]["limits"]
    features = []
    for c in section["content"]:
        if c[0] == "bullet":
            parts = c[1].split("：", 1)
            if len(parts) < 2:
                parts = c[1].split(":", 1)
            if len(parts) >= 2:
                features.append({
                    "keyword": truncate(parts[0].strip(), limits["keyword_len"]),
                    "desc": truncate(parts[1].strip(), limits["desc_len"]),
                })
            else:
                features.append({
                    "keyword": truncate(c[1], limits["keyword_len"]),
                    "desc": "",
                })
    if not features:
        for i, c in enumerate(section["content"][:4]):
            features.append({
                "keyword": truncate(c[1], limits["keyword_len"]),
                "desc": "",
            })
    return {
        "type": "feature",
        "title": truncate(heading or "概念详解", limits["title"]),
        "features": features[: limits["features"]],
        "duration": max(8, len(features) * 4),
    }


def _parse_grid(section):
    heading = section["heading"]
    limits = TEMPLATE_SCHEMA["grid"]["limits"]
    cards = []
    for c in section["content"]:
        if c[0] == "bullet":
            parts = c[1].split("：", 1)
            if len(parts) < 2:
                parts = c[1].split(":", 1)
            if len(parts) >= 2:
                cards.append({
                    "title": truncate(parts[0].strip(), limits["card_title_len"]),
                    "desc": truncate(parts[1].strip(), limits["card_desc_len"]),
                })
            else:
                cards.append({
                    "title": truncate(c[1], limits["card_title_len"]),
                    "desc": "",
                })
    if not cards:
        for i, c in enumerate(section["content"][:6]):
            cards.append({
                "title": truncate(c[1], limits["card_title_len"]),
                "desc": "",
            })
    return {
        "type": "grid",
        "title": truncate(heading or "多维网格", limits["title"]),
        "cards": cards[: limits["cards"]],
        "duration": max(8, len(cards) * 3),
    }


def _parse_line_chart(section):
    heading = section["heading"]
    limits = TEMPLATE_SCHEMA["line_chart"]["limits"]
    labels = []
    datasets = []
    for c in section["content"]:
        if c[0] == "bullet":
            parts = c[1].split("|")
            if len(parts) >= 2:
                label = truncate(parts[0].strip(), limits["name_len"])
                labels.append(label)
                values = [v.strip() for v in parts[1:]]
                for vi, v in enumerate(values):
                    while len(datasets) <= vi:
                        datasets.append({"name": f"数据{vi+1}", "values": []})
                    try:
                        datasets[vi]["values"].append(float(v))
                    except ValueError:
                        datasets[vi]["values"].append(0)
    if not labels:
        labels = ["Q1", "Q2", "Q3", "Q4"]
        datasets = [{"name": "数据1", "values": [10, 25, 30, 45]}]
    return {
        "type": "line_chart",
        "title": truncate(heading or "趋势对比", limits["title"]),
        "labels": labels[: limits["labels"]],
        "datasets": datasets[: limits["datasets"]],
        "duration": 8,
    }


_TEMPLATE_PARSERS = {
    "title": _parse_title,
    "stat": _parse_stat,
    "bullet": _parse_bullet,
    "chart": _parse_chart,
    "quote": _parse_quote,
    "timeline": _parse_timeline,
    "focus": _parse_focus,
    "steps": _parse_steps,
    "qa": _parse_qa,
    "compare": _parse_compare,
    "summary": _parse_summary,
    "feature": _parse_feature,
    "grid": _parse_grid,
    "line_chart": _parse_line_chart,
}


def parse_section(section):
    type_hint = section.get("type_hint")
    if type_hint and type_hint in _TEMPLATE_PARSERS:
        return _TEMPLATE_PARSERS[type_hint](section)
    return None


def validate_slide(slide):
    stype = slide.get("type", "")
    schema = TEMPLATE_SCHEMA.get(stype)
    if not schema:
        return False, f"Unknown type: {stype}"
    for field in schema["required"]:
        if not slide.get(field):
            return False, f"Missing required field: {field}"
    limits = schema["limits"]
    if "title" in limits and slide.get("title") and len(slide["title"]) > limits["title"]:
        return False, f"title too long: {len(slide['title'])} > {limits['title']}"
    if stype == "bullet":
        items = slide.get("items", [])
        if len(items) > limits["items"]:
            return False, f"too many items: {len(items)} > {limits['items']}"
        for i, item in enumerate(items):
            if len(item) > limits["item_len"]:
                return False, f"item[{i}] too long: {len(item)} > {limits['item_len']}"
    elif stype == "summary":
        items = slide.get("items", [])
        if len(items) > limits["items"]:
            return False, f"too many items: {len(items)} > {limits['items']}"
        for i, item in enumerate(items):
            if len(item) > limits["item_len"]:
                return False, f"item[{i}] too long: {len(item)} > {limits['item_len']}"
    elif stype == "chart":
        data = slide.get("data", [])
        if len(data) > limits["data"]:
            return False, f"too many data points: {len(data)} > {limits['data']}"
        for i, d in enumerate(data):
            if len(d.get("label", "")) > limits["label_len"]:
                return False, f"data[{i}].label too long"
    elif stype == "timeline":
        events = slide.get("events", [])
        if len(events) > limits["events"]:
            return False, f"too many events: {len(events)} > {limits['events']}"
    elif stype == "steps":
        steps = slide.get("steps", [])
        if len(steps) > limits["steps"]:
            return False, f"too many steps: {len(steps)} > {limits['steps']}"
    elif stype == "compare":
        for side in ["left", "right"]:
            items = slide.get(side, [])
            if len(items) > limits["items_per_col"]:
                return False, f"too many {side} items: {len(items)} > {limits['items_per_col']}"
            for i, item in enumerate(items):
                if len(item) > limits["item_len"]:
                    return False, f"{side}[{i}] too long: {len(item)} > {limits['item_len']}"
    elif stype == "qa":
        if len(slide.get("question", "")) > limits["question"]:
            return False, f"question too long"
        if len(slide.get("answer", "")) > limits["answer"]:
            return False, f"answer too long"
    elif stype == "focus":
        if len(slide.get("keyword", "")) > limits["keyword"]:
            return False, f"keyword too long"
        if len(slide.get("explanation", "")) > limits["explanation"]:
            return False, f"explanation too long"
    elif stype == "stat":
        if len(slide.get("value", "")) > limits["value"]:
            return False, f"value too long"
        if len(slide.get("label", "")) > limits["label"]:
            return False, f"label too long"
    elif stype == "quote":
        if len(slide.get("text", "")) > limits["text"]:
            return False, f"text too long"
    elif stype == "feature":
        features = slide.get("features", [])
        if len(features) > limits["features"]:
            return False, f"too many features: {len(features)} > {limits['features']}"
        for i, f in enumerate(features):
            if len(f.get("keyword", "")) > limits["keyword_len"]:
                return False, f"feature[{i}].keyword too long"
            if len(f.get("desc", "")) > limits["desc_len"]:
                return False, f"feature[{i}].desc too long"
    elif stype == "grid":
        cards = slide.get("cards", [])
        if len(cards) > limits["cards"]:
            return False, f"too many cards: {len(cards)} > {limits['cards']}"
        for i, c in enumerate(cards):
            if len(c.get("title", "")) > limits["card_title_len"]:
                return False, f"card[{i}].title too long"
            if len(c.get("desc", "")) > limits["card_desc_len"]:
                return False, f"card[{i}].desc too long"
    elif stype == "line_chart":
        labels = slide.get("labels", [])
        datasets = slide.get("datasets", [])
        if len(labels) > limits["labels"]:
            return False, f"too many labels: {len(labels)} > {limits['labels']}"
        if len(datasets) > limits["datasets"]:
            return False, f"too many datasets: {len(datasets)} > {limits['datasets']}"
        for i, ds in enumerate(datasets):
            if len(ds.get("name", "")) > limits["name_len"]:
                return False, f"dataset[{i}].name too long"
    return True, "ok"
