# Проверка Dependency-Track → данные для Jira

Стенд: Dependency-Track API/frontend 4.13.0, Docker Compose, локальная embedded DB в volume sbom-test_dt-data.
UI: http://localhost:19091 ; API: http://127.0.0.1:19090/api .
Логин admin; случайный пароль хранится только в .secrets.json (не публиковать).
Запуск: docker compose up -d. Остановка без удаления данных: docker compose stop.
JAVA_OPTIONS: -Xms512m -Xmx4g: 4 GB — минимальный heap, требуемый сервисом.

## Результат
- Реальный npm-проект: fixture/package.json + package-lock.json; core 7.23.0, traverse закреплён 7.23.0 через override для воспроизводимого исторического кейса.
- CycloneDX создан @cyclonedx/cyclonedx-npm@4.0.3: bom.json, 43 компонента, 44 записи dependencies.
- SBOM импортирован, API подтвердил три пути к traverse через прямую зависимость core.
- После включения OSV npm INTERNAL_ANALYZER обнаружил GHSA-67hx-6x53-jw92 с алиасом CVE-2023-45133.
- OSS Index без credentials вернул 401. Найденная уязвимость — результат реального анализа по OSV, а не вручную созданная/прикреплённая находка.
- В vulnerability.description этой находки есть текст рекомендации core >=7.23.2. Структурированного универсального parentFixVersion нет.
- API latestVersion означает последнюю доступную версию, не минимальное исправление.
- Для исправления создан fixture-fixed: override убран, core 7.23.2, npm разрешил traverse 7.29.8. bom-fixed.json загружен отдельной версией проекта. Целевая находка отсутствует, другая GHSA у core остаётся.
- Все три пути и найденная уязвимость связаны по component.uuid, а не только по имени.

## API, фактически использованные
Authorization: Bearer <локальный JWT>; токен получается POST /api/v1/user/login.
GET /api/v1/finding/project/{projectUuid}
GET /api/v1/dependencyGraph/project/{projectUuid}/directDependencies
GET /api/v1/dependencyGraph/component/{componentUuid}/directDependencies
GET /api/v1/vulnerability/source/GITHUB/vuln/GHSA-67hx-6x53-jw92
POST /api/v1/finding/project/{projectUuid}/analyze
GET /api/v1/bom/token/{token}
PUT /api/v1/bom

## Файлы и повторная проверка
experiment.py — первоначальная настройка локального admin, создание vulnerable-проекта и импорт bom.json (bootstrap, не запускать повторно для существующего проекта).
enable_osv.py — включение публичного зеркала OSV npm и алиасов; после первоначального включения перезапускали только apiserver стенда.
inspect_api.py — повторная выгрузка компонентов/корневых связей/находок и assertions основной цепочки.
collect_graph.py — обход всех узлов через API с защитой от циклов, сохранение графа и всех путей для целевого traverse.
upload_fixed.py — первоначальный импорт отдельного fixed-target-cve проекта (bootstrap).
verify_fixed.py — проверка завершения импорта, установленного исправленного traverse и отсутствия целевой находки.
generate_jira.py — генерация jira-draft.md/json из сохранённых API-данных и manifest; правило извлечения версии специфично для этого advisory и при отсутствии текста завершится ошибкой.
evidence/ — реальные ответы API, внешний advisory OSV, логи и состояния контейнеров.

Для повторного чтения текущего стенда:
python inspect_api.py
python collect_graph.py
python verify_fixed.py
python generate_jira.py

Сгенерировать SBOM повторно (из каталога fixture или fixture-fixed):
npx --yes @cyclonedx/cyclonedx-npm@4.0.3 --output-file ../bom.json
Для fixed использовать ../bom-fixed.json.

## Границы автоматизации
Граф зависит от полноты исходного SBOM. При отсутствии связей нельзя угадывать родителя.
Рекомендация родительской версии в этом примере извлечена из текста; для других CVE её может не быть. Нужен fallback на advisory/метаданные менеджера пакетов и валидацию разрешённых зависимостей.
Override обнаружен чтением package.json — из SBOM/DT он не восстанавливается надёжно.
7.23.2 — исторический минимум для одной CVE, не рекомендация безопасной версии Babel на сегодня.
Эксплуатация и совместимость реального приложения не проверялись; прикладного кода в fixture нет.
Jira не подключалась; задача не отправлялась, создан только проверяемый черновик.
