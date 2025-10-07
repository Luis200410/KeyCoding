from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.utils.text import slugify

from .langdata import (
    load_language_data,
    normalize_language_data,
    save_language_data,
)


def _clean_text(value):
    return str(value or "").strip()


def _clean_multiline(value):
    return str(value or "").replace("\r\n", "\n").strip()


def _parse_index(raw, *, label: str) -> int:
    try:
        idx = int(raw)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid {label} index")
    if idx < 0:
        raise ValueError(f"Invalid {label} index")
    return idx


def _apply_language_action(data, action, payload):
    if not action:
        raise ValueError("Unrecognised action")

    if action == 'update_language_meta':
        data['name'] = _clean_text(payload.get('name')) or data.get('name', '')
        data['version'] = _clean_text(payload.get('version'))
        return 'Language details updated'

    if action == 'add_quick_start':
        title = _clean_text(payload.get('title'))
        description = _clean_multiline(payload.get('description'))
        code = _clean_multiline(payload.get('code'))
        if not title:
            raise ValueError('Title is required for Quick Start entries')
        data.setdefault('quick_start', []).append({
            'title': title,
            'description': description,
            'code': code,
        })
        return 'Quick Start entry added'

    if action == 'update_quick_start':
        index = _parse_index(payload.get('index'), label='Quick Start')
        entries = data.setdefault('quick_start', [])
        if index >= len(entries):
            raise ValueError('Quick Start entry not found')
        title = _clean_text(payload.get('title'))
        if not title:
            raise ValueError('Title is required for Quick Start entries')
        entries[index] = {
            'title': title,
            'description': _clean_multiline(payload.get('description')),
            'code': _clean_multiline(payload.get('code')),
        }
        return 'Quick Start entry updated'

    if action == 'delete_quick_start':
        index = _parse_index(payload.get('index'), label='Quick Start')
        entries = data.setdefault('quick_start', [])
        if index >= len(entries):
            raise ValueError('Quick Start entry not found')
        entries.pop(index)
        return 'Quick Start entry removed'

    if action == 'add_concept':
        concept_id = _clean_text(payload.get('concept_id'))
        title = _clean_text(payload.get('title'))
        if not concept_id:
            raise ValueError('Concept ID is required')
        if not title:
            raise ValueError('Concept title is required')
        data.setdefault('concepts', []).append({
            'id': concept_id,
            'title': title,
            'tag': _clean_text(payload.get('tag')),
            'description': _clean_multiline(payload.get('description')),
            'code': _clean_multiline(payload.get('code')),
        })
        return 'Concept added'

    if action == 'update_concept':
        index = _parse_index(payload.get('index'), label='concept')
        concepts = data.setdefault('concepts', [])
        if index >= len(concepts):
            raise ValueError('Concept not found')
        concept_id = _clean_text(payload.get('concept_id'))
        title = _clean_text(payload.get('title'))
        if not concept_id:
            raise ValueError('Concept ID is required')
        if not title:
            raise ValueError('Concept title is required')
        concepts[index] = {
            'id': concept_id,
            'title': title,
            'tag': _clean_text(payload.get('tag')),
            'description': _clean_multiline(payload.get('description')),
            'code': _clean_multiline(payload.get('code')),
        }
        return 'Concept updated'

    if action == 'delete_concept':
        index = _parse_index(payload.get('index'), label='concept')
        concepts = data.setdefault('concepts', [])
        if index >= len(concepts):
            raise ValueError('Concept not found')
        concepts.pop(index)
        return 'Concept removed'

    if action == 'add_common_task':
        group_name = _clean_text(payload.get('group'))
        title = _clean_text(payload.get('title'))
        if not group_name:
            raise ValueError('Task group is required')
        if not title:
            raise ValueError('Task title is required')
        task = {
            'title': title,
            'description': _clean_multiline(payload.get('description')),
            'code': _clean_multiline(payload.get('code')),
        }
        groups = data.setdefault('common_tasks', [])
        for group in groups:
            if group.get('group') == group_name:
                group.setdefault('tasks', []).append(task)
                break
        else:
            groups.append({'group': group_name, 'tasks': [task]})
        return 'Task added'

    if action == 'update_common_task':
        group_index = _parse_index(payload.get('group_index'), label='task group')
        task_index = _parse_index(payload.get('task_index'), label='task')
        groups = data.setdefault('common_tasks', [])
        if group_index >= len(groups):
            raise ValueError('Task group not found')
        group = groups[group_index]
        tasks = group.setdefault('tasks', [])
        if task_index >= len(tasks):
            raise ValueError('Task not found')
        title = _clean_text(payload.get('title'))
        if not title:
            raise ValueError('Task title is required')
        original_group_name = group.get('group', '')
        updated_group_name = _clean_text(payload.get('group')) or original_group_name
        task = {
            'title': title,
            'description': _clean_multiline(payload.get('description')),
            'code': _clean_multiline(payload.get('code')),
        }
        tasks.pop(task_index)
        removed_group = False
        if not tasks:
            groups.pop(group_index)
            removed_group = True
        if updated_group_name:
            if not removed_group and updated_group_name == original_group_name:
                # Reinsert into same group at the original position to keep ordering stable.
                group.setdefault('tasks', []).insert(min(task_index, len(group['tasks'])), task)
            else:
                for candidate in groups:
                    if candidate.get('group') == updated_group_name:
                        candidate.setdefault('tasks', []).append(task)
                        break
                else:
                    groups.append({
                        'group': updated_group_name,
                        'tasks': [task],
                    })
        return 'Task updated'

    if action == 'delete_common_task':
        group_index = _parse_index(payload.get('group_index'), label='task group')
        task_index = _parse_index(payload.get('task_index'), label='task')
        groups = data.setdefault('common_tasks', [])
        if group_index >= len(groups):
            raise ValueError('Task group not found')
        group = groups[group_index]
        tasks = group.setdefault('tasks', [])
        if task_index >= len(tasks):
            raise ValueError('Task not found')
        tasks.pop(task_index)
        if not tasks:
            groups.pop(group_index)
        return 'Task removed'

    if action == 'rename_common_task_group':
        group_index = _parse_index(payload.get('group_index'), label='task group')
        new_name = _clean_text(payload.get('group'))
        if not new_name:
            raise ValueError('Group name is required')
        groups = data.setdefault('common_tasks', [])
        if group_index >= len(groups):
            raise ValueError('Task group not found')
        groups[group_index]['group'] = new_name
        return 'Task group renamed'

    if action == 'delete_common_task_group':
        group_index = _parse_index(payload.get('group_index'), label='task group')
        groups = data.setdefault('common_tasks', [])
        if group_index >= len(groups):
            raise ValueError('Task group not found')
        groups.pop(group_index)
        return 'Task group removed'

    if action == 'add_project':
        title = _clean_text(payload.get('title'))
        if not title:
            raise ValueError('Project title is required')
        data.setdefault('projects', []).append({
            'title': title,
            'summary': _clean_text(payload.get('summary')),
            'description': _clean_multiline(payload.get('description')),
            'steps': [],
        })
        return 'Project added'

    if action == 'update_project':
        project_index = _parse_index(payload.get('project_index'), label='project')
        projects = data.setdefault('projects', [])
        if project_index >= len(projects):
            raise ValueError('Project not found')
        title = _clean_text(payload.get('title'))
        if not title:
            raise ValueError('Project title is required')
        project = projects[project_index]
        project.update({
            'title': title,
            'summary': _clean_text(payload.get('summary')),
            'description': _clean_multiline(payload.get('description')),
        })
        return 'Project updated'

    if action == 'delete_project':
        project_index = _parse_index(payload.get('project_index'), label='project')
        projects = data.setdefault('projects', [])
        if project_index >= len(projects):
            raise ValueError('Project not found')
        projects.pop(project_index)
        return 'Project removed'

    if action == 'add_project_step':
        project_index = _parse_index(payload.get('project_index'), label='project')
        projects = data.setdefault('projects', [])
        if project_index >= len(projects):
            raise ValueError('Project not found')
        title = _clean_text(payload.get('title'))
        text = _clean_multiline(payload.get('text'))
        code = _clean_multiline(payload.get('code'))
        if not any([title, text, code]):
            raise ValueError('Provide at least one field for the step')
        projects[project_index].setdefault('steps', []).append({
            'title': title,
            'text': text,
            'code': code,
        })
        return 'Project step added'

    if action == 'update_project_step':
        project_index = _parse_index(payload.get('project_index'), label='project')
        step_index = _parse_index(payload.get('step_index'), label='project step')
        projects = data.setdefault('projects', [])
        if project_index >= len(projects):
            raise ValueError('Project not found')
        steps = projects[project_index].setdefault('steps', [])
        if step_index >= len(steps):
            raise ValueError('Project step not found')
        title = _clean_text(payload.get('title'))
        text = _clean_multiline(payload.get('text'))
        code = _clean_multiline(payload.get('code'))
        if not any([title, text, code]):
            raise ValueError('Provide at least one field for the step')
        steps[step_index] = {
            'title': title,
            'text': text,
            'code': code,
        }
        return 'Project step updated'

    if action == 'delete_project_step':
        project_index = _parse_index(payload.get('project_index'), label='project')
        step_index = _parse_index(payload.get('step_index'), label='project step')
        projects = data.setdefault('projects', [])
        if project_index >= len(projects):
            raise ValueError('Project not found')
        steps = projects[project_index].setdefault('steps', [])
        if step_index >= len(steps):
            raise ValueError('Project step not found')
        steps.pop(step_index)
        return 'Project step removed'

    if action == 'add_glossary':
        term = _clean_text(payload.get('term'))
        definition = _clean_multiline(payload.get('definition'))
        if not term:
            raise ValueError('Glossary term is required')
        if not definition:
            raise ValueError('Glossary definition is required')
        data.setdefault('glossary', []).append({'term': term, 'definition': definition})
        return 'Glossary entry added'

    if action == 'update_glossary':
        index = _parse_index(payload.get('index'), label='glossary entry')
        glossary = data.setdefault('glossary', [])
        if index >= len(glossary):
            raise ValueError('Glossary entry not found')
        term = _clean_text(payload.get('term'))
        definition = _clean_multiline(payload.get('definition'))
        if not term:
            raise ValueError('Glossary term is required')
        if not definition:
            raise ValueError('Glossary definition is required')
        glossary[index] = {'term': term, 'definition': definition}
        return 'Glossary entry updated'

    if action == 'delete_glossary':
        index = _parse_index(payload.get('index'), label='glossary entry')
        glossary = data.setdefault('glossary', [])
        if index >= len(glossary):
            raise ValueError('Glossary entry not found')
        glossary.pop(index)
        return 'Glossary entry removed'

    if action == 'add_tip':
        note = _clean_multiline(payload.get('note'))
        if not note:
            raise ValueError('Tip note is required')
        data.setdefault('tips', []).append({
            'title': _clean_text(payload.get('title')),
            'note': note,
        })
        return 'Tip added'

    if action == 'update_tip':
        index = _parse_index(payload.get('index'), label='tip')
        tips = data.setdefault('tips', [])
        if index >= len(tips):
            raise ValueError('Tip not found')
        note = _clean_multiline(payload.get('note'))
        if not note:
            raise ValueError('Tip note is required')
        tips[index] = {
            'title': _clean_text(payload.get('title')),
            'note': note,
        }
        return 'Tip updated'

    if action == 'delete_tip':
        index = _parse_index(payload.get('index'), label='tip')
        tips = data.setdefault('tips', [])
        if index >= len(tips):
            raise ValueError('Tip not found')
        tips.pop(index)
        return 'Tip removed'

    if action == 'add_builtin':
        name = _clean_text(payload.get('name'))
        if not name:
            raise ValueError('Built-in name is required')
        data.setdefault('builtins', []).append({
            'name': name,
            'kind': _clean_text(payload.get('kind')),
            'signature': _clean_text(payload.get('signature')),
            'description': _clean_multiline(payload.get('description')),
        })
        return 'Built-in entry added'

    if action == 'update_builtin':
        index = _parse_index(payload.get('index'), label='built-in')
        builtins = data.setdefault('builtins', [])
        if index >= len(builtins):
            raise ValueError('Built-in not found')
        name = _clean_text(payload.get('name'))
        if not name:
            raise ValueError('Built-in name is required')
        builtins[index] = {
            'name': name,
            'kind': _clean_text(payload.get('kind')),
            'signature': _clean_text(payload.get('signature')),
            'description': _clean_multiline(payload.get('description')),
        }
        return 'Built-in entry updated'

    if action == 'delete_builtin':
        index = _parse_index(payload.get('index'), label='built-in')
        builtins = data.setdefault('builtins', [])
        if index >= len(builtins):
            raise ValueError('Built-in not found')
        builtins.pop(index)
        return 'Built-in entry removed'

    if action == 'add_stdlib':
        name = _clean_text(payload.get('name'))
        if not name:
            raise ValueError('Standard library name is required')
        data.setdefault('stdlib', []).append({
            'name': name,
            'description': _clean_multiline(payload.get('description')),
        })
        return 'Standard library entry added'

    if action == 'update_stdlib':
        index = _parse_index(payload.get('index'), label='standard library entry')
        stdlib = data.setdefault('stdlib', [])
        if index >= len(stdlib):
            raise ValueError('Standard library entry not found')
        name = _clean_text(payload.get('name'))
        if not name:
            raise ValueError('Standard library name is required')
        stdlib[index] = {
            'name': name,
            'description': _clean_multiline(payload.get('description')),
        }
        return 'Standard library entry updated'

    if action == 'delete_stdlib':
        index = _parse_index(payload.get('index'), label='standard library entry')
        stdlib = data.setdefault('stdlib', [])
        if index >= len(stdlib):
            raise ValueError('Standard library entry not found')
        stdlib.pop(index)
        return 'Standard library entry removed'

    if action == 'add_tool':
        name = _clean_text(payload.get('name'))
        if not name:
            raise ValueError('Tool name is required')
        data.setdefault('tools', []).append({
            'name': name,
            'description': _clean_multiline(payload.get('description')),
        })
        return 'Tool added'

    if action == 'update_tool':
        index = _parse_index(payload.get('index'), label='tool')
        tools = data.setdefault('tools', [])
        if index >= len(tools):
            raise ValueError('Tool not found')
        name = _clean_text(payload.get('name'))
        if not name:
            raise ValueError('Tool name is required')
        tools[index] = {
            'name': name,
            'description': _clean_multiline(payload.get('description')),
        }
        return 'Tool updated'

    if action == 'delete_tool':
        index = _parse_index(payload.get('index'), label='tool')
        tools = data.setdefault('tools', [])
        if index >= len(tools):
            raise ValueError('Tool not found')
        tools.pop(index)
        return 'Tool removed'

    if action == 'add_link':
        title = _clean_text(payload.get('title'))
        url = _clean_text(payload.get('url'))
        if not title:
            raise ValueError('Link title is required')
        if not url:
            raise ValueError('Link URL is required')
        data.setdefault('links', []).append({
            'title': title,
            'url': url,
            'description': _clean_multiline(payload.get('description')),
        })
        return 'Link added'

    if action == 'update_link':
        index = _parse_index(payload.get('index'), label='link')
        links = data.setdefault('links', [])
        if index >= len(links):
            raise ValueError('Link not found')
        title = _clean_text(payload.get('title'))
        url = _clean_text(payload.get('url'))
        if not title:
            raise ValueError('Link title is required')
        if not url:
            raise ValueError('Link URL is required')
        links[index] = {
            'title': title,
            'url': url,
            'description': _clean_multiline(payload.get('description')),
        }
        return 'Link updated'

    if action == 'delete_link':
        index = _parse_index(payload.get('index'), label='link')
        links = data.setdefault('links', [])
        if index >= len(links):
            raise ValueError('Link not found')
        links.pop(index)
        return 'Link removed'

    raise ValueError('Unrecognised action')


