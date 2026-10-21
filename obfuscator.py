from __future__ import annotations

import ast
import base64
import collections
import hashlib
import marshal
import os
import random
import secrets
import string
import subprocess
import sys
import time
import traceback
import zlib
from pathlib import Path


VERSION = "1.0.0"
GITHUB_HANDLE  = "Hidden-Rhythm"
GITHUB_URL     = "https://github.com/Hidden-Rhythm"
DISCORD_HANDLE = "hidden_rhythm"
DISCORD_URL    = "https://discord.com/users/hidden_rhythm"


def _ensure_rich() -> None:
    try:
        import rich  # noqa: F401
        return
    except ImportError:
        pass
    sys.stdout.write("Installing UI dependency (rich)…\n")
    sys.stdout.flush()
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--quiet", "--upgrade", "rich"],
        check=True,
    )
    os.execv(sys.executable, [sys.executable] + sys.argv)


_ensure_rich()

from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table
from rich.text import Text


# palette

_C_ACCENT = "#e0af68"   # soft gold
_C_RUN    = "#7aa2f7"   # cool blue — active stage
_C_OK     = "#9ece6a"   # muted green — done
_C_ERR    = "#f7768e"   # muted red — fail
_C_WARN   = "#e0af68"   # reuse accent
_C_MUTED  = "#565f89"   # slate — secondary text
_C_DIM    = "#3b4261"   # deep slate — borders, hints
_C_FG     = "default"

_SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"


# primitives

def _rid(n: int | None = None) -> str:
    n = n or random.randint(8, 14)
    return "_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def _rhex(n: int = 16) -> str:
    return secrets.token_hex(n)


def _keystream(key: bytes, n: int) -> bytes:
    out = bytearray()
    ctr = 0
    while len(out) < n:
        out.extend(hashlib.sha256(key + ctr.to_bytes(8, "big")).digest())
        ctr += 1
    return bytes(out[:n])


def _xor_stream(data: bytes, key: bytes) -> bytes:
    ks = _keystream(key, len(data))
    return bytes(a ^ b for a, b in zip(data, ks))


