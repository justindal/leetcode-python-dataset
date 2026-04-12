from .clean import extract_python_code


def format_newfacade(item: dict) -> dict:
    raw = item["completion"].strip()
    code = extract_python_code(raw) or raw

    return {
        "slug": item["task_id"],
        "difficulty": item["difficulty"],
        "tags": item["tags"],
        "problem": item["problem_description"],
        "starter_code": item["starter_code"],
        "solution": code,
        "tests": item["input_output"],
        "entry_point": item.get("entry_point", ""),
        "test_code": item.get("test", ""),
        "source": "newfacade",
    }


def format_greengerong(item: dict, keys: dict) -> dict:
    slug = item["slug"]
    key_match = keys.get(slug, {})

    code = extract_python_code(item["python"]) or ""

    return {
        "slug": slug,
        "difficulty": item["difficulty"],
        "tags": key_match.get("tags"),
        "problem": item["content"],
        "starter_code": key_match.get("starter_code"),
        "solution": code,
        "tests": key_match.get("tests"),
        "entry_point": key_match.get("entry_point", ""),
        "test_code": key_match.get("test_code", ""),
        "source": "greengerong",
    }
