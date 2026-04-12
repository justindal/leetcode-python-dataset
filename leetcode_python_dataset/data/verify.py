import ast
import os
import subprocess
import sys
import tempfile

from datasets import Dataset

from ..solution_env import ALLOWED_IMPORT_BLOCK
from .clean import _normalize_name

IMPORT_PRELUDE = ALLOWED_IMPORT_BLOCK

DATA_STRUCTURE_HELPERS = """\
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Node:
    def __init__(self, val=0, neighbors=None, left=None, right=None,
                 next=None, random=None, children=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []
        self.left = left
        self.right = right
        self.next = next
        self.random = random
        self.children = children if children is not None else []

def list_node(values):
    if not values:
        return None
    head = ListNode(values[0])
    current = head
    for val in values[1:]:
        current.next = ListNode(val)
        current = current.next
    return head

def tree_node(values):
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    q = [root]
    i = 1
    while q and i < len(values):
        node = q.pop(0)
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            q.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            q.append(node.right)
        i += 1
    return root

def is_same_list(l1, l2):
    while l1 and l2:
        if l1.val != l2.val:
            return False
        l1, l2 = l1.next, l2.next
    return l1 is None and l2 is None

def is_same_tree(t1, t2):
    if t1 is None and t2 is None:
        return True
    if t1 is None or t2 is None:
        return False
    return (t1.val == t2.val
            and is_same_tree(t1.left, t2.left)
            and is_same_tree(t1.right, t2.right))
"""

_PASS_MARKER = "__VERIFY_PASS__"


def _method_name_from_entry_point(entry_point: str) -> str:
    entry = (entry_point or "").strip()
    if not entry:
        return ""
    if "(" in entry:
        entry = entry.split("(", 1)[0]
    if "." in entry:
        entry = entry.split(".")[-1]
    return entry.strip()


def _top_level_functions(tree: ast.Module) -> list[str]:
    return [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]


def _solution_class_methods(tree: ast.Module) -> list[str]:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "Solution":
            return [
                child.name for child in node.body if isinstance(child, ast.FunctionDef)
            ]
    return []


def _matched_name(candidates: list[str], target: str) -> str | None:
    if not target:
        return None
    target_norm = _normalize_name(target)
    for name in candidates:
        if _normalize_name(name) == target_norm:
            return name
    return None


def _resolve_candidate_expr(solution: str, entry_point: str) -> str:
    try:
        tree = ast.parse(solution)
    except SyntaxError:
        method = _method_name_from_entry_point(entry_point)
        return method or "Solution()"

    method = _method_name_from_entry_point(entry_point)

    solution_methods = _solution_class_methods(tree)
    if solution_methods:
        matched_method = _matched_name(solution_methods, method)
        if matched_method:
            return f"Solution().{matched_method}"
        if len(solution_methods) == 1:
            return f"Solution().{solution_methods[0]}"
        return "Solution()"

    top_funcs = _top_level_functions(tree)
    matched_func = _matched_name(top_funcs, method)
    if matched_func:
        return matched_func
    if top_funcs:
        return top_funcs[-1]

    return method or "Solution()"


def _build_script(solution: str, test_code: str, candidate_expr: str) -> str:
    return f"""{IMPORT_PRELUDE}

{DATA_STRUCTURE_HELPERS}

{solution}

{test_code}

candidate = {candidate_expr}
check(candidate)
print("{_PASS_MARKER}")
"""


def verify_solution(
    solution: str,
    test_code: str,
    entry_point: str,
    timeout: int = 15,
) -> bool:
    candidate_expr = _resolve_candidate_expr(solution, entry_point)
    script = _build_script(solution, test_code, candidate_expr)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(script)
        f.flush()
        try:
            result = subprocess.run(
                [sys.executable, f.name],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return False
        finally:
            os.unlink(f.name)

    if result.returncode != 0:
        return False

    stdout_lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return bool(stdout_lines) and stdout_lines[-1] == _PASS_MARKER


def verify_dataset(
    ds: Dataset,
    test_lookup: dict[str, dict],
    verbose: bool = True,
) -> Dataset:
    passed_indices: set[int] = set()
    nf_pass = 0
    gg_pass = 0

    slugs = ds["slug"]
    solutions = ds["solution"]
    sources = ds["source"]

    for i, (slug, solution, source) in enumerate(zip(slugs, solutions, sources)):
        meta = test_lookup.get(slug)
        if not meta:
            continue

        test_code = meta.get("test", "")
        entry_point = meta.get("entry_point", "")
        if not test_code or not entry_point:
            continue

        ok = verify_solution(solution, test_code, entry_point)
        if ok:
            passed_indices.add(i)
            if source == "newfacade":
                nf_pass += 1
            else:
                gg_pass += 1

        if verbose and (i + 1) % 200 == 0:
            print(f"  Verified {i + 1}/{len(ds)} rows...")

    if verbose:
        print(f"  newfacade pass: {nf_pass}")
        print(f"  greengerong pass: {gg_pass}")
        print(f"  total pass: {nf_pass + gg_pass}")

    return ds.select(sorted(passed_indices))
