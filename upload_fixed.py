from experiment import *
pw=json.loads((ROOT/'.secrets.json').read_text())['password']
token=req('/v1/user/login',{'username':'admin','password':pw},form=True)
p=req('/v1/project',{'name':'babel-transitive-demo','version':'fixed-target-cve'},method='PUT',token=token)
(ROOT/'evidence/project-fixed.json').write_text(json.dumps(p,indent=2))
u=req('/v1/bom',{'project':p['uuid'],'bom':base64.b64encode((ROOT/'bom-fixed.json').read_bytes()).decode()},method='PUT',token=token)
(ROOT/'evidence/upload-fixed.json').write_text(json.dumps(u,indent=2))
print('Fixed uploaded',p['uuid'])
