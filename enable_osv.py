from experiment import *
pw=json.loads((ROOT/'.secrets.json').read_text())['password']
token=req('/v1/user/login',{'username':'admin','password':pw},form=True)
for name,value,kind in [('google.osv.enabled','npm','STRING'),('google.osv.alias.sync.enabled','true','BOOLEAN')]:
    print(req('/v1/configProperty',{'groupName':'vuln-source','propertyName':name,'propertyValue':value,'propertyType':kind},method='POST',token=token))
