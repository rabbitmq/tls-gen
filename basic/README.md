# Basic ("Leaf") Certificates

This tls-gen variation generates a root CA
and two certificate/key pairs signed by it:

 * Chain 1: root CA => client certificate/key pair
 * Chain 2: root CA => server certificate/key pair

## Generating

    # pass a password using the PASSWORD env variable
    make PASSWORD=bunnies
    # results will be under the ./result directory
    ls -lha ./result

Generated CA certificate as well as client and server certificate and private keys will be
under the `result` directory.

### Regeneration

To regenerate, use

    make regen PASSWORD=bunnies

### Verification

You can verify the generated client and server certificates against the generated CA one with

    make verify

## Certificate Information

To display client and server certificate information, use

    make info

This assumes the certificates were previously generated.
