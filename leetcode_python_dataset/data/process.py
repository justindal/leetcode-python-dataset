from datasets import Dataset, DatasetDict, concatenate_datasets

from .clean import (
    ensure_solution_class,
    is_python,
    is_row_valid,
    solution_matches_starter,
)
from .format import format_greengerong, format_newfacade
from .load import load_greengerong, load_newfacade
from .verify import verify_dataset


def _nf_key_map(ds: Dataset) -> dict:
    slugs = ds["slug"]
    tags = ds["tags"]
    starters = ds["starter_code"]
    tests = ds["tests"]
    entry_points = ds["entry_point"]
    test_codes = ds["test_code"]

    return {
        slug: {
            "tags": tag,
            "starter_code": starter,
            "tests": t,
            "entry_point": ep,
            "test_code": tc,
        }
        for slug, tag, starter, t, ep, tc in zip(
            slugs, tags, starters, tests, entry_points, test_codes
        )
    }


def _test_lookup(ds: Dataset) -> dict[str, dict[str, str]]:
    lookup: dict[str, dict[str, str]] = {}
    slugs = ds["slug"]
    test_codes = ds["test_code"]
    entry_points = ds["entry_point"]

    for slug, test_code, entry_point in zip(slugs, test_codes, entry_points):
        if not slug or not test_code or not entry_point:
            continue

        if slug not in lookup:
            lookup[slug] = {"test": test_code, "entry_point": entry_point}

    return lookup


def process() -> DatasetDict:
    nf_train = load_newfacade("train")
    nf_train_fmt = nf_train.map(format_newfacade, remove_columns=nf_train.column_names)
    nf_train_fmt = nf_train_fmt.filter(is_row_valid)

    keys = _nf_key_map(nf_train_fmt)

    nf_test = load_newfacade("test")
    nf_test_fmt = nf_test.map(format_newfacade, remove_columns=nf_test.column_names)
    nf_test_fmt = nf_test_fmt.filter(is_row_valid)

    gg = load_greengerong("train")
    gg_fmt = gg.map(
        lambda item: format_greengerong(item, keys),
        remove_columns=gg.column_names,
    )
    gg_fmt = gg_fmt.filter(is_row_valid)
    gg_fmt = gg_fmt.filter(lambda row: is_python(row["solution"]))
    gg_fmt = gg_fmt.filter(
        lambda row: solution_matches_starter(row["solution"], row["starter_code"])
    )

    def _wrap_solution(row: dict) -> dict:
        row["solution"] = ensure_solution_class(row["solution"], row["starter_code"])
        return row

    nf_train_fmt = nf_train_fmt.map(_wrap_solution)
    gg_fmt = gg_fmt.map(_wrap_solution)
    nf_test_fmt = nf_test_fmt.map(_wrap_solution)

    combined = concatenate_datasets([nf_train_fmt, gg_fmt])

    print(f"newfacade total: {len(nf_train_fmt)}")
    print(f"greengerong name-matched: {len(gg_fmt)}")
    print(f"combined train: {len(combined)}")
    print(f"test: {len(nf_test_fmt)}")

    return DatasetDict({"train": combined, "test": nf_test_fmt})


def verify(ds: DatasetDict, include_test: bool = False) -> DatasetDict:
    print("Verifying solutions against tests...")
    datasets = [ds["train"]]
    if "test" in ds:
        datasets.append(ds["test"])
    all_rows = concatenate_datasets(datasets)
    tests = _test_lookup(all_rows)

    verified_train = verify_dataset(ds["train"], tests)
    print(f"verified train: {len(verified_train)} (was {len(ds['train'])})")

    if "test" in ds:
        if include_test:
            verified_test = verify_dataset(ds["test"], tests)
            print(f"verified test: {len(verified_test)} (was {len(ds['test'])})")
            return DatasetDict({"train": verified_train, "test": verified_test})
        return DatasetDict({"train": verified_train, "test": ds["test"]})

    return DatasetDict({"train": verified_train})
