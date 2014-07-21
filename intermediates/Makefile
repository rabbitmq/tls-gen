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

.PRECIOUS: %/root_ca
.PHONY: %/clean target all ensure_passphrase

all: cas client server copy announce

regen: clean all

cas: ensure_passphrase root_ca intermediate_ca1 intermediate_ca2

client: ensure_passphrase
	@echo Using $(CN) as CN value.
	$(MAKE) target DIR=$(DIR) TARGET=client EXTENSIONS=client_extensions CN=$(CN)

server: ensure_passphrase
	@echo Using $(CN) as CN value.
	$(MAKE) target DIR=$(DIR) TARGET=server EXTENSIONS=server_extensions CN=$(CN)

ensure_passphrase:
	$(ENSURE_PASSPHRASE)

target: root_ca
	intermediate_ca1
	intermediate_ca2
	mkdir $(DIR)/$(TARGET)
	{ ( cd $(DIR)/$(TARGET) && \
	    $(OPENSSL) genrsa -out key.pem 2048 &&\
	    $(OPENSSL) req -new -key key.pem -out req.pem -days 3650 -outform PEM\
		-subj /CN=$(CN)/O=$(TARGET)/L=$$$$/ -nodes &&\
	    cd ../root_ca && \
	    $(OPENSSL) ca -config openssl.cnf  -days 3650 -in ../$(TARGET)/req.pem -out \
	      ../$(TARGET)/cert.pem -notext -batch -extensions \
	      $(EXTENSIONS) && \
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
	    $(OPENSSL) genrsa -out private/root_ca_key.pem 2048 && \
	    $(OPENSSL) req -x509 -config openssl.cnf -new \
		-key private/root_ca_key.pem \
		-out certs/root_ca_certificate.pem -subj /CN=MyTestRootCA/ && \
	    $(OPENSSL) x509 -days 3650 \
			-in certs/root_ca_certificate.pem \
                        -out certs/root_ca_certificate.cer \
			-outform DER ) || (rm -rf $@ && false); }

intermediate_ca1:
	@echo "Will generate intermediate CA 1"
	$(MAKE) intermediate_ca N=1 PARENT_KEY=$(DIR)/root_ca/private/root_ca_key.pem PARENT_CERT=$(DIR)/root_ca/certs/root_ca_certificate.pem DIR=$(DIR) CN=$(CN)
	$(OPENSSL) verify -CAfile $(DIR)/root_ca/certs/root_ca_certificate.pem \
	           $(DIR)/intermediate_ca$(N)/certs/intermediate_ca_certificate.pem

intermediate_ca2:
	@echo "Will generate intermediate CA 2"
	$(MAKE) intermediate_ca N=2 PARENT_KEY=$(DIR)/intermediate_ca1/private/intermediate_ca_key.pem PARENT_CERT=$(DIR)/intermediate_ca1/certs/intermediate_ca_certificate.pem DIR=$(DIR) CN=$(CN)
	$(OPENSSL) verify -CAfile $(DIR)/root_ca/certs/root_ca_certificate.pem \
			  -CAfile $(DIR)/intermediate_ca1/certs/intermediate_ca_certificate.pem \
	           $(DIR)/intermediate_ca2/certs/intermediate_ca_certificate.pem

intermediate_ca:
	mkdir $(DIR)/intermediate_ca$(N)
	cp openssl.cnf $(DIR)/intermediate_ca$(N)/openssl.cnf
	{ ( cd $(DIR)/intermediate_ca$(N) && \
	    mkdir certs private && \
	    chmod 700 private && \
	    echo 01 > serial && \
	    touch index.txt && \
	    $(OPENSSL) genrsa -out $(DIR)/intermediate_ca$(N)/private/intermediate_ca_key.pem 2048 && \
	    $(OPENSSL) req -config openssl.cnf -new \
	            -key $(DIR)/intermediate_ca$(N)/private/intermediate_ca_key.pem \
	            -out $(DIR)/intermediate_ca$(N)/certs/intermediate_ca_csr.pem \
		    -passin pass:$(PASSWORD) && \
	   $(OPENSSL) ca -config openssl.cnf -days 3650 \
		           -keyfile $(PARENT_KEY) \
		           -cert    $(PARENT_CERT) \
		           -in      $(DIR)/intermediate_ca$(N)/certs/intermediate_ca_csr.pem \
		           -out     $(DIR)/intermediate_ca$(N)/certs/intermediate_ca_certificate.pem \
		           -notext -md sha1 -batch -extensions ca_extensions ) || (rm -rf $@ &&  false); }

clean:
	rm -rf $(DIR)/root_ca
	rm -rf $(DIR)/intermediate_ca1
	rm -rf $(DIR)/intermediate_ca2
	rm -rf $(DIR)/server
	rm -rf $(DIR)/client
	rm -rf $(DIR)/result

ROOT_CA_CERT_LOCATION = result/root_ca_certificate.pem
INT1_CA_CERT_LOCATION = result/intermediate_ca1_certificate.pem
INT1_CA_KEY_LOCATION  = result/intermediate_ca1_key.pem
INT2_CA_CERT_LOCATION = result/intermediate_ca2_certificate.pem
INT2_CA_KEY_LOCATION  = result/intermediate_ca2_key.pem

CLIENT_CERT_LOCATION  = result/client_certificate.pem
SERVER_CERT_LOCATION  = result/server_certificate.pem

copy:
	mkdir -p result
	cp $(DIR)/root_ca/cacert.pem        $(CA_CERT_LOCATION)
	cp $(DIR)/root_ca/private/cakey.pem result/root_ca_key.pem

	cp $(DIR)/intermediate1_ca/cacert.pem        $(CA_CERT_LOCATION)
	cp $(DIR)/intermediate1_ca/private/cakey.pem result/root_ca_key.pem

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
	$(OPENSSL) verify -CAfile $(CA_CERT_LOCATION) $(SERVER_CERT_LOCATION)
	$(OPENSSL) verify -CAfile $(CA_CERT_LOCATION) $(CLIENT_CERT_LOCATION)

verify-pkcs12:
	@echo "Will verify PKCS12 stores..."
	keytool -v -list -storetype pkcs12 -keystore result/server_key.p12
	keytool -v -list -storetype pkcs12 -keystore result/client_key.p12
