from datasets import DatasetDict, Dataset, concatenate_datasets

from .load import load_newfacade, load_greengerong
from .format import format_newfacade, format_greengerong
from .clean import is_row_valid, is_python


def nf_keys(ds: Dataset) -> dict:
    slugs = ds["slug"]
    tags = ds["tags"]
    starters = ds["starter_code"]
    tests = ds["tests"]

    return {
        slug: {"tags": tag, "starter_code": starter, "tests": t}
        for slug, tag, starter, t in zip(slugs, tags, starters, tests)
    }


def process() -> DatasetDict:
    nf_train = load_newfacade("train")
    nf_train_fmt = nf_train.map(
        format_newfacade, remove_columns=nf_train.column_names
    )
    nf_train_fmt = nf_train_fmt.filter(is_row_valid)

    nf_key_map = nf_keys(nf_train_fmt)

    nf_test = load_newfacade("test")
    nf_test_fmt = nf_test.map(
        format_newfacade, remove_columns=nf_test.column_names
    )
    nf_test_fmt = nf_test_fmt.filter(is_row_valid)

    gg = load_greengerong("train")
    gg_fmt = gg.map(
        lambda item: format_greengerong(item, nf_key_map),
        remove_columns=gg.column_names,
    )
    gg_fmt = gg_fmt.filter(is_row_valid)
    gg_fmt = gg_fmt.filter(lambda row: is_python(row["solution"]))

    combined = concatenate_datasets([nf_train_fmt, gg_fmt])

    print(f"newfacade train: {len(nf_train_fmt)}")
    print(f"greengerong train: {len(gg_fmt)}")
    print(f"combined train: {len(combined)}")
    print(f"test: {len(nf_test_fmt)}")

    return DatasetDict({"train": combined, "test": nf_test_fmt})
