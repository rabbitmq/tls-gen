import sys
import os
from optparse import OptionParser

import socket

def build_parser():
    p = OptionParser(usage = "usage: %prog [options] (generate|clean|regenerate|verify|info)")
    p.add_option("-p", "--password",
                 type = "string", dest = "password", action = "store",
                 help = "Private key password", default = "")
    p.add_option("-n", "--common-name", dest = "common_name", action = "store",
                 help = "Certificate CN (Common Name)", default = socket.gethostname())
    p.add_option("--client-alt-name", dest = "client_alt_name", action = "store",
                 help = "SAN (subject Alternative Name) for the client", default = socket.gethostname())
    p.add_option("--server-alt-name", dest = "server_alt_name", action = "store",
                 help = "SAN (subject Alternative Name) for the server", default = socket.gethostname())
    p.add_option("-b", "--key-bits", dest = "key_bits", action = "store",
                 help = "Number of private key bits",
                 type = "int", default = 4096)
    p.add_option("-e", "--use-ecc", dest = "use_ecc", action = "store_true",
                 help = "Should Elliptic Curve Cryptography be used?",
                 default = False)
    p.add_option("-c", "--ecc-curve",
                 type = "string", dest = "ecc_curve", action = "store",
                 help = "ECC curve to use (see 'openssl ecparam -list_curves')",
                 default = "prime256v1")
    p.add_option("-V", "--days-of-validity", dest = "validity_days", action = "store",
                 help = "For how many days should generated certificates be valid?",
                 type = "int", default = 3650)
    return p

def dispatch_command(commands, parser, args, options):
    try:
        cmd = args[0]
        fn  = commands[cmd]

        fn(options)
    except IndexError:
        parser.print_help()
        sys.exit(1)
    except KeyError:
        print_known_commands()
        parser.print_help()
        sys.exit(1)

def print_known_commands():
    s = ", ".join(list(f.__name__ for f in commands.values()))
    print("Known commands: {}".format(s))

def validate_password_if_provided(options):
    if len(options.password) > 0 and (len(options.password) < 4 or len(options.password) > 1023):
        sys.stderr.write("Password must be between 4 and 1023 characters in length.\n")
        sys.exit(1)

def run(commands):
    parser = build_parser()
    (options, args) = parser.parse_args()
    dispatch_command(commands, parser, args, options)
