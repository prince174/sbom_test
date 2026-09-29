# Устранить CVE-2023-45133 в транзитивной зависимости Babel

Проект: babel-transitive-demo / vulnerable.
Компонент: @babel/traverse@7.23.0.
Находка: GHSA-67hx-6x53-jw92; CVE-2023-45133 (алиас из API).
Источник обнаружения: Dependency-Track 4.13.0, INTERNAL_ANALYZER, публичные данные OSV.

## Подтверждённые пути из API
- babel-transitive-demo → @babel/core@7.23.0 → @babel/traverse@7.23.0
- babel-transitive-demo → @babel/core@7.23.0 → @babel/helper-module-transforms@7.29.7 → @babel/helper-module-imports@7.29.7 → @babel/traverse@7.23.0
- babel-transitive-demo → @babel/core@7.23.0 → @babel/helper-module-transforms@7.29.7 → @babel/traverse@7.23.0

## Действия
1. Удалить тестовое закрепление overrides["@babel/traverse"] = "7.23.0" в fixture/package.json. Этот факт получен из проекта, не из Dependency-Track.
2. Обновить прямую зависимость @babel/core до совместимой версии не ниже 7.23.2; обновить package-lock.json.
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
