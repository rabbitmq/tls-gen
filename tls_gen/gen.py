import os
from os import path
from subprocess import run
import shutil
import stat

from .paths import *

#
# General
#

def copy_root_ca_certificate_and_key_pair():
    copy_tuple_path((root_ca_dir_name, "cacert.pem"),           (result_dir_name, "ca_certificate.pem"))
    copy_tuple_path((root_ca_dir_name, "private", "cakey.pem"), (result_dir_name, "ca_key.pem"))

def copy_leaf_certificate_and_key_pair(peer):
    copy_tuple_path((peer, "cert.pem"),    (result_dir_name, "{}_certificate.pem".format(peer)))
    copy_tuple_path((peer, "key.pem"),     (result_dir_name, "{}_key.pem".format(peer)))
    copy_tuple_path((peer, "keycert.p12"), (result_dir_name, "{}_key.p12".format(peer)))

def openssl_req(*args, **kwargs):
    print("=>\t[openssl_req]")
    # avoids requiring Python 3.5, see
    # https://www.python.org/dev/peps/pep-0448/
    xs = ["openssl", "req"] + list(args)
    run(xs, **kwargs)

def openssl_x509(*args, **kwargs):
    print("=>\t[openssl_x509]")
    xs = ["openssl", "x509"] + list(args)
    run(xs, **kwargs)

def openssl_genrsa(*args, **kwargs):
    print("=>\t[openssl_genrsa]")
    xs = ["openssl", "genrsa"] + list(args)
    run(xs, **kwargs)

def openssl_ecparam(*args, **kwargs):
    print("=>\t[openssl_ecparam]")
    xs = ["openssl", "ecparam"] + list(args)
    run(xs, **kwargs)

def openssl_ca(*args, **kwargs):
    print("=>\t[openssl_ca]")
    xs = ["openssl", "ca"] + list(args)
    run(xs, **kwargs)

