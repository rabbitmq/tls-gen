# Chained (With One Intermediate) Certificates

This tls-gen variation generates a root CA, one intermediary CA and two
certificate/key pairs signed by the intermediate CA:

 * Chain 1: root CA => intermediate 1 => client certificate/key pair
 * Chain 2: root CA => intermediate 1 => server certificate/key pair

## Generating

``` shell
# pass a password using the PASSWORD env variable
make
# results will be under the ./result directory
ls -lha ./result
```

Generated CA certificate as well as client and server certificate and private keys will be
under the `result` directory.

It possible to use [ECC][ecc-intro] for intermediate and leaf keys:

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

You can verify the generated client and server certificates against the generated CA one with

``` shell
make verify
```

## Certificate Information

To display client and server certificate information, use

``` shell
make info
```

This assumes the certificates were previously generated.
