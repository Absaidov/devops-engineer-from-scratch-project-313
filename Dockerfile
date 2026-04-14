FROM node:20-alpine AS frontend

WORKDIR /frontend

COPY package.json package-lock.json ./
RUN npm ci
RUN mkdir -p /frontend/public \
    && cp -r ./node_modules/@hexlet/project-devops-deploy-crud-frontend/dist/. /frontend/public/

FROM python:3.12-slim

WORKDIR /app

# Устанавливаем системные пакеты:
# - nginx для раздачи статики и reverse proxy
# - curl по мелочи полезен для диагностики
RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx curl \
    && rm -rf /var/lib/apt/lists/*

# Ставим uv
RUN pip install --no-cache-dir uv

# Сначала копируем файлы зависимостей Python
COPY pyproject.toml uv.lock ./

# Ставим Python-зависимости
RUN uv sync --frozen

# Копируем код приложения
COPY . .

# Копируем frontend-статику из frontend stage
COPY --from=frontend /frontend/public /app/public

# Удаляем дефолтный nginx-конфиг
RUN rm -f /etc/nginx/sites-enabled/default
RUN rm -f /etc/nginx/conf.d/default.conf

# Копируем свой конфиг и скрипт запуска
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY docker/start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 80

CMD ["/app/start.sh"]
