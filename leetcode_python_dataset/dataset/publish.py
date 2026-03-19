from pathlib import Path
from tempfile import TemporaryDirectory

from datasets import load_from_disk
from huggingface_hub import HfApi

REPO_ID = "justindal/leetcode-python-dataset"


def _write_jsonl_export(output_dir: Path) -> None:
    ds = load_from_disk("./output")
    for split in ds.keys():
        ds[split].to_json(
            str(output_dir / f"{split}.jsonl"),
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
