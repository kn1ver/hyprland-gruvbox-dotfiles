#!/usr/bin/env bash

# CONFIG
API_KEY="$1"
CITY="$2"
UNITS="metric"
LANG="en"

CACHE_DIR="$HOME/.cache/openweather"
DATA_CACHE="$CACHE_DIR/weather.txt"
ICON_CACHE="$CACHE_DIR/icon.png"
TTL=1800   # 30 minutes

CURL="/usr/bin/curl"
JQ="/usr/bin/jq"

# INIT
mkdir -p "$CACHE_DIR"

# Check to cache expired
if [ -f "$DATA_CACHE" ]; then
    last_modified=$(stat -c %Y "$DATA_CACHE")
    now=$(date +%s)
    diff=$((now - last_modified))

    if [ "$diff" -lt "$TTL" ]; then
        cat "$DATA_CACHE"
        exit 0
    fi
fi

# API request
response=$($CURL -Ls "https://api.openweathermap.org/data/2.5/weather?q=${CITY}&appid=${API_KEY}&units=${UNITS}&lang=${LANG}")

code=$(echo "$response" | $JQ -r '.cod' 2>/dev/null)

if [ "$code" != "200" ]; then
    # fallback no response
    if [ -f "$DATA_CACHE" ]; then
        cat "$DATA_CACHE"
    else
        echo "--°C"
    fi
    exit 0
fi

# Parsing values
main=$(echo "$response" | $JQ -r '.weather[0].main')
icon_code=$(echo "$response" | $JQ -r '.weather[0].icon')
temp=$(echo "$response" | $JQ -r '.main.temp')
feels=$(echo "$response" | $JQ -r '.main.feels_like')
wind=$(echo "$response" | $JQ -r '.wind.speed')

# fallback if null values
if [ -z "$temp" ] || [ "$temp" = "null" ]; then
    echo "--°C"
    exit 0
fi


# Downloading PNG icon
if [ -n "$icon_code" ]; then
    $CURL -Ls -o "$ICON_CACHE" \
    "https://openweathermap.org/img/wn/${icon_code}@4x.png"
fi

# Output
NBSP=$'\u00A0'

temp_str="${temp}°C${NBSP}|${NBSP}${feels}°C"
wind_str="${wind}${NBSP}m/s"

output="${temp_str} ${wind_str} ${CITY}"

echo "$output" > "$DATA_CACHE"
echo "$output"
