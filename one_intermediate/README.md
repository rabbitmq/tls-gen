# Chained (With One Intermediate) Certificates

This tls-gen variation generates a root CA, one intermediary CA and four
certificate/key pairs:

 * Chain 1: root CA => intermediate 1 => client certificate/key pair
 * Chain 2: root CA => intermediate 1 => server certificate/key pair
 * Chain 3: root CA => client_direct certificate/key pair (no intermediate)
 * Chain 4: root CA => server_direct certificate/key pair (no intermediate)

## Certificate Chain Structure

```
Root CA
    │
    ├─→ Intermediate CA
    │       │
    │       ├─→ server_certificate.pem
    │       └─→ client_certificate.pem
    │
    ├─→ server_direct_certificate.pem
    └─→ client_direct_certificate.pem
```

All certificates share the same root CA, allowing you to test both intermediate
and direct certificate chains with a single trusted root.

## Generating

``` shell
# pass a password using the PASSWORD env variable
make
# results will be under the ./result directory
ls -lha ./result
```

Generated CA certificates as well as four certificate/key pairs (server, client,
server_direct, and client_direct) will be under the `result` directory.

It is possible to use [ECC][ecc-intro] for intermediate and leaf keys:

```
# pass a private key password using the PASSWORD variable if needed
make USE_ECC=true ECC_CURVE="prime256v1"
# results will be under the ./result directory
ls -lha ./result
```

The list of available curves can be obtained with

``` shell
openssl ecparam -list_curves
```

### Regeneration

To regenerate, use

``` shell
# pass a private key password using the PASSWORD variable if needed
make regen
```

The `regen` target accepts the same variables as `gen` (default target) above.

### Verification

You can verify the generated certificates against the CA chain with

``` shell
make verify
```

This verifies the intermediate-signed certificates (server and client) against
the full CA chain. The direct certificates (server_direct and client_direct)
can be verified directly against the root CA.

## Certificate Information

To display certificate information for all generated certificates, use

``` shell
make info
```

This assumes the certificates were previously generated.
