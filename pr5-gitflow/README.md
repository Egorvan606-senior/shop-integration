# ПР №5. Git Flow — вариант 5: АИС «Цифровой университетский архив»

Отчёт: `docs/пр5_Иванов.pdf`. Вариант выбран по номеру в списке группы (№ 10 → вариант 5).

| Файл | Что это |
|---|---|
| `gitflow_demo.sh` | Скрипт, который создаёт учебный репозиторий и выполняет весь сценарий: `feature/crypto-module` и `feature/key-storage` → `develop` → `release/2.0.0` (месяц тестирования) → `main` (v2.0.0), плюс `hotfix/1.0.1` во время открытого релиза |
| `gitflow_demo_output.txt` | Вывод скрипта: граф `git log --graph`, ветки и теги |
| `gitflow_graph.py` → `gitflow_graph.png` | Графическая схема ветвления (по дорожкам веток) |

## Запуск

```bash
bash gitflow_demo.sh /tmp/archive-demo        # Linux/macOS или Git Bash в Windows
cd /tmp/archive-demo && git log --graph --oneline --all --decorate
```

Хеши коммитов детерминированы (даты и авторы заданы в скрипте), поэтому вывод совпадает с `gitflow_demo_output.txt`.

## Кратко про SAST

SAST подключается на каждом pull request `feature → develop` (до слияния в общую ветку), полный SAST, SCA и пентест — на ветке `release` перед выпуском в `main`; `hotfix` проходит сокращённую обязательную проверку.
