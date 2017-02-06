# Chained (With Shared Intermediates) Certificates

This tls-gen variation generates a root CA,
two intermediary CAs and two certificate/key pairs signed by
the 2nd intermediate CA:

 * Chain 1: root CA => intermediate 1 => intermediate 2 => client certificate/key pair
 * Chain 2: root CA => intermediate 1 => intermediate 2 => server certificate/key pair

## Generating

    # pass a password using the PASSWORD env variable
    PASSWORD=bunnies make
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
