#!/usr/bin/env bash
set -euo pipefail

# ================= USER CONFIG =================
ACCOUNT_ID="YOUR_ACCOUNT_ID_HERE"
ZONE_ID="YOUR_ZONE_ID_HERE"
API_TOKEN="YOUR_API_TOKEN_HERE"
TUNNEL_NAME="YOUR_TUNNEL_NAME_HERE"

ENABLE_TEST_INGRESS=true
# TEST_ROUTE format: "subdomain=protocol://host:port"
# The subdomain and port are parsed from this value and used both for:
#   - registering the ingress rule with Cloudflare
#   - launching the local test FastAPI server on the correct port
TEST_ROUTE="testpc1=http://localhost:12355"

DOMAIN="YOUR_DOMAIN.TLD"
#subdomain=hosturl
INGRESS_RULES=(
  "ssh=tcp://localhost:22"
  "subdomain=http://localhost:8000"
)

CF_API="https://api.cloudflare.com/client/v4"
AUTH=(-H "Authorization: Bearer ${API_TOKEN}" -H "Content-Type: application/json")

CONFIG_FILE=".tunnelconfig"

# ================= FUNCTIONS =================

load_config() {
  if [[ -f "$CONFIG_FILE" ]]; then
    source "$CONFIG_FILE"
    return 0
  fi
  return 1
}

save_config() {
  local user_created="${USER_CREATED_TUNNEL:-false}"
  local skip_prompt="${SKIP_TUNNEL_PROMPT:-false}"
  
  cat > "$CONFIG_FILE" << EOF
# Tunnel configuration (auto-generated)
SAVED_TUNNEL_ID="$TUNNEL_ID"
SAVED_TUNNEL_TOKEN="$TUNNEL_TOKEN"
SAVED_TUNNEL_NAME="$TUNNEL_NAME"
USER_CREATED_TUNNEL="$user_created"
SKIP_TUNNEL_PROMPT="$skip_prompt"
EOF
  echo "✓ Configuration saved to $CONFIG_FILE"
}

cf_api_request() {
  local method="$1"
  local endpoint="$2"
  local data="${3:-}"
  
  if [[ -n "$data" ]]; then
    curl -s --request "$method" "${CF_API}${endpoint}" "${AUTH[@]}" --data "$data"
  else
    curl -s --request "$method" "${CF_API}${endpoint}" "${AUTH[@]}"
  fi
}

check_cloudflared() {
  if command -v cloudflared &>/dev/null; then
    echo "✓ cloudflared is installed: $(cloudflared --version)"
    return 0
  else
    echo "✗ cloudflared is not installed"
    return 1
  fi
}

install_cloudflared() {
  echo "Installing cloudflared..."

  sudo mkdir -p --mode=0755 /usr/share/keyrings
  curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
  echo 'deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main' | sudo tee /etc/apt/sources.list.d/cloudflared.list
  sudo apt-get update && sudo apt-get install -y cloudflared
  
  echo "✓ cloudflared installed successfully"
}

check_user_config() {
  local config_valid=true
  
  if [[ "$ACCOUNT_ID" == "YOUR_ACCOUNT_ID_HERE" ]]; then
    echo "✗ ACCOUNT_ID is not configured"
    config_valid=false
  fi  
  if [[ "$ZONE_ID" == "YOUR_ZONE_ID_HERE" ]]; then
    echo "✗ ZONE_ID is not configured"
    config_valid=false
  fi
  if [[ "$API_TOKEN" == "YOUR_API_TOKEN_HERE" ]]; then
    echo "✗ API_TOKEN is not configured"
    config_valid=false
  fi
  if [[ "$TUNNEL_NAME" == "YOUR_TUNNEL_NAME_HERE" ]]; then
    echo "✗ TUNNEL_NAME is not configured"
    config_valid=false
  fi

  if [[ "$DOMAIN" == "YOUR_DOMAIN.TLD" ]]; then
    echo "✗ DOMAIN is not configured"
    config_valid=false
  fi
  
  if [[ "$config_valid" == false ]]; then
    echo ""
    echo "Please update the USER CONFIG section at the top of this script with your Cloudflare credentials."
    return 1
  fi
  
  echo "✓ User configuration is set"
  return 0
}

