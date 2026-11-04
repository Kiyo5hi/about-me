FROM ghcr.io/kiyo5hi/gmwe@sha256:a0c4ab539b935cd3fce294aa795619ac2bf3911e3e63d4950d4e29d4f8b55743

COPY . /srv
RUN mv /srv/Caddyfile /etc/caddy/Caddyfile

EXPOSE 80
