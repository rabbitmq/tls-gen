# -*- mode: BSDmakefile; tab-width: 8; indent-tabs-mode: nil -*-

OPENSSL=openssl

ifndef DIR
DIR := .
endif

ifndef CN
CN := $(shell hostname)
endif

ifdef PASSWORD
P12PASS := true
else
P12PASS := @echo No PASSWORD defined. && false
endif

ifndef NUMBER_OF_PRIVATE_KEY_BITS
NUMBER_OF_PRIVATE_KEY_BITS := 4096
endif

ifndef DAYS_OF_VALIDITY
DAYS_OF_VALIDITY := 3650
endif

.PRECIOUS: %/testca
.PHONY: %/clean target all p12pass

all: client server copy announce

regen: clean all

client: p12pass
	@echo Using $(CN) as CN value.
	$(MAKE) target DIR=$(DIR) TARGET=client EXTENSIONS=client_extensions CN=$(CN)

server: p12pass
	@echo Using $(CN) as CN value.
	$(MAKE) target DIR=$(DIR) TARGET=server EXTENSIONS=server_extensions CN=$(CN)

p12pass:
	$(P12PASS)

target: $(DIR)/testca
	mkdir $(DIR)/$(TARGET)
	{ ( cd $(DIR)/$(TARGET) && \
	    $(OPENSSL) genrsa -out key.pem $(NUMBER_OF_PRIVATE_KEY_BITS) &&\
	    $(OPENSSL) req -new -key key.pem -out req.pem -days $(DAYS_OF_VALIDITY) -outform PEM\
		-subj /CN=$(CN)/O=$(TARGET)/L=$$$$/ -nodes &&\
	    cd ../testca && \
	    $(OPENSSL) ca -config openssl.cnf  -days $(DAYS_OF_VALIDITY) -in ../$(TARGET)/req.pem -out \
	      ../$(TARGET)/cert.pem -notext -batch -extensions \
	      $(EXTENSIONS) && \
	    cd ../$(TARGET) && \
	    $(OPENSSL) pkcs12 -export -out keycert.p12 -in cert.pem -inkey key.pem \
	      -passout pass:$(PASSWORD) ) || (rm -rf $(DIR)/$(TARGET) && false); }

$(DIR)/testca:
	mkdir $(DIR)/testca
	cp openssl.cnf $(DIR)/testca/openssl.cnf
	{ ( cd $(DIR)/testca && \
	    mkdir certs private && \
	    chmod 700 private && \
	    echo 01 > serial && \
	    touch index.txt && \
	    $(OPENSSL) req -x509 -days $(DAYS_OF_VALIDITY) -config openssl.cnf -newkey rsa:$(NUMBER_OF_PRIVATE_KEY_BITS) \
	      -out cacert.pem -outform PEM -subj /CN=MyTestRootCA/L=$$$$/ -nodes && \
	    $(OPENSSL) x509 -in cacert.pem -out cacert.cer -outform DER ) \
	  || (rm -rf $@ && false); }

clean:
	rm -rf $(DIR)/testca
	rm -rf $(DIR)/server
	rm -rf $(DIR)/client
	rm -rf $(DIR)/result

CA_CERT_LOCATION     = result/ca_certificate.pem
CLIENT_CERT_LOCATION = result/client_certificate.pem
SERVER_CERT_LOCATION = result/server_certificate.pem

copy:
	mkdir -p result
	cp $(DIR)/testca/cacert.pem        $(CA_CERT_LOCATION)
	cp $(DIR)/testca/private/cakey.pem result/ca_key.pem
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
