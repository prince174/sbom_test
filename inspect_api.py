from experiment import *
pw=json.loads((ROOT/'.secrets.json').read_text())['password']
token=req('/v1/user/login',{'username':'admin','password':pw},form=True)
p=json.loads((ROOT/'evidence/project.json').read_text()); pid=p['uuid']
def get(path,name):
    data=req(path,token=token)
    (ROOT/'evidence'/name).write_text(json.dumps(data,indent=2))
    return data
upload=json.loads((ROOT/'evidence/upload.json').read_text())
print('processing',get('/v1/bom/token/'+upload['token'],'processing.json'))
roots=get('/v1/dependencyGraph/project/'+pid+'/directDependencies','roots.json')
print('roots',json.dumps(roots)[:2200])
components=get('/v1/component/project/'+pid+'?pageSize=100','components.json')
core=next(c for c in components if c['name']=='core' and c.get('group')=='@babel')
traverse=next(c for c in components if c['name']=='traverse' and c.get('group')=='@babel')
children=get('/v1/dependencyGraph/component/'+core['uuid']+'/directDependencies','core-dependencies.json')
print('core children',[(c.get('name'),c.get('version'),c.get('uuid')) for c in children])
findings=get('/v1/finding/project/'+pid,'findings.json')
print('findings',json.dumps(findings)[:3500])
assert any(c['uuid']==core['uuid'] for c in roots)
assert any(c['uuid']==traverse['uuid'] for c in children)
print('VERIFIED project -> core -> traverse',traverse['uuid'])
