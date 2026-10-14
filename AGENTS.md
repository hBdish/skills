# AGENTS.md

Репозиторий agent skills. Инструкции для агента, работающего **над этим репозиторием**. Как писать сами скиллы — `skills/meta/skill-authoring/SKILL.md` и его `references/`; прочитай его перед созданием или правкой скилла.

```
skills/<group>/<name>/SKILL.md   единственный источник правды
profiles.json                    наборы для установки
scripts/install.py               установка в проекты, любые агенты и ОС
scripts/validate.py              валидатор = определение корректности
scripts/new_skill.py             скилл из templates/skill
```

## Инварианты

1. Правь только `skills/`, `templates/`, `scripts/`, `profiles.json` и документацию. Каталоги `.claude/skills`, `.agents/skills` и т.п. в корне — артефакты установки, они в `.gitignore`.
2. `name` во frontmatter == имя каталога и уникально по всему репозиторию: агенты видят плоское пространство имён и молча отбрасывают скилл с несовпадающим именем.
3. Frontmatter — только поля спецификации Agent Skills (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`); своё — в `metadata` строками.
4. Правило живёт ровно в одном скилле. `lang` не описывает процесс, `practice` не содержит языковых правил.
5. Скрипты — Python 3.8+, только stdlib, `pathlib`, `encoding="utf-8"`. Никаких bash/PowerShell: скиллы должны работать на macOS, Linux и Windows. Внешние инструменты вызываются через `shutil.which`, отсутствие инструмента — `SKIP`, а не тихий успех.
6. Ссылки из `SKILL.md` — относительные и только внутри каталога скилла: при установке копируется только он.
7. Изменение `description` — breaking change: перепрогони `trigger-evals.json` этого скилла и соседей, которых он называет в границах.
8. Удаление скилла = удаление каталога и записи в `profiles.json`. Заглушки «deprecated» не оставлять.

## Команды

```bash
python3 scripts/validate.py --strict                       # обязательно перед коммитом
python3 scripts/new_skill.py <group> <name>                # новый скилл
python3 scripts/install.py --list                          # скиллы, профили, агенты
python3 scripts/install.py -p <profile> --project <dir> --dry-run
```

Не хватает проверки — добавь её в `validate.py`, а не в текст этого файла.

## Definition of Done

- [ ] `validate.py --strict` чист
- [ ] Скилл добавлен в профиль в `profiles.json`
- [ ] Есть `evals/trigger-evals.json` (~20 запросов, половина — near-miss негативы) и `evals/evals.json` с кейсом на чистый вход
- [ ] Границы с соседями названы в `description` с обеих сторон
- [ ] Для производного контента указаны источник и дата синка

## Не размещать здесь

Секреты, внутренние URL и данные: скиллы копируются в чужие проекты и попадают в контекст модели.
