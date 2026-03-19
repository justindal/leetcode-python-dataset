from datasets import disable_caching

from .data.process import process
from .dataset.publish import publish


def main() -> None:
    disable_caching()

    ds = process()
    ds.save_to_disk("./output")

    c = input("publish? y/n: ").strip().lower()
    if c in {"y", "yes"}:
        message = ""
        while not message:
            message = input("enter commit message: ").strip()
        publish(message)
        print("published to huggingface")
    print("done")
