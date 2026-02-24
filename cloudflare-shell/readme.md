# Cloudflare Tunnel Auto-Setup Script — README

## Purpose

This script automatically:

* Installs `cloudflared` if missing
* Creates or reuses a Cloudflare Tunnel
* Configures ingress routing rules
* Creates or updates DNS records
* Installs and starts the systemd service

Result: your local services become accessible via Cloudflare without opening firewall ports.

---

## Requirements

System requirements:

* Debian / Ubuntu / Raspberry Pi OS
* sudo privileges
* Domain already added to Cloudflare
* Cloudflare API Token with correct permissions (see below)

Dependencies (auto-checked except jq/curl):

```bash
sudo apt update
sudo apt install -y curl jq
```

---

## Cloudflare API Token Setup

Go to:

https://dash.cloudflare.com/profile/api-tokens

Click:

**Create Token → Custom Token**

Use these exact permissions:

### Account Permissions

```
Cloudflare Tunnel    Edit
```

### Zone Permissions

```
DNS                  Edit
Zone                 Read
```

### Account Resources

```
Include → All accounts
```

### Zone Resources

```
Include → Specific zone → aimsdtu.in
```

(or your domain)

---

## Required Values

You must fill these variables at the top of the script:

```bash
ACCOUNT_ID="your_account_id"
ZONE_ID="your_zone_id"
API_TOKEN="your_api_token"
TUNNEL_NAME="api-tunnel"
```

---

## How to Get Required IDs

### Get Account ID

Cloudflare Dashboard → Right sidebar → copy **Account ID**

---

### Get Zone ID

Cloudflare Dashboard → Domain → Right sidebar → copy **Zone ID**

---

## Configure Ingress Rules

Format:

```bash
INGRESS_RULES=(
  "hostname=service"
)
```

Examples:

```bash
INGRESS_RULES=(
  "api.example.com=http://localhost:8000"
  "ssh.example.com=ssh://localhost:22"
  "app.example.com=http://localhost:3000"
)
```

Supported services:

```
http://localhost:PORT
https://localhost:PORT
ssh://localhost:22
tcp://localhost:PORT
```

---

## How to Run

Make executable:

```bash
chmod +x tunnel.sh
```

Run:

```bash
./tunnel.sh
```

---

## What Happens Internally

The script performs:

1. Installs cloudflared if missing
2. Creates tunnel (or reuses existing)
3. Applies ingress routing config
4. Creates DNS CNAME records
5. Installs systemd service
6. Starts and enables tunnel

---

## Verify Tunnel Running

Check service:

```bash
systemctl status cloudflared
```

Check tunnel:

```bash
cloudflared tunnel list
```

Test DNS:

```bash
curl https://your-subdomain.example.com
```

---

## File Locations Used

Systemd service:

```
/etc/systemd/system/cloudflared.service
```

Tunnel credentials:

```
/etc/cloudflared/
```

---

## Security Model

This tunnel:

* requires no open ports
* works behind NAT
* uses outbound-only connection
* protected by Cloudflare proxy

---

## Adding New Services Later

Edit script:

```bash
INGRESS_RULES+=(
  "new.example.com=http://localhost:5000"
)
```

Run script again:

```bash
./tunnel.sh
```

It will update safely.

---

## Removing Tunnel

List tunnels:

```bash
cloudflared tunnel list
```

Delete tunnel:

```bash
cloudflared tunnel delete TUNNEL_NAME
```

Delete service:

```bash
sudo systemctl stop cloudflared
sudo systemctl disable cloudflared
sudo rm /etc/systemd/system/cloudflared.service
```

---

## Troubleshooting

Check logs:

```bash
journalctl -u cloudflared -f
```

Check DNS:

```bash
dig subdomain.example.com
```

Restart service:

```bash
sudo systemctl restart cloudflared
```

---

## Token Permission Summary (Exact Required Scope)

Minimum required permissions:

```
Account
  Cloudflare Tunnel: Edit

Zone
  DNS: Edit
  Zone: Read

Resources
  Account: Include All Accounts
  Zone: Include Specific Zone
```

Nothing else required.

---

## Safe Usage Model

This token cannot:

* access website content
* read emails
* modify workers
* access other zones

Only tunnel and DNS.

---

## Deployment Model

Recommended:

* one tunnel per machine
* reuse tunnel for multiple services
* run as systemd service

---

## Done

Your services are now securely exposed via Cloudflare Tunnel.
