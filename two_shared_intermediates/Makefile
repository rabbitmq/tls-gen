# -*- mode: BSDmakefile; tab-width: 8; indent-tabs-mode: nil -*-

OPENSSL=openssl

ifndef DIR
DIR := $(shell pwd)
endif

ifndef CN
CN := $(shell hostname)
endif

ifdef PASSWORD
ENSURE_PASSPHRASE := true
else
ENSURE_PASSPHRASE := @echo No PASSWORD defined. && false
endif

ifndef NUMBER_OF_PRIVATE_KEY_BITS
NUMBER_OF_PRIVATE_KEY_BITS := 4096
endif

ifndef DAYS_OF_VALIDITY
DAYS_OF_VALIDITY := 3650
endif

.PRECIOUS: %/root_ca
.PHONY: %/clean target all ensure_passphrase

all: cas client server copy announce

regen: clean all

info:
	@echo "===> Server certificate details:"
	openssl x509 -in $(SERVER_CERT_LOCATION) -text -noout
	@echo "\n\n===> Client certificate details:"
	openssl x509 -in $(CLIENT_CERT_LOCATION) -text -noout

cas: ensure_passphrase root_ca intermediate_ca1 intermediate_ca2 concat

client: ensure_passphrase
	@echo Using $(CN) as CN value.
	$(MAKE) target DIR=$(DIR) TARGET=client EXTENSIONS=client_extensions CN=$(CN)

server: ensure_passphrase
	@echo Using $(CN) as CN value.
	$(MAKE) target DIR=$(DIR) TARGET=server EXTENSIONS=server_extensions CN=$(CN)

ensure_passphrase:
	$(ENSURE_PASSPHRASE)

ROOT_CA_KEY  = $(DIR)/root_ca/private/root_ca_key.pem
ROOT_CA_CERT = $(DIR)/root_ca/certs/root_ca_certificate.pem

target: cas
	mkdir $(DIR)/$(TARGET)
	{ ( cd $(DIR)/$(TARGET) && \
	    $(OPENSSL) genrsa -out key.pem $(NUMBER_OF_PRIVATE_KEY_BITS) &&\
	    $(OPENSSL) req -new -key key.pem -out req.pem -days $(DAYS_OF_VALIDITY) -outform PEM\
		-subj /CN=$(CN)/O=$(TARGET)/L=$$$$/ -nodes && \
	    cd ../intermediate_ca2 && \
	    $(OPENSSL) ca -config openssl.cnf  -days $(DAYS_OF_VALIDITY) -in ../$(TARGET)/req.pem \
	        -out ../$(TARGET)/cert.pem \
		-key $(INTERMEDIATE_CA2_KEY) -cert $(INTERMEDIATE_CA2_CERT) \
	        -notext -batch -extensions $(EXTENSIONS) && \
	    cd ../$(TARGET) && \
	    $(OPENSSL) pkcs12 -export -out keycert.p12 -in cert.pem -inkey key.pem \
	      -passout pass:$(PASSWORD) ) || (rm -rf $(DIR)/$(TARGET) && false); }

root_ca:
	mkdir $(DIR)/root_ca
	cp openssl.cnf $(DIR)/root_ca/openssl.cnf
	{ ( cd $(DIR)/root_ca && \
	    mkdir certs private && \
	    chmod 700 private && \
	    echo 01 > serial && \
	    touch index.txt && \
	    $(OPENSSL) genrsa -out $(ROOT_CA_KEY) $(NUMBER_OF_PRIVATE_KEY_BITS) && \
	    $(OPENSSL) req -x509 -config openssl.cnf -new \
		-key $(ROOT_CA_KEY) \
		-out $(ROOT_CA_CERT) -subj /CN=MyTestRootCA/ && \
	    $(OPENSSL) x509 -days $(DAYS_OF_VALIDITY) \
			-in $(ROOT_CA_CERT) \
                        -out certs/root_ca_certificate.cer \
			-outform DER -extensions ca_extensions ) || (rm -rf $@ && false); }

INTERMEDIATE_CA1_KEY  = $(DIR)/intermediate_ca1/private/cakey.pem
INTERMEDIATE_CA1_CERT = $(DIR)/intermediate_ca1/certs/cacert.pem

INTERMEDIATE_CA2_KEY  = $(DIR)/intermediate_ca2/private/cakey.pem
INTERMEDIATE_CA2_CERT = $(DIR)/intermediate_ca2/certs/cacert.pem

ROOT_INTERMEDIATE1_CHAINED_CERT = $(DIR)/intermediate_ca2/certs/i1_r_chained_certificate.pem
FULLY_CHAINED_CERT              = $(DIR)/intermediate_ca2/certs/i2_i1_r_chained_certificate.pem

intermediate_ca1:
	@echo "Will generate intermediate CA 1"
	$(MAKE) intermediate_ca N=1 PARENT_KEY=$(ROOT_CA_KEY) PARENT_CERT=$(ROOT_CA_CERT) DIR=$(DIR) CN=MyIntermediateCA1
	@echo "\n\nWill verify intermediate CA 1"
	$(OPENSSL) verify -CAfile $(ROOT_CA_CERT) $(INTERMEDIATE_CA1_CERT)
	@echo "\n\n----------------------------------------------------------------------------------------------\n\n"

