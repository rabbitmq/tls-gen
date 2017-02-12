import os
from subprocess import call
import shutil

from .paths import *

def verify_leaf_certificate_against_root_ca(peer):
    print("Will verify {} certificate against root CA".format(peer))
    call(["openssl", "verify",
          "-CAfile", root_ca_certificate_path(),
          leaf_certificate_path(peer)])

    print("Will verify {} PKCS12 store".format(peer))
    call(["keytool", "-v", "-list",
          "-storetype", "pkcs12",
          "-keystore", leaf_pkcs12_key_store_path(peer)])

