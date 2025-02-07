- Use ttyd

We use a nginx reverse proxy on port 7681 which authenticates using a bash script nd once authenticates connects with the ttyd.sock

`/etc/nginx/sites-available/default`
```
server {
    listen 7681;

    location /auth {
        internal;
        include fastcgi_params;
        fastcgi_pass unix:/var/run/fcgiwrap.socket;
        fastcgi_param SCRIPT_FILENAME /usr/local/bin/auth_script.sh;
        fastcgi_param QUERY_STRING $query_string;
    }

    location / {
        auth_request /auth;
        auth_request_set $auth_status $upstream_status;
        error_page 401 = @error401;

        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_pass http://unix:/run/ttyd.sock;
        proxy_set_header X-Original-URI $request_uri;  # Pass original URI with query string
    }

    location @error401 {
        return 401 "Unauthorized";
    }
}
```

`/usr/local/bin/auth_script.sh`
```
#!/bin/bash
env > /tmp/env_variables.log
# Path to the authentication log (for debugging purposes)
LOG_FILE="/tmp/auth_script.log"

# Read the request URI from QUERY_STRING
QUERY_STRING=$(echo "$REQUEST_URI")
echo "$(date) - Query String: '$QUERY_STRING'" >> $LOG_FILE

# Function to send a HTTP request to the local server with JWT token header
send_request() {
  local jwt_token="$1"
  local response=$(curl -s -o /dev/null -w "%{http_code}" \
                  -H "Authorization: Bearer $jwt_token" \
                  http://127.0.0.1:8000/api/allow_terminal)
  echo "$response"
}

# Check if the request is for /ws and extract jwt_token
if [[ $QUERY_STRING == */ws* ]]; then
  # Extract JWT token from QUERY_STRING
  jwt_token=$(echo "$QUERY_STRING" | grep -oP '(?<=jwt_token=)[^& ]+')

  if [[ -n "$jwt_token" ]]; then
    # Send request to the local server with JWT token
    response_code=$(send_request "$jwt_token")

    if [[ "$response_code" == "200" ]]; then
      echo "$(date) - AUTHENTICATED" >> $LOG_FILE
      echo "Status: 200 OK"
      echo "Content-Type: text/plain"
      echo ""
      echo "User authenticated successfully"
    else
      echo "$(date) - NOT AUTHENTICATED" >> $LOG_FILE
      echo "Status: 401 Unauthorized"
      echo "Content-Type: text/plain"
      echo ""
      echo "Unauthorized"
    fi
  else
    # No jwt_token found, deny access
    echo "$(date) - NOT AUTHENTICATED - NO JWT TOKEN PRESENT" >> $LOG_FILE
    echo "Status: 401 Unauthorized"
    echo "Content-Type: text/plain"
    echo ""
    echo "Unauthorized"
  fi
else
  # Allow access for requests other than /ws without authentication
  echo "Status: 200 OK"
  echo "Content-Type: text/plain"
  echo ""
  echo "Access granted (no authentication required)"
fi
```
