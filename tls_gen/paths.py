import os
from os import path
import shutil

root             = os.getcwd()
root_ca_dir_name = "testca"
result_dir_name  = "result"

def relative_path(*paths):
    return path.join(root, *paths)

def root_ca_path():
    return path.join(root, root_ca_dir_name)

def root_ca_certificate_path():
    return path.join(root, result_dir_name, "ca_certificate.pem")

def result_path():
    return path.join(root, result_dir_name)

def leaf_pair_path(peer):
    return path.join(root, peer)

def leaf_certificate_path(peer):
    return path.join(result_path(), "{}_certificate.pem".format(peer))

def leaf_pkcs12_key_store_path(peer):
    return path.join(result_path(), "{}_key.p12".format(peer))

def copy_tuple_path(from_tuple, to_tuple):
    shutil.copy(relative_path(*from_tuple), relative_path(*to_tuple))
