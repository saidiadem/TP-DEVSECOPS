#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p reports
# L'image ZAP écrit les rapports avec son propre utilisateur.
chmod 777 reports
suffix="${GITHUB_RUN_ID:-local}-$$"
network="tp2-$suffix"
container="tp2-app-$suffix"
cleanup() {
  docker logs "$container" > reports/application.log 2>&1 || true
  docker rm -f "$container" >/dev/null 2>&1 || true
  docker network rm "$network" >/dev/null 2>&1 || true
}
trap cleanup EXIT
docker network create "$network" >/dev/null
docker run -d --name "$container" --network "$network" --network-alias app tp2-app >/dev/null
ready=false
for attempt in {1..30}; do
  if docker exec "$container" python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"; then
    ready=true
    break
  fi
  sleep 2
done
if [ "$ready" != true ]; then
  echo "L'application ne démarre pas" >&2
  exit 1
fi
# Supprimer tout ancien rapport pour ne jamais valider un scan précédent.
rm -f reports/zap.json reports/zap.html
set +e
docker run --rm --network "$network" \
  -v "$PWD/reports:/zap/wrk:rw" \
  ghcr.io/zaproxy/zaproxy:stable zap-full-scan.py \
  -t http://app:8000/ -m 1 -T 10 -J zap.json -r zap.html
status=$?
set -e
# 0, 1, 2 sont des résultats de scan ; 3 et les erreurs Docker sont bloquants.
if [ "$status" -gt 2 ]; then
  echo "Erreur d'exécution ZAP : $status" >&2
  exit "$status"
fi
python scripts/zap_gate.py reports/zap.json