validate_api_token() {
  echo "Validating API token with Cloudflare..."
  
  local response
  response=$(cf_api_request GET "/user/tokens/verify")
  
  local success
  local status
  success=$(echo "$response" | grep -o '"success":[^,]*' | cut -d':' -f2)
  status=$(echo "$response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
  
  if [[ "$success" == "true" && "$status" == "active" ]]; then
    echo "✓ API token is valid and active"
    return 0
  else
    echo "✗ API token validation failed"
    echo "Response: $response"
    return 1
  fi
}

get_tunnel_by_name() {
  local response
  response=$(cf_api_request GET "/accounts/${ACCOUNT_ID}/cfd_tunnel?name=${TUNNEL_NAME}&is_deleted=false")
  
  local success
  success=$(echo "$response" | grep -o '"success":[^,]*' | cut -d':' -f2)
  
  if [[ "$success" != "true" ]]; then
    echo ""
    return 1
  fi
  
  local tunnel_id
  tunnel_id=$(echo "$response" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
  
  echo "$tunnel_id"
}

create_tunnel() {
  echo "Creating tunnel '${TUNNEL_NAME}'..."
  
  local tunnel_secret
  tunnel_secret=$(openssl rand -base64 32)
  
  local response
  response=$(cf_api_request POST "/accounts/${ACCOUNT_ID}/cfd_tunnel" \
    "{\"name\":\"${TUNNEL_NAME}\",\"config_src\":\"cloudflare\",\"tunnel_secret\":\"${tunnel_secret}\"}")
  
  local success
  success=$(echo "$response" | grep -o '"success":[^,]*' | cut -d':' -f2)
  
  if [[ "$success" == "true" ]]; then
    local tunnel_id
    tunnel_id=$(echo "$response" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "✓ Tunnel created successfully (ID: $tunnel_id)"
    echo "$tunnel_id"
    return 0
  else
    echo "✗ Failed to create tunnel"
    echo "Response: $response"
    return 1
  fi
}

# Check tunnel exists or create it
ensure_tunnel_exists() {
  echo "Checking for tunnel '${TUNNEL_NAME}'..."
  
  local tunnel_id
  tunnel_id=$(get_tunnel_by_name)
  
  if [[ -n "$tunnel_id" ]]; then
    echo "✓ Tunnel '${TUNNEL_NAME}' exists (ID: $tunnel_id)"
    TUNNEL_ID="$tunnel_id"
    return 0
  else
    echo "✗ Tunnel '${TUNNEL_NAME}' does not exist"
    read -p "Would you like to create it? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      tunnel_id=$(create_tunnel)
      if [[ -n "$tunnel_id" ]]; then
        echo "Waiting for Cloudflare to provision tunnel..."
        sleep 2
        TUNNEL_ID="$tunnel_id"
        USER_CREATED_TUNNEL="true"
        return 0
      fi
      return 1
    else
      echo "Exiting. Tunnel is required to continue."
      return 1
    fi
  fi
}

setup_tunnel() {
  if load_config && [[ -n "${SAVED_TUNNEL_ID:-}" ]]; then
    if [[ "${SKIP_TUNNEL_PROMPT:-}" == "true" ]]; then
      TUNNEL_ID="$SAVED_TUNNEL_ID"
      TUNNEL_TOKEN="$SAVED_TUNNEL_TOKEN"
      echo "✓ Using saved tunnel configuration (Tunnel ID: $TUNNEL_ID)"
      return 0
    fi
    
    echo "Found existing tunnel configuration:"
    echo "  Tunnel Name: $SAVED_TUNNEL_NAME"
    echo "  Tunnel ID: $SAVED_TUNNEL_ID"
    echo ""
    read -p "Use this tunnel? [Y/n] " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
      TUNNEL_ID="$SAVED_TUNNEL_ID"
      TUNNEL_TOKEN="$SAVED_TUNNEL_TOKEN"
      SKIP_TUNNEL_PROMPT="true"
      save_config
      echo "✓ Using saved tunnel configuration"
      return 0
    fi
  fi
  
  if ! ensure_tunnel_exists; then
    return 1
  fi
  if ! get_tunnel_token; then
    return 1
  fi
  save_config
  return 0
}

get_tunnel_token() {
  echo "Fetching tunnel token..."
  
  local response
  response=$(cf_api_request GET "/accounts/${ACCOUNT_ID}/cfd_tunnel/${TUNNEL_ID}/token")
  
  local success
  success=$(echo "$response" | grep -o '"success":[^,]*' | cut -d':' -f2)
  
  if [[ "$success" == "true" ]]; then
    local token
    token=$(echo "$response" | grep -o '"result":"[^"]*"' | cut -d'"' -f4)
    echo "✓ Tunnel token retrieved"
    TUNNEL_TOKEN="$token"
    return 0
  else
    echo "✗ Failed to get tunnel token"
    echo "Response: $response"
    return 1
  fi
}

install_tunnel_service() {
  echo "Installing cloudflared as a system service..."
  
  set +e
  local install_output
  install_output=$(sudo cloudflared service install "$TUNNEL_TOKEN" 2>&1)
  local install_result=$?
  set -e
  
  if [[ $install_result -ne 0 ]]; then
    echo "$install_output"
    echo ""
    echo "⚠ A tunnel service is already configured on this device."
    read -p "Would you like to replace it with the new tunnel? [y/N] " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      echo "Uninstalling existing cloudflared service..."
      sudo cloudflared service uninstall
      echo "Reinstalling cloudflared service..."
      sudo cloudflared service install "$TUNNEL_TOKEN"
      USER_CREATED_TUNNEL="true"
      SKIP_TUNNEL_PROMPT="true"
      save_config
      echo "✓ Cloudflared service reinstalled successfully"
      return 0
    else
      echo "✓ Keeping existing tunnel service."
      SKIP_TUNNEL_PROMPT="true"
      save_config
      return 0
    fi
  else
    echo "$install_output"
    echo "✓ Cloudflared service installed successfully"
    SKIP_TUNNEL_PROMPT="true"
    save_config
    return 0
  fi
}

# Configure tunnel with ingress rules
configure_tunnel_ingress() {
  echo "Configuring tunnel ingress rules..."
  
  # Build ingress JSON array
  local ingress_json="["
  local first=true
  
  for rule in "${INGRESS_RULES[@]}"; do
    local subdomain="${rule%%=*}"
    local service="${rule#*=}"
    local hostname="${subdomain}.${DOMAIN}"
    
    if [[ "$first" == true ]]; then
      first=false
    else
      ingress_json+=","
    fi
    
    ingress_json+="{\"hostname\":\"${hostname}\",\"service\":\"${service}\"}"
  done
  
  # Add catch-all rule (required)
  ingress_json+=",{\"service\":\"http_status:404\"}"
  ingress_json+="]"
  
  local config_data="{\"config\":{\"ingress\":${ingress_json}}}"
  
  local response
  response=$(cf_api_request PUT "/accounts/${ACCOUNT_ID}/cfd_tunnel/${TUNNEL_ID}/configurations" "$config_data")
  
  local success
  success=$(echo "$response" | grep -o '"success":[^,]*' | cut -d':' -f2)
  
  if [[ "$success" == "true" ]]; then
    echo "✓ Tunnel ingress rules configured"
    return 0
  else
    echo "✗ Failed to configure tunnel ingress"
    echo "Response: $response"
    return 1
  fi
}

# Create DNS CNAME record for a subdomain pointing to the tunnel
create_dns_record() {
  local subdomain="$1"
  local hostname="${subdomain}.${DOMAIN}"
  local tunnel_target="${TUNNEL_ID}.cfargotunnel.com"
  
  # Check if record already exists
  local check_response
  check_response=$(cf_api_request GET "/zones/${ZONE_ID}/dns_records?type=CNAME&name=${hostname}")
  
  local existing_id
  existing_id=$(echo "$check_response" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
  
  local response
  if [[ -n "$existing_id" ]]; then
    # Update existing record
    response=$(cf_api_request PUT "/zones/${ZONE_ID}/dns_records/${existing_id}" \
      "{\"type\":\"CNAME\",\"name\":\"${hostname}\",\"content\":\"${tunnel_target}\",\"proxied\":true}")
  else
    # Create new record
    response=$(cf_api_request POST "/zones/${ZONE_ID}/dns_records" \
      "{\"type\":\"CNAME\",\"name\":\"${hostname}\",\"content\":\"${tunnel_target}\",\"proxied\":true}")
  fi
  
  local success
  success=$(echo "$response" | grep -o '"success":[^,]*' | cut -d':' -f2)
  
  if [[ "$success" == "true" ]]; then
    echo "✓ DNS record configured: ${hostname} -> ${tunnel_target}"
    return 0
  else
    echo "✗ Failed to configure DNS for ${hostname}"
    echo "Response: $response"
    return 1
  fi
}

# Configure all DNS records for ingress rules
configure_dns_records() {
  echo "Configuring DNS records..."
  
  local all_success=true
  
  for rule in "${INGRESS_RULES[@]}"; do
    local subdomain="${rule%%=*}"
    if ! create_dns_record "$subdomain"; then
      all_success=false
    fi
  done
  
  if [[ "$all_success" == true ]]; then
    echo "✓ All DNS records configured"
    return 0
  else
    echo "⚠ Some DNS records failed to configure"
    return 1
  fi
}

# Inject test ingress rule if enabled.
# Reads the subdomain and full service URL from TEST_ROUTE rather than
# using hardcoded values, so changing TEST_ROUTE at the top is sufficient.
inject_test_ingress() {
  if [[ "${ENABLE_TEST_INGRESS}" == "true" ]]; then
    # Skip injection if the exact TEST_ROUTE entry is already present
    local found=false
    for rule in "${INGRESS_RULES[@]}"; do
      if [[ "$rule" == "$TEST_ROUTE" ]]; then
        found=true
        break
      fi
    done

    if [[ "$found" == false ]]; then
      INGRESS_RULES+=("$TEST_ROUTE")
    fi
  fi
}

# Run test FastAPI app if enabled.
# The port is parsed from TEST_ROUTE so it always matches the registered ingress rule.
run_test_ingress() {
  if [[ "${ENABLE_TEST_INGRESS}" == "true" ]]; then
    # Parse the port from TEST_ROUTE (format: "subdomain=protocol://host:port")
    # We strip everything up to the last ':' to get the port number.
    local test_service="${TEST_ROUTE#*=}"          # e.g. http://localhost:12355
    local test_port="${test_service##*:}"           # e.g. 12355

    # Install uv from astral if not present
    if ! command -v uv &>/dev/null; then
      echo "Installing uv from astral..."
      curl -Ls https://astral.sh/uv/install.sh | bash
      export PATH="$HOME/.local/bin:$PATH"
    fi

    # Generate test.py using the port derived from TEST_ROUTE.
    # Regenerated every run so the file always reflects the current config.
    cat > test.py << EOF
# /// script
# requires-python = ">=3.12"
# dependencies = [
#  "fastapi",
#  "uvicorn",
# ]
# ///
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
def health():
    return JSONResponse({"status": "ok"})

if __name__ == "__main__":
    import uvicorn
    # Port is set from TEST_ROUTE in setup_tunnel.sh (currently: ${test_port})
    uvicorn.run("test:app", host="0.0.0.0", port=${test_port})
EOF

    # Run the test server
    echo "Running test.py with uv on port ${test_port}..."
    uv run test.py
  fi
}

# ================= CODE FLOW =================


if ! check_cloudflared; then
  read -p "Would you like to install cloudflared? [y/N] " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    install_cloudflared
  else
    echo "Exiting. cloudflared is required to continue."
    exit 1
  fi
fi

if ! check_user_config; then
  exit 1
fi

if ! validate_api_token; then 
  exit 1
fi

if ! setup_tunnel; then
  exit 1
fi

echo ""
echo "Tunnel ID: $TUNNEL_ID"
echo ""


if [[ "${SKIP_TUNNEL_PROMPT:-}" != "true" ]]; then
  install_tunnel_service
else
  echo "✓ Using existing tunnel service"
fi

inject_test_ingress

if ! configure_tunnel_ingress; then
  echo "⚠ Tunnel ingress configuration failed"
  exit 1
fi

if ! configure_dns_records; then
  echo "⚠ DNS configuration had issues"
  exit 1
fi

echo ""
echo "✓ Tunnel setup complete!"
echo "Your services are available at:"
for rule in "${INGRESS_RULES[@]}"; do
  subdomain="${rule%%=*}"
  echo "  https://${subdomain}.${DOMAIN}"
done

run_test_ingress