def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')


@login_required
def dashboard_view(request):
    categories = {
        'Frontend': [
            'JavaScript','TypeScript','HTML','CSS'
        ],
        'Backend Web': [
            'Python','JavaScript','TypeScript','Java','C#','Go','PHP','Ruby','Rust','Kotlin','Scala','Elixir','Clojure','Crystal','Nim'
        ],
        'Mobile': [
            'Swift','Kotlin','Dart','Objective-C'
        ],
        'Data / ML / Science': [
            'Python','R','Julia','MATLAB','SQL'
        ],
        'Systems / Low-Level': [
            'C','C++','Rust','Zig','Assembly','Ada'
        ],
        'Scripting / Automation': [
            'Bash','Shell','PowerShell','Perl','Python','Lua'
        ],
        'Functional & Logic': [
            'Haskell','Elixir','Erlang','F#','OCaml','Scheme','Clojure','Prolog'
        ],
        'Blockchain / Smart Contracts': [
            'Solidity'
        ],
        'Legacy / Enterprise': [
            'COBOL','Fortran','ABAP','Visual Basic .NET','Delphi','Groovy','Apex','Objective-C','Smalltalk'
        ],
        'Hardware / HDL': [
            'VHDL','Verilog'
        ],
        'Game / Engines': [
            'GDScript','Lua'
        ],
    }

    slug_map = {
        'C++': 'cpp',
        'C#': 'csharp',
        'F#': 'fsharp',
        'Visual Basic .NET': 'vbnet',
        'Objective-C': 'objective-c',
        'Shell': 'shell',
        'Bash': 'bash',
        'PowerShell': 'powershell',
        'C': 'c',
        'R': 'r',
        'Go': 'go',
        'Rust': 'rust',
        'JavaScript': 'javascript',
        'TypeScript': 'typescript',
        'HTML': 'html',
        'CSS': 'css',
    }

    def make_slug(name: str) -> str:
        return slug_map.get(name, slugify(name))

    prepared = {
        cat: [
            {'name': name, 'slug': make_slug(name)}
            for name in names
        ]
        for cat, names in categories.items()
    }
    return render(request, 'dashboard.html', {'categories': prepared})