def _xor_repeat(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def _b64_chunks(raw: bytes, lo: int = 120, hi: int = 240) -> list[str]:
    s = base64.b64encode(raw).decode()
    out, i = [], 0
    while i < len(s):
        n = random.randint(lo, hi)
        out.append(s[i:i + n])
        i += n
    return out


# AST constant + import encryption

_SKIP_LONG_THRESHOLD = 500


class _ConstEncryptor(ast.NodeTransformer):
    def __init__(self, key: bytes, skip_ids: set[int], s_name: str, b_name: str):
        self.key = key
        self.skip_ids = skip_ids
        self.s_name = s_name
        self.b_name = b_name

    def _enc_str_call(self, s: str) -> ast.Call:
        enc = _xor_repeat(s.encode("utf-8"), self.key)
        return ast.Call(
            func=ast.Name(id=self.s_name, ctx=ast.Load()),
            args=[ast.Constant(value=enc.hex())],
            keywords=[],
        )

    def visit_Constant(self, node: ast.Constant):
        if id(node) in self.skip_ids:
            return node
        v = node.value
        if isinstance(v, str) and v:
            if len(v) > _SKIP_LONG_THRESHOLD:
                return node
            enc = _xor_repeat(v.encode("utf-8"), self.key)
            return ast.copy_location(ast.Call(
                func=ast.Name(id=self.s_name, ctx=ast.Load()),
                args=[ast.Constant(value=enc.hex())], keywords=[]), node)
        if isinstance(v, bytes) and v:
            if len(v) > _SKIP_LONG_THRESHOLD:
                return node
            enc = _xor_repeat(v, self.key)
            return ast.copy_location(ast.Call(
                func=ast.Name(id=self.b_name, ctx=ast.Load()),
                args=[ast.Constant(value=enc.hex())], keywords=[]), node)
        return node

    def visit_JoinedStr(self, node):
        return node

    def visit_Import(self, node):
        new_nodes: list[ast.stmt] = []
        for alias in node.names:
            name = alias.name
            if alias.asname:
                bind = alias.asname
                fromlist = ast.keyword(arg="fromlist", value=ast.List(
                    elts=[ast.Constant(value="*")], ctx=ast.Load()))
            else:
                bind = name.split(".")[0]
                fromlist = None
            import_call = ast.Call(
                func=ast.Name(id="__import__", ctx=ast.Load()),
                args=[self._enc_str_call(name)],
                keywords=([fromlist] if fromlist is not None else []),
            )
            new_nodes.append(ast.Assign(
                targets=[ast.Name(id=bind, ctx=ast.Store())],
                value=import_call,
            ))
        return new_nodes

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.level != 0 or node.module == "__future__":
            return node
        module = node.module or ""
        new_nodes: list[ast.stmt] = []
        for alias in node.names:
            name = alias.name
            bind = alias.asname or name
            import_call = ast.Call(
                func=ast.Name(id="__import__", ctx=ast.Load()),
                args=[self._enc_str_call(module)],
                keywords=[ast.keyword(arg="fromlist", value=ast.List(
                    elts=[self._enc_str_call(name)], ctx=ast.Load()))],
            )
            new_nodes.append(ast.Assign(
                targets=[ast.Name(id=bind, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Name(id="getattr", ctx=ast.Load()),
                    args=[import_call, self._enc_str_call(name)],
                    keywords=[],
                ),
            ))
        return new_nodes


def _find_skip(tree: ast.AST) -> set[int]:
    skip: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.body and isinstance(node.body[0], ast.Expr):
                e = node.body[0]
                if isinstance(e.value, ast.Constant) and isinstance(e.value.value, str):
                    skip.add(id(e.value))
    if hasattr(ast, "MatchValue"):
        for node in ast.walk(tree):
            if isinstance(node, ast.MatchValue):
                skip.add(id(node.value))
    return skip


def _pick_names(tree: ast.AST) -> tuple[str, str, str]:
    existing = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            existing.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            existing.add(node.name)
    s, b, k = "_s", "_b", "_K"
    while s in existing:
        s = "_" + s
    while b in existing:
        b = "_" + b
    while k in existing:
        k = "_" + k
    return s, b, k


def _decoder_src(key: bytes, s_name: str, b_name: str, k_name: str) -> str:
    return (
        f"{k_name} = bytes({list(key)})\n"
        f"def {s_name}(_h):\n"
        f"    _x = bytes.fromhex(_h)\n"
        f"    return bytes(_a ^ {k_name}[_i % 32] for _i, _a in enumerate(_x)).decode('utf-8')\n"
        f"def {b_name}(_h):\n"
        f"    _x = bytes.fromhex(_h)\n"
        f"    return bytes(_a ^ {k_name}[_i % 32] for _i, _a in enumerate(_x))\n"
    )


def _transform(source_text: str, key: bytes) -> tuple[ast.Module, str, str, str]:
    tree = ast.parse(source_text)
    skip = _find_skip(tree)
    s_name, b_name, k_name = _pick_names(tree)

    future, rest = [], []
    for stmt in tree.body:
        if isinstance(stmt, ast.ImportFrom) and stmt.module == "__future__":
            future.append(stmt)
        else:
            rest.append(stmt)
    tree.body = rest

    _ConstEncryptor(key, skip, s_name, b_name).visit(tree)

    decoder_tree = ast.parse(_decoder_src(key, s_name, b_name, k_name)).body
    tree.body = future + decoder_tree + tree.body
    ast.fix_missing_locations(tree)
    return tree, s_name, b_name, k_name


def _encrypt_module_source(src: str, key: bytes) -> ast.Module:
    tree = ast.parse(src)
    skip = _find_skip(tree)
    s_name, b_name, k_name = _pick_names(tree)
    _ConstEncryptor(key, skip, s_name, b_name).visit(tree)
    decoder_tree = ast.parse(_decoder_src(key, s_name, b_name, k_name)).body
    tree.body = decoder_tree + tree.body
    ast.fix_missing_locations(tree)
    return tree


def _build_payload(source_text: str, key: bytes) -> bytes:
    tree, _, _, _ = _transform(source_text, key)
    compressed = zlib.compress(marshal.dumps(compile(tree, "<obf>", "exec")), 9)
    return _xor_stream(compressed, key)


# stage-2 template

_STAGE2_TEMPLATE = r'''
def {warmup}():
    _sys = __import__("sys")
    if getattr(_sys, "gettrace")() is not None:
        getattr(_sys, "exit")(0)
    _t = __import__("time")
    _t0 = getattr(_t, "perf_counter")()
    _x = 0
    for _i in range(64):
        _x = (_x + _i) & 0xffff
    if getattr(_t, "perf_counter")() - _t0 > 0.02:
        getattr(_sys, "exit")(0)
    _o = __import__("os")
    if getattr(_o, "cpu_count")() < 2:
        getattr(_sys, "exit")(0)
    _r = __import__("random")
    getattr(_t, "sleep")(0.3 + getattr(_r, "random")() * 2.5)


def {loadfn}():
    _b = __import__("base64")
    _z = __import__("zlib")
    _m = __import__("marshal")
    _B = __import__("builtins")
    _h = __import__("hashlib")
    _data = getattr(_b, "b64decode")({payload_b64})
    _ks = b""
    _c = 0
    while len(_ks) < len(_data):
        _hash = getattr(_h, "sha256")({payload_key} + getattr(_c, "to_bytes")(8, "big"))
        _ks += getattr(_hash, "digest")()
        _c += 1
    _buf = bytes(_a ^ _b for _a, _b in zip(_data, _ks))
    _raw = getattr(_z, "decompress")(_buf)
    _co = getattr(_m, "loads")(_raw)
    _e = getattr(_B, "exec")
    _e(_co, {{"__name__": "__main__", "__file__": __file__}})


{warmup}()
{loadfn}()
'''


def _build_stage2_source(payload_key: bytes, payload_cipher: bytes) -> str:
    payload_b64 = _b64_chunks(payload_cipher, lo=100, hi=200)
    joined = "(\n" + "\n".join(f'    "{c}"' for c in payload_b64) + "\n)"
    return _STAGE2_TEMPLATE.format(
        warmup=_rid(),
        loadfn=_rid(),
        payload_b64=joined,
        payload_key=repr(payload_key),
    )


def _build_stage1(payload_key: bytes, payload_cipher: bytes) -> tuple[str, bytes]:
    stage2_src = _build_stage2_source(payload_key, payload_cipher)
    stage2_tree = _encrypt_module_source(stage2_src, secrets.token_bytes(32))
    stage2_code = compile(stage2_tree, "<mod>", "exec")
    stage2_marshaled = marshal.dumps(stage2_code)
    loader_key = secrets.token_bytes(32)
    stage2_cipher = _xor_stream(zlib.compress(stage2_marshaled, 9), loader_key)

    cipher_b64 = _b64_chunks(stage2_cipher, lo=120, hi=240)
    salt = hashlib.sha256(stage2_cipher[:64]).digest()
    key_masked = _xor_repeat(loader_key, salt)

    n = {k: _rid() for k in ("blob", "salt", "km", "load", "apply", "init")}

    lines: list[str] = []
    lines.append(f"{n['blob']} = (")
    for chunk in cipher_b64:
        lines.append(f'    "{chunk}"')
    lines.append(")")
    lines.append(f"{n['salt']} = bytes.fromhex({salt.hex()!r})")
    lines.append(f"{n['km']} = bytes.fromhex({key_masked.hex()!r})")
    lines.append("")
    lines.append(f"def {n['load']}(_d, _s, _k):")
    lines.append(f"    _h = __import__('hashlib')")
    lines.append(f"    _z = __import__('zlib')")
    lines.append(f"    _key = bytes(_a ^ _b for _a, _b in zip(_k, _s))")
    lines.append(f"    _ks = b''")
    lines.append(f"    _c = 0")
    lines.append(f"    while len(_ks) < len(_d):")
    lines.append(f"        _ks += getattr(getattr(_h, 'sha256')(_key + _c.to_bytes(8, 'big')), 'digest')()")
    lines.append(f"        _c += 1")
    lines.append(f"    _buf = bytes(_a ^ _b for _a, _b in zip(_d, _ks))")
    lines.append(f"    return getattr(_z, 'decompress')(_buf)")
    lines.append("")
    lines.append(f"def {n['apply']}(_m):")
    lines.append(f"    _ml = __import__('marshal')")
    lines.append(f"    _B = __import__('builtins')")
    lines.append(f"    _co = getattr(_ml, 'loads')(_m)")
    lines.append(f"    _e = getattr(_B, 'exec')")
    lines.append(f"    _e(_co, {{'__name__': '__main__', '__file__': __file__}})")
    lines.append("")
    lines.append(f"def {n['init']}():")
    lines.append(f"    _b = __import__('base64')")
    lines.append(f"    _c = getattr(_b, 'b64decode')({n['blob']})")
    lines.append(f"    _m = {n['load']}(_c, {n['salt']}, {n['km']})")
    lines.append(f"    {n['apply']}(_m)")
    lines.append("")
    lines.append("if __name__ == '__main__':")
    lines.append(f"    {n['init']}()")

    body_src = "\n".join(lines) + "\n"

    bootstrap_tree = _encrypt_module_source(body_src, secrets.token_bytes(32))
    final_source = ast.unparse(bootstrap_tree) + "\n"

    return final_source, stage2_cipher


# neutral surface

_JUNK_IMPORTS = ["os", "sys", "json", "datetime", "textwrap", "collections", "typing", "abc"]

_JUNK_HELPERS = [
    "load_env", "merge_dict", "chunk_iter", "coerce_int", "size_of",
    "retry", "slugify", "paginate", "fmt_delta", "cache_call",
    "read_json", "write_json", "norm_path", "safe_call", "dict_get",
    "list_uniq", "sort_keys", "deep_copy", "flatten", "batched",
    "unpack_tuple", "defaults_of", "parse_bool", "fmt_size", "clamp",
]

_JUNK_CLASSES = [
    "Config", "Cache", "Buffer", "Registry", "Store",
    "Pool", "Queue", "Ring", "Pair", "Frame", "Record",
]


def _decoy_surface() -> str:
    return (
        "# AUTO-GENERATED — do not edit\n"
        f"# template: {secrets.token_hex(3)}.tpl\n"
        f"# generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        "# regenerate via tools/build.py\n"
    )


def _junk_function() -> str:
    fn = "_" + random.choice(_JUNK_HELPERS) + "_" + _rhex(3)
    a, b, c = _rid(), _rid(), _rid()
    kind = random.choice(("str", "dict", "iter", "size", "num", "deco"))
    if kind == "str":
        doc = random.choice(["Normalize a string.", "", "Return a slug."])
        body = (
            f"    if not isinstance({a}, str):\n"
            f"        return ''\n"
            f"    return {a}.strip().lower().replace(' ', '_').replace('-', '_')\n"
        )
    elif kind == "dict":
        doc = random.choice(["Merge dicts.", "", "Return merged mapping."])
        body = (
            f"    _out = dict({b} or {{}})\n"
            f"    _out.update({a} or {{}})\n"
            f"    for _k, _v in _out.items():\n"
            f"        if _v is None:\n"
            f"            _out[_k] = {c}\n"
            f"    return _out\n"
        )
    elif kind == "iter":
        doc = random.choice(["Yield batches.", "", "Chunk an iterable."])
        body = (
            f"    _n = int({b} or 16)\n"
            f"    _buf = []\n"
            f"    for _item in {a}:\n"
            f"        _buf.append(_item)\n"
            f"        if len(_buf) >= _n:\n"
            f"            yield _buf\n"
            f"            _buf = []\n"
            f"    if _buf:\n"
            f"        yield _buf\n"
        )
    elif kind == "size":
        doc = random.choice(["Return byte length.", "", "Size of file."])
        body = (
            f"    try:\n"
            f"        with open({a}, 'rb') as _fh:\n"
            f"            return len(_fh.read())\n"
            f"    except OSError:\n"
            f"        return 0\n"
        )
    elif kind == "num":
        doc = random.choice(["Coerce to int.", "", "Return non-negative int."])
        body = (
            f"    try:\n"
            f"        _v = int({a})\n"
            f"    except (TypeError, ValueError):\n"
            f"        _v = {b} or 0\n"
            f"    return max({c or 0}, _v)\n"
        )
    else:
        doc = random.choice(["Wrap a callable.", "", "Return a passthrough wrapper."])
        body = (
            f"    def _wrap(*_a, **_kw):\n"
            f"        return {a}(*_a, **_kw)\n"
            f"    return _wrap\n"
        )
    doc_line = f'    """{doc}"""\n' if doc else ""
    return f"def {fn}({a}, {b}=None, {c}=None):\n{doc_line}{body}"


def _junk_class() -> str:
    cls = random.choice(_JUNK_CLASSES) + "_" + _rhex(2)
    m = "_" + random.choice(["put", "get", "add", "push", "pop", "has", "len"]) + "_" + _rhex(3)
    return (
        f"class {cls}:\n"
        f"    __slots__ = ('items', 'index', 'name')\n"
        f"    def __init__(self, items=None, name=None):\n"
        f"        self.items = list(items or [])\n"
        f"        self.index = {{}}\n"
        f"        self.name = name\n"
        f"    def {m}(self, key):\n"
        f"        self.items.append(key)\n"
        f"        self.index[len(self.items) - 1] = key\n"
        f"        return len(self.items)\n"
        f"    def __repr__(self):\n"
        f"        return f'<{cls} n={{len(self.items)}}>'\n"
        f"    def __len__(self):\n"
        f"        return len(self.items)\n"
    )


def _junk_block() -> str:
    out: list[str] = []
    for mod in random.sample(_JUNK_IMPORTS, k=random.randint(3, 5)):
        out.append(f"import {mod} as {_rid()}")
    out.append("")
    for _ in range(random.randint(5, 12)):
        out.append(_junk_function())
        out.append("")
    for _ in range(random.randint(1, 3)):
        out.append(_junk_class())
        out.append("")
    return "\n".join(out)


# TUI — state

STAGES = [
    ("read",      "read source"),
    ("parse",     "encrypt constants"),
    ("payload",   "build payload"),
    ("stage2",    "build stage-2"),
    ("bootstrap", "build bootstrap"),
    ("surface",   "emit surface"),
    ("verify",    "syntax verify"),
    ("write",     "write output"),
]


class BuildState:
    def __init__(self) -> None:
        self.stages: dict[str, dict] = {k: {"status": "pending", "t": None} for k, _ in STAGES}
        self.log: collections.deque[tuple[str, str, str]] = collections.deque(maxlen=400)
        self.metrics: dict[str, object] = {
            "src_path": "", "out_path": "",
            "src_bytes": 0, "payload_bytes": 0,
            "stage2_bytes": 0, "out_bytes": 0,
            "sha256": "",
        }
        self.done = False
        self.failed = False

    def log_line(self, level: str, msg: str) -> None:
        self.log.append((time.strftime("%H:%M:%S"), level, msg))

    def info(self, msg: str) -> None: self.log_line("info", msg)
    def ok(self, msg: str) -> None:   self.log_line("ok",   msg)
    def warn(self, msg: str) -> None: self.log_line("warn", msg)
    def err(self, msg: str) -> None:  self.log_line("err",  msg)


# TUI — rendering

def _bytes_fmt(n: int) -> str:
    return f"{n:,} B" if n else "—"


def _short_hash(h: str) -> str:
    return f"{h[:8]}…{h[-8:]}" if len(h) >= 20 else (h or "—")


def _link(text: str, url: str, color: str) -> Text:
    """Clickable hyperlink via OSC 8 (Windows Terminal, iTerm2, WezTerm, Kitty, …)."""
    return Text(text, style=f"link {url} {color} underline")


def _render_header(state: BuildState) -> Panel:
    total = len(STAGES)
    done = sum(1 for s in state.stages.values() if s["status"] == "done")

    bar_w = 24
    filled = int(bar_w * done / total) if total else 0
    bar = Text()
    bar.append("█" * filled, style=_C_ACCENT)
    bar.append("░" * (bar_w - filled), style=_C_DIM)
    bar.append(f"  {done}/{total}", style=_C_MUTED)

    top = Table.grid(expand=True, padding=(0, 0))
    top.add_column(justify="left")
    top.add_column(justify="right")
    top.add_row(
        Text.assemble(
            ("obfuscator", f"bold {_C_ACCENT}"),
            ("   ·   ", _C_DIM),
            ("multi-layer python hardening", _C_MUTED),
        ),
        Text.assemble((f"v{VERSION}", _C_MUTED)),
    )

    # signature row — links are clickable
    sig = Text.assemble(
        ("by ", _C_DIM),
        _link(GITHUB_HANDLE, GITHUB_URL, f"bold {_C_ACCENT}"),
        ("   ·   ", _C_DIM),
        ("github ", _C_DIM),
        _link("github.com/Hidden-Rhythm", GITHUB_URL, _C_RUN),
        ("   ·   ", _C_DIM),
        ("discord ", _C_DIM),
        _link(DISCORD_HANDLE, DISCORD_URL, _C_RUN),
    )

    body = Group(top, sig, Text(""), bar)
    return Panel(body, box=box.ROUNDED, border_style=_C_DIM, padding=(0, 2))


def _render_stages(state: BuildState) -> Panel:
    t = Table.grid(expand=True, padding=(0, 1))
    t.add_column(width=2)
    t.add_column(ratio=1)
    t.add_column(justify="right", width=10)

    frame = _SPINNER[int(time.time() * 12) % len(_SPINNER)]

    for key, label in STAGES:
        s = state.stages[key]
        st = s["status"]
        if st == "pending":
            icon = Text("·", style=_C_DIM)
            name = Text(label, style=_C_DIM)
            time_col = Text("", style=_C_DIM)
        elif st == "run":
            icon = Text(frame, style=_C_RUN)
            name = Text(label, style=_C_RUN)
            time_col = Text("running", style=_C_RUN)
        elif st == "done":
            icon = Text("✓", style=_C_OK)
            name = Text(label, style=_C_MUTED)
            ms = int((s["t"] or 0) * 1000)
            time_col = Text(f"{ms} ms", style=_C_DIM)
        elif st == "fail":
            icon = Text("✗", style=_C_ERR)
            name = Text(label, style=_C_ERR)
            time_col = Text("failed", style=_C_ERR)
        else:
            icon = Text("·", style=_C_DIM)
            name = Text(label, style=_C_MUTED)
            time_col = Text("", style=_C_DIM)

        t.add_row(icon, name, time_col)

    return Panel(
        t,
        title=f"[{_C_MUTED}]pipeline[/]",
        title_align="left",
        box=box.ROUNDED,
        border_style=_C_DIM,
        padding=(0, 1),
    )


def _render_metrics(state: BuildState) -> Panel:
    m = state.metrics
    t = Table.grid(expand=True, padding=(0, 1))
    t.add_column(style=_C_MUTED, no_wrap=True)
    t.add_column(justify="right", style=_C_FG, no_wrap=True)

    def row(label: str, value: str, accent: str = _C_FG) -> None:
        t.add_row(Text(label, style=_C_MUTED), Text(value, style=accent))

    row("source",  _bytes_fmt(m["src_bytes"]))
    row("payload", _bytes_fmt(m["payload_bytes"]))
    row("stage-2", _bytes_fmt(m["stage2_bytes"]))
    row("output",  _bytes_fmt(m["out_bytes"]), accent=_C_ACCENT)
    row("layers",  "4")
    row("sha256",  _short_hash(m["sha256"]))

    return Panel(
        t,
        title=f"[{_C_MUTED}]metrics[/]",
        title_align="left",
        box=box.ROUNDED,
        border_style=_C_DIM,
        padding=(0, 1),
    )


_LEVEL_STYLE = {
    "info": (_C_RUN, "info"),
    "ok":   (_C_OK,  "ok  "),
    "warn": (_C_WARN, "warn"),
    "err":  (_C_ERR, "err "),
}


def _render_log(state: BuildState) -> Panel:
    body = Text()
    if not state.log:
        body.append("waiting…", style=_C_DIM)
    else:
        for ts, level, msg in state.log:
            color, chip = _LEVEL_STYLE.get(level, (_C_MUTED, "info"))
            body.append(f"{ts}  ", style=_C_DIM)
            body.append(f" {chip} ", style=f"bold {color} on #1a1b26")
            body.append("  ", style=_C_DIM)
            body.append_text(Text.from_markup(msg, style=_C_FG))
            body.append("\n")

    return Panel(
        body,
        title=f"[{_C_MUTED}]log[/]",
        title_align="left",
        box=box.ROUNDED,
        border_style=_C_DIM,
        padding=(0, 1),
    )


def _render_footer(state: BuildState) -> Text:
    if state.failed:
        return Text.assemble(
            ("  ✗  ", f"bold {_C_ERR}"),
            ("build failed", _C_ERR),
            ("  ·  inspect log above", _C_DIM),
        )
    if state.done:
        return Text.assemble(
            ("  ✓  ", f"bold {_C_OK}"),
            ("build complete", _C_OK),
            ("  ·  ", _C_DIM),
            (f"{state.metrics['out_path']}", _C_MUTED),
            ("  ·  run  ", _C_DIM),
            (f"python {state.metrics['out_path']}", _C_MUTED),
        )
    return Text.assemble(
        ("  ", ""),
        ("8 stages", _C_DIM),
        ("  ·  ", _C_DIM),
        ("fresh keys per build", _C_DIM),
        ("  ·  ", _C_DIM),
        ("ctrl+c to cancel", _C_DIM),
    )


def _render(state: BuildState) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="head", size=6),
        Layout(name="main", ratio=1, minimum_size=11),
        Layout(name="log",  size=13),
        Layout(name="foot", size=1),
    )
    layout["main"].split_row(
        Layout(name="stages",  ratio=3, minimum_size=36),
        Layout(name="metrics", ratio=2, minimum_size=28),
    )
    layout["head"].update(_render_header(state))
    layout["stages"].update(_render_stages(state))
    layout["metrics"].update(_render_metrics(state))
    layout["log"].update(_render_log(state))
    layout["foot"].update(_render_footer(state))
    return layout


