## TLS/SSL Certificate Generator

These certificates are self-signed and supposed to be used for development.

The project is extracted from a number of RabbitMQ test suites.


## What It Does

`tls-gen` generates a self-signed Certificate Authority (CA) certificate
and 2 pairs of keys: client and server, with a single command.
It can also generate a chain of CA certificates.

Use these certificates in development and QA environments. They are self-signed and not intended to be used
in production.


## Prerequisites

`tls-gen` requires

 * `openssl`
 * Python 3 in `PATH` as `python3` (Python 2.7 is *not* and will not be supported)
 * `make`



## Usage

Certificate authorities (CAs) and certificates can form chains. tls-gen provides
different "profiles", for example:

 * [Profile 1](./basic/): a root CA with leaf certificate/key pairs signed by it
 * [Profile 2](./two_shared_intermediates/): a root CA with multiple shared intermediary certificates and leaf pairs signed by the intermediaries
 * [Profile 3](./separate_intermediates/): a root CA with two intermediary certificates (one for server, one for client) and leaf pairs signed by the intermediaries

Each profile has a sub-directory in repository root. All profiles use
the same `make` targets and directory layouts that are as close as possible.

### Profile 1 (Basic Profile)

To generate a CA, client and server private key/certificate pairs, run
`make` from the [basic](./basic) profile directory with `PASSWORD` environment variable
providing the passphrase:

    cd [path to tls-gen repository]/basic
    # pass a password using the PASSWORD variable
    make PASSWORD=bunnies
    # results will be under the ./result directory
    ls -lha ./result

Generated CA certificate as well as client and server certificate and private keys will be
under the `result` directory.


### Profile 2 (Shared Chained Certificates)

To generate a root CA, 2 shared intermediate CAs, client and server key/certificate pairs, run `make` from
the [two_shared_intermediates](./two_shared_intermediates) directory:

    make PASSWORD=bunnies
    # results will be under the ./result directory
    ls -lha ./result

### Profile 3 (Separate Certificate Chains)

To generate a root CA, 2 intermediate CAs (one for server, one for client), client and server key/certificate pairs, run `make` from
the [separate_intermediates](./separate_intermediates) directory:

    make PASSWORD=bunnies
    # results will be under the ./result directory
    ls -lha ./result


### Regeneration

To generate a new set of keys and certificates, use

    make regen PASSWORD=bunnies

### Verification

You can verify the generated client and server certificates against the generated CA one with

    make verify

### Overriding CN (Common Name)

By default, certificate's CN ([Common Name](http://tldp.org/HOWTO/Apache-WebDAV-LDAP-HOWTO/glossary.html)) is calculated using `hostname`.

It is possible to override CN with an environment variable:

    make PASSWORD=bunnies CN=secure.mydomain.local


### Certificate Information

To display information about generated certificates, use

    make info

This assumes the certificates were previously generated.

## License

Mozilla Public License, see `LICENSE`.
