#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'langdata' / 'python.json'

def main() -> int:
    data = json.loads(P.read_text(encoding='utf-8'))

    # Expand common_tasks
    groups = data.get('common_tasks', [])
    # Keep existing groups but replace "I/O" with richer "Files & Data", and extend with more
    new_groups = []
    for g in groups:
        if g.get('group') == 'I/O':
            new_groups.append({
                'group': 'Files & Data',
                'tasks': [
                    {'title':'Read a text file','description':'Open and read file contents.','code':"from pathlib import Path\ntext = Path('README.md').read_text(encoding='utf-8')\nprint(text[:200])"},
                    {'title':'Write JSON','description':'Serialize a dict to a JSON file.','code':"import json\ndata = {'ok': True, 'items': [1,2,3]}\nwith open('data.json', 'w', encoding='utf-8') as f:\n    json.dump(data, f, indent=2)"},
                    {'title':'Read CSV','description':'Load rows from a CSV file.','code':"import csv\nwith open('people.csv', newline='', encoding='utf-8') as f:\n    for row in csv.DictReader(f):\n        print(row['name'], row['age'])"},
                    {'title':'Write CSV','description':'Write rows to a CSV file.','code':"import csv\nrows = [{'name':'Ada','age':36},{'name':'Linus','age':54}]\nwith open('out.csv', 'w', newline='', encoding='utf-8') as f:\n    w = csv.DictWriter(f, fieldnames=['name','age'])\n    w.writeheader(); w.writerows(rows)"},
                    {'title':'SQLite (database)','description':'Create a table, insert, and query.','code':"import sqlite3\ncon = sqlite3.connect('app.db')\ncur = con.cursor()\ncur.execute('CREATE TABLE IF NOT EXISTS users (name TEXT, age INT)')\ncur.executemany('INSERT INTO users VALUES (?, ?)', [('Ada',36),('Guido',68)])\nfor name, age in cur.execute('SELECT name, age FROM users ORDER BY age DESC'):\n    print(name, age)\ncon.commit(); con.close()"},
                    {'title':'ZIP files','description':'Zip and unzip files/folders.','code':"import zipfile, pathlib\n# Create zip\nwith zipfile.ZipFile('site.zip', 'w', zipfile.ZIP_DEFLATED) as z:\n    z.write('index.html')\n# Extract\npathlib.Path('unzipped').mkdir(exist_ok=True)\nwith zipfile.ZipFile('site.zip') as z:\n    z.extractall('unzipped')"},
                    {'title':'List files (glob)','description':'Find files by pattern.','code':"from pathlib import Path\nfor p in Path('.').glob('**/*.py'):\n    print(p)"},
                ]
            })
        else:
            new_groups.append(g)

    # Ensure additional helpful groups exist
    def ensure_group(name: str, tasks: list[dict]):
        if not any(g.get('group') == name for g in new_groups):
            new_groups.append({'group': name, 'tasks': tasks})

    ensure_group('Text & Regex', [
        {'title':'Find emails','description':'Extract emails with a regex.','code':"import re\ntext = 'Contact us: team@example.com or help@site.org'\nprint(re.findall(r'[\\w.-]+@[\\w.-]+', text))"},
        {'title':'Replace text','description':'Substitute patterns in text.','code':"import re\ns = 'color colour'\nprint(re.sub(r'colou?r', 'shade', s))"},
        {'title':'Split / join','description':'Split into words and join back.','code':"s = 'one two  three'\nparts = s.split()\nprint(parts, ' | '.join(parts))"},
    ])

    # Extend HTTP group to include stdlib GET example and POST with requests
    for g in new_groups:
        if g.get('group') == 'HTTP + APIs':
            tasks = g.setdefault('tasks', [])
            have_get_stdlib = any('GET JSON (stdlib)' in t.get('title','') for t in tasks)
            if not have_get_stdlib:
                tasks.insert(0, {'title':'GET JSON (stdlib)','description':'Fetch JSON using urllib.','code':"import json, urllib.request\nwith urllib.request.urlopen('https://httpbin.org/json') as r:\n    data = json.load(r)\nprint(data['slideshow']['title'])"})
            have_post = any('POST JSON' in t.get('title','') for t in tasks)
            if not have_post:
                tasks.append({'title':'POST JSON (requests)','description':'Send data as JSON (pip install requests).','code':"# pip install requests\nimport requests\nr = requests.post('https://httpbin.org/post', json={'ok': True}, timeout=10)\nr.raise_for_status()\nprint(r.json()['json'])"})

    ensure_group('Env & Config', [
        {'title':'Read environment variables','description':'Use defaults when not set.','code':"import os\nport = int(os.environ.get('PORT', 8000))\nmode = os.environ.get('MODE', 'dev')\nprint(port, mode)"},
    ])

    ensure_group('Logging', [
        {'title':'Basic logging','description':'Log info, warnings, and errors.','code':"import logging\nlogging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')\nlogging.info('Starting...')\nlogging.warning('Careful!')\nlogging.error('Something went wrong')"},
    ])

    ensure_group('Concurrency', [
        {'title':'Thread pool','description':'Run tasks in parallel threads.','code':"from concurrent.futures import ThreadPoolExecutor\nimport urllib.request\nurls = ['https://example.com','https://httpbin.org/get']\nwith ThreadPoolExecutor(max_workers=4) as ex:\n    for html in ex.map(lambda u: urllib.request.urlopen(u).read(), urls):\n        print(len(html))"},
    ])

    data['common_tasks'] = new_groups

    # Projects
    data['projects'] = [
        {
            'title': 'To-Do CLI',
            'summary': 'Add/list tasks saved to a JSON file.',
            'description': 'A simple command-line app that stores tasks in todo.json.',
            'steps': [
                {'title': 'Script', 'code': "# todo.py\nimport argparse, json, pathlib\nPATH = pathlib.Path('todo.json')\n\ndef load():\n    return json.loads(PATH.read_text()) if PATH.exists() else []\n\ndef save(items):\n    PATH.write_text(json.dumps(items, indent=2))\n\nparser = argparse.ArgumentParser()\nparser.add_argument('cmd', choices=['add','list'])\nparser.add_argument('text', nargs='?')\nargs = parser.parse_args([])  # replace [] with real args when running\nitems = load()\nif args.cmd == 'add' and args.text:\n    items.append({'text': args.text, 'done': False})\n    save(items)\nif args.cmd == 'list':\n    for i, it in enumerate(items, 1):\n        print(f\"{i}. {'[x]' if it['done'] else '[ ]'} {it['text']}\")"}
            ]
        },
        {
            'title': 'CSV Summarizer',
            'summary': 'Compute quick stats from a CSV file.',
            'description': 'Reads a CSV and prints count and averages.',
            'steps': [
                {'title': 'Script', 'code': "# summarize.py\nimport csv, statistics as stats\nwith open('data.csv', newline='', encoding='utf-8') as f:\n    rows = list(csv.DictReader(f))\n    ages = [int(r['age']) for r in rows if r.get('age')]\nprint('rows:', len(rows))\nprint('avg age:', round(stats.mean(ages), 1))"}
            ]
        },
        {
            'title': 'Web Fetcher',
            'summary': 'Download JSON and save to disk.',
            'description': 'Fetch an API and store the response.',
            'steps': [
                {'title': 'Script', 'code': "# fetch.py\nimport json, urllib.request, pathlib\nurl = 'https://httpbin.org/json'\nwith urllib.request.urlopen(url) as r:\n    data = json.load(r)\npathlib.Path('out').mkdir(exist_ok=True)\nopen('out/data.json','w',encoding='utf-8').write(json.dumps(data, indent=2))\nprint('saved to out/data.json')"}
            ]
        },
    ]

    # Glossary
    data['glossary'] = [
        {'term':'Variable','definition':'A named reference to a value (e.g., x = 3).'},
        {'term':'Function','definition':'Reusable block of code that can take inputs and return a value.'},
        {'term':'Module','definition':'A .py file with code you can import.'},
        {'term':'Package','definition':'A folder of modules (often with __init__.py).'},
        {'term':'Virtual environment','definition':'Self-contained folder for project-specific Python and packages.'},
        {'term':'pip','definition':'Python’s package installer (downloads from PyPI).'},
        {'term':'Standard library','definition':'Batteries-included modules that ship with Python.'},
        {'term':'REPL','definition':'Interactive prompt where you can type and run Python line by line.'},
        {'term':'Exception','definition':'An error you can handle with try/except.'},
        {'term':'Iterable','definition':'Something you can loop over (like list, str, file).'},
        {'term':'Dict','definition':'Key–value mapping, e.g., {\'name\':\'Ada\'}.'},
        {'term':'List','definition':'Ordered, changeable collection: [1, 2, 3].'},
        {'term':'Tuple','definition':'Ordered, unchangeable collection: (1, 2).'},
        {'term':'Set','definition':'Unordered collection of unique items: {\'a\',\'b\'}.'},
        {'term':'Comprehension','definition':'Compact way to build a list/dict/set from a loop.'},
        {'term':'Decorator','definition':'Function that modifies another function or method.'},
        {'term':'Dataclass','definition':'Class helper that auto-generates __init__ and more for data fields.'},
    ]

    # Tips
    data['tips'] = [
        {'title':'Indentation','note':'Use 4 spaces (not tabs) and keep it consistent.'},
        {'title':'Virtualenv','note':'Create a venv per project; install packages inside it.'},
        {'title':'Formatting','note':'Use f-strings for readable messages: f\'User {name}\'.'},
        {'title':'Paths','note':'Prefer pathlib.Path over os.path for file work.'},
        {'title':'Files','note':'Use with open(...) so files always close.'},
        {'title':'Errors','note':'Catch specific exceptions (ValueError, FileNotFoundError), not bare except.'},
        {'title':'Loops','note':'Use enumerate(list) instead of manual indexes.'},
        {'title':'Help','note':'Use help(name) in the REPL to read docs quickly.'},
    ]

    P.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    print('Updated sections: common_tasks, projects, glossary, tips')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

