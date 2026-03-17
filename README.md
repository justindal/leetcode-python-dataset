# leetcode-python-dataset

Code for building and publishing the [`justindal/leetcode-python-dataset`](https://huggingface.co/datasets/justindal/leetcode-python-dataset) dataset on Hugging Face.

Merges two open-source LeetCode datasets into a unified schema with consistent formatting, field normalisation, and solution validation.

## Dataset

| Split | Rows | Source |
|---|---|---|
| train | 5000 | newfacade + greengerong |
| test | 228 | newfacade only |


## Schema

| Column | Type | Description |
|---|---|---|
| `task_id` | string | Problem slug e.g. `two-sum` |
| `difficulty` | string | `Easy`, `Medium`, or `Hard` |
| `tags` | list[string] | Topic tags e.g. `["Array", "Hash Table"]` |
| `problem` | string | Full problem description |
| `starter_code` | string | Function signature to complete |
| `solution` | string | Accepted Python solution |
| `source` | string | `newfacade` or `greengerong` |

## Sources

- [`newfacade/LeetCodeDataset`](https://huggingface.co/datasets/newfacade/LeetCodeDataset) (Apache 2.0)
- [`greengerong/leetcode`](https://huggingface.co/datasets/greengerong/leetcode) (MIT)

## Usage

uv:

```bash
git clone https://github.com/justindal/leetcode-python-dataset
cd leetcode-python-dataset
uv sync
```

Run the build:

```bash
uv run leetcode-dataset

# or
./.venv/bin/leetcode-dataset
```

pip:

```bash
git clone https://github.com/justindal/leetcode-python-dataset
cd leetcode-python-dataset
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

Build the dataset locally:

```bash
leetcode-dataset

# or
python3 main.py
```

## Citation

newfacade/LeetCodeDataset:

```bibtex
@misc{xia2025leetcodedatasettemporaldatasetrobust,
	title={LeetCodeDataset: A Temporal Dataset for Robust Evaluation and Efficient Training of Code LLMs},
	author={Yunhui Xia and Wei Shen and Yan Wang and Jason Klein Liu and Huifeng Sun and Siyue Wu and Jian Hu and Xiaolong Xu},
	year={2025},
	eprint={2504.14655},
	archivePrefix={arXiv},
	primaryClass={cs.LG},
	url={https://arxiv.org/abs/2504.14655},
}
```

## License

Apache 2.0