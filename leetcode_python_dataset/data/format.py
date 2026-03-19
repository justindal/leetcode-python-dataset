from .clean import extract_python_code, normalize_solution_style


def format_newfacade(item: dict) -> dict:
    return {
        "slug": item["task_id"],
        "difficulty": item["difficulty"],
        "tags": item["tags"],
        "problem": item["problem_description"],
        "starter_code": item["starter_code"],
        "solution": item["completion"].strip(),
        "tests": item["input_output"],
        "source": "newfacade",
    }


def format_greengerong(item: dict, keys: dict) -> dict:
    slug = item["slug"]
    key_match = keys.get(slug, {})

    code = extract_python_code(item["python"]) or ""
    code = normalize_solution_style(code, key_match.get("starter_code"))

    return {
        "slug": slug,
        "difficulty": item["difficulty"],
        "tags": key_match.get("tags"),
        "problem": item["content"],
        "starter_code": key_match.get("starter_code"),
        "solution": code,
        "tests": key_match.get("tests"),
        "source": "greengerong",
    }
