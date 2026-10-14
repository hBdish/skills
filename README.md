# Skills

Скиллы для ИИ-агентов, которые пишут код (Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot и др.). Они учат агента писать и ревьюить код по нашим правилам: Go — по Google Go Style Guide, React — по правилам конкретного проекта.

- [Зачем это](#зачем-это)
- [Какие скиллы есть](#какие-скиллы-есть)
- [Быстрый старт](#быстрый-старт)
- [Как пользоваться: примеры](#как-пользоваться-примеры)
- [Как задать правила своего проекта](#как-задать-правила-своего-проекта)
- [Установка подробно](#установка-подробно)
- [Обновление и удаление](#обновление-и-удаление)
- [Если не работает](#если-не-работает)
- [Добавить или изменить скилл](#добавить-или-изменить-скилл)

## Зачем это

Без инструкций агент пишет «в среднем по интернету»: `GetUserId()` вместо `UserID()` в Go, `useEffect` для производного состояния в React, Tailwind в проекте на styled-components. Каждый раз объяснять правила в промпте долго, и все объясняют по-разному.

Скилл — папка с инструкцией (`SKILL.md`), справочниками и скриптами проверок. Агент всегда видит только короткое описание каждого скилла и сам подгружает нужный, когда задача подходит: пишете Go — подключается `go-style`, правите React-компонент — `react-style`. Полная инструкция не висит в контексте постоянно и не мешает другим задачам.

Формат — открытый стандарт [Agent Skills](https://agentskills.io/specification), поэтому одни и те же скиллы работают в разных агентах и на macOS, Linux и Windows.

## Какие скиллы есть

| Скилл | Когда срабатывает | Что делает | Откуда правила |
|---|---|---|---|
| `go-style` | пишете, правите или ревьюите Go-код | применяет Google Go Style Guide; запускает gofmt, go vet, staticcheck, golangci-lint | [Google Go Style Guide](https://google.github.io/styleguide/go/) |
| `react-style` | компоненты, хуки, JSX на TS или JS (Next.js, Vite, Remix, React Native) | сначала собирает правила вашего проекта, пишет и ревьюит по ним | ваш проект → умолчания современного React |
| `typescript-style` | TS-код вне компонентов: утилиты, сервисы, типы | строгая типизация, обработка ошибок, null | конфиги проекта → умолчания |
| `python-style` | Python-код | типизация, исключения, логирование, нейминг; запускает ruff и mypy | конфиги проекта → умолчания |
| `skill-authoring` | просите агента создать или поправить скилл | помогает писать новые скиллы для этого репозитория | — |

Скиллы ставятся **профилями**, а не все сразу:

| Профиль | Скиллы | Для кого |
|---|---|---|
| `go` | go-style | Go-бэкенд |
| `react` | react-style, typescript-style | фронтенд на React |
| `typescript` | typescript-style | TS без React (Node, библиотеки) |
| `python` | python-style | Python |
| `fullstack` | go-style, python-style, react-style, typescript-style | монорепы |
| `authors` | skill-authoring | тем, кто пишет скиллы |

Почему не все сразу: описания всех установленных скиллов лежат в контексте агента на каждом запросе. Python-скилл в React-проекте — лишние токены и ложные срабатывания.

## Быстрый старт

Нужны git и Python 3.8+. Ничего больше ставить не нужно: на macOS подойдёт встроенный `python3`, на Windows — `py` из установщика python.org.

**1. Склонируйте репозиторий один раз** (в любое место, ниже — `~/skills`):

```bash
git clone https://github.com/hBdish/skills.git ~/skills
```

**2. Установите профиль в проект.** Из корня проекта:

```bash
python3 ~/skills/scripts/install.py --profile react
```

Windows (PowerShell), если клонировали в `$HOME\skills`:

```powershell
py $HOME\skills\scripts\install.py --profile react
```

Скрипт создаст ссылки на скиллы в `.agents/skills/` (их читают Codex, Cursor, Gemini CLI, Copilot, OpenCode и др.) и в `.claude/skills/` (Claude Code). Сами файлы остаются в `~/skills`.

**3. Добавьте каталоги в `.gitignore` проекта.** Ссылки указывают на путь на вашей машине, коллегам они не нужны:

```gitignore
.agents/skills/
.claude/skills/
```

**4. Перезапустите агента и проверьте.** Спросите его: «какие скиллы тебе доступны?» — в списке должны быть `react-style` и `typescript-style`. Как вызвать скилл явно:

| Агент | Как вызвать |
|---|---|
| Claude Code | `/react-style` |
| Codex | `$react-style` (список — `/skills`) |
| Остальные | напишите в сообщении «используй react-style» |

Обычно явно вызывать не нужно: агент подключает скилл сам, когда задача подходит.

## Как пользоваться: примеры

Пишите агенту как обычно, упоминать скилл не нужно.

### Новый компонент в React-проекте

> Сделай компонент QuantityStepper (минус / число / плюс) и тест к нему

Что сделает агент с `react-style`:

1. Запустит `scripts/conventions.py` и узнает правила проекта, например:
   ```
   RULE DOCS: AGENTS.md
   styling: styled-components   state/data: Zustand   tests: Vitest, Testing Library
   file naming: kebab-case folder/index   exports: default export
   component declaration: arrow function   props typing: interface
   ```
2. Прочитает `AGENTS.md` проекта и откроет соседний компонент как образец.
3. Создаст `src/components/quantity-stepper/index.tsx` и `styles.ts` в том же стиле, что и соседние компоненты, плюс тест на Testing Library.
4. Прогонит tsc, ESLint и Prettier проекта и скажет, если что-то из них не запустилось.

Без скилла агент с большой вероятностью выбрал бы свои привычки: named export, Tailwind или CSS-модули, тест рядом с файлом.

### Ревью Go-кода

> Посмотри handler.go перед PR

Агент запустит проверки и выдаст замечания по важности: сначала ошибки и безопасность, потом нейминг и стиль. Пример замечания:

```
[high] in-band error — handler.go:44
  current: func (h *UserHandler) LookupAge(id string) int { ... return -1 }
  fix:     func (h *UserHandler) LookupAge(ctx context.Context, id string) (int, error)
  why:     -1 легко принять за настоящий возраст; ошибка должна быть отдельным значением
```

В конце агент перечислит проверки, которые не запустились (например, `goimports: not installed`). Значит, эта часть не проверена, а не «всё чисто».

### Вопросы по правилам

> Тут нужен %w или %v? Ошибка из pgx уходит наверх в хендлер
>
> useEffect здесь нужен? Он пересчитывает total, когда меняются items
>
> Как назвать пакет, который читает и валидирует конфиги?

Агент ответит по правилам из скилла и укажет, откуда правило: Google Go Style Guide или правила вашего проекта.

### Отключить стиль на одну задачу

> Не трогай стиль, у нас фриз. Найди, почему воркер обрабатывает сообщение дважды

Агент займётся только багом, без замечаний по стилю.

## Как задать правила своего проекта

`react-style` (и частично остальные скиллы) подчиняется правилам проекта в таком порядке:

1. **Документы с правилами**: `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `.cursor/rules/`, `.github/copilot-instructions.md`, `docs/conventions/`.
2. **Конфиги**: ESLint, Prettier/Biome, tsconfig, `.golangci.yml`, `pyproject.toml`.
3. **Существующий код**: как уже написаны соседние файлы.
4. **Умолчания скилла** — только там, где проект молчит.

Хотите, чтобы агент всегда делал по-вашему — напишите это в `AGENTS.md` в корне проекта. Пример:

```markdown
## Code conventions

- One component per folder: `src/components/<kebab-name>/index.tsx`, styles in `styles.ts` next to it.
- Components are arrow functions with a default export.
- Props are declared as `interface <Name>Props`.
- Styling only via styled-components; no inline `style={{}}`, no CSS files.
- Global client state lives in zustand stores under `src/store/`; no React Context for shared state.
- Tests go in `src/components/__tests__/<kebab-name>.test.tsx`, using Testing Library + user-event.
```

Посмотреть, что скилл видит в вашем проекте, можно и самому:

```bash
python3 ~/skills/skills/framework/react-style/scripts/conventions.py .
```

Механическое форматирование (отступы, кавычки, порядок импортов) скиллы не диктуют: они запускают форматтер и линтер проекта. Скилл срабатывает по решению модели, а не всегда, поэтому то, что должно соблюдаться железно, должно проверяться ещё и линтером в CI.

## Установка подробно

Все варианты:

```bash
python3 ~/skills/scripts/install.py --list                                 # скиллы, профили, агенты
python3 ~/skills/scripts/install.py --profile go                           # в текущий проект
python3 ~/skills/scripts/install.py --profile react --project ~/work/shop  # в другой проект
python3 ~/skills/scripts/install.py --profile go --profile python          # несколько профилей
python3 ~/skills/scripts/install.py --skill go-style                       # один скилл
python3 ~/skills/scripts/install.py --profile react --agent claude         # только для Claude Code
python3 ~/skills/scripts/install.py --profile react --agents-md            # + список скиллов в AGENTS.md
python3 ~/skills/scripts/install.py --profile authors --global             # для всех проектов сразу
python3 ~/skills/scripts/install.py --profile react --copy                 # копии вместо ссылок
python3 ~/skills/scripts/install.py --profile react --dry-run              # показать план, ничего не менять
```

| Флаг | Когда нужен |
|---|---|
| `--agent <name>` | ставить не в агентов по умолчанию (`universal` + `claude`). Полный список — `--list`: windsurf, kiro, roo, junie, goose и др. |
| `--global` | скилл нужен во всех проектах (ставится в `~/.agents/skills`, `~/.claude/skills`). Языковые скиллы лучше ставить в проект. |
| `--agents-md` | агент не умеет скиллы, но читает `AGENTS.md`. Скрипт допишет туда список скиллов, и агент будет открывать их сам. Повторный запуск обновляет список, ваш текст не трогается. |
| `--copy` | CI, Docker, devcontainer, или вы хотите закоммитить скиллы в проект, чтобы они были у всей команды без клонирования этого репозитория. |

Как это работает на разных ОС:

| ОС | Как ставится |
|---|---|
| macOS, Linux | символическая ссылка на папку в `~/skills` |
| Windows | символическая ссылка (если включён Developer Mode), иначе junction (админ не нужен), иначе копия |

Без клонирования, через npm (тот же формат):

```bash
npx skills add hBdish/skills --skill go-style
```

## Обновление и удаление

Обновиться:

```bash
git -C ~/skills pull
```

Ссылки обновятся во всех проектах сразу. Если ставили с `--copy`, повторите `install.py` с теми же параметрами.

Удалить из проекта (удаляет только то, что поставил скрипт):

```bash
python3 ~/skills/scripts/install.py --profile react --uninstall
```

## Если не работает

**Агент не видит скилл.**
- Перезапустите агента: каталог скиллов читается при старте.
- Проверьте, что ставили в нужный проект: `ls .agents/skills .claude/skills`.
- Ваш агент читает другой каталог — поставьте с `--agent` (список — `--list`) или с `--agents-md`.

**Скилл есть, но не срабатывает.**
- Вызовите явно (`/go-style` в Claude Code, `$go-style` в Codex) или напишите «используй go-style».
- Если не срабатывает на типичный запрос, это баг описания скилла. Заведите issue с текстом запроса.

**Срабатывает не тот скилл** (например, python-style на TS-файл) — тоже issue с текстом запроса.

**В выводе проверок `SKIP`.** Инструмент не установлен, и эта часть кода не проверена. Поставьте его:

| Скилл | Инструменты |
|---|---|
| go-style | `go install golang.org/x/tools/cmd/goimports@latest`, `go install honnef.co/go/tools/cmd/staticcheck@latest`, [golangci-lint](https://golangci-lint.run/welcome/install/) |
| react-style, typescript-style | `npm install` в проекте: используются tsc, eslint, prettier/biome из `node_modules` проекта |
| python-style | `pip install ruff mypy` (или `uv tool install ruff`) |

**Windows: `python3` не найден.** Используйте `py` или `python`.

**Windows: скилл поставился копией, а не ссылкой.** Значит, не удалось ни создать symlink, ни junction. Всё работает, только после `git pull` нужно повторить `install.py`. Чтобы были ссылки, включите Developer Mode: Settings → System → For developers.

**`exists and was not installed from this repo; skipped`.** В проекте уже есть свой скилл с таким именем. Скрипт его не трогает; заменить можно флагом `--force`.

## Добавить или изменить скилл

См. [CONTRIBUTING.md](CONTRIBUTING.md). Коротко: `python3 scripts/new_skill.py <группа> <имя>`, заполнить по шаблону, `python3 scripts/validate.py --strict`, PR. Можно попросить агента: при установленном профиле `authors` он сделает это по правилам репозитория.
