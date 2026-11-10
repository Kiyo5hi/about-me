FROM docker.io/library/caddy:2.11.8@sha256:4fcafa98afd1c2e642e353e3c5cf9ddbe892fcee14bc990e7ba2c5b78e51f9cf

COPY --chown=10001:10001 index.html avatar.webp /srv/
COPY --chown=10001:10001 Caddyfile /etc/caddy/Caddyfile

USER 10001:10001

EXPOSE 80
