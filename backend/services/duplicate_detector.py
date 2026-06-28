from difflib import SequenceMatcher


def is_similar(first: str, second: str, threshold: float = 0.88) -> bool:
    return SequenceMatcher(None, first[:5000], second[:5000]).ratio() >= threshold
