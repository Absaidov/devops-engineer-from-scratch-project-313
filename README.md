# Проект Деплой приложения на PaaS

### Hexlet tests and linter status:
[![Actions Status](https://github.com/Absaidov/devops-engineer-from-scratch-project-313/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/Absaidov/devops-engineer-from-scratch-project-313/actions)
### Badge of My workflow
[![PaaS](https://github.com/Absaidov/devops-engineer-from-scratch-project-313/actions/workflows/main.yml/badge.svg)](https://github.com/Absaidov/devops-engineer-from-scratch-project-313/actions/workflows/main.yml)


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

## Выполняем команду
```bash
  make start
```

## Смотрим на мое творение по данной ссылке в браузере и радуемся за меня
```bash
  http://127.0.0.1:8080/ping
```

