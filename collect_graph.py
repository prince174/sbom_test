from experiment import *
from collections import deque
pw=json.loads((ROOT/'.secrets.json').read_text())['password']
token=req('/v1/user/login',{'username':'admin','password':pw},form=True)
p=json.loads((ROOT/'evidence/project.json').read_text()); pid=p['uuid']
nodes={}; edges={}; queue=deque([('project',pid)]); seen=set()
while queue:
    kind,uid=queue.popleft()
    if uid in seen: continue
    seen.add(uid)
    children=req(f'/v1/dependencyGraph/{kind}/{uid}/directDependencies',token=token)
    edges[uid]=[c['uuid'] for c in children]
    for c in children:
        nodes[c['uuid']]=c
        queue.append(('component',c['uuid']))
(ROOT/'evidence/graph.json').write_text(json.dumps({'root':pid,'nodes':nodes,'edges':edges},indent=2))
target=next(k for k,c in nodes.items() if c.get('purl','').startswith('pkg:npm/%40babel/traverse@7.23.0'))
paths=[]
def walk(uid,path):
    if uid==target: paths.append(path); return
    for child in edges.get(uid,[]):
        if child not in path: walk(child,path+[child])
walk(pid,[pid])
(ROOT/'evidence/paths.json').write_text(json.dumps(paths,indent=2))
print('Graph verified:',len(nodes),'nodes;',len(paths),'paths to traverse')
for path in paths:
    print(' -> '.join(p['name'] if x==pid else nodes[x].get('purl',nodes[x]['name']) for x in path))
