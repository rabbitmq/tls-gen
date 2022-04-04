# Basic ("Leaf") Certificates

This tls-gen variation generates a root CA
and two certificate/key pairs signed by it:

 * Chain 1: root CA => client certificate/key pair
 * Chain 2: root CA => server certificate/key pair

## Generating

```shell
# pass a private key password using the PASSWORD variable if needed
make
# results will be under the ./result directory
ls -lha ./result
```

Generated CA certificate as well as client and server certificate and private keys will be
under the `result` directory.

It possible to use [ECC](https://blog.cloudflare.com/a-relatively-easy-to-understand-primer-on-elliptic-curve-cryptography/) for leaf keys:

```shell
cd [path to tls-gen repository]/basic
# pass a password using the PASSWORD variable
make USE_ECC=true ECC_CURVE="prime256v1"
# results will be under the ./result directory
ls -lha ./result
```

The list of available curves can be obtained with

```shell
openssl ecparam -list_curves
```

### Generate additional server certificate

If you want to generate additional server certificates using the same Root CA, use:

```shell
make CN=newname gen-server
```

### Generate additional client certificate

If you want to generate additional client certificates using the same Root CA, use:

```shell
make CN=newname gen-client
```

### Regeneration

To regenerate, use

```shell
make regen
```

The `regen` target accepts the same variables as `gen` (default target) above.

### Verification

You can verify the generated client and server certificates against the generated CA one with

```shell
make verify
```

## Certificate Information

To display client and server certificate information, use

```shell
make info
```

This assumes the certificates were previously generated.

## CRL

The Root CA creates certificates whose CRL distribution point is `http://localhost:8000/basic.crl`. To make this CRL available, Python 3 can be used:

```
cd result
python -m http.server
```

If you need to test revoking a certificate do the following from the `basic` directory:

```
openssl ca -config openssl.cnf -revoke ./result/server_MY-CN_certificate.pem -keyfile ./testca/private/cakey.pem -cert ./testca/cacert.pem
```

Then regenerate the CRL file:

```
make gen-crl
```