@login_required
def language_dashboard_view(request, lang: str):
    # Build reverse mapping
    categories = {
        'Frontend': ['JavaScript','TypeScript','HTML','CSS'],
        'Backend Web': ['Python','JavaScript','TypeScript','Java','C#','Go','PHP','Ruby','Rust','Kotlin','Scala','Elixir','Clojure','Crystal','Nim'],
        'Mobile': ['Swift','Kotlin','Dart','Objective-C'],
        'Data / ML / Science': ['Python','R','Julia','MATLAB','SQL'],
        'Systems / Low-Level': ['C','C++','Rust','Zig','Assembly','Ada'],
        'Scripting / Automation': ['Bash','Shell','PowerShell','Perl','Python','Lua'],
        'Functional & Logic': ['Haskell','Elixir','Erlang','F#','OCaml','Scheme','Clojure','Prolog'],
        'Blockchain / Smart Contracts': ['Solidity'],
        'Legacy / Enterprise': ['COBOL','Fortran','ABAP','Visual Basic .NET','Delphi','Groovy','Apex','Objective-C','Smalltalk'],
        'Hardware / HDL': ['VHDL','Verilog'],
        'Game / Engines': ['GDScript','Lua'],
    }
    slug_map = {
        'C++': 'cpp', 'C#': 'csharp', 'F#': 'fsharp', 'Visual Basic .NET': 'vbnet',
        'Objective-C': 'objective-c', 'Shell': 'shell', 'Bash': 'bash', 'PowerShell': 'powershell',
    }
    def make_slug(name: str) -> str:
        return slug_map.get(name, slugify(name))

    all_names = {name for names in categories.values() for name in names}
    by_slug = {make_slug(name): name for name in all_names}
    if lang not in by_slug:
        raise Http404("Language not found")
    display_name = by_slug[lang]
    in_categories = [cat for cat, names in categories.items() if display_name in names]

    data = normalize_language_data(load_language_data(lang))
    if not data.get('name'):
        data['name'] = display_name
    if not data.get('slug'):
        data['slug'] = lang

    manage_mode = request.user.is_superuser and request.GET.get('manage') == '1'

    if request.method == 'POST':
        if not request.user.is_superuser:
            return HttpResponseForbidden('Only superusers can edit language data')
        action = request.POST.get('action')
        try:
            message = _apply_language_action(data, action, request.POST)
            save_language_data(lang, data)
            if message:
                messages.success(request, message)
        except ValueError as exc:
            messages.error(request, str(exc))
        redirect_url = request.path
        if manage_mode:
            redirect_url = f"{redirect_url}?manage=1"
        return redirect(redirect_url)

    context = {
        'lang_slug': lang,
        'lang_name': display_name,
        'categories': in_categories,
        'lang': data,
        'manage_mode': manage_mode,
    }
    template = 'language_dashboard_manage.html' if manage_mode else 'language_dashboard.html'
    return render(request, template, context)
