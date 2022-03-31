include ../common.mk

PASSWORD ?= test1234

keystore:
	keytool -noprompt -import -trustcacerts -keystore truststore.jks \
		-file testca/cacert.pem -alias ca_certificate -storepass $(PASSWORD) || true
	keytool -noprompt -import -trustcacerts -keystore truststore.jks \
		-file server_$(CN)/cert.pem -alias server_$(CN)_certificate -storepass $(PASSWORD) || true
	keytool -noprompt -import -trustcacerts -keystore truststore.jks \
		-file server_$(CN)/key.pem -alias server_$(CN)_key -storepass $(PASSWORD) || true
	keytool -noprompt -import -trustcacerts -keystore truststore.jks \
		-file client_$(CN)/cert.pem -alias server_$(CN)_certificate -storepass $(PASSWORD) || true
	keytool -noprompt -import -trustcacerts -keystore truststore.jks \
		-file client_$(CN)/key.pem -alias server_$(CN)_key -storepass $(PASSWORD) || true
