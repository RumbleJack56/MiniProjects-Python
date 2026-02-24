#!/usr/bin/env bash
set -euo pipefail

# ================= USER CONFIG =================
ACCOUNT_ID="YOUR_ACCOUNT_ID_HERE"
ZONE_ID="YOUR_ZONE_ID_HERE"
API_TOKEN="YOUR_API_TOKEN_HERE"
TUNNEL_NAME="YOUR_TUNNEL_NAME_HERE"

INGRESS_RULES=(
  "api.example.com=http://localhost:8000"
  "ssh.example.com=ssh://localhost:22"
  "app.example.com=http://localhost:3000"
)
# ===============================================


CF_API="https://api.cloudflare.com/client/v4"
HDR=(-H "Authorization: Bearer ${API_TOKEN}" -H "Content-Type: application/json")


# ---------- VALIDATE CONFIG ----------
assert_set() {
  local var_name="$1"
  local var_value="$2"
  [[ -n "$var_value" && "$var_value" != *"YOUR_"* ]] || {
    echo "Error: $var_name not configured"
    exit 1
  }
}

assert_set "ACCOUNT_ID" "$ACCOUNT_ID"
assert_set "ZONE_ID" "$ZONE_ID"
assert_set "API_TOKEN" "$API_TOKEN"
assert_set "TUNNEL_NAME" "$TUNNEL_NAME"


# ---------- REQUIRE DEPENDENCIES ----------
require() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing dependency: $1"
    exit 1
  }
}

require curl
require jq


# ---------- INSTALL CLOUDFLARED IF MISSING ----------
if ! command -v cloudflared >/dev/null 2>&1; then

  echo "Installing cloudflared..."

  ARCH="$(dpkg --print-architecture)"
  TMP_DEB="/tmp/cloudflared.deb"

  curl -fsSL \
    "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-${ARCH}.deb" \
    -o "$TMP_DEB"

  sudo dpkg -i "$TMP_DEB"
  rm -f "$TMP_DEB"

  echo "cloudflared installed"

fi


# ---------- API WRAPPER ----------
api() {
  curl -fsS "${HDR[@]}" "$@"
  echo
}


# ---------- GET OR CREATE TUNNEL ----------
echo "Checking tunnel..."

TUNNEL_ID="$(
  api "${CF_API}/accounts/${ACCOUNT_ID}/cfd_tunnel" \
  | jq -r ".result[] | select(.name==\"${TUNNEL_NAME}\") | .id"
)"

if [[ -z "${TUNNEL_ID}" ]]; then

  echo "Creating tunnel..."

  TUNNEL_JSON="$(
    api -X POST "${CF_API}/accounts/${ACCOUNT_ID}/cfd_tunnel" \
      --data "{\"name\":\"${TUNNEL_NAME}\",\"config_src\":\"cloudflare\"}"
  )"

  TUNNEL_ID="$(jq -r '.result.id' <<<"$TUNNEL_JSON")"
  TUNNEL_TOKEN="$(jq -r '.result.token' <<<"$TUNNEL_JSON")"

else

  echo "Tunnel exists"

  TUNNEL_TOKEN="$(
    api "${CF_API}/accounts/${ACCOUNT_ID}/cfd_tunnel/${TUNNEL_ID}/token" \
    | jq -r '.result'
  )"

fi


# ---------- BUILD INGRESS CONFIG ----------
echo "Building ingress config..."

INGRESS_JSON="["

for rule in "${INGRESS_RULES[@]}"; do

  HOST="${rule%%=*}"
  SVC="${rule##*=}"

  INGRESS_JSON+="{\"hostname\":\"${HOST}\",\"service\":\"${SVC}\"},"

done

INGRESS_JSON+="{\"service\":\"http_status:404\"}]"


# ---------- APPLY CONFIG ----------
echo "Applying tunnel config..."

api -X PUT \
  "${CF_API}/accounts/${ACCOUNT_ID}/cfd_tunnel/${TUNNEL_ID}/configurations" \
  --data "{\"config\":{\"ingress\":${INGRESS_JSON}}}" \
  >/dev/null


# ---------- UPSERT DNS ----------
echo "Configuring DNS..."

for rule in "${INGRESS_RULES[@]}"; do

  HOST="${rule%%=*}"

  DNS_ID="$(
    api "${CF_API}/zones/${ZONE_ID}/dns_records?type=CNAME&name=${HOST}" \
    | jq -r '.result[0].id // empty'
  )"

  DNS_PAYLOAD="{
    \"type\":\"CNAME\",
    \"name\":\"${HOST}\",
    \"content\":\"${TUNNEL_ID}.cfargotunnel.com\",
    \"proxied\":true
  }"

  if [[ -n "${DNS_ID}" ]]; then

    api -X PUT \
      "${CF_API}/zones/${ZONE_ID}/dns_records/${DNS_ID}" \
      --data "${DNS_PAYLOAD}" \
      >/dev/null

    echo "Updated DNS: ${HOST}"

  else

    api -X POST \
      "${CF_API}/zones/${ZONE_ID}/dns_records" \
      --data "${DNS_PAYLOAD}" \
      >/dev/null

    echo "Created DNS: ${HOST}"

  fi

done


# ---------- INSTALL SERVICE ----------
if [[ ! -f /etc/systemd/system/cloudflared.service ]]; then

  echo "Installing cloudflared service..."

  sudo cloudflared service install "${TUNNEL_TOKEN}"

else

  echo "cloudflared service already installed"

fi


# ---------- ENABLE + START ----------
sudo systemctl enable cloudflared >/dev/null 2>&1 || true
sudo systemctl restart cloudflared


# ---------- OUTPUT ----------
echo
echo "Tunnel Ready"
echo "Tunnel Name: ${TUNNEL_NAME}"
echo "Tunnel ID:   ${TUNNEL_ID}"
echo

for rule in "${INGRESS_RULES[@]}"; do
  printf "  https://%-30s -> %s\n" \
    "${rule%%=*}" \
    "${rule##*=}"
done

echo
echo "Service status:"
systemctl is-active cloudflared
