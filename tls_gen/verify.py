# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2007-2014 VMware, Inc. or its affiliates. All rights reserved.
# Copyright (c) 2014-2020 Michael Klishin and contributors.
# Copyright (c) 2022 VMware, Inc. or its affiliates. All rights reserved.

from subprocess import call

import tls_gen.paths as p


def verify_leaf_certificate_against_root_ca(peer):
    print("Will verify {} certificate against root CA".format(peer))
    call(["openssl", "verify",
          "-CAfile", p.result_root_ca_certificate_path(),
          p.result_leaf_certificate_path(peer)])


def verify_leaf_certificate_against_ca_chain(peer):
    print("Will verify {} certificate against CA certificate chain {}".format(
        peer, p.result_chained_certificate_path()))
    call(["openssl", "verify",
          "-CAfile", p.result_chained_certificate_path(),
          p.result_leaf_certificate_path(peer)])


def verify_leaf_certificate_against_peer_ca_chain(peer):
    print("Will verify {} certificate against its CA certificate chain {}".format(
        peer, p.result_chained_peer_ca_certificate_path(peer)))
    call(["openssl", "verify",
          "-CAfile", p.result_chained_peer_ca_certificate_path(peer),
          p.result_leaf_certificate_path(peer)])


def verify_pkcs12_store(peer, opts):
    print("Will verify {} PKCS12 store".format(peer))
    call(["keytool", "-v", "-list",
          "-storetype", "pkcs12",
          "-keystore", p.leaf_pkcs12_key_store_path(peer),
          "-storepass", opts.password])
