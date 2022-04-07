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

def _copy_artifacts_to_results(opts):
    os.makedirs(paths.relative_path("result"), exist_ok = True)
    gen.copy_root_ca_certificate_and_key_pair()
    cn = opts.common_name
    name = 'server_{}'.format(cn)
    gen.copy_leaf_certificate_and_key_pair(name)
    name = 'client_{}'.format(cn)
    gen.copy_leaf_certificate_and_key_pair(name)

def generate(opts):
    cli.validate_password_if_provided(opts)
    print("Will generate a root CA and two certificate/key pairs (server and client)")
    gen.generate_root_ca(opts)
    cn = opts.common_name
    name = 'server_{}'.format(cn)
    gen.generate_leaf_certificate_and_key_pair('server', opts, name)
    name = 'client_{}'.format(cn)
    gen.generate_leaf_certificate_and_key_pair('client', opts, name)
    _copy_artifacts_to_results(opts)
    print("Done! Find generated certificates and private keys under ./result!")

def generate_client(opts):
    cli.ensure_password_is_provided(opts)
    print("Will generate a certificate/key pair (client only)")
    cn = opts.common_name
    name = 'client_{}'.format(cn)
    gen.generate_leaf_certificate_and_key_pair('client', opts, name)
    gen.copy_leaf_certificate_and_key_pair(name)
    print("Done! Find generated certificates and private keys under ./result!")

def generate_server(opts):
    cli.ensure_password_is_provided(opts)
    print("Will generate a certificate/key pair (server only)")
    cn = opts.common_name
    name = 'server_{}'.format(cn)
    gen.generate_leaf_certificate_and_key_pair('server', opts, name)
    gen.copy_leaf_certificate_and_key_pair(name)
    print("Done! Find generated certificates and private keys under ./result!")

def clean(opts):
    cn = opts.common_name
    for s in [paths.root_ca_path(),
              paths.result_path(),
              paths.leaf_pair_path('server'.format(cn)),
              paths.leaf_pair_path('client'.format(cn))]:
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
    verify.verify_leaf_certificate_against_root_ca('client_{}'.format(opts.common_name))
    verify.verify_leaf_certificate_against_root_ca('server_{}'.format(opts.common_name))

def verify_pkcs12(opts):
    cli.validate_password_if_provided(opts)

    print("Will verify generated PKCS12 certificate stores...")
    verify.verify_pkcs12_store("client", opts)
    verify.verify_pkcs12_store("server", opts)

def info(opts):
    cn = opts.common_name
    client_name = 'client_{}'.format(cn)
    info.leaf_certificate_info(client_name)

    server_name = 'server_{}'.format(cn)
    info.leaf_certificate_info(server_name)

def alias_leaf_artifacts(opts):
    cn = opts.common_name
    client_name = 'client_{}'.format(cn)
    server_name = 'server_{}'.format(cn)

    print("Will copy certificate and key for {} to {}".format(client_name, paths.relative_path(*("result", "client_*.pem"))))
    print("Will copy certificate and key for {} to {}".format(server_name, paths.relative_path(*("result", "server_*.pem"))))

    gen.alias_file("client", client_name)
    gen.alias_file("server", server_name)

    print("Done! Find new copies under ./result!")



commands = {"generate":        generate,
            "gen":             generate,
            "generate-client": generate_client,
            "generate-server": generate_server,
            "clean":           clean,
            "regenerate":      regenerate,
            "regen":           regenerate,
            "verify":          verify,
            "verify-pkcs12":   verify_pkcs12,
            "info":            info,
            "alias-leaf-artifacts": alias_leaf_artifacts}

if __name__ == "__main__":
    sys.path.append("..")
    from tls_gen import cli
    from tls_gen import gen
    from tls_gen import paths
    from tls_gen import verify
    from tls_gen import info

    cli.run(commands)
