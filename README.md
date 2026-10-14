# Skills

Личный репозиторий agent skills: один источник — любые проекты, любые агенты, любая ОС.

Скилл — каталог с `SKILL.md` по открытому стандарту [Agent Skills](https://agentskills.io/specification). Его понимают Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot, OpenCode, Amp, Cline, Goose, Junie, Kiro, Roo, Windsurf и др. Для агентов без поддержки скиллов есть индекс в `AGENTS.md`.

## Структура

```
skills/<группа>/<имя>/        единственный источник правды
  SKILL.md                    frontmatter (name, description) + процедура
  references/                 детали, читаются по требованию
  scripts/                    детерминированные проверки (Python, stdlib)
  evals/                      trigger-evals.json + evals.json
profiles.json                 наборы скиллов для установки
templates/skill/              шаблон нового скилла
scripts/
  install.py                  установка в проект / глобально, для любых агентов
  validate.py                 проверка по спецификации и конвенциям репо
  new_skill.py                создать скилл из шаблона
```

Группы — для людей: `lang` (правила конкретного языка), `framework` (фреймворки поверх языка), `practice` (процесс вне языка: ревью, коммиты, тесты), `tooling` (инфраструктура), `meta` (работа со скиллами). Агент видит плоское пространство имён, поэтому имя скилла уникально по всему репозиторию.

## Скиллы

| Скилл | Что делает | Откуда правила |
|---|---|---|
| [go-style](skills/lang/go-style/SKILL.md) | Google Go Style Guide: принципы, decisions, best practices; проверки gofmt, go vet, staticcheck, golangci-lint | [google.github.io/styleguide/go](https://google.github.io/styleguide/go/), синк 2026-09-07 |
| [react-style](skills/framework/react-style/SKILL.md) | React на TS/JS: сначала собирает правила проекта (`scripts/conventions.py`), умолчания — только где проект молчит | правила проекта → конфиги → паттерны в коде → умолчания |
| [typescript-style](skills/lang/typescript-style/SKILL.md) | Типизация и идиомы TS вне компонентов | конфиги проекта → умолчания |
| [python-style](skills/lang/python-style/SKILL.md) | Типизация, ошибки, логирование, нейминг | конфиги проекта → умолчания |
| [skill-authoring](skills/meta/skill-authoring/SKILL.md) | Как писать скиллы для этого репозитория | — |

Правила форматирования и написания кода в скиллах делятся на два типа. Механические вещи (отступы, кавычки, порядок импортов) скилл не диктует: он запускает форматтер и линтер проекта и подчиняется их конфигу. Остальное (нейминг, обработка ошибок, структура, идиомы) описано текстом в `SKILL.md` и `references/`. Скилл срабатывает по решению модели, поэтому то, что должно соблюдаться всегда, дублируйте в линтере и CI проекта.

## Установка

Нужен только Python 3.8+ (подходит системный `python3` на macOS; на Windows — `py -3` или `python`).

```bash
git clone <url> ~/skills
```

```bash
python3 ~/skills/scripts/install.py --list
```

В проект (запускать из корня проекта или указать `--project`):

```bash
python3 ~/skills/scripts/install.py --profile python
```

```bash
python3 ~/skills/scripts/install.py --profile fullstack --project ~/work/api --agents-md
```

Глобально, для всех проектов:

```bash
python3 ~/skills/scripts/install.py --profile everyone --global
```

По умолчанию ставится в `.agents/skills/` (общий каталог Codex, Cursor, Gemini CLI, Copilot, OpenCode, Amp и др.) и `.claude/skills/`. Другие агенты — через `--agent` (`--list` покажет все). `--agents-md` дописывает в `AGENTS.md` проекта индекс установленных скиллов для агентов, которые читают только `AGENTS.md`.

Как это работает на разных ОС:

| ОС | Как ставится | Обновление |
|---|---|---|
| macOS / Linux | symlink на каталог в репозитории | `git pull` в репозитории — и всё |
| Windows | symlink (если включён Developer Mode), иначе junction (админ не нужен), иначе копия | `git pull`; для копий — повторить `install.py` |
| CI, контейнеры, песочницы | `--copy` | повторить `install.py` |

Установщик не трогает каталоги, которые создал не он (`--force` чтобы заменить), и отказывается ставить в сам репозиторий скиллов. `--uninstall` удаляет только своё; `--dry-run` показывает план.

Альтернативы:

- `npx skills add <owner>/<repo> --skill python-style` — тот же формат, без клонирования.
- Чтобы скиллы получили коллеги по проекту, ставьте с `--copy` и коммитьте копии в репозиторий проекта: симлинки указывают на путь на вашей машине.

## Почему профили, а не «всё сразу»

`name` + `description` каждого установленного скилла лежат в контексте агента на каждом запросе. Python-скиллы в TypeScript-проекте — это токены впустую и ложные срабатывания. Глобально — только то, что нужно везде (`everyone`); языки и стек — в проект.

## Новый скилл

```bash
python3 scripts/new_skill.py lang go-style
```

Дальше: написать `description`, тело, евалы, добавить в `profiles.json`, прогнать валидатор:

```bash
python3 scripts/validate.py --strict
```

Как писать — в [skills/meta/skill-authoring/SKILL.md](skills/meta/skill-authoring/SKILL.md) (этот же скилл агент использует, когда вы просите его сделать скилл). Коротко:

1. **Один скилл — одна задача.** Если `description` описывает две — это два скилла.
2. **`description` отвечает за срабатывание**: что делает → «Use when …» с реальными формулировками и типами файлов → «Do NOT use for …» с соседями по имени. 300–700 символов, главное — в первых 150.
3. **Progressive disclosure**: `SKILL.md` — процедура до 500 строк; детали в `references/` с явным «читай X, когда Y»; вычислимое — в `scripts/`.
4. **Правила проекта главнее скилла**: конфиги линтеров и окружающий код решают, скилл заполняет пробелы.
5. **Объяснять «почему»**, а MUST оставлять только для того, что ломает результат.
6. **Переносимость**: только поля из спецификации, относительные ссылки внутри скилла, скрипты на Python stdlib, без названий инструментов конкретного агента.
7. **Две оценки**: срабатывание (`trigger-evals.json`, ~20 запросов с near-miss негативами) и качество (`evals.json`, с скиллом против без).
8. **Изменение `description` — breaking change**: перепрогнать евалы свои и соседей.

## CI

`.github/workflows/ci.yml` гоняет валидатор и установку в обоих режимах на Ubuntu, macOS и Windows.
