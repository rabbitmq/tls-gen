import os
from subprocess import call
import shutil

from .paths import *

def leaf_certificate_info(peer):
    print("Will display {} certificate info\n\n".format(peer))
    call(["openssl", "x509",
          "-in", result_leaf_certificate_path(peer),
          "-text",
          "-noout"])
