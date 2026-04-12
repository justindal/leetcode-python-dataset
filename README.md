---
pretty_name: LeetCode Python Dataset
license: apache-2.0
language:
  - en
task_categories:
  - text-generation
task_ids:
  - text2text-generation
size_categories:
  - 1K<n<10K
tags:
  - code
  - python
  - leetcode
configs:
  - config_name: default
    default: true
    data_files:
      - split: train
        path: train.jsonl
      - split: valid
        path: valid.jsonl
      - split: test
        path: test.jsonl
  - config_name: benchmark
    data_files:
      - split: benchmark
        path: benchmark.jsonl
---

# leetcode-python-dataset

Code for building and publishing the [`justindal/leetcode-python-dataset`](https://huggingface.co/datasets/justindal/leetcode-python-dataset) dataset on Hugging Face.

Merges two open-source LeetCode datasets into a unified schema with consistent formatting, field normalisation, and solution validation.

## Dataset

| Split | Rows | Source |
|---|---|---|
| train | 2856 | newfacade + greengerong |
| valid | 310 | slug-group split from train |
| test | 228 | newfacade only |


## Schema

### `default` config (training)

Each row is a single-turn chat conversation in the standard `messages` format:

| Column | Type | Description |
|---|---|---|
| `messages` | list[dict] | Chat messages: system prompt, user problem, assistant solution |

Each message dict has keys `role` (`"system"`, `"user"`, or `"assistant"`) and `content` (string).

### `benchmark` config

Rows keep the full structured problem fields and include a split label:

| Column | Type | Description |
|---|---|---|
| `slug` | string | Problem slug / task id |
| `difficulty` | string | Problem difficulty |
| `tags` | list[string] | Topic tags |
| `problem` | string | Problem statement |
| `starter_code` | string | Prompt starter code |
| `solution` | string | Reference Python solution |
| `tests` | string or object | Source-provided tests metadata |
| `source` | string | Upstream source dataset |
| `type` | string | Original split: `train`, `valid`, or `test` |

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
```

Optional flags:
- `--verify` to filter the dataset against source tests
- `--verify-test` to also verify the test split
- `--publish --message "..."` for a non-interactive publish run

Verification is optional and can change the final row counts.

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

The same optional flags are available here as well.

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