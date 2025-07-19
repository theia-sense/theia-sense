import json
from pathlib import Path
from typing import List, Tuple, Dict
from collections import Counter

def load_tags_and_categories(json_path: Path) -> Tuple[List[str], Dict[str, List[str]]]:
    with open(json_path, "r", encoding="utf-8") as f:
        categories = json.load(f)
    
    # Flatten all category tags into a single list, removing duplicates
    all_tags = set()
    tag_to_categories = {}

    for category, tags in categories.items():
        for tag in tags:
            tag_lower = tag.lower()
            all_tags.add(tag_lower)
            tag_to_categories.setdefault(tag_lower, []).append(category)
    
    return sorted(all_tags), tag_to_categories


def assign_categories(tags: List[str], tag_to_categories: Dict[str, List[str]], min_count=1, top_n=3) -> List[str]:
    category_counter = Counter()
    for tag in tags:
        categories = tag_to_categories.get(tag.lower(), [])
        category_counter.update(categories)

    # Filter categories that appear at least min_count times
    filtered = [(cat,count) for cat, count in category_counter.items() if count >= min_count]

    # Sort by descending count
    filtered.sort(key=lambda x: x[1], reverse=True)
    return [cat for cat, _ in filtered[:top_n]]

