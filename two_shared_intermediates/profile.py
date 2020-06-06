#!/usr/bin/env python3

import sys
import os
import shutil
from subprocess import call

def _copy_artifacts_to_results():
    os.makedirs(paths.relative_path("result"), exist_ok = True)

    gen.copy_root_ca_certificate_and_key_pair()
    gen.copy_leaf_certificate_and_key_pair("server")
    gen.copy_leaf_certificate_and_key_pair("client")

def _concat_certificates():
    # concat [intermediate CA 2] [intermediate CA 1] [root CA] > full_chain
    print("Will concatenate all CA certificates into {}".format(paths.result_chained_certificate_path()))
    chain_file = open(paths.result_chained_certificate_path(), "w")
    call(["cat",
          paths.intermediate_ca_certificate_path("2"),
          paths.intermediate_ca_certificate_path("1"),
          paths.root_ca_certificate_path()],
         stdout = chain_file)
    chain_file.close

def generate(opts):
    cli.validate_password_if_provided(opts)
    print("Will generate a root CA and two certificate/key pairs (server and client)")
    gen.generate_root_ca(opts)
    print("Will generate first intermediate CA signed by the root CA")
    gen.generate_intermediate_ca(opts,
                                 parent_certificate_path = paths.root_ca_certificate_path(),
                                 parent_key_path         = paths.root_ca_key_path(),
                                 suffix = "1")
    print("Will generate first intermediate CA signed by the root CA")
    gen.generate_intermediate_ca(opts,
                                 parent_certificate_path = paths.intermediate_ca_certificate_path("1"),
                                 parent_key_path         = paths.intermediate_ca_key_path("1"),
                                 suffix = "2")
    print("Will generate server certificate/key pair signed by the second CA")
    gen.generate_server_certificate_and_key_pair(opts,
                                                 parent_certificate_path = paths.intermediate_ca_certificate_path("2"),
                                                 parent_key_path         = paths.intermediate_ca_key_path("2"))
    print("Will generate client certificate/key pair signed by the second CA")
    gen.generate_client_certificate_and_key_pair(opts,
                                                 parent_certificate_path = paths.intermediate_ca_certificate_path("2"),
                                                 parent_key_path         = paths.intermediate_ca_key_path("2"))
    _copy_artifacts_to_results()
    _concat_certificates()    
    print("Done! Find generated certificates and private keys under ./result!")

def clean(opts):
    for s in [paths.root_ca_path(),
              paths.intermediate_ca_path("1"),
              paths.intermediate_ca_path("2"),
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
    print("Will verify generated certificates against the CA certificate chain...")
    verify.verify_leaf_certificate_against_ca_chain("client")
    verify.verify_leaf_certificate_against_ca_chain("server")

def info(opts):
    info.leaf_certificate_info("client")
    info.leaf_certificate_info("server")

commands = {"generate":   generate,
            "gen":        generate,
            "clean":      clean,
            "regenerate": regenerate,
            "regen":      regenerate,
            "verify":     verify,
            "info":       info}

if __name__ == "__main__":
    sys.path.append("..")
    from tls_gen import cli
    from tls_gen import gen
    from tls_gen import paths
    from tls_gen import verify
    from tls_gen import info

    cli.run(commands)
