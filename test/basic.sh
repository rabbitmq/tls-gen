#!/usr/bin/env bash

set -o nounset

# shellcheck disable=SC2155
declare -r repo_dir="$(cd "$(dirname "$0")"/.. && pwd)"
declare -r tmp_dir="$repo_dir/tmp"
declare -r basic_dir="$repo_dir/basic"
declare -r basic_certs_dir="$basic_dir/result"
declare -r test_string="TEST_$$_$RANDOM"
declare -i server_pid=0

mkdir "$tmp_dir" > /dev/null 2>&1

function on_exit
{
    set +o errexit
    if kill -0 "$server_pid"
    then
        printf '[INFO] killing openssl server with pid %d\n' "$server_pid"
        kill "$server_pid"
    fi
    printf '[INFO] exiting\n'
}

trap on_exit EXIT

set -o errexit

make -C "$basic_dir" clean
make -C "$basic_dir" CN=localhost

echo "$test_string" | openssl s_server -quiet -cert "$basic_certs_dir/server_localhost_certificate.pem" -key "$basic_certs_dir/server_localhost_key.pem" -CAfile "$basic_certs_dir/ca_certificate.pem" > "$tmp_dir/server.log" 2>&1 &
server_pid="$!"

sleep 1

openssl s_client -quiet -cert "$basic_certs_dir/client_localhost_certificate.pem" -key "$basic_certs_dir/client_localhost_key.pem" -CAfile "$basic_certs_dir/ca_certificate.pem" -verify 4 -verify_return_error > "$tmp_dir/client.log" 2>&1

grep -Fq "$test_string" "$tmp_dir/client.log"
