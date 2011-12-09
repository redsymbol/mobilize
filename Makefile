API_DOC_DIR=doc/api

clean:
	rm -f $$(find . -name '*.pyc' -o -name '*~')
	rm -fr $$(find . -name __pycache__ -type d)
test:
	nosetests
test-pdb:
	nosetests --pdb
doc-api:
	rm -rf $(API_DOC_DIR)
	mkdir -p $(API_DOC_DIR)
	epydoc -v --output $(API_DOC_DIR) mobilize

locdevpublish: clean
	locdevpublish.sh ./mobilize /var/www/share/mobilize-libs/dev/

co:
	rm -rf pack pack.tgz
	git checkout-index -a --prefix=pack/

pack: co
	tar zcf pack.tgz pack
	rm -rf pack
