include ../common.mk

gen-crl:
	$(OPENSSL) ca -config openssl.cnf -gencrl -keyfile $(CURDIR)/testca/private/cakey.pem -cert $(CURDIR)/testca/cacert.pem -out $(CURDIR)/result/basic.crl.pem
	$(OPENSSL) crl -inform PEM -in $(CURDIR)/result/basic.crl.pem -outform DER -out $(CURDIR)/result/basic.crl

server:
	openssl s_server -cert $(CURDIR)/result/server_$(CN)_certificate.pem -key $(CURDIR)/result/server_$(CN)_key.pem -CAfile $(CURDIR)/result/ca_certificate.pem

client:
	openssl s_client -cert $(CURDIR)/result/client_$(CN)_certificate.pem  -key $(CURDIR)/result/client_$(CN)_key.pem -CAfile $(CURDIR)/result/ca_certificate.pem -verify 8 -verify_hostname $(CN)
