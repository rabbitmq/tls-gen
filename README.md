## Development TLS Certificates

These certificates are supposed to be used by the test suite,
are self-signed and imported to `keytool` using a script under `./bin`.

They are generated using the [rabbitmq-test](http://hg.rabbitmq.com/rabbitmq-test/file/4bb389276318/certs) toolchain.

## Generation

    cd test/resources/tls
    PASSWORD=bunnies make
