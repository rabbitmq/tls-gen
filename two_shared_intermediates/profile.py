#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2007-2014 VMware, Inc. or its affiliates. All rights reserved.
# Copyright (c) 2014-2020 Michael Klishin and contributors.
# Copyright (c) 2022 VMware, Inc. or its affiliates. All rights reserved.

import sys
import os
import shutil
from subprocess import call


def _copy_artifacts_to_results():
    os.makedirs(p.relative_path("result"), exist_ok=True)

    g.copy_root_ca_certificate_and_key_pair()
    g.copy_leaf_certificate_and_key_pair("server")
    g.copy_leaf_certificate_and_key_pair("client")


def _concat_certificates():
    # concat [intermediate CA 2] [intermediate CA 1] [root CA] > full_chain
    print("Will concatenate all CA certificates into {}".format(p.result_chained_certificate_path()))
    chain_file = open(p.result_chained_certificate_path(), "w")
    call(["cat",
          p.intermediate_ca_certificate_path("2"),
          p.intermediate_ca_certificate_path("1"),
          p.root_ca_certificate_path()],
         stdout=chain_file)
    chain_file.close()


def generate(opts):
    cli.validate_password_if_provided(opts)
    print("Will generate a root CA and two certificate/key pairs (server and client)")
    g.generate_root_ca(opts)
    print("Will generate first intermediate CA signed by the root CA")
    g.generate_intermediate_ca(opts,
                               parent_certificate_path=p.root_ca_certificate_path(),
                               parent_key_path=p.root_ca_key_path(),
                               suffix="1")
    print("Will generate first intermediate CA signed by the root CA")
    g.generate_intermediate_ca(opts,
                               parent_certificate_path=p.intermediate_ca_certificate_path("1"),
                               parent_key_path=p.intermediate_ca_key_path("1"),
                               suffix="2")
    print("Will generate server certificate/key pair signed by the second CA")
    g.generate_server_certificate_and_key_pair(opts,
                                               parent_certificate_path=p.intermediate_ca_certificate_path("2"),
                                               parent_key_path=p.intermediate_ca_key_path("2"))
    print("Will generate client certificate/key pair signed by the second CA")
    g.generate_client_certificate_and_key_pair(opts,
                                               parent_certificate_path=p.intermediate_ca_certificate_path("2"),
                                               parent_key_path=p.intermediate_ca_key_path("2"))
    _copy_artifacts_to_results()
    _concat_certificates()
    print("Done! Find generated certificates and private keys under ./result!")


def clean(opts):
    for s in [p.root_ca_path(),
              p.intermediate_ca_path("1"),
              p.intermediate_ca_path("2"),
              p.result_path(),
              p.leaf_pair_path("server"),
              p.leaf_pair_path("client")]:
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
    v.verify_leaf_certificate_against_ca_chain("client")
    v.verify_leaf_certificate_against_ca_chain("server")


def info(opts):
    i.leaf_certificate_info("client")
    i.leaf_certificate_info("server")


def alias_leaf_artifacts(opts):
    print("This command is not supported by this profile")


commands = {"generate":   generate,
            "gen":        generate,
            "clean":      clean,
            "regenerate": regenerate,
            "regen":      regenerate,
            "verify":     verify,
            "info":       info,
            "alias-leaf-artifacts": alias_leaf_artifacts}

if __name__ == "__main__":
    sys.path.append(os.path.realpath('..'))
    import tls_gen.cli as cli
    import tls_gen.gen as g
    import tls_gen.info as i
    import tls_gen.paths as p
    import tls_gen.verify as v
    cli.run(commands)
