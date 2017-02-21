import os
from os import path
import shutil

root             = os.getcwd()
root_ca_dir_name = "testca"
result_dir_name  = "result"

#
# General
#

def relative_path(*paths):
    return path.join(root, *paths)

def copy_tuple_path(from_tuple, to_tuple):
    shutil.copy(relative_path(*from_tuple), relative_path(*to_tuple))

def openssl_cnf_path():
    return relative_path("openssl.cnf")

#
# Root CA
#

def root_ca_path():
    return path.join(root, root_ca_dir_name)

def root_ca_certs_path():
    return path.join(root, root_ca_dir_name, "certs")

def root_ca_certificate_path():
    return path.join(root, root_ca_dir_name, "cacert.pem")

def root_ca_key_path():
    return path.join(root, root_ca_dir_name, "private", "cakey.pem")

def root_ca_certificate_cer_path():
    return path.join(root, root_ca_dir_name, "cacert.cer")

#
# Intermediate CAs
#

def intermediate_ca_path(suffix = ""):
    return path.join(root, "intermediate_ca_{}".format(suffix))

def intermediate_ca_certs_path(suffix = ""):
    return path.join(intermediate_ca_path(suffix), "certs")

def intermediate_ca_certificate_path(suffix = ""):
    return path.join(intermediate_ca_path(suffix), "certs", "cacert.pem")

def intermediate_ca_certificate_csr_path(suffix = ""):
    return path.join(intermediate_ca_path(suffix), "certs", "ca_csr.pem")

def intermediate_ca_key_path(suffix = ""):
    return path.join(intermediate_ca_path(suffix), "private", "cakey.pem")

#
# Leaf (peer) certificates and keys
#

def leaf_pair_path(peer):
    return path.join(root, peer)

def leaf_certificate_path(peer):
    return relative_path(peer, "cert.pem")

def leaf_key_path(peer):
    return relative_path(peer, "key.pem")


#
# Results directory
#

def result_path():
    return path.join(root, result_dir_name)

def result_root_ca_certificate_path():
    return path.join(root, result_dir_name, "ca_certificate.pem")

def result_leaf_certificate_path(peer):
    return path.join(result_path(), "{}_certificate.pem".format(peer))

def result_leaf_key_path(peer):
    return path.join(result_path(), "{}_key.pem".format(peer))

def result_leaf_pkcs12_key_store_path(peer):
    return path.join(result_path(), "{}_key.p12".format(peer))

def result_chained_certificate_path():
    return path.join(root, result_dir_name, "chained_ca_certificate.pem")

def result_chained_peer_ca_certificate_path(peer):
    return path.join(root, result_dir_name, "chained_{}_ca_certificate.pem".format(peer))
