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

# Ставим Node.js, чтобы получить собранный frontend из npm-пакета
RUN apt-get update \
    && apt-get install -y --no-install-recommends nodejs npm \
    && rm -rf /var/lib/apt/lists/*

# Сначала копируем файлы зависимостей Python и Node
COPY pyproject.toml uv.lock ./
COPY package.json package-lock.json ./

# Ставим Python-зависимости
RUN uv sync --frozen

# Ставим npm-зависимости, в том числе пакет с уже собранным UI
RUN npm ci

# Копируем код приложения
COPY . .

# Устанавливаем приложение в систему Python
RUN uv pip install --system -e .

# Копируем frontend-статику туда, откуда ее будет отдавать nginx
RUN mkdir -p /app/public \
    && cp -r ./node_modules/@hexlet/project-devops-deploy-crud-frontend/dist/. /app/public/

# Удаляем дефолтный nginx-конфиг
RUN rm -f /etc/nginx/sites-enabled/default
RUN rm -f /etc/nginx/conf.d/default.conf

# Копируем свой конфиг и скрипт запуска
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY docker/start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 80

CMD ["/app/start.sh"]