import os
from os import path
from subprocess import call
import shutil
import stat

from .paths import *

def copy_root_ca_certificate_and_key_pair():
    copy_tuple_path((root_ca_dir_name, "cacert.pem"),           (result_dir_name, "ca_certificate.pem"))
    copy_tuple_path((root_ca_dir_name, "private", "cakey.pem"), (result_dir_name, "ca_key.pem"))

def copy_leaf_certificate_and_key_pair(peer):
    copy_tuple_path((peer, "cert.pem"),    (result_dir_name, "{}_certificate.pem".format(peer)))
    copy_tuple_path((peer, "key.pem"),     (result_dir_name, "{}_key.pem".format(peer)))
    copy_tuple_path((peer, "keycert.p12"), (result_dir_name, "{}_key.p12".format(peer)))

def openssl_req(*args):
    print("=>\t[openssl_req]")
    call(["openssl", "req", *args])

def openssl_x509(*args):
    print("=>\t[openssl_x509]")
    call(["openssl", "x509", *args])

def openssl_genrsa(*args):
    print("=>\t[openssl_genrsa]: {}".format(args))
    call(["openssl", "genrsa", *args])

def openssl_ca(*args):
    print("=>\t[openssl_ca]")
    call(["openssl", "ca", *args])

def generate_root_ca(opts):
    os.makedirs(relative_path(root_ca_dir_name), exist_ok = True)

    os.makedirs(relative_path(root_ca_dir_name, "certs"),   exist_ok = True)
    os.makedirs(relative_path(root_ca_dir_name, "private"), exist_ok = True)

    os.chmod(relative_path(root_ca_dir_name, "private"), stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

    serial = open(relative_path(root_ca_dir_name, "serial"), "w")
    serial.write("01")
    serial.close

    index_txt = open(relative_path(root_ca_dir_name, "index.txt"), "w")
    index_txt.close

    openssl_req("-x509",
                "-days",    str(opts.validity_days),
                "-config",  openssl_cnf_path(),
                "-newkey",  "rsa:{}".format(opts.key_bits),
                "-keyout",  root_ca_key_path(),
                "-out",     root_ca_certificate_path(),
                "-outform", "PEM",
                "-subj",    "/CN=MyTestRootCA/L=$$$$/",
                "-nodes")
    openssl_x509("-in",      root_ca_certificate_path(),
                 "-out",     root_ca_certificate_cer_path(),
                 "-outform", "DER")

def generate_server_certificate_and_key_pair(opts):
    generate_leaf_certificate_and_key_pair("server", opts)

def generate_client_certificate_and_key_pair(opts):
    generate_leaf_certificate_and_key_pair("client", opts)

def generate_leaf_certificate_and_key_pair(peer, opts):
    print("Using {} for Common Name (CN)".format(opts.common_name))
    os.makedirs(relative_path(peer), exist_ok = True)
    openssl_genrsa("-out", leaf_key_path(peer), str(opts.key_bits))
    openssl_req("-new",
                "-key",     leaf_key_path(peer),
                "-keyout",  leaf_certificate_path(peer),
                "-out",     relative_path(peer, "req.pem"),
                "-days",    str(opts.validity_days),
                "-outform", "PEM",
                "-subj",    "/CN={}/O={}/L=$$$$/".format(opts.common_name, peer),
                "-nodes")
    openssl_ca("-config",  openssl_cnf_path(),
               "-days",    str(opts.validity_days),
               "-cert",    root_ca_certificate_path(),
               "-keyfile", root_ca_key_path(),
               "-in",      relative_path(peer, "req.pem"),
               "-out",     leaf_certificate_path(peer),
               "-outdir",  root_ca_certs_path(),
               "-notext",
               "-batch",
               "-extensions", "{}_extensions".format(peer))
    call(["openssl", "pkcs12",
          "-export",
          "-out",     relative_path(peer, "keycert.p12"),
          "-in",      leaf_certificate_path(peer),
          "-inkey",   leaf_key_path(peer),
          "-passout", "pass:{}".format(opts.password)])
