#!/usr/bin/env python3
"""
Generate a knowledge-graph JSON for the Foam workspace.

Outputs: web/data/graph.json with the structure:
  { "nodes": [{"id": 1, "label": "note.md", "path": "notes/note.md"}, ...],
    "edges": [{"from": 1, "to": 2}, ...] }

This script looks for wikilinks like [[Note Title]] and markdown links to .md files.
It uses no external dependencies so it can run in GitHub Actions without extra installs.
"""
import os
import re
import json
from collections import OrderedDict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WEB_DATA_DIR = os.path.join(ROOT, "web", "data")

WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
MDLINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+\.md)\)")

def find_markdown_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        # remove hidden dirs in-place so os.walk won't traverse them
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for fn in filenames:
            if fn.lower().endswith('.md'):
                yield os.path.join(dirpath, fn)

def relpath(path):
    return os.path.relpath(path, ROOT).replace('\\', '/')

def parse_frontmatter(text):
    """Extract YAML-like frontmatter title and aliases (best-effort).

    Returns (title, [aliases]) where title may be None and aliases an empty list.
    """
    title = None
    aliases = []
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return title, aliases
    body = m.group(1)
    # title: value
    mm = re.search(r"^title:\s*(.+)$", body, re.MULTILINE)
    if mm:
        title = mm.group(1).strip().strip('"\'')
    # aliases: - a\n- b   or aliases: [a, b]
    mam = re.search(r"^aliases:\s*\[(.*?)\]", body, re.MULTILINE | re.DOTALL)
    if mam:
        inner = mam.group(1)
        aliases = [s.strip().strip('"\'') for s in inner.split(',') if s.strip()]
    else:
        # list style
        am = re.search(r"^aliases:\s*$", body, re.MULTILINE)
        if am:
            # find lines after 'aliases:' that start with -
            following = body[am.end():]
            for line in following.splitlines():
                line = line.strip()
                if not line:
                    break
                if line.startswith('-'):
                    aliases.append(line.lstrip('-').strip().strip('"\''))
                else:
                    break
    return title, aliases


def build_graph():
    files = list(find_markdown_files(ROOT))
    # map path -> node id
    nodes = OrderedDict()
    meta = {}
    for i, p in enumerate(sorted(files), start=1):
        rp = relpath(p)
        # read file to extract title/aliases
        title = None
        aliases = []
        try:
            txt = open(p, encoding='utf-8').read()
            title, aliases = parse_frontmatter(txt)
        except (IOError, OSError):
            txt = ''
        nodes[rp] = {
            'id': i,
            'label': os.path.basename(p),
            'path': rp,
            'title': title,
            'aliases': aliases
        }
        meta[rp] = {'title': title, 'aliases': aliases}

    # helper maps for resolution
    title_map = {}
    alias_map = {}
    basename_map = {}
    for path, n in nodes.items():
        if n.get('title'):
            title_map[n['title'].lower()] = path
        for a in n.get('aliases', []):
            alias_map[a.lower()] = path
        basename_map[os.path.splitext(os.path.basename(path))[0].lower()] = path

    edges = []

    for src_path in files:
        src = relpath(src_path)
        try:
            text = open(src_path, encoding='utf-8').read()
        except (IOError, OSError):
            continue

        # wikilinks [[Note]]
        for m in WIKILINK_RE.findall(text):
            target = m.strip()
            t_low = target.lower()
            resolved = None
            # direct filename
            if t_low.endswith('.md'):
                cand = t_low
                for node_path in nodes:
                    if node_path.lower().endswith(cand):
                        resolved = node_path
                        break
            # by title
            if not resolved and t_low in title_map:
                resolved = title_map[t_low]
            # by alias
            if not resolved and t_low in alias_map:
                resolved = alias_map[t_low]
            # by basename
            if not resolved and t_low in basename_map:
                resolved = basename_map[t_low]

            if resolved:
                edges.append({'from': nodes[src]['id'], 'to': nodes[resolved]['id']})

        # markdown links to .md
        for m in MDLINK_RE.findall(text):
            raw = m.strip()
            # resolve relative to the file
            target_abs = os.path.normpath(os.path.join(os.path.dirname(src_path), raw))
            target_rel = relpath(target_abs)
            if target_rel in nodes:
                edges.append({'from': nodes[src]['id'], 'to': nodes[target_rel]['id']})

    graph = {'nodes': list(nodes.values()), 'edges': edges}
    return graph

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def main():
    graph = build_graph()
    ensure_dir(WEB_DATA_DIR)
    out = os.path.join(WEB_DATA_DIR, 'graph.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)
    print('Wrote', out)

if __name__ == '__main__':
    main()
