from datasets import load_from_disk


def publish(message: str) -> None:
    ds = load_from_disk("./output")
    ds.push_to_hub(
        "justindal/leetcode-python-dataset",
        private=True,
        commit_message=message,
    )
