# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2007-2014 VMware, Inc. or its affiliates. All rights reserved.
# Copyright (c) 2014-2020 Michael Klishin and contributors.

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
