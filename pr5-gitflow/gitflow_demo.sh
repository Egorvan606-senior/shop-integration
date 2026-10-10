#!/usr/bin/env bash
# ПР №5. Git Flow, вариант 5: АИС «Цифровой университетский архив».
# Скрипт воспроизводит весь жизненный цикл в учебном репозитории и печатает граф коммитов:
#   feature/crypto-module + feature/key-storage -> develop -> release/2.0.0 (месяц
#   интеграционного тестирования) -> main (v2.0.0); параллельно hotfix/1.0.1 с прода.
# Используются обычные команды git (без расширения git-flow), чтобы было видно каждое действие.
#
# Запуск (Linux/macOS или Git Bash в Windows):  bash gitflow_demo.sh [папка]
set -euo pipefail

DIR="${1:-./archive-gitflow-demo}"
rm -rf "$DIR" && mkdir -p "$DIR" && cd "$DIR"

git init -q -b main
git config user.name  "Учебный стенд"
git config user.email "demo@archive.local"
git config commit.gpgsign false

# Коммит с заданной датой и автором (роль в команде)
commit() {  # commit "дата" "автор" "файл" "сообщение"
  local when="$1" who="$2" file="$3" msg="$4"
  mkdir -p "$(dirname "$file")"; echo "$msg ($when)" >> "$file"
  git add "$file"
  GIT_AUTHOR_DATE="$when" GIT_COMMITTER_DATE="$when" \
    git -c user.name="$who" commit -q -m "$msg"
}
merge() {   # merge "дата" "ветка" "сообщение"
  GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" \
    git -c user.name="Тимлид (релиз-менеджер)" merge -q --no-ff "$2" -m "$3"
}
tag() { GIT_COMMITTER_DATE="$1" git -c user.name="Тимлид (релиз-менеджер)" tag -a "$2" -m "$3"; }

# ---------- Исходное состояние: работающая версия 1.0.0 на проде ----------
commit "2026-09-01T10:00:00+03:00" "Тимлид (релиз-менеджер)" src/archive/storage.py "feat: хранилище документов, электронная подпись (v1.0.0)"
tag    "2026-09-01T10:05:00+03:00" v1.0.0 "Релиз 1.0.0"
git switch -q -c develop                      # интеграционная ветка

# ---------- Этап 1. feature: два разработчика параллельно ----------
git switch -q -c feature/crypto-module develop
commit "2026-09-02T11:00:00+03:00" "Разработчик 1" src/crypto/cipher.py      "feat(crypto): шифрование файлов ГОСТ Р 34.12-2015 «Кузнечик» в режиме MGM"
git switch -q develop
git switch -q -c feature/key-storage develop
commit "2026-09-03T12:00:00+03:00" "Разработчик 2" src/crypto/keystore.py    "feat(keys): хранилище ключей шифрования, ключи вне репозитория"
git switch -q feature/crypto-module
commit "2026-09-05T15:00:00+03:00" "Разработчик 1" src/crypto/cipher.py      "feat(crypto): потоковое шифрование больших файлов (диссертации, сканы)"
commit "2026-09-08T16:00:00+03:00" "Разработчик 1" tests/test_cipher.py      "test(crypto): модульные тесты шифрования и расшифрования"
git switch -q feature/key-storage
commit "2026-09-09T10:30:00+03:00" "Разработчик 2" src/crypto/keystore.py    "feat(keys): ротация ключей и журнал доступа к ключам"

# ---------- Этап 2. Слияние в develop через pull request (после ревью и SAST) ----------
git switch -q develop
merge "2026-09-10T18:00:00+03:00" feature/key-storage   "Merge PR #12: feature/key-storage -> develop"
merge "2026-09-11T18:00:00+03:00" feature/crypto-module "Merge PR #14: feature/crypto-module -> develop"
git branch -q -d feature/crypto-module feature/key-storage

# ---------- Этап 3. release: месяц интеграционного тестирования ----------
git switch -q -c release/2.0.0 develop
commit "2026-09-14T09:00:00+03:00" "Тимлид (релиз-менеджер)" VERSION            "chore(release): версия 2.0.0, заморозка функционала"
commit "2026-09-22T14:00:00+03:00" "Разработчик 1" src/crypto/cipher.py      "fix(crypto): ошибка на файлах больше 2 ГБ (найдено на интеграционных тестах)"

# ---------- Параллельно: критическая ошибка на проде -> hotfix ----------
git switch -q -c hotfix/1.0.1 main
commit "2026-09-24T20:00:00+03:00" "Разработчик 2" src/archive/storage.py    "fix(sign): подпись с истёкшим сертификатом принималась как действительная"
commit "2026-09-24T20:30:00+03:00" "Разработчик 2" VERSION                    "chore: версия 1.0.1"
git switch -q main
merge "2026-09-24T21:00:00+03:00" hotfix/1.0.1 "Merge hotfix/1.0.1 -> main"
tag   "2026-09-24T21:05:00+03:00" v1.0.1 "Hotfix 1.0.1"
git switch -q release/2.0.0                 # release открыт -> исправление вливаем в него
# Конфликт в VERSION ожидаем: в hotfix версия 1.0.1, в релизе 2.0.0 -> оставляем версию релиза
if ! merge "2026-09-25T10:00:00+03:00" hotfix/1.0.1 "Merge hotfix/1.0.1 -> release/2.0.0" >/dev/null 2>&1; then
  git checkout -q --ours VERSION && git add VERSION
  GIT_AUTHOR_DATE="2026-09-25T10:00:00+03:00" GIT_COMMITTER_DATE="2026-09-25T10:00:00+03:00" \
    git -c user.name="Тимлид (релиз-менеджер)" commit -q --no-edit
  echo "[hotfix -> release] конфликт в VERSION разрешён в пользу версии релиза 2.0.0"
fi
git branch -q -d hotfix/1.0.1

commit "2026-10-02T13:00:00+03:00" "Разработчик 1" src/crypto/keystore.py    "fix(keys): права доступа к файлу ключей (замечание пентеста)"
commit "2026-10-12T17:00:00+03:00" "Тимлид (релиз-менеджер)" CHANGELOG.md     "docs: CHANGELOG 2.0.0, тестирование завершено"

# ---------- Этап 4. Выпуск: release -> main (тег) и обратно в develop ----------
git switch -q main
merge "2026-10-14T10:00:00+03:00" release/2.0.0 "Merge release/2.0.0 -> main"
tag   "2026-10-14T10:05:00+03:00" v2.0.0 "Релиз 2.0.0: модуль шифрования файлов"
git switch -q develop
merge "2026-10-14T10:10:00+03:00" release/2.0.0 "Merge release/2.0.0 -> develop"
git branch -q -d release/2.0.0

echo "===== Граф коммитов (git log --graph) ====="
git log --graph --all --decorate --date=short --format='%h %ad %s%d'
echo
echo "===== Ветки ====="; git branch
echo "===== Теги =====";  git tag -n1
