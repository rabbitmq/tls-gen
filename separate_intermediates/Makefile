# -*- mode: BSDmakefile; tab-width: 8; indent-tabs-mode: nil -*-

OPENSSL=openssl

ifndef PYTHON
PYTHON := python3
endif

ifndef CN
CN := $(shell hostname)
endif

ifndef NUMBER_OF_PRIVATE_KEY_BITS
NUMBER_OF_PRIVATE_KEY_BITS := 4096
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

all: regen verify

clean:
	$(PYTHON) profile.py clean

gen:
	$(PYTHON) profile.py generate   --password $(PASSWORD) --common-name $(CN) -V $(DAYS_OF_VALIDITY) $(ECC_FLAGS)

regen:
	$(PYTHON) profile.py regenerate --password $(PASSWORD) --common-name $(CN) -V $(DAYS_OF_VALIDITY) $(ECC_FLAGS)

info:
	$(PYTHON) profile.py info

verify:
	$(PYTHON) profile.py verify

help:
	$(PYTHON) profile.py --help
