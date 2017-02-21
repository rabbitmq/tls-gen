import os
from subprocess import call
import shutil

from .paths import *

def verify_leaf_certificate_against_root_ca(peer):
    print("Will verify {} certificate against root CA".format(peer))
    call(["openssl", "verify",
          "-CAfile", result_root_ca_certificate_path(),
          result_leaf_certificate_path(peer)])

def verify_leaf_certificate_against_ca_chain(peer):
    print("Will verify {} certificate against CA certificate chain {}".format(
        peer, result_chained_certificate_path()))
    call(["openssl", "verify",
          "-CAfile", result_chained_certificate_path(),
          result_leaf_certificate_path(peer)])

def verify_leaf_certificate_against_peer_ca_chain(peer):
    print("Will verify {} certificate against its CA certificate chain {}".format(
        peer, result_chained_peer_ca_certificate_path(peer)))
    call(["openssl", "verify",
          "-CAfile", result_chained_peer_ca_certificate_path(peer),
          result_leaf_certificate_path(peer)])

def verify_pkcs12_store(peer, opts):
    print("Will verify {} PKCS12 store".format(peer))
    call(["keytool", "-v", "-list",
          "-storetype", "pkcs12",
          "-keystore", leaf_pkcs12_key_store_path(peer),
          "-storepass", opts.password])
