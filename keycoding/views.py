from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import Http404
from django.utils.text import slugify


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

    context = {
        'lang_slug': lang,
        'lang_name': display_name,
        'categories': in_categories,
    }
    return render(request, 'language_dashboard.html', context)
