dist/rolltable: clean **/*.py
	pyinstaller -n rolltable -F rolltable/__main__.py

clean:
	rm -rf build/

init:
	pip install -r requirements.txt
	
test:
	pytest

install: dist/rolltable
	install-local-bin dist/rolltable

