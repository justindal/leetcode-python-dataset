from pathlib import Path
from random import Random
from tempfile import TemporaryDirectory

from datasets import Dataset, DatasetDict, load_from_disk
from huggingface_hub import HfApi

REPO_ID = "justindal/leetcode-python-dataset"
VALIDATION_RATIO = 0.1
VALIDATION_SEED = 42


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
            splits["validation"] = ds["validation"]
        elif "valid" in ds:
            splits["train"] = ds["train"]
            splits["validation"] = ds["valid"]
        else:
            train_split, validation_split = _split_train_validation(ds["train"])
            splits["train"] = train_split
            splits["validation"] = validation_split

    if "test" in ds:
        splits["test"] = ds["test"]

    return splits


def _write_jsonl_export(output_dir: Path) -> None:
    ds = load_from_disk("./output")
    splits = _build_publish_splits(ds)
    for split_name, split_ds in splits.items():
        split_ds.to_json(
            str(output_dir / f"{split_name}.jsonl"),
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
