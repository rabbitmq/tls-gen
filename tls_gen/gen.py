# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2007-2014 VMware, Inc. or its affiliates. All rights reserved.
# Copyright (c) 2014-2020 Michael Klishin and contributors.
# Copyright (c) 2022 VMware, Inc. or its affiliates. All rights reserved.

import os
import stat
import tempfile

from datetime import datetime
from os import path
from subprocess import run

import tls_gen.paths as p

#
# General
#

generated_cnf_file = None


def get_openssl_cnf_path(opts):
    global generated_cnf_file

    try:
        if path.exists(generated_cnf_file):
            return generated_cnf_file
    except TypeError:
        pass

    cn = opts.common_name
    client_alt_name = opts.client_alt_name or opts.common_name
    server_alt_name = opts.server_alt_name or opts.common_name
    cnf_path = p.openssl_cnf_path()
    tmp_cnf_path = None

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as outfile:
        with open(cnf_path, 'r') as infile:
            in_cnf = infile.read()
            out_cnf0 = in_cnf.replace('@COMMON_NAME@', cn)
            out_cnf1 = out_cnf0.replace('@CLIENT_ALT_NAME@', client_alt_name)
            out_cnf2 = out_cnf1.replace('@SERVER_ALT_NAME@', server_alt_name)
            outfile.write(out_cnf2)
            tmp_cnf_path = outfile.name

    generated_cnf_file = tmp_cnf_path

    return tmp_cnf_path


def copy_root_ca_certificate_and_key_pair():
    p.copy_tuple_path((p.root_ca_dir_name, "cacert.pem"),           (p.result_dir_name, "ca_certificate.pem"))
    p.copy_tuple_path((p.root_ca_dir_name, "private", "cakey.pem"), (p.result_dir_name, "ca_key.pem"))


def copy_leaf_certificate_and_key_pair(peer):
    p.copy_tuple_path((peer, "cert.pem"),    (p.result_dir_name, "{}_certificate.pem".format(peer)))
    p.copy_tuple_path((peer, "key.pem"),     (p.result_dir_name, "{}_key.pem".format(peer)))
    p.copy_tuple_path((peer, "keycert.p12"), (p.result_dir_name, "{}.p12".format(peer)))


def alias_file(kind, peer):
    """
    Copies a leaf certificate to commonly used file names (e.g. client_certificate.pem)
    under the results directory
    """
    p.copy_tuple_path((p.result_dir_name, "{}_certificate.pem".format(peer)),
                      (p.result_dir_name, "{}_certificate.pem".format(kind)))
    p.copy_tuple_path((p.result_dir_name, "{}_key.pem".format(peer)),
                      (p.result_dir_name, "{}_key.pem".format(kind)))


def openssl_req(opts, *args, **kwargs):
    cnf_path = get_openssl_cnf_path(opts)
    # avoids requiring Python 3.5, see
    # https://www.python.org/dev/peps/pep-0448/
    xs = ["openssl", "req", "-config", cnf_path] + list(args)
    print("=>", xs, kwargs)
    run(xs, **kwargs)


def openssl_x509(*args, **kwargs):
    xs = ["openssl", "x509"] + list(args)
    print("=>", xs, kwargs)
    run(xs, **kwargs)


def openssl_genpkey(*args, **kwargs):
    xs = ["openssl", "genpkey"] + list(args)
    print("=>", xs, kwargs)
    run(xs, **kwargs)


def openssl_ca(opts, *args, **kwargs):
    cnf_path = get_openssl_cnf_path(opts)
    xs = ["openssl", "ca", "-config", cnf_path] + list(args)
    print("=>", xs, kwargs)
    run(xs, **kwargs)


def openssl_pkcs12(*args, **kwargs):
    xs = ["openssl", "pkcs12"] + list(args)
    print("=>", xs, kwargs)
    run(xs, **kwargs)


