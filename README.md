## TLS/SSL Certificate Generator

These certificates are self-signed and supposed to be used for development.

The project is extracted from the [rabbitmq-test](http://hg.rabbitmq.com/rabbitmq-test/file/4bb389276318/certs) toolchain.

## Generation

    cd [path to tls-gen repository]
    PASSWORD=bunnies make
    ls -lha ./result

Generated CA certificate as well as client and server certificate and private keys will be
under the `result` directory.


## License

Mozilla Public License, see `LICENSE`.