def prepare_ca_directory(dir_name):
    os.makedirs(relative_path(dir_name), exist_ok = True)
    os.makedirs(relative_path(dir_name, "certs"),   exist_ok = True)
    os.makedirs(relative_path(dir_name, "private"), exist_ok = True)

    os.chmod(relative_path(dir_name, "private"), stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

    serial = open(relative_path(dir_name, "serial"), "w")
    serial.write("01")
    serial.close

    index_txt = open(relative_path(dir_name, "index.txt"), "w")
    index_txt.close
    index_txt = open(relative_path(dir_name, "index.txt.attr"), "w")
    index_txt.close

#
# Root CA
#

def generate_root_ca(opts):
    prepare_ca_directory(root_ca_path())

    openssl_req("-x509",
                "-days",    str(opts.validity_days),
                "-config",  openssl_cnf_path(),
                "-newkey",  "rsa:{}".format(opts.key_bits),
                "-keyout",  root_ca_key_path(),
                "-out",     root_ca_certificate_path(),
                "-outform", "PEM",
                "-subj",    "/CN=TLSGenSelfSignedtRootCA/L=$$$$/",
                "-nodes")
    openssl_x509("-in",      root_ca_certificate_path(),
                 "-out",     root_ca_certificate_cer_path(),
                 "-outform", "DER")


#
# Intermediate CAs
#

def generate_intermediate_ca(opts,
                             parent_certificate_path = root_ca_certificate_path(),
                             parent_key_path = root_ca_key_path(),
                             suffix = ""):
    print("Will generate intermediate CA with suffix {}".format(suffix))
    print("Using parent certificate path at {}".format(parent_certificate_path))
    print("Using parent key path at {}".format(parent_key_path))
    prepare_ca_directory(intermediate_ca_path(suffix))

    if opts.use_ecc:
        print("Will use Elliptic Curve Cryptography...")
        openssl_ecparam("-out", intermediate_ca_key_path(suffix), "-genkey", "-name", opts.ecc_curve)
    else:
        print("Will use RSA...")
        openssl_genrsa("-out", intermediate_ca_key_path(suffix), str(opts.key_bits))

    openssl_req("-new",
                "-config",  openssl_cnf_path(),
                "-key",     intermediate_ca_key_path(suffix),
                "-out",     intermediate_ca_certificate_csr_path(suffix),
                "-subj",    "/CN={}/O={}/L=$$$$/".format(opts.common_name, "Intermediate CA {}".format(suffix)),
                "-passout", "pass:{}".format(opts.password))
    openssl_ca("-config",     openssl_cnf_path(),
               "-days",       str(opts.validity_days),
               "-cert",       parent_certificate_path,
               "-keyfile",    parent_key_path,
               "-in",         intermediate_ca_certificate_csr_path(suffix),
               "-out",        intermediate_ca_certificate_path(suffix),
               "-outdir",     intermediate_ca_certs_path(suffix),
               "-notext",
               "-batch",
               "-extensions", "ca_extensions")


#
# Leaf (peer) certificate/key pairs
#

def generate_server_certificate_and_key_pair(opts, **kwargs):
    generate_leaf_certificate_and_key_pair("server", opts, **kwargs)

def generate_client_certificate_and_key_pair(opts, **kwargs):
    generate_leaf_certificate_and_key_pair("client", opts, **kwargs)

def generate_leaf_certificate_and_key_pair(peer, opts,
                                           parent_certificate_path = root_ca_certificate_path(),
                                           parent_key_path         = root_ca_key_path(),
                                           parent_certs_path       = root_ca_certs_path()):
    env = os.environ.copy()

    print("Will generate leaf certificate and key pair for {}".format(peer))
    print("Using {} for Common Name (CN)".format(opts.common_name))

    if peer == "client":
        env["CLIENT_ALT_NAME"] = opts.client_alt_name or opts.common_name
        print("Using {0} for client's SAN (alternative name)".format(env["CLIENT_ALT_NAME"]))

    if peer == "server":
        env["SERVER_ALT_NAME"] = opts.server_alt_name or opts.common_name
        print("Using {0} for server's SAN (alternative name)".format(env["SERVER_ALT_NAME"]))

    print("Using parent certificate path at {}".format(parent_certificate_path))
    print("Using parent key path at {}".format(parent_key_path))
    os.makedirs(relative_path(peer), exist_ok = True)

    if opts.use_ecc:
        print("Will use Elliptic Curve Cryptography...")
        openssl_ecparam("-out", leaf_key_path(peer), "-genkey", "-name", opts.ecc_curve, env = env)
    else:
        print("Will use RSA...")
        openssl_genrsa("-out", leaf_key_path(peer), str(opts.key_bits), env = env)

    openssl_req("-new",
                "-config",  openssl_cnf_path(),
                "-key",     leaf_key_path(peer),
                "-keyout",  leaf_certificate_path(peer),
                "-out",     relative_path(peer, "req.pem"),
                "-days",    str(opts.validity_days),
                "-outform", "PEM",
                "-subj",    "/CN={}/O={}/L=$$$$/".format(opts.common_name, peer),
                "-nodes",
                env = env)
    openssl_ca("-config",  openssl_cnf_path(),
               "-days",    str(opts.validity_days),
               "-cert",    parent_certificate_path,
               "-keyfile", parent_key_path,
               "-in",      relative_path(peer, "req.pem"),
               "-out",     leaf_certificate_path(peer),
               "-outdir",  parent_certs_path,
               "-notext",
               "-batch",
               "-extensions", "{}_extensions".format(peer),
               env = env)
    run(["openssl", "pkcs12",
          "-export",
          "-out",     relative_path(peer, "keycert.p12"),
          "-in",      leaf_certificate_path(peer),
          "-inkey",   leaf_key_path(peer),
          "-passout", "pass:{}".format(opts.password)],
          env = env)
