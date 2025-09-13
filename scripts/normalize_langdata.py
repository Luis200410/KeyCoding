#!/usr/bin/env python3
"""
Normalize langdata/*.json to share a common structure so the dashboard renders consistently.

Ensures the following top-level keys exist with sensible defaults:
- name: str (unchanged)
- slug: str (unchanged)
- version: str (unchanged)
- quick_start: list
- concepts: list
- common_tasks: list
- stdlib: list
- tools: list
- links: list
- builtins: list
- projects: list
- glossary: list
- tips: list

Also gently normalizes tools/links entries to be lists, and prints a short report.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LD = ROOT / 'langdata'

REQUIRED_LIST_KEYS = [
    'quick_start', 'concepts', 'common_tasks', 'stdlib', 'tools', 'links',
    'builtins', 'projects', 'glossary', 'tips'
]

def normalize_file(p: Path) -> tuple[bool, dict]:
    raw = json.loads(p.read_text(encoding='utf-8'))
    changed = False
    for k in REQUIRED_LIST_KEYS:
        if k not in raw or raw[k] is None:
            raw[k] = []
            changed = True
        elif not isinstance(raw[k], list):
            # Coerce to list when a single object/string is present
            raw[k] = [ raw[k] ]
            changed = True

    # Normalize tools: allow strings or objects; nothing to coerce further
    # Normalize links: ensure entries have title/url when objects
    def fix_links(lst):
        new = []
        for it in lst:
            if isinstance(it, str):
                new.append({'title': it, 'url': it})
            elif isinstance(it, dict):
                if 'title' in it and 'url' in it:
                    new.append(it)
                else:
                    # skip malformed link silently
                    continue
            else:
                continue
        return new
    links_fixed = fix_links(raw.get('links', []))
    if links_fixed != raw.get('links', []):
        raw['links'] = links_fixed
        changed = True

    # Ensure builtins is a list of dicts
    if not all(isinstance(x, dict) for x in raw.get('builtins', [])):
        raw['builtins'] = [x for x in raw['builtins'] if isinstance(x, dict)]
        changed = True

    if changed:
        p.write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding='utf-8')
    return changed, {k: len(raw.get(k, [])) for k in REQUIRED_LIST_KEYS}

def main() -> int:
    files = sorted(LD.glob('*.json'))
    any_changed = False
    for p in files:
        changed, summary = normalize_file(p)
        flag = 'UPDATED' if changed else 'ok'
        print(f"{flag:7} {p.name} -> " + ", ".join(f"{k}:{summary[k]}" for k in ('quick_start','concepts','common_tasks','projects','glossary','tips')))
        any_changed = any_changed or changed
    print('Done.' + (' (changes written)' if any_changed else ''))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

