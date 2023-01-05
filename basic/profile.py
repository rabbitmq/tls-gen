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
    os.makedirs(p.relative_path("result"), exist_ok=True)
    g.copy_root_ca_certificate_and_key_pair()
    cn = opts.common_name
    name = 'server_{}'.format(cn)
    g.copy_leaf_certificate_and_key_pair(name)
    name = 'client_{}'.format(cn)
    g.copy_leaf_certificate_and_key_pair(name)


def generate(opts):
    cli.validate_password_if_provided(opts)
    print("Will generate a root CA and two certificate/key pairs (server and client)")
    g.generate_root_ca(opts)
    cn = opts.common_name
    name = 'server_{}'.format(cn)
    g.generate_leaf_certificate_and_key_pair('server', opts, name)
    name = 'client_{}'.format(cn)
    g.generate_leaf_certificate_and_key_pair('client', opts, name)
    _copy_artifacts_to_results(opts)
    print("Done! Find generated certificates and private keys under ./result!")


def generate_client(opts):
    cli.ensure_password_is_provided(opts)
    print("Will generate a certificate/key pair (client only)")
    cn = opts.common_name
    name = 'client_{}'.format(cn)
    g.generate_leaf_certificate_and_key_pair('client', opts, name)
    g.copy_leaf_certificate_and_key_pair(name)
    print("Done! Find generated certificates and private keys under ./result!")


def generate_server(opts):
    cli.ensure_password_is_provided(opts)
    print("Will generate a certificate/key pair (server only)")
    cn = opts.common_name
    name = 'server_{}'.format(cn)
    g.generate_leaf_certificate_and_key_pair('server', opts, name)
    g.copy_leaf_certificate_and_key_pair(name)
    print("Done! Find generated certificates and private keys under ./result!")


def clean(opts):
    cn = opts.common_name
    for s in [p.root_ca_path(),
              p.result_path(),
              p.leaf_pair_path('server_{}'.format(cn)),
              p.leaf_pair_path('client_{}'.format(cn))]:
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
    v.verify_leaf_certificate_against_root_ca('client_{}'.format(opts.common_name))
    v.verify_leaf_certificate_against_root_ca('server_{}'.format(opts.common_name))


def verify_pkcs12(opts):
    cli.validate_password_if_provided(opts)

    print("Will verify generated PKCS12 certificate stores...")
    v.verify_pkcs12_store("client", opts)
    v.verify_pkcs12_store("server", opts)


def info(opts):
    cn = opts.common_name
    client_name = 'client_{}'.format(cn)
    i.leaf_certificate_info(client_name)

    server_name = 'server_{}'.format(cn)
    i.leaf_certificate_info(server_name)


def alias_leaf_artifacts(opts):
    cn = opts.common_name
    client_name = 'client_{}'.format(cn)
    server_name = 'server_{}'.format(cn)

    print("Will copy certificate and key for {} to {}".format(client_name, p.relative_path(*("result", "client_*.pem"))))
    print("Will copy certificate and key for {} to {}".format(server_name, p.relative_path(*("result", "server_*.pem"))))

    g.alias_file("client", client_name)
    g.alias_file("server", server_name)

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
    sys.path.append(os.path.realpath('..'))
    import tls_gen.cli as cli
    import tls_gen.gen as g
    import tls_gen.info as i
    import tls_gen.paths as p
    import tls_gen.verify as v
    cli.run(commands)
