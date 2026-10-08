#!/usr/bin/env bash
# Deploy stt-server ke VPS (⚠️ gerbang manusia, docs/22). Pemakaian: ./deploy.sh <host-ssh>
# Prasyarat VPS: user `stt`, /opt/stt-server/{releases,models,.env} milik stt, uv terpasang,
# unit /etc/systemd/system/stt-server.service (salinan stt-server.service), Caddy aktif.
set -euo pipefail

host="${1:?pemakaian: ./deploy.sh <host-ssh>}"
release="$(date -u +%Y%m%d%H%M%S)"
base=/opt/stt-server
here="$(cd "$(dirname "$0")" && pwd)"

echo "→ tes lokal"
(cd "$here" && uv run pytest -q)

echo "→ unggah rilis $release"
rsync -az --delete --exclude .venv --exclude tests --exclude .env \
  "$here/" "$host:$base/releases/$release/"

echo "→ pasang dependensi & alihkan symlink"
ssh "$host" "set -euo pipefail
  cd $base/releases/$release && uv sync --frozen --no-dev -q
  ln -sfn $base/releases/$release $base/current
  sudo systemctl restart stt-server
  sleep 2
  for i in \$(seq 1 60); do curl -fsS http://127.0.0.1:8080/healthz && exit 0; sleep 5; done
  echo 'healthz gagal — rollback: ln -sfn <rilis-sebelumnya> $base/current && sudo systemctl restart stt-server' >&2
  exit 1"

echo "→ bersihkan rilis lama (sisakan 3)"
ssh "$host" "ls -1dt $base/releases/* | tail -n +4 | xargs -r rm -rf"
echo "selesai: $release"
