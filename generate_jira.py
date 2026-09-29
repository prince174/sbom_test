"""Generate a Jira draft from captured DT evidence; rule is specific to this advisory."""
import json, pathlib, re
R=pathlib.Path(__file__).parent
load=lambda name:json.loads((R/'evidence'/name).read_text())
f=next(x for x in load('findings.json') if x['vulnerability']['vulnId']=='GHSA-67hx-6x53-jw92')
g=load('graph.json'); paths=load('paths.json'); c=f['component']; v=f['vulnerability']
assert all(path[-1]==c['uuid'] for path in paths)
pattern=r'`@babel/core`\s*>=\s*(\d+\.\d+\.\d+)'
m=re.search(pattern,v['description'])
assert m, 'No supported parent recommendation found; manual remediation analysis required'
version=m.group(1)
def label(uid):
    if uid==g['root']: return 'babel-transitive-demo'
    n=g['nodes'][uid]
    return (n.get('group','')+'/' if n.get('group') else '')+n['name']+'@'+n['version']
# Some graph DTOs omit group; reconstruct display names from percent-encoded npm PURL.
from urllib.parse import unquote
for n in g['nodes'].values():
    if n.get('purl','').startswith('pkg:npm/%40babel/'): n['group']='@babel'
manifest=json.loads((R/'fixture/package.json').read_text(encoding='utf-8-sig'))
assert manifest['overrides']['@babel/traverse']=='7.23.0'
text=f'''# Устранить CVE-2023-45133 в транзитивной зависимости Babel

Проект: babel-transitive-demo / vulnerable.
Компонент: @babel/traverse@{c['version']}.
Находка: {v['vulnId']}; CVE-2023-45133 (алиас из API).
Источник обнаружения: Dependency-Track 4.13.0, INTERNAL_ANALYZER, публичные данные OSV.

## Подтверждённые пути из API
'''+''.join('- '+' → '.join(map(label,p))+'\n' for p in paths)+f'''
## Действия
1. Удалить тестовое закрепление overrides["@babel/traverse"] = "7.23.0" в fixture/package.json. Этот факт получен из проекта, не из Dependency-Track.
2. Обновить прямую зависимость @babel/core до совместимой версии не ниже {version}; обновить package-lock.json.
3. Проверить все копии @babel/traverse, выполнить сборку/тесты проекта и повторно сформировать SBOM.

Основание версии: vulnerability.description из findings.json, advisory https://github.com/babel/babel/security/advisories/GHSA-67hx-6x53-jw92.
Это извлечение из текста конкретного advisory, не универсальное структурированное поле API. latestVersion не используется как fixVersion.

## Критерии приёмки
- В новом SBOM отсутствуют версии traverse, затронутые CVE-2023-45133.
- После завершения анализа отсутствует GHSA-67hx-6x53-jw92 для проекта.
- Сборка и тесты реального приложения проходят.

## Проверка на стенде
Удалён override, core обновлён с 7.23.0 до 7.23.2; npm разрешил traverse 7.29.8.
Новый SBOM загружен как fixed-target-cve. Целевая находка отсутствует.
Отдельная GHSA-4x5r-pxfx-6jf8 у core осталась: это исправление только целевой CVE, не всех уязвимостей.
Тестовый проект не содержит прикладного кода; совместимость реального приложения не проверялась.
Наличие пакета подтверждено; эксплуатация зависит от конфигурации Babel и входного кода и здесь не проверялась.
'''
(R/'jira-draft.md').write_text(text,encoding='utf-8')
(R/'jira-draft.json').write_text(json.dumps({'summary':'Устранить CVE-2023-45133 в транзитивной зависимости Babel','description':text,'evidence':{'componentUuid':c['uuid'],'vulnerabilityUuid':v['uuid'],'paths':paths,'recommendationSource':'vulnerability.description','parentMinimumVersion':version}},ensure_ascii=False,indent=2),encoding='utf-8')
print('Jira draft generated; 3 verified API paths; recommendation extracted from DT advisory text')