intermediate_ca2:
	@echo "Will generate intermediate CA 2"
	$(MAKE) intermediate_ca N=2 PARENT_KEY=$(INTERMEDIATE_CA1_KEY) PARENT_CERT=$(INTERMEDIATE_CA1_CERT) DIR=$(DIR) CN=MyIntermediateCA2
	cat $(INTERMEDIATE_CA1_CERT) $(ROOT_CA_CERT) > $(ROOT_INTERMEDIATE1_CHAINED_CERT)
	@echo "Will verify intermediate CA 2\n\n"
	$(OPENSSL) verify -CAfile $(ROOT_INTERMEDIATE1_CHAINED_CERT) \
	           $(INTERMEDIATE_CA2_CERT)

intermediate_ca:
	mkdir $(DIR)/intermediate_ca$(N)
	cp openssl.cnf $(DIR)/intermediate_ca$(N)/openssl.cnf
	{ ( cd $(DIR)/intermediate_ca$(N) && \
	    mkdir certs private && \
	    chmod 700 private && \
	    echo 01 > serial && \
	    touch index.txt && \
	    $(OPENSSL) genrsa -out $(DIR)/intermediate_ca$(N)/private/cakey.pem $(NUMBER_OF_PRIVATE_KEY_BITS) && \
	    $(OPENSSL) req -config openssl.cnf -new \
	            -key $(DIR)/intermediate_ca$(N)/private/cakey.pem \
	            -out $(DIR)/intermediate_ca$(N)/certs/ca_csr.pem \
		    -passin pass:$(PASSWORD) \
		    -subj /CN=$(CN)/O=$(TARGET)/L=$$$$/ && \
	   $(OPENSSL) ca -config openssl.cnf -days $(DAYS_OF_VALIDITY) \
		           -keyfile $(PARENT_KEY) \
		           -cert    $(PARENT_CERT) \
		           -in      $(DIR)/intermediate_ca$(N)/certs/ca_csr.pem \
		           -out     $(DIR)/intermediate_ca$(N)/certs/cacert.pem \
		           -notext -md sha1 -batch -extensions ca_extensions ) || (rm -rf $@ &&  false); }

concat: 
	cat $(INTERMEDIATE_CA2_CERT) $(INTERMEDIATE_CA1_CERT) $(ROOT_CA_CERT) > $(FULLY_CHAINED_CERT)

clean:
	rm -rf $(DIR)/root_ca
	rm -rf $(DIR)/intermediate_ca1
	rm -rf $(DIR)/intermediate_ca2
	rm -rf $(DIR)/server
	rm -rf $(DIR)/client
	rm -rf $(DIR)/result

ROOT_CA_CERT_LOCATION = result/root_ca_certificate.pem
ROOT_CA_KEY_LOCATION  = result/root_ca_key.pem
INT1_CA_CERT_LOCATION = result/intermediate_ca1_certificate.pem
INT1_CA_KEY_LOCATION  = result/intermediate_ca1_key.pem
INT2_CA_CERT_LOCATION = result/intermediate_ca2_certificate.pem
INT2_CA_KEY_LOCATION  = result/intermediate_ca2_key.pem

CHAINED_CA_CERTIFICATE_LOCATION = result/chained_ca_certificate.pem

CLIENT_CERT_LOCATION  = result/client_certificate.pem
SERVER_CERT_LOCATION  = result/server_certificate.pem

copy:
	mkdir -p result
	cp $(ROOT_CA_CERT) $(ROOT_CA_CERT_LOCATION)
	cp $(ROOT_CA_KEY)  $(ROOT_CA_KEY_LOCATION)

	cp $(INTERMEDIATE_CA1_CERT) $(INT1_CA_CERT_LOCATION)
	cp $(INTERMEDIATE_CA1_KEY)  $(INT1_CA_KEY_LOCATION)

	cp $(INTERMEDIATE_CA2_CERT) $(INT2_CA_CERT_LOCATION)
	cp $(INTERMEDIATE_CA2_KEY)  $(INT2_CA_KEY_LOCATION)

	cp $(FULLY_CHAINED_CERT)    $(CHAINED_CA_CERTIFICATE_LOCATION)

	cp $(DIR)/server/cert.pem    $(SERVER_CERT_LOCATION)
	cp $(DIR)/server/key.pem     result/server_key.pem
	cp $(DIR)/server/keycert.p12 result/server_key.p12
	cp $(DIR)/client/cert.pem    $(CLIENT_CERT_LOCATION)
	cp $(DIR)/client/key.pem     result/client_key.pem
	cp $(DIR)/client/keycert.p12 result/client_key.p12

announce:
	$(info Done! Find generated certificates and private keys under ./result!)

verify:
	@echo "Will verify generated certificates against the CA..."
	$(OPENSSL) verify -CAfile $(CHAINED_CA_CERTIFICATE_LOCATION) $(SERVER_CERT_LOCATION)
	$(OPENSSL) verify -CAfile $(CHAINED_CA_CERTIFICATE_LOCATION) $(CLIENT_CERT_LOCATION)

verify-pkcs12:
	@echo "Will verify PKCS12 stores..."
	keytool -v -list -storetype pkcs12 -keystore result/server_key.p12
	keytool -v -list -storetype pkcs12 -keystore result/client_key.p12
