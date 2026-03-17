from datasets import Dataset, load_dataset

def load_newfacade(split: str) -> Dataset:
    ds = load_dataset("newfacade/LeetCodeDataset")
    return ds[split]

def load_greengerong(split: str) -> Dataset:
    ds = load_dataset("greengerong/leetcode")
    return ds[split]