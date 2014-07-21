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

.PRECIOUS: %/testca
.PHONY: %/clean target all p12pass

all: client server copy announce

regen: clean all

client: p12pass
	@echo Using $(CN) as CN value.
	$(MAKE) target DIR=$(DIR) TARGET=client EXTENSIONS=client_ca_extensions CN=$(CN)

server: p12pass
	@echo Using $(CN) as CN value.
	$(MAKE) target DIR=$(DIR) TARGET=server EXTENSIONS=server_ca_extensions CN=$(CN)

p12pass:
	$(P12PASS)

target: $(DIR)/testca
	mkdir $(DIR)/$(TARGET)
	{ ( cd $(DIR)/$(TARGET) && \
	    openssl genrsa -out key.pem 2048 &&\
	    openssl req -new -key key.pem -out req.pem -days 3650 -outform PEM\
		-subj /CN=$(CN)/O=$(TARGET)/L=$$$$/ -nodes &&\
	    cd ../testca && \
	    openssl ca -config openssl.cnf  -days 3650 -in ../$(TARGET)/req.pem -out \
	      ../$(TARGET)/cert.pem -notext -batch -extensions \
	      $(EXTENSIONS) && \
	    cd ../$(TARGET) && \
	    openssl pkcs12 -export -out keycert.p12 -in cert.pem -inkey key.pem \
	      -passout pass:$(PASSWORD) ) || (rm -rf $(DIR)/$(TARGET) && false); }

$(DIR)/testca:
	mkdir $(DIR)/testca
	cp openssl.cnf $(DIR)/testca/openssl.cnf
	{ ( cd $(DIR)/testca && \
	    mkdir certs private && \
	    chmod 700 private && \
	    echo 01 > serial && \
	    touch index.txt && \
	    openssl req -x509 -days 3650 -config openssl.cnf -newkey rsa:2048 \
	      -out cacert.pem -outform PEM -subj /CN=MyTestRootCA/L=$$$$/ -nodes && \
	    openssl x509 -in cacert.pem -out cacert.cer -outform DER ) \
	  || (rm -rf $@ && false); }

clean:
	rm -rf $(DIR)/testca
	rm -rf $(DIR)/server
	rm -rf $(DIR)/client
	rm -rf $(DIR)/result

copy:
	mkdir -p result
	cp $(DIR)/testca/cacert.pem        result/ca_certificate.pem
	cp $(DIR)/testca/private/cakey.pem result/ca_key.pem
	cp $(DIR)/server/cert.pem    result/server_certificate.pem
	cp $(DIR)/server/key.pem     result/server_key.pem
	cp $(DIR)/server/keycert.p12 result/server_key.p12
	cp $(DIR)/client/cert.pem    result/client_certificate.pem
	cp $(DIR)/client/key.pem     result/client_key.pem
	cp $(DIR)/client/keycert.p12 result/client_key.p12

announce:
	$(info Done! Find generated certificates and private keys under ./result!)

verify:
	@echo "Will verify generated certificates against the CA..."
	openssl verify -CAfile result/ca_certificate.pem result/server_certificate.pem
	openssl verify -CAfile result/ca_certificate.pem result/client_certificate.pem

verify-pkcs12:
	@echo "Will verify PKCS12 stores..."
	keytool -v -list -storetype pkcs12 -keystore result/server_key.p12
	keytool -v -list -storetype pkcs12 -keystore result/client_key.p12
