#!/usr/bin/env python3

import sys
import os
import shutil

def _copy_artifacts_to_results():
    os.makedirs(paths.relative_path("result"), exist_ok = True)
    gen.copy_root_ca_certificate_and_key_pair()
    gen.copy_leaf_certificate_and_key_pair("server")
    gen.copy_leaf_certificate_and_key_pair("client")

def generate(opts):
    cli.validate_password_if_provided(opts)
    print("Will generate a root CA and two certificate/key pairs (server and client)")
    gen.generate_root_ca(opts)
    gen.generate_server_certificate_and_key_pair(opts)
    gen.generate_client_certificate_and_key_pair(opts)
    _copy_artifacts_to_results()
    print("Done! Find generated certificates and private keys under ./result!")

def clean(opts):
    for s in [paths.root_ca_path(),
              paths.result_path(),
              paths.leaf_pair_path("server"),
              paths.leaf_pair_path("client")]:
        print("Removing {}".format(s))
        try:
            shutil.rmtree(s)
        except FileNotFoundError:
            pass

def regenerate(opts):
    clean(opts)
    generate(opts)

def verify(opts):
    print("Will verify generated certificates against the CA...")
    verify.verify_leaf_certificate_against_root_ca("client")
    verify.verify_leaf_certificate_against_root_ca("server")

def verify_pkcs12(opts):
    cli.validate_password_if_provided(opts)
    print("Will verify generated PKCS12 certificate stores...")
    verify.verify_pkcs12_store("client", opts)
    verify.verify_pkcs12_store("server", opts)

def info(opts):
    info.leaf_certificate_info("client")
    info.leaf_certificate_info("server")

commands = {"generate":   generate,
            "gen":        generate,
            "clean":      clean,
            "regenerate": regenerate,
            "regen":      regenerate,
            "verify":     verify,
            "verify-pkcs12": verify_pkcs12,
            "info":       info}

if __name__ == "__main__":
    sys.path.append("..")
    from tls_gen import cli
    from tls_gen import gen
    from tls_gen import paths
    from tls_gen import verify
    from tls_gen import info

    cli.run(commands)
