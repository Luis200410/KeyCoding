#!/usr/bin/env python3
"""
Generate a comprehensive builtins list for Python and update langdata/python.json.
Collects:
- Builtin functions (from builtins)
- Builtin classes/types (list, dict, str, etc.)
- Methods of core types (list/dict/set/tuple/str/int/float/bool/bytes/bytearray/memoryview/range)
- Builtin exceptions
- Stdlib modules (sys.stdlib_module_names)

Writes back into langdata/python.json's `builtins` field (replacing it).
"""
from __future__ import annotations
import inspect
import json
import sys
import builtins as bi
from pathlib import Path
from types import BuiltinFunctionType, FunctionType
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / 'langdata' / 'python.json'


def first_line(doc: str | None) -> str:
    if not doc:
        return ""
    return doc.strip().splitlines()[0].strip()


def safe_signature(obj: Any) -> str:
    try:
        sig = str(inspect.signature(obj))
        return f"{getattr(obj, '__name__', type(obj).__name__)}{sig}"
    except Exception:
        name = getattr(obj, '__name__', None) or getattr(obj, '__qualname__', None) or type(obj).__name__
        return f"{name}(...)"


def add_entry(out: List[Dict[str, Any]], name: str, kind: str, signature: str, description: str, category: str):
    out.append({
        'name': name,
        'kind': kind,
        'signature': signature,
        'description': description or '',
        'category': category,
    })


def collect_builtins_functions(out: List[Dict[str, Any]]):
    for name in sorted(dir(bi)):
        obj = getattr(bi, name)
        if isinstance(obj, (BuiltinFunctionType, FunctionType)):
            if name.startswith('__'):
                continue
            add_entry(
                out,
                name=name,
                kind='function',
                signature=safe_signature(obj),
                description=first_line(getattr(obj, '__doc__', None)),
                category='Functions',
            )


CORE_TYPES = [list, dict, set, tuple, str, int, float, bool, bytes, bytearray, memoryview, range, complex]


def collect_builtin_types(out: List[Dict[str, Any]]):
    # Builtin classes/types
    for t in sorted({t for t in CORE_TYPES + [type, object, property, slice, staticmethod, classmethod, super, enumerate, reversed, zip, map, filter] }, key=lambda x: x.__name__):
        name = t.__name__
        cat = 'Types' if name not in ('property','staticmethod','classmethod','super','enumerate','reversed','zip','map','filter') else 'Utilities'
        add_entry(
            out,
            name=name,
            kind='class',
            signature=f"{name}(...)",
            description=first_line(getattr(t, '__doc__', None)),
            category=cat,
        )


def collect_methods_for_type(out: List[Dict[str, Any]], t: type, category: str):
    tname = t.__name__
    for attr in sorted(dir(t)):
        if attr.startswith('_'):
            continue
        try:
            obj = getattr(t, attr)
        except Exception:
            continue
        if not callable(obj):
            continue
        qname = f"{tname}.{attr}"
        sig = safe_signature(obj)
        desc = first_line(getattr(obj, '__doc__', None))
        add_entry(out, qname, 'method', sig, desc, category)


def collect_core_methods(out: List[Dict[str, Any]]):
    collect_methods_for_type(out, list, 'Containers')
    collect_methods_for_type(out, dict, 'Containers')
    collect_methods_for_type(out, set, 'Containers')
    collect_methods_for_type(out, tuple, 'Containers')
    collect_methods_for_type(out, str, 'Text & RegExp')
    collect_methods_for_type(out, bytes, 'Binary')
    collect_methods_for_type(out, bytearray, 'Binary')
    collect_methods_for_type(out, memoryview, 'Binary')
    collect_methods_for_type(out, int, 'Numeric & Math')
    collect_methods_for_type(out, float, 'Numeric & Math')
    collect_methods_for_type(out, complex, 'Numeric & Math')
    collect_methods_for_type(out, range, 'Iteration & Functional')


def collect_exceptions(out: List[Dict[str, Any]]):
    for name in sorted(dir(bi)):
        obj = getattr(bi, name)
        try:
            if isinstance(obj, type) and issubclass(obj, BaseException):
                add_entry(out, name, 'class', f"{name}(...)", first_line(getattr(obj, '__doc__', None)), 'Exceptions')
        except Exception:
            continue


def collect_stdlib_modules(out: List[Dict[str, Any]]):
    names = sorted(getattr(sys, 'stdlib_module_names', set()))
    for name in names:
        # avoid private names
        if name.startswith('_'):
            continue
        add_entry(out, name, 'module', f"import {name}", 'Standard library module.', 'Stdlib')


def unique_by_name(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out: List[Dict[str, Any]] = []
    for it in items:
        name = it.get('name')
        if name in seen:
            continue
        seen.add(name)
        out.append(it)
    return out


def main() -> int:
    items: List[Dict[str, Any]] = []
    collect_builtins_functions(items)
    collect_builtin_types(items)
    collect_core_methods(items)
    collect_exceptions(items)
    collect_stdlib_modules(items)

    items = unique_by_name(items)
    # stable sort: by category group, then name
    items.sort(key=lambda x: (x.get('category',''), x.get('name', '')))

    data = json.loads(JSON_PATH.read_text(encoding='utf-8'))
    data['builtins'] = items
    JSON_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Updated builtins: {len(items)} entries → {JSON_PATH}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

