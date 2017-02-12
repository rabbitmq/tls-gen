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

def generate_root_ca(opts):
    os.chdir(root)
    os.makedirs(relative_path(root_ca_dir_name), exist_ok = True)
    shutil.copy(relative_path("openssl.cnf"), relative_path(root_ca_dir_name, "openssl.cnf"))
    os.makedirs(relative_path(root_ca_dir_name, "certs"), exist_ok = True)
    os.makedirs(relative_path(root_ca_dir_name, "private"), exist_ok = True)
    os.chmod(relative_path(root_ca_dir_name, "private"), stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

    serial = open(relative_path(root_ca_dir_name, "serial"), "w")
    serial.write("01")
    serial.close

    index_txt = open(relative_path(root_ca_dir_name, "index.txt"), "w")
    index_txt.close

    os.chdir(relative_path(root_ca_dir_name))
    call(["openssl", "req",
          "-x509",
          "-days",    str(opts.validity_days),
          "-config",  "openssl.cnf",
          "-newkey",  "rsa:{}".format(opts.key_bits),
          "-out",     "cacert.pem",
          "-outform", "PEM",
          "-subj",    "/CN=MyTestRootCA/L=$$$$/",
          "-nodes"])
    call(["openssl", "x509",
          "-in",      "cacert.pem",
          "-out",     "cacert.cer",
          "-outform", "DER"])
    os.chdir(root)

def generate_server_certificate_and_key_pair(opts):
    generate_leaf_certificate_and_key_pair("server", opts)

def generate_client_certificate_and_key_pair(opts):
    generate_leaf_certificate_and_key_pair("client", opts)

def generate_leaf_certificate_and_key_pair(peer, opts):
    print("Using {} for Common Name (CN)".format(opts.common_name))
    os.chdir(root)
    os.makedirs(relative_path(peer), exist_ok = True)
    os.chdir(relative_path(peer))
    call(["openssl", "genrsa",
          "-out", "key.pem", str(opts.key_bits)])
    call(["openssl", "req",
          "-new",
          "-key",     "key.pem",
          "-out",     "req.pem",
          "-days",    str(opts.validity_days),
          "-outform", "PEM",
          "-subj",    "/CN={}/O={}/L=$$$$/".format(opts.common_name, peer),
          "-nodes"])
    os.chdir(relative_path(root_ca_dir_name))
    call(["openssl", "ca",
          "-config", "openssl.cnf",
          "-days",   str(opts.validity_days),
          "-in",     relative_path(peer, "req.pem"),
          "-out",    relative_path(peer, "cert.pem"),
          "-notext",
          "-batch",
          "-extensions", "{}_extensions".format(peer)])
    os.chdir(relative_path(peer))
    call(["openssl", "pkcs12",
          "-export",
          "-out",     "keycert.p12",
          "-in",      "cert.pem",
          "-inkey",   "key.pem",
          "-passout", "pass:{}".format(opts.password)])
    os.chdir(root)
