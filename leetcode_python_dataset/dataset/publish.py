from pathlib import Path
from random import Random
from tempfile import TemporaryDirectory

from datasets import Dataset, DatasetDict, concatenate_datasets, load_from_disk
from huggingface_hub import HfApi

from ..solution_env import SYSTEM_PROMPT

REPO_ID = "justindal/leetcode-python-dataset"
VALIDATION_RATIO = 0.1
VALIDATION_SEED = 42
BENCHMARK_FILE_NAME = "benchmark.jsonl"
BENCHMARK_COLUMNS = (
    "slug",
    "difficulty",
    "tags",
    "problem",
    "starter_code",
    "solution",
    "tests",
    "source",
)


def _build_user_message(row: dict) -> str:
    tags = ", ".join(row["tags"]) if row["tags"] else "Unknown"
    starter_code = row.get("starter_code") or ""
    return (
        f"Difficulty: {row['difficulty']}\n"
        f"Topics: {tags}\n\n"
        f"Problem:\n{row['problem'].strip()}\n\n"
        f"Starter code:\n{starter_code}"
    )


def _row_to_chat(row: dict) -> dict:
    solution = (row.get("solution") or "").strip()
    if not solution:
        return {"messages": [], "_skip": True}
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_message(row)},
            {"role": "assistant", "content": solution},
        ],
        "_skip": False,
    }


def _to_chat_format(ds: Dataset) -> Dataset:
    mapped = ds.map(_row_to_chat, remove_columns=ds.column_names)
    return mapped.filter(lambda row: not row["_skip"]).remove_columns(["_skip"])


def _row_to_benchmark(row: dict, split_name: str) -> dict:
    benchmark_row = {column: row.get(column) for column in BENCHMARK_COLUMNS}
    benchmark_row["type"] = split_name
    return benchmark_row


def _to_benchmark_format(splits: dict[str, Dataset]) -> Dataset:
    typed_splits: list[Dataset] = []
    for split_name, split_ds in splits.items():
        typed_splits.append(
            split_ds.map(
                lambda row, s=split_name: _row_to_benchmark(row, s),
                remove_columns=split_ds.column_names,
            )
        )
    return concatenate_datasets(typed_splits)


def _split_train_validation(
    train: Dataset,
    validation_ratio: float = VALIDATION_RATIO,
    seed: int = VALIDATION_SEED,
) -> tuple[Dataset, Dataset]:
    if "slug" not in train.column_names:
        split = train.train_test_split(test_size=validation_ratio, seed=seed)
        return split["train"], split["test"]

    slug_to_indices: dict[str, list[int]] = {}
    for idx, slug in enumerate(train["slug"]):
        slug_to_indices.setdefault(slug, []).append(idx)

    slugs = list(slug_to_indices.keys())
    rng = Random(seed)
    rng.shuffle(slugs)
    num_validation_slugs = max(1, int(round(len(slugs) * validation_ratio)))
    validation_slugs = set(slugs[:num_validation_slugs])

    train_indices: list[int] = []
    validation_indices: list[int] = []
    for slug, indices in slug_to_indices.items():
        if slug in validation_slugs:
            validation_indices.extend(indices)
        else:
            train_indices.extend(indices)

    return train.select(train_indices), train.select(validation_indices)


def _build_publish_splits(ds: DatasetDict) -> dict[str, Dataset]:
    splits: dict[str, Dataset] = {}

    if "train" in ds:
        if "validation" in ds:
            splits["train"] = ds["train"]
            splits["valid"] = ds["validation"]
        elif "valid" in ds:
            splits["train"] = ds["train"]
            splits["valid"] = ds["valid"]
        else:
            train_split, validation_split = _split_train_validation(ds["train"])
            splits["train"] = train_split
            splits["valid"] = validation_split

    if "test" in ds:
        splits["test"] = ds["test"]

    return splits


def _write_jsonl_export(output_dir: Path) -> None:
    ds = load_from_disk("./output")
    if not isinstance(ds, DatasetDict):
        raise TypeError("Expected a DatasetDict at ./output")
    splits = _build_publish_splits(ds)
    for split_name, split_ds in splits.items():
        chat_ds = _to_chat_format(split_ds)
        chat_ds.to_json(
            str(output_dir / f"{split_name}.jsonl"),
            orient="records",
            lines=True,
            force_ascii=False,
        )
    benchmark_ds = _to_benchmark_format(splits)
    benchmark_ds.to_json(
        str(output_dir / BENCHMARK_FILE_NAME),
        orient="records",
        lines=True,
        force_ascii=False,
    )

    readme = Path("README.md")
    if readme.exists():
        (output_dir / "README.md").write_text(readme.read_text())


def publish(message: str) -> None:
    api = HfApi()
    api.create_repo(REPO_ID, repo_type="dataset", private=True, exist_ok=True)

    with TemporaryDirectory() as temp_dir:
        export_dir = Path(temp_dir)
        _write_jsonl_export(export_dir)
        api.upload_folder(
            repo_id=REPO_ID,
            repo_type="dataset",
            folder_path=str(export_dir),
            commit_message=message,
            delete_patterns=[
                "*.parquet",
                "**/*.parquet",
                "*.arrow",
                "**/*.arrow",
                "dataset_infos.json",
                "dataset_dict.json",
                "**/dataset_info.json",
                "**/state.json",
            ],
        )