def _run(state: BuildState, live, key: str, fn, *a, **kw):
    s = state.stages[key]
    s["status"] = "run"
    live.update(_render(state))
    t0 = time.perf_counter()
    try:
        r = fn(*a, **kw)
    except Exception:
        s["status"] = "fail"
        live.update(_render(state))
        raise
    s["t"] = time.perf_counter() - t0
    s["status"] = "done"
    live.update(_render(state))
    return r


# path prompt

def _prompt_paths(console: Console) -> tuple[Path, Path] | None:
    console.print()
    console.print(Rule(
        f"[{_C_ACCENT}]obfuscator[/] [{_C_MUTED}]· setup[/]",
        style=_C_DIM, align="left",
    ))
    console.print()
    console.print(Text("  source file", style=f"bold {_C_MUTED}"))
    raw = Prompt.ask("    path", console=console).strip().strip('"').strip("'")
    if not raw:
        return None
    src = Path(raw).expanduser().resolve()
    if not src.is_file() or src.suffix != ".py":
        console.print(f"    [bold {_C_ERR}]not a .py:[/] {src}")
        return None

    default_out = src.with_name(f"{src.stem}_obf.py")
    console.print()
    console.print(Text("  output file", style=f"bold {_C_MUTED}"))
    raw_out = Prompt.ask(
        "    path", default=str(default_out), console=console,
    ).strip().strip('"').strip("'")
    return src, Path(raw_out).expanduser().resolve()


