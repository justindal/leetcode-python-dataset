from datasets import Dataset

def is_row_valid(item: dict) -> bool:
    """Checks if a given row is valid.

    Args:
        item (dict): the row to check

    Returns:
        bool: Whether the given row is valid.
    """

    required_items = ["slug", "difficulty", "content", "python"]

    for i in required_items:
        if not item[i]:
            return False

    return True


