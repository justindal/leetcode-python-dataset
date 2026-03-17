from .data.process import process
from .dataset.publish import publish


def main() -> None:
    ds = process()
    ds.save_to_disk("./output")

    c = input("publish? y/n: ")
    if c.lower() == "y":
        message = ""
        while not message:
            message = input("enter commit message: ")
            publish(message)
            print("published to huggingface")
    print("done")
