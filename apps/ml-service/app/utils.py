import json
from collections import Counter
from pathlib import Path


def load_tags_and_categories(
    json_path: Path,
) -> tuple[list[str], dict[str, list[str]]]:
    with open(json_path, encoding="utf-8") as f:
        categories = json.load(f)

    all_tags: set[str] = set()
    tag_to_categories: dict[str, list[str]] = {}

    for category, tags in categories.items():
        for tag in tags:
            tag_lower = tag.lower()
            all_tags.add(tag_lower)
            tag_to_categories.setdefault(tag_lower, []).append(category)

    return sorted(all_tags), tag_to_categories


def assign_categories(
    tags: list[str],
    tag_to_categories: dict[str, list[str]],
    min_count: int = 1,
    top_n: int = 3,
) -> list[str]:
    category_counter: Counter[str] = Counter()
    for tag in tags:
        category_counter.update(tag_to_categories.get(tag.lower(), []))

    filtered = [(cat, n) for cat, n in category_counter.items() if n >= min_count]
    filtered.sort(key=lambda x: x[1], reverse=True)
    return [cat for cat, _ in filtered[:top_n]]

