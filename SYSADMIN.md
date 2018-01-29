# Sysadmin

Этот документ содержит краткие заметки, касающиеся администрирования.

## SSL-сертификат для ci.fidals.com

Мы используем letsencrypt. На сервере в crontab прописан autorenew, но nginx не умеет автоматически перезагружать сертификаты. Поэтому, если браузер будет ругаться на истекший сертификат, достаточно зайти на сервер и перезагрузить nginx: `systemctl restart nginx`.

Сами сертификаты и ключи лежат в стандартной локации letsencrypt: `/etc/letsencrypt/live/ci.fidals.com`

## Конфиги Drone CI

Лежат в `/etc/drone-ci`.

## Nginx-конфиг для Drone CI

Находится в `/etc/nginx/sites-enabled/fidals-ci`.
