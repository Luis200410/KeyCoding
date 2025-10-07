from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List

from django.conf import settings


LANGDATA_DIR = Path(settings.BASE_DIR) / 'langdata'


def _langdata_path(slug: str) -> Path:
    return LANGDATA_DIR / f"{slug}.json"


def load_language_data(slug: str) -> Dict[str, Any]:
    """Load a language JSON document from disk."""
    path = _langdata_path(slug)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            # Return empty shell to avoid crashes if file is corrupted
            return {"name": slug.title(), "slug": slug}
    return {"name": slug.title(), "slug": slug}


def save_language_data(slug: str, data: Dict[str, Any]) -> None:
    """Persist the language JSON document back to disk."""
    path = _langdata_path(slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    # We deep copy to avoid side-effects when dumping to JSON.
    payload = deepcopy(data)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding='utf-8',
    )
def _ensure_task(task: Any) -> Dict[str, Any]:
    if isinstance(task, dict):
        return {
            'title': str(task.get('title', "")),
            'description': str(task.get('description', "")),
            'code': str(task.get('code', "")),
        }
    return {'title': "", 'description': "", 'code': ""}


def _ensure_task_group(group: Any) -> Dict[str, Any]:
    name = ""
    tasks: List[Any] = []
    if isinstance(group, dict):
        name = str(group.get('group', ""))
        tasks = group.get('tasks', []) or []
    return {
        'group': name,
        'tasks': [_ensure_task(t) for t in tasks],
    }


def _ensure_project_step(step: Any) -> Dict[str, Any]:
    if isinstance(step, dict):
        return {
            'title': str(step.get('title', "")),
            'text': str(step.get('text', "")),
            'code': str(step.get('code', "")),
        }
    return {'title': "", 'text': "", 'code': ""}


def _ensure_project(project: Any) -> Dict[str, Any]:
    if isinstance(project, dict):
        return {
            'title': str(project.get('title', "")),
            'summary': str(project.get('summary', "")),
            'description': str(project.get('description', "")),
            'steps': [_ensure_project_step(s) for s in project.get('steps', []) or []],
        }
    return {'title': "", 'summary': "", 'description': "", 'steps': []}


def _ensure_concept(concept: Any) -> Dict[str, Any]:
    if isinstance(concept, dict):
        return {
            'id': str(concept.get('id', "")),
            'title': str(concept.get('title', "")),
            'tag': str(concept.get('tag', "")),
            'description': str(concept.get('description', "")),
            'code': str(concept.get('code', "")),
        }
    return {'id': "", 'title': "", 'tag': "", 'description': "", 'code': ""}


def _ensure_quick_start(item: Any) -> Dict[str, Any]:
    if isinstance(item, dict):
        return {
            'title': str(item.get('title', "")),
            'description': str(item.get('description', "")),
            'code': str(item.get('code', "")),
        }
    return {'title': "", 'description': "", 'code': ""}


def _ensure_glossary_entry(item: Any) -> Dict[str, Any]:
    if isinstance(item, dict):
        return {
            'term': str(item.get('term', "")),
            'definition': str(item.get('definition', "")),
        }
    return {'term': "", 'definition': ""}


def _ensure_tip(item: Any) -> Dict[str, Any]:
    if isinstance(item, dict):
        return {
            'title': str(item.get('title', "")),
            'note': str(item.get('note', item.get('text', ""))),
        }
    return {'title': "", 'note': str(item)}


def _ensure_tool(item: Any) -> Dict[str, Any]:
    if isinstance(item, dict):
        return {
            'name': str(item.get('name', item.get('title', ""))),
            'description': str(item.get('description', "")),
        }
    return {'name': str(item), 'description': ""}


def _ensure_link(item: Any) -> Dict[str, Any]:
    if isinstance(item, dict):
        return {
            'title': str(item.get('title', "")),
            'url': str(item.get('url', "")),
            'description': str(item.get('description', "")),
        }
    return {'title': str(item), 'url': "", 'description': ""}


def _ensure_builtin(item: Any) -> Dict[str, Any]:
    if isinstance(item, dict):
        return {
            'name': str(item.get('name', "")),
            'kind': str(item.get('kind', "")),
            'signature': str(item.get('signature', "")),
            'description': str(item.get('description', "")),
        }
    return {'name': "", 'kind': "", 'signature': "", 'description': ""}


def _ensure_stdlib_entry(item: Any) -> Dict[str, Any]:
    if isinstance(item, dict):
        return {
            'name': str(item.get('name', "")),
            'description': str(item.get('description', "")),
        }
    return {'name': str(item), 'description': ""}


def normalize_language_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Return a deep-copied, normalized language document."""
    doc = deepcopy(data) if isinstance(data, dict) else {}
    doc.setdefault('name', '')
    doc.setdefault('slug', '')
    doc.setdefault('version', '')

    doc['quick_start'] = [_ensure_quick_start(item) for item in doc.get('quick_start', []) or []]
    doc['concepts'] = [_ensure_concept(item) for item in doc.get('concepts', []) or []]
    doc['common_tasks'] = [_ensure_task_group(group) for group in doc.get('common_tasks', []) or []]
    doc['projects'] = [_ensure_project(item) for item in doc.get('projects', []) or []]
    doc['glossary'] = [_ensure_glossary_entry(item) for item in doc.get('glossary', []) or []]
    doc['tips'] = [_ensure_tip(item) for item in doc.get('tips', []) or []]
    doc['tools'] = [_ensure_tool(item) for item in doc.get('tools', []) or []]
    doc['links'] = [_ensure_link(item) for item in doc.get('links', []) or []]
    doc['builtins'] = [_ensure_builtin(item) for item in doc.get('builtins', []) or []]
    doc['stdlib'] = [_ensure_stdlib_entry(item) for item in doc.get('stdlib', []) or []]

    return doc


__all__ = [
    'load_language_data',
    'save_language_data',
    'normalize_language_data',
]
