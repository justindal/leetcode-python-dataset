import argparse

from datasets import disable_caching

from .data.process import process, verify
from .dataset.publish import publish


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build, optionally verify, and optionally publish the dataset."
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify the train split against tests before publishing.",
    )
    parser.add_argument(
        "--verify-test",
        action="store_true",
        help="Also verify the test split when verification is enabled.",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Publish the dataset after processing.",
    )
    parser.add_argument(
        "--message",
        default="",
        help="Commit message to use when publishing.",
    )
    return parser.parse_args()


def main() -> None:
    disable_caching()
    args = _parse_args()

    ds = process()
    ds.save_to_disk("./output")

    should_verify = args.verify
    should_publish = args.publish

    if not should_verify:
        c = input("verify? y/n: ").strip().lower()
        should_verify = c in {"y", "yes"}

    if should_verify:
        ds = verify(ds, include_test=args.verify_test)
        ds.save_to_disk("./output")

    if not should_publish:
        c = input("publish? y/n: ").strip().lower()
        should_publish = c in {"y", "yes"}

    if should_publish:
        message = args.message.strip()
        while not message:
            message = input("enter commit message: ").strip()
        publish(message)
        print("published to huggingface")

    print("done")
