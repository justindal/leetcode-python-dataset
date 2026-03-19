import ast
import re

_FENCE_PYTHON = re.compile(r"```python\s*\n(.*?)```", re.DOTALL)
_FENCE_GENERIC = re.compile(r"```\s*\n(.*?)```", re.DOTALL)
_JS_INDICATORS = ("function ", "let ", "const ", "var ", "=> ", "===", "constructor(")
_DEF_LINE_RE = re.compile(
    r"^def\s+([A-Za-z_]\w*)\s*\((.*)\)(\s*(?:->\s*.+)?\s*:)$"
)


def extract_python_code(solution: str) -> str | None:
    sol = solution.strip()
    if not sol or sol == "None":
        return None

    for pattern in (_FENCE_PYTHON, _FENCE_GENERIC):
        matches = pattern.findall(sol)
        if matches:
            code = matches[0].strip()
            if "class " in code or "def " in code:
                return code

    if ("class " in sol or "def " in sol) and not sol.startswith("```"):
        return sol

    return None


def _normalize_name(name: str) -> str:
    return name.replace("_", "").lower()


def _ensure_self_in_def(def_line: str) -> str:
    stripped = def_line.strip()
    match = _DEF_LINE_RE.match(stripped)
    if not match:
        return stripped
    name, params, suffix = match.groups()
    params = params.strip()
    if params.startswith("self"):
        return f"def {name}({params}){suffix}"
    new_params = f"self, {params}" if params else "self"
    return f"def {name}({new_params}){suffix}"


def _extract_starter_method(starter_code: str | None) -> tuple[str | None, str | None]:
    if not starter_code:
        return None, None

    for line in starter_code.splitlines():
        stripped = line.strip()
        if not stripped.startswith("def "):
            continue
        if not stripped.endswith(":"):
            stripped = f"{stripped}:"
        match = _DEF_LINE_RE.match(stripped)
        if match:
            return match.group(1), _ensure_self_in_def(stripped)

    block = re.search(
        r"def\s+[A-Za-z_]\w*\s*\(.*?\)\s*(?:->\s*[^:]+)?\s*:",
        starter_code,
        re.DOTALL,
    )
    if not block:
        return None, None
    collapsed = " ".join(block.group(0).split())
    match = _DEF_LINE_RE.match(collapsed)
    if not match:
        return None, None
    return match.group(1), _ensure_self_in_def(collapsed)


def _signature_arg_exprs(def_line: str) -> list[str]:
    stub = f"class Solution:\n    {def_line}\n        pass\n"
    try:
        tree = ast.parse(stub)
    except SyntaxError:
        return []

    method = tree.body[0].body[0]
    args: list[str] = []
    for arg in method.args.posonlyargs + method.args.args:
        if arg.arg != "self":
            args.append(arg.arg)
    if method.args.vararg:
        args.append(f"*{method.args.vararg.arg}")
    for arg in method.args.kwonlyargs:
        args.append(f"{arg.arg}={arg.arg}")
    if method.args.kwarg:
        args.append(f"**{method.args.kwarg.arg}")
    return args


def _choose_target_function(
    top_level_funcs: list[ast.FunctionDef], starter_name: str | None
) -> ast.FunctionDef:
    if starter_name:
        for fn in top_level_funcs:
            if fn.name == starter_name:
                return fn
        starter_norm = _normalize_name(starter_name)
        for fn in top_level_funcs:
            if _normalize_name(fn.name) == starter_norm:
                return fn
    return top_level_funcs[-1]


def _wrapper_insert_line(tree: ast.Module) -> int:
    insert_line = 0
    for node in tree.body:
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            insert_line = node.end_lineno or node.lineno
            continue
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            insert_line = node.end_lineno or node.lineno
            continue
        break
    return insert_line


def normalize_solution_style(solution: str, starter_code: str | None = None) -> str:
    code = solution.strip()
    if not code:
        return code
    if re.search(r"\bclass\s+Solution\b", code):
        return code

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return code

    top_level_funcs = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    if not top_level_funcs:
        return code

    starter_name, starter_def = _extract_starter_method(starter_code)
    target = _choose_target_function(top_level_funcs, starter_name)

    if starter_def:
        method_def = starter_def
        call_args = _signature_arg_exprs(method_def)
    else:
        method_def = f"def {target.name}(self, *args, **kwargs):"
        call_args = ["*args", "**kwargs"]

    call_expr = ", ".join(call_args)
    call_stmt = (
        f"return {target.name}({call_expr})"
        if call_expr
        else f"return {target.name}()"
    )
    wrapper = [
        "class Solution:",
        f"    {method_def}",
        f"        {call_stmt}",
    ]

    lines = code.splitlines()
    insert_line = _wrapper_insert_line(tree)
    if insert_line > 0:
        new_lines = lines[:insert_line] + [""] + wrapper + [""] + lines[insert_line:]
    else:
        new_lines = wrapper + [""] + lines
    return "\n".join(new_lines).strip()


def is_python(code: str) -> bool:
    return not any(ind in code for ind in _JS_INDICATORS)


def is_row_valid(item: dict) -> bool:
    required = ["slug", "difficulty", "problem", "solution"]
    return all(item.get(k) for k in required)
