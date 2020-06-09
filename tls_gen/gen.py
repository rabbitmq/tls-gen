import os
import shutil
import stat
import tempfile

from os import path
from subprocess import run

from .paths import *

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
    cnf_path = openssl_cnf_path()
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
    copy_tuple_path((root_ca_dir_name, "cacert.pem"),           (result_dir_name, "ca_certificate.pem"))
    copy_tuple_path((root_ca_dir_name, "private", "cakey.pem"), (result_dir_name, "ca_key.pem"))

def copy_leaf_certificate_and_key_pair(peer):
    copy_tuple_path((peer, "cert.pem"),    (result_dir_name, "{}_certificate.pem".format(peer)))
    copy_tuple_path((peer, "key.pem"),     (result_dir_name, "{}_key.pem".format(peer)))
    copy_tuple_path((peer, "keycert.p12"), (result_dir_name, "{}_key.p12".format(peer)))

def openssl_req(opts, *args, **kwargs):
    cnf_path = get_openssl_cnf_path(opts)
    print("=>\t[openssl_req]")
    # avoids requiring Python 3.5, see
    # https://www.python.org/dev/peps/pep-0448/
    xs = ["openssl", "req", "-config", cnf_path] + list(args)
    run(xs, **kwargs)

def openssl_x509(*args, **kwargs):
    print("=>\t[openssl_x509]")
    xs = ["openssl", "x509"] + list(args)
    run(xs, **kwargs)

def openssl_genpkey(*args, **kwargs):
    print("=>\t[openssl_genpkey]")
    xs = ["openssl", "genpkey"] + list(args)
    run(xs, **kwargs)

def openssl_ca(opts, *args, **kwargs):
    cnf_path = get_openssl_cnf_path(opts)
    print("=>\t[openssl_ca]")
    xs = ["openssl", "ca", "-config", cnf_path] + list(args)
    run(xs, **kwargs)

def openssl_pkcs12(*args, **kwargs):
    print("=>\t[openssl_pkcs12]")
    xs = ["openssl", "pkcs12"] + list(args)
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
    args = ["-x509",
            "-days",    str(opts.validity_days),
            "-newkey",  "rsa:{}".format(opts.key_bits),
            "-keyout",  root_ca_key_path(),
            "-out",     root_ca_certificate_path(),
            "-outform", "PEM",
            "-subj",    "/CN=TLSGenSelfSignedtRootCA/L=$$$$/"]
    if len(opts.password) > 0:
        args.append("-passout")
        args.append("pass:{}".format(opts.password))
    else:
        args.append("-nodes")
    openssl_req(opts, *args)
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
        args = ["-algorithm", "EC",
                "-outform",   "PEM",
                "-out",       intermediate_ca_key_path(suffix),
                "-pkeyopt",   "ec_paramgen_curve:{}".format(opts.ecc_curve)]
    else:
        print("Will use RSA...")
        args = ["-algorithm", "RSA",
                "-outform",   "PEM",
                "-out",       intermediate_ca_key_path(suffix),
                "-pkeyopt",   "rsa_keygen_bits:{}".format(str(opts.key_bits))]

    if len(opts.password) > 0:
        args.append("-aes256")
        args.append("-pass")
        args.append("pass:{}".format(opts.password))
    openssl_genpkey(*args)

    args = ["-new",
            "-key",     intermediate_ca_key_path(suffix),
            "-out",     intermediate_ca_certificate_csr_path(suffix),
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
            "-in",         intermediate_ca_certificate_csr_path(suffix),
            "-out",        intermediate_ca_certificate_path(suffix),
            "-outdir",     intermediate_ca_certs_path(suffix),
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
                                           parent_certificate_path = root_ca_certificate_path(),
                                           parent_key_path         = root_ca_key_path(),
                                           parent_certs_path       = root_ca_certs_path()):
    print("Will generate leaf certificate and key pair for {}".format(peer))
    print("Using {} for Common Name (CN)".format(opts.common_name))

    print("Using parent certificate path at {}".format(parent_certificate_path))
    print("Using parent key path at {}".format(parent_key_path))
    os.makedirs(relative_path(peer), exist_ok = True)

    if opts.use_ecc:
        print("Will use Elliptic Curve Cryptography...")
        args = ["-algorithm", "EC",
                "-outform",   "PEM",
                "-out",       leaf_key_path(peer),
                "-pkeyopt",   "ec_paramgen_curve:{}".format(opts.ecc_curve)]
    else:
        print("Will use RSA...")
        args = ["-algorithm", "RSA",
                "-outform",   "PEM",
                "-out",       leaf_key_path(peer),
                "-pkeyopt",   "rsa_keygen_bits:{}".format(str(opts.key_bits))]

    if len(opts.password) > 0:
        args.append("-aes256")
        args.append("-pass")
        args.append("pass:{}".format(opts.password))
    openssl_genpkey(*args)

    args = ["-new",
            "-key",     leaf_key_path(peer),
            "-keyout",  leaf_certificate_path(peer),
            "-out",     relative_path(peer, "req.pem"),
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
            "-in",      relative_path(peer, "req.pem"),
            "-out",     leaf_certificate_path(peer),
            "-outdir",  parent_certs_path,
            "-notext",
            "-batch",
            "-extensions", "{}_extensions".format(peer)]
    if len(opts.password) > 0:
        args.append("-passin")
        args.append("pass:{}".format(opts.password))
    openssl_ca(opts, *args)

    args = ["-export",
            "-out",     relative_path(peer, "keycert.p12"),
            "-in",      leaf_certificate_path(peer),
            "-inkey",   leaf_key_path(peer),
            "-passout", "pass:{}".format(opts.password)]
    if len(opts.password) > 0:
        args.append("-passin")
        args.append("pass:{}".format(opts.password))
    openssl_pkcs12(*args)
