import urllib.request, urllib.parse, json, pathlib, secrets, base64
ROOT=pathlib.Path(__file__).parent
BASE='http://127.0.0.1:19090/api'
def req(path, data=None, method=None, token=None, form=False):
    headers={}
    if token: headers['Authorization']='Bearer '+token
    if data is not None:
        headers['Content-Type']='application/x-www-form-urlencoded' if form else 'application/json'
        data=(urllib.parse.urlencode(data) if form else json.dumps(data)).encode()
    r=urllib.request.urlopen(urllib.request.Request(BASE+path,data=data,headers=headers,method=method),timeout=90)
    text=r.read().decode()
    try: return json.loads(text)
    except ValueError: return text
if __name__=='__main__':
    secret_path=ROOT/'.secrets.json'
    if secret_path.exists(): password=json.loads(secret_path.read_text())['password']
    else:
        password=secrets.token_urlsafe(24)
        req('/v1/user/forceChangePassword',{'username':'admin','password':'admin','newPassword':password,'confirmPassword':password},form=True)
        secret_path.write_text(json.dumps({'username':'admin','password':password}))
    token=req('/v1/user/login',{'username':'admin','password':password},form=True)
    project=req('/v1/project',{'name':'babel-transitive-demo','version':'vulnerable'},method='PUT',token=token)
    (ROOT/'evidence/project.json').write_text(json.dumps(project,indent=2))
    result=req('/v1/bom',{'project':project['uuid'],'bom':base64.b64encode((ROOT/'bom.json').read_bytes()).decode()},method='PUT',token=token)
    (ROOT/'evidence/upload.json').write_text(json.dumps(result,indent=2))
    print('Uploaded',project['uuid'],result)
