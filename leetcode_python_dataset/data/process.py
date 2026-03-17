from .load import load_newfacade, load_greengerong
from .format import format_newfacade, format_greengerong
from .clean import is_row_valid

from datasets import DatasetDict, Dataset, concatenate_datasets


def nf_keys(ds: Dataset) -> dict:
    """Create a dict by slug from the nf dataset, to be used for missing keys in gg.

    Args:
        ds (Dataset): newfacade ds

    Returns:
        dict: dict with required keys
    """

    slugs = ds["slug"]
    tags = ds["tags"]
    starters = ds["starter_code"]

    return {
        slug: {"tags": tag, "starter_code": starter_code}
        for slug, tag, starter_code in zip(slugs, tags, starters)
    }


def process() -> DatasetDict:
    """Process both datasets; cleans, formats, and merges the data.

    Returns:
        DatasetDict: The merged dataset
    """

    # process new facade training split first
    nf_train = load_newfacade("train")
    nf_train_formatted = nf_train.map(
        format_newfacade, remove_columns=nf_train.column_names
    )
    nf_key_map = nf_keys(nf_train_formatted)

    nf_test = load_newfacade("test")
    nf_test_formatted = nf_test.map(
        format_newfacade, remove_columns=nf_test.column_names
    )

    # process greengerong
    gg = load_greengerong("train")
    gg = gg.filter(is_row_valid)
    gg_formatted = gg.map(
        lambda item: format_greengerong(item, nf_key_map),
        remove_columns=gg.column_names,
    )

    # merge datasets
    combined = concatenate_datasets([nf_train_formatted, gg_formatted])

    return DatasetDict({"train": combined, "test": nf_test_formatted})