def prepare_ca_directory(dir_name):
    os.makedirs(p.relative_path(dir_name), exist_ok=True)
    os.makedirs(p.relative_path(dir_name, "certs"),   exist_ok=True)
    os.makedirs(p.relative_path(dir_name, "private"), exist_ok=True)

    os.chmod(p.relative_path(dir_name, "private"), stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

    serial = open(p.relative_path(dir_name, "serial"), "w")
    serial.write("01")
    serial.close()

    index_txt = open(p.relative_path(dir_name, "index.txt"), "w")
    index_txt.close()
    index_txt = open(p.relative_path(dir_name, "index.txt.attr"), "w")
    index_txt.close()

#
# Root CA
#


def generate_root_ca(opts):
    prepare_ca_directory(p.root_ca_path())
    iso_date = datetime.now().isoformat()
    args = ["-x509",
            "-days",    str(opts.validity_days),
            "-newkey",  "rsa:{}".format(opts.key_bits),
            "-keyout",  p.root_ca_key_path(),
            "-out",     p.root_ca_certificate_path(),
            "-outform", "PEM",
            "-subj",    "/CN=TLSGenSelfSignedRootCA {}/L=$$$$/".format(iso_date)]
    if len(opts.password) > 0:
        args.append("-passout")
        args.append("pass:{}".format(opts.password))
    else:
        args.append("-nodes")
    openssl_req(opts, *args)
    openssl_x509("-in",      p.root_ca_certificate_path(),
                 "-out",     p.root_ca_certificate_cer_path(),
                 "-outform", "DER")


#
# Intermediate CAs
#

def generate_intermediate_ca(opts,
                             parent_certificate_path=p.root_ca_certificate_path(),
                             parent_key_path=p.root_ca_key_path(),
                             suffix=""):
    print("Will generate intermediate CA with suffix {}".format(suffix))
    print("Using parent certificate path at {}".format(parent_certificate_path))
    print("Using parent key path at {}".format(parent_key_path))
    prepare_ca_directory(p.intermediate_ca_path(suffix))

    if opts.use_ecc:
        print("Will use Elliptic Curve Cryptography...")
        args = ["-algorithm", "EC",
                "-outform",   "PEM",
                "-out",       p.intermediate_ca_key_path(suffix),
                "-pkeyopt",   "ec_paramgen_curve:{}".format(opts.ecc_curve)]
    else:
        print("Will use RSA...")
        args = ["-algorithm", "RSA",
                "-outform",   "PEM",
                "-out",       p.intermediate_ca_key_path(suffix),
                "-pkeyopt",   "rsa_keygen_bits:{}".format(str(opts.key_bits))]

    if len(opts.password) > 0:
        args.append("-aes256")
        args.append("-pass")
        args.append("pass:{}".format(opts.password))
    openssl_genpkey(*args)

    args = ["-new",
            "-key",     p.intermediate_ca_key_path(suffix),
            "-out",     p.intermediate_ca_certificate_csr_path(suffix),
            "-subj",    "/CN={}/O={}/L=$$$$/".format(opts.common_name, "Intermediate CA {}".format(suffix))]
    if len(opts.password) > 0:
        args.append("-passin")
        args.append("pass:{}".format(opts.password))
        args.append("-passout")
        args.append("pass:{}".format(opts.password))
    else:
        args.append("-nodes")
    openssl_req(opts, *args)

    args = ["-days",       str(opts.validity_days),
            "-cert",       parent_certificate_path,
            "-keyfile",    parent_key_path,
            "-in",         p.intermediate_ca_certificate_csr_path(suffix),
            "-out",        p.intermediate_ca_certificate_path(suffix),
            "-outdir",     p.intermediate_ca_certs_path(suffix),
            "-notext",
            "-batch",
            "-extensions", "ca_extensions"]
    if len(opts.password) > 0:
        args.append("-passin")
        args.append("pass:{}".format(opts.password))
    openssl_ca(opts, *args)


#
# Leaf (peer) certificate/key pairs
#

def generate_server_certificate_and_key_pair(opts, **kwargs):
    generate_leaf_certificate_and_key_pair("server", opts, **kwargs)


def generate_client_certificate_and_key_pair(opts, **kwargs):
    generate_leaf_certificate_and_key_pair("client", opts, **kwargs)


def generate_leaf_certificate_and_key_pair(peer, opts,
                                           peer_path=None,
                                           parent_certificate_path=p.root_ca_certificate_path(),
                                           parent_key_path=p.root_ca_key_path(),
                                           parent_certs_path=p.root_ca_certs_path()):
    if peer_path:
        pp = peer_path
    else:
        pp = peer

    print("Will generate leaf certificate and key pair for {}".format(peer))
    print("Using {} for Common Name (CN)".format(opts.common_name))

    print("Using parent certificate path at {}".format(parent_certificate_path))
    print("Using parent key path at {}".format(parent_key_path))
    os.makedirs(p.relative_path(pp), exist_ok=True)

    if opts.use_ecc:
        print("Will use Elliptic Curve Cryptography...")
        args = ["-algorithm", "EC",
                "-outform",   "PEM",
                "-out",       p.leaf_key_path(pp),
                "-pkeyopt",   "ec_paramgen_curve:{}".format(opts.ecc_curve)]
    else:
        print("Will use RSA...")
        args = ["-algorithm", "RSA",
                "-outform",   "PEM",
                "-out",       p.leaf_key_path(pp),
                "-pkeyopt",   "rsa_keygen_bits:{}".format(str(opts.key_bits))]

    if len(opts.password) > 0:
        args.append("-aes256")
        args.append("-pass")
        args.append("pass:{}".format(opts.password))
    openssl_genpkey(*args)

    args = ["-new",
            "-key",     p.leaf_key_path(pp),
            "-keyout",  p.leaf_certificate_path(pp),
            "-out",     p.relative_path(pp, "req.pem"),
            "-outform", "PEM",
            "-subj",    "/CN={}/O={}/L=$$$$/".format(opts.common_name, peer)]
    if len(opts.password) > 0:
        args.append("-passin")
        args.append("pass:{}".format(opts.password))
        args.append("-passout")
        args.append("pass:{}".format(opts.password))
    else:
        args.append("-nodes")
    openssl_req(opts, *args)

    args = ["-days",    str(opts.validity_days),
            "-cert",    parent_certificate_path,
            "-keyfile", parent_key_path,
            "-in",      p.relative_path(pp, "req.pem"),
            "-out",     p.leaf_certificate_path(pp),
            "-outdir",  parent_certs_path,
            "-notext",
            "-batch",
            "-extensions", "{}_extensions".format(peer)]
    if len(opts.password) > 0:
        args.append("-passin")
        args.append("pass:{}".format(opts.password))
    openssl_ca(opts, *args)

    args = ["-export",
            "-out",     p.relative_path(pp, "keycert.p12"),
            "-in",      p.leaf_certificate_path(pp),
            "-inkey",   p.leaf_key_path(pp),
            "-certfile", parent_certificate_path,
            "-passout", "pass:{}".format(opts.password)]
    if len(opts.password) > 0:
        args.append("-passin")
        args.append("pass:{}".format(opts.password))
    openssl_pkcs12(*args)
