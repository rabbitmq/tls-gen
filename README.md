## TLS/SSL Certificate Generator

These certificates are self-signed and supposed to be used for development.

The project is extracted from the [rabbitmq-test](http://hg.rabbitmq.com/rabbitmq-test/file/4bb389276318/certs) toolchain.

## Generation

    cd [path to tls-gen repository]
    # pass a password using the PASSWORD env variable
    PASSWORD=bunnies make
    # results will be under the ./result directory
    ls -lha ./result

Generated CA certificate as well as client and server certificate and private keys will be
under the `result` directory.

## Verification

You can verify the generated client and server certificates against the generated CA one with

    make verify

## Overriding CN (Common Name)

By default, certificate's CN ([Common Name](http://tldp.org/HOWTO/Apache-WebDAV-LDAP-HOWTO/glossary.html)) is calculated using `hostname`.

It is possible to override CN with an environment variable:

    CN=secure.mydomain.local PASSWORD=bunnies make


## License

Mozilla Public License, see `LICENSE`.


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/ruby-amqp/tls-gen/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

