API_DOC_DIR=doc/api

clean:
	rm $$(find . -name '*.pyc' -o -name '*~')
test:
	nosetests
test-pdb:
	nosetests --pdb
doc-api:
	rm -rf $(API_DOC_DIR)
	mkdir -p $(API_DOC_DIR)
	epydoc -v --output $(API_DOC_DIR) mobilize