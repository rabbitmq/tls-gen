# -*- mode: BSDmakefile; tab-width: 8; indent-tabs-mode: nil -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2007-2014 VMware, Inc. or its affiliates. All rights reserved.
# Copyright (c) 2014-2020 Michael Klishin and contributors.

OPENSSL = openssl

ifndef PYTHON
PYTHON := python3
endif

ifndef CN
CN := $(shell hostname)
endif

ifndef CLIENT_ALT_NAME
CLIENT_ALT_NAME := $(shell hostname)
endif

ifndef SERVER_ALT_NAME
SERVER_ALT_NAME := $(shell hostname)
endif

ifndef NUMBER_OF_PRIVATE_KEY_BITS
NUMBER_OF_PRIVATE_KEY_BITS := 2048
endif

ifndef DAYS_OF_VALIDITY
DAYS_OF_VALIDITY := 3650
endif

ifndef ECC_CURVE
ECC_CURVE := "prime256v1"
endif

ifndef USE_ECC
USE_ECC := false
endif

ifeq ($(USE_ECC),true)
ECC_FLAGS := --use-ecc --ecc-curve $(ECC_CURVE)
endif

PASS := ""
ifdef PASSWORD
PASS = "$(PASSWORD)"
endif

all: regen verify

clean:
	$(PYTHON) profile.py clean

gen:
	$(PYTHON) profile.py generate --password $(PASS) \
	--common-name $(CN) \
	--client-alt-name $(CLIENT_ALT_NAME) \
	--server-alt-name $(SERVER_ALT_NAME) \
	--days-of-validity $(DAYS_OF_VALIDITY) \
	--key-bits $(NUMBER_OF_PRIVATE_KEY_BITS) $(ECC_FLAGS)

gen-client:
	$(PYTHON) profile.py generate-client --password $(PASS) \
	--common-name $(CN) \
	--client-alt-name $(CLIENT_ALT_NAME) \
	--days-of-validity $(DAYS_OF_VALIDITY) \
	--key-bits $(NUMBER_OF_PRIVATE_KEY_BITS) $(ECC_FLAGS)

regen:
	$(PYTHON) profile.py regenerate --password $(PASS) \
	--common-name $(CN) \
	--client-alt-name $(CLIENT_ALT_NAME) \
	--server-alt-name $(SERVER_ALT_NAME) \
	--days-of-validity $(DAYS_OF_VALIDITY) \
	--key-bits $(NUMBER_OF_PRIVATE_KEY_BITS) $(ECC_FLAGS)

info:
	$(PYTHON) profile.py info

verify:
	$(PYTHON) profile.py verify

help:
	$(PYTHON) profile.py --help
