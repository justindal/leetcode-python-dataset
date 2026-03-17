from datasets import Dataset


def format_newfacade(item: dict) -> dict:
    return {
        "slug": item["task_id"],
        "difficulty": item["difficulty"],
        "tags": item["tags"],
        "problem": item["problem_description"],
        "starter_code": item["starter_code"],
        "solution": item["response"],
        "tests": item["input_output"],
        "source": "newfacade",
    }


def format_greengerong(item: dict, keys: dict) -> dict:
    slug = item["slug"]
    key_match = keys.get(slug, {})

    return {
        "slug": item["slug"],
        "difficulty": item["difficulty"],
        "tags": key_match.get("tags"),  # from nf
        "problem": item["content"],
        "starter_code": key_match.get("starter_code"),  # from nf
        "solution": item["python"],
        "source": "greengerong",
    }