# build pipeline

def _build(state: BuildState, live, src: Path, out: Path) -> None:
    state.metrics["src_path"] = str(src)
    state.metrics["out_path"] = str(out)

    def _read():
        text = src.read_text(encoding="utf-8")
        state.metrics["src_bytes"] = len(text.encode())
        state.ok(f"source read · [bold]{state.metrics['src_bytes']:,}[/bold] bytes")
        return text

    source_text = _run(state, live, "read", _read)

    def _parse():
        tree, s_name, b_name, _ = _transform(source_text, secrets.token_bytes(32))
        n_const = sum(
            1 for n in ast.walk(tree)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            and n.func.id in (s_name, b_name)
        )
        state.ok(f"constants encrypted · [bold]{n_const}[/bold] nodes (str + bytes)")
        return source_text

    _run(state, live, "parse", _parse)

    def _payload():
        key = secrets.token_bytes(32)
        cipher = _build_payload(source_text, key)
        state.metrics["payload_bytes"] = len(cipher)
        state.ok(f"payload · [bold]{len(cipher):,}[/bold] bytes · compile → marshal → zlib → xor")
        return key, cipher

    payload_key, payload_cipher = _run(state, live, "payload", _payload)

    def _stage2():
        src2 = _build_stage2_source(payload_key, payload_cipher)
        state.ok(f"stage-2 source · [bold]{len(src2):,}[/bold] chars pre-encrypt")
        return src2

    _run(state, live, "stage2", _stage2)

    def _bootstrap():
        body, s2_cipher = _build_stage1(payload_key, payload_cipher)
        state.metrics["stage2_bytes"] = len(s2_cipher)
        state.ok(f"bootstrap · [bold]{len(s2_cipher):,}[/bold] bytes cipher · AST-encrypted")
        return body

    body = _run(state, live, "bootstrap", _bootstrap)

    def _surface():
        block = _decoy_surface() + "\n" + _junk_block()
        state.ok(f"neutral surface · [bold]{len(block):,}[/bold] chars decoy")
        return block

    surface = _run(state, live, "surface", _surface)

    final = surface + "\n" + body
    state.metrics["out_bytes"] = len(final.encode())

    def _verify():
        compile(final, "<verify>", "exec")
        state.ok("syntax check passed")

    _run(state, live, "verify", _verify)

    def _write():
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(final, encoding="utf-8")
        state.metrics["sha256"] = hashlib.sha256(out.read_bytes()).hexdigest()
        state.ok(f"written · [bold]{out.name}[/bold] · {state.metrics['out_bytes']:,} bytes")
        state.info(f"sha256 · [{_C_DIM}]{state.metrics['sha256']}[/]")

    _run(state, live, "write", _write)
    state.done = True


# entry

def main() -> int:
    console = Console(highlight=False, soft_wrap=False)
    console.clear()

    paths = _prompt_paths(console)
    if paths is None:
        console.print(f"  [{_C_ERR}]aborted[/]")
        return 1
    src, out = paths

    console.print()
    console.print(Rule(style=_C_DIM))
    console.print()

    state = BuildState()
    state.metrics["src_path"] = str(src)
    state.metrics["out_path"] = str(out)
    state.info(f"source · [bold]{src.name}[/bold]")
    state.info(f"output · [bold]{out.name}[/bold]")

    with Live(
        _render(state),
        console=console,
        refresh_per_second=20,
        screen=False,
        transient=False,
    ) as live:
        try:
            _build(state, live, src, out)
            live.update(_render(state))
            time.sleep(0.4)
        except Exception as e:
            state.failed = True
            state.err(f"error · {e}")
            for line in traceback.format_exc().splitlines():
                state.log_line("err", f"[{_C_DIM}]{line}[/]")
            live.update(_render(state))
            time.sleep(1.5)
            return 2

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print()
        raise SystemExit(130)