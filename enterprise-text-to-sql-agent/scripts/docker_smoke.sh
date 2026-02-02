#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="text2sql-agent"
CONTAINER_NAME="text2sql-agent-smoke"
BASE_URL="http://127.0.0.1:8000"
METRIC_REGEX="text2sql_requests_total|text2sql_cache_hits_total"

cleanup() {
  if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
  fi
}

fail() {
  echo "Smoke test failed. Container logs:"
  docker logs "${CONTAINER_NAME}" || true
  exit 1
}

retry_request() {
  local method="$1"
  local url="$2"
  local data="${3:-}"
  local check_regex="${4:-}"
  local attempts=10
  local delay=1
  local body_file
  local err_file
  local status=""
  local curl_exit=0
  local last_error=""

  body_file=$(mktemp)
  err_file=$(mktemp)
  trap 'rm -f "${body_file}" "${err_file}"' RETURN

  for _ in $(seq 1 "${attempts}"); do
    curl_exit=0
    status=""
    : >"${body_file}"
    : >"${err_file}"
    if [[ "${method}" == "POST" ]]; then
      status=$(curl -s -o "${body_file}" -w "%{http_code}" \
        -H "Content-Type: application/json" -d "${data}" "${url}" 2>"${err_file}") \
        || curl_exit=$?
    else
      status=$(curl -s -o "${body_file}" -w "%{http_code}" \
        "${url}" 2>"${err_file}") || curl_exit=$?
    fi

    if [[ ${curl_exit} -eq 0 && "${status}" =~ ^2 ]]; then
      curl_exit=0
      if [[ -n "${check_regex}" ]]; then
        if grep -Eq "${check_regex}" "${body_file}"; then
          cat "${body_file}"
          return 0
        fi
      else
        cat "${body_file}"
        return 0
      fi
    fi

    if [[ -s "${err_file}" ]]; then
      last_error=$(tail -n 20 "${err_file}")
    else
      last_error="HTTP ${status}"
    fi

    sleep "${delay}"
    if (( delay < 5 )); then
      delay=$((delay * 2))
    fi
  done

  echo "Request failed: ${method} ${url}"
  echo "Last status: ${status:-none}"
  echo "Last error: ${last_error:-none}"
  echo "Last body:"
  head -c 200 "${body_file}" || true
  fail
}

trap cleanup EXIT

docker build -t "${IMAGE_NAME}" .
docker run -d --name "${CONTAINER_NAME}" -p 8000:8000 "${IMAGE_NAME}" >/dev/null

retry_request "GET" "${BASE_URL}/healthz" >/dev/null
retry_request "GET" "${BASE_URL}/metrics" "" "${METRIC_REGEX}" >/dev/null
retry_request "POST" "${BASE_URL}/ask" \
  '{"question":"order fill rate last 30 days","scope":"default"}' \
  '"outcome_type".*("result"|"sql"|"message")' >/dev/null

echo "Docker smoke passed."
