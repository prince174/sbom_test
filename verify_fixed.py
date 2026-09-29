from experiment import *
pw=json.loads((ROOT/'.secrets.json').read_text())['password']
token=req('/v1/user/login',{'username':'admin','password':pw},form=True)
p=json.loads((ROOT/'evidence/project-fixed.json').read_text())
u=json.loads((ROOT/'evidence/upload-fixed.json').read_text())
assert req('/v1/bom/token/'+u['token'],token=token)['processing'] is False
f=req('/v1/finding/project/'+p['uuid'],token=token)
(ROOT/'evidence/findings-fixed.json').write_text(json.dumps(f,indent=2))
assert not any(x['vulnerability']['vulnId']=='GHSA-67hx-6x53-jw92' for x in f)
c=req('/v1/component/project/'+p['uuid']+'?pageSize=100',token=token)
(ROOT/'evidence/components-fixed.json').write_text(json.dumps(c,indent=2))
assert any(x['name']=='traverse' and x['version']=='7.29.8' for x in c)
print('Target finding absent; remaining findings:',[(x['component']['name'],x['vulnerability']['vulnId']) for x in f])
