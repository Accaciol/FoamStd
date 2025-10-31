import json
import os

candidates = [
    'graph_published.json',
    os.path.join('web','data','graph.json')
]
for p in candidates:
    if os.path.exists(p):
        path = p
        break
else:
    print('No graph JSON found in', candidates)
    raise SystemExit(1)

with open(path, 'r', encoding='utf-8') as f:
    g = json.load(f)

nodes = g.get('nodes', [])
edges = g.get('edges', [])
print('graph file:', path)
print('nodes:', len(nodes))
print('edges:', len(edges))
print('\nfirst 8 nodes:')
for n in nodes[:8]:
    print(' -', n.get('id'), n.get('path'))
print('\nfirst 8 edges:')
for e in edges[:8]:
    print(' -', e)
