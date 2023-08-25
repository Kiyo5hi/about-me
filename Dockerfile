FROM docker.io/library/caddy:2

COPY . /srv
RUN mv /srv/Caddyfile /etc/caddy/Caddyfile

EXPOSE 80
