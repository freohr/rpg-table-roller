dist/rolltable: **/*.py
	pyinstaller -n rolltable -F rolltable/__main__.py

clean:
	rm -rf build/

init:
	pip install -r requirements.txt
	
test:
	pytest

