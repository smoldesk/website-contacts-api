#!/usr/bin/env bash
# One lookup. Usage: RAPIDAPI_KEY=your_key ./curl.sh example.com [COUNTRY]
set -euo pipefail
domain="${1:?usage: ./curl.sh <domain> [country]}"
country="${2:-US}"
curl --silent --show-error --max-time 60 --get \
  --url "https://website-contacts-company-info.p.rapidapi.com/v1/contacts" \
  --data-urlencode "domain=${domain}" \
  --data-urlencode "country=${country}" \
  --header "x-rapidapi-host: website-contacts-company-info.p.rapidapi.com" \
  --header "x-rapidapi-key: ${RAPIDAPI_KEY:?set RAPIDAPI_KEY first}"
echo
