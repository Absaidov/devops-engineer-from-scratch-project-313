# Проект Деплой приложения на PaaS

### Status
[![CI](https://github.com/Absaidov/devops-engineer-from-scratch-project-313/actions/workflows/main.yml/badge.svg)](https://github.com/Absaidov/devops-engineer-from-scratch-project-313/actions/workflows/main.yml)
[![Hexlet Check](https://github.com/Absaidov/devops-engineer-from-scratch-project-313/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/Absaidov/devops-engineer-from-scratch-project-313/actions/workflows/hexlet-check.yml)


## Установка Python

Перед тем как начать, убедитесь, что:

- Вы используете операционную систему, удобную для разработки (например Ubuntu,
  MacOS). Владельцам Windows рекомендую настроить Windows Subsystem for
  Linux (WSL). О том, как это сделать написано тут
  [гайд](https://ru.hexlet.io/blog/posts/ubuntu-linux-in-windows/).

## Установлен ли у Вас Python. Проверить это можно, выполнив команду:
```bash
  python3 -V
```

## Если не установлен можно установить используя менеджер пакетов

### MacOS (если установлен Homebrew)

```bash
  brew install python3
```

### Ubuntu Linux

```bash
  sudo apt install python3
```
## Теперь когда Python установлен устанавливаем утилиту uv
## MacOS и Linux
```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Ставим зависимости (FAST API и сервер uvicorn)
```bash
  uv add fastapi "uvicorn[standard]"
```

## Клонируем репозиторий локально
```bash
  git clone git@github.com:Absaidov/devops-engineer-from-scratch-project-313.git
```

## Переходим в директорию
```bash
  cd devops-engineer-from-scratch-project-313
```

## Запуск приложения

Выполните команду:

```bash
make run
```

Приложение будет доступно по адресу:

```bash
http://127.0.0.1:8080/ping
```

Для запуска в production-режиме используйте:

```bash
make start
```

## Простое API, которое отвечает `"pong"` на `/ping`


[![Посмотреть](https://img.shields.io/badge/🌐%20Посмотреть_-blue?style=for-the-badge)](https://devops-engineer-from-scratch-project-313-rq7w.onrender.com/ping)

## Специальный эндпоинт для отслеживания ошибок на Sentry
[![Посмотреть_ошибку](https://img.shields.io/badge/🌐%20Посмотреть_ошибку-blue?style=for-the-badge)](https://devops-engineer-from-scratch-project-313-rq7w.onrender.com/sentry-debug)

