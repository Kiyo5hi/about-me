"""Check the served artifact, including accidental build-context exposure."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request


def docker(*args):
    return subprocess.check_output(['docker', *args], text=True).strip()


image = sys.argv[1]
root = Path(__file__).resolve().parents[1]
container = docker(
    'run', '-d', '--read-only', '--cap-drop', 'ALL', '--cap-add', 'NET_BIND_SERVICE',
    '--memory', '128m', '--cpus', '0.5', '--tmpfs', '/config:uid=10001,gid=10001,mode=0700',
    '--tmpfs', '/data:uid=10001,gid=10001,mode=0700', '-p', '127.0.0.1::80', image)
try:
    state = json.loads(docker('inspect', container))[0]
    assert state['Config']['User'] == '10001:10001', 'runtime must be non-root'
    files = docker('exec', container, 'find', '/srv', '-type', 'f').splitlines()
    assert set(files) == {'/srv/index.html', '/srv/avatar.webp'}, 'unexpected public files'
    port = state['NetworkSettings']['Ports']['80/tcp'][0]['HostPort']
    base = f'http://127.0.0.1:{port}'
    for attempt in range(30):
        try:
            with urllib.request.urlopen(base, timeout=2):
                break
        except (OSError, urllib.error.URLError):
            if attempt == 29:
                raise
            time.sleep(0.2)
    for route, filename in [('/', 'index.html'), ('/avatar.webp', 'avatar.webp')]:
        with urllib.request.urlopen(base + route, timeout=5) as response:
            assert response.status == 200
            assert hashlib.sha256(response.read()).digest() == hashlib.sha256((root / filename).read_bytes()).digest()
    for route in ['/.git/HEAD', '/.git/config', '/%2egit/config', '/.github/workflows/cd.yaml',
                  '/.dockerignore', '/Dockerfile', '/Caddyfile', '/scripts/verify-image.py', '/missing']:
        try:
            with urllib.request.urlopen(base + route, timeout=5) as response:
                raise AssertionError(f'unexpected public path: {route}, HTTP {response.status}')
        except urllib.error.HTTPError as error:
            assert error.code == 404, (route, error.code)
    print('PASS non-root read-only runtime, exact public files and hashes, internal paths return 404')
finally:
    docker('rm', '-f', container)
