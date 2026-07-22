PYTHON ?= python3

.PHONY: build validate subsets package posters fontbakery test test-update release

build:
	$(PYTHON) scripts/build_zutat_sans_v0.6.py
	$(PYTHON) scripts/build_zutat_sans_web_subsets.py

validate:
	$(PYTHON) scripts/validate_zutat_sans_v0.6.py

subsets:
	$(PYTHON) scripts/build_zutat_sans_web_subsets.py

package: build
	$(PYTHON) scripts/package_zutat_font_npm.py

posters: build
	$(PYTHON) scripts/render_zutat_sans_v0.6.py
	$(PYTHON) scripts/render_zutat_posters.py

fontbakery: build
	mkdir -p reports
	$(PYTHON) -m fontbakery check-universal build/zutat-font-v0.6/*.ttf --loglevel WARN --no-progress --html reports/ZutatSans-v0.6-FontBakery.html
	$(PYTHON) -m fontbakery check-universal build/zutat-font-v0.6/*.otf --loglevel WARN --no-progress --html reports/ZutatSans-v0.6-FontBakery-OTF.html

test: build validate
	cd qa/browser && npm ci && npm test

test-update: build validate
	cd qa/browser && npm ci && npm run test:update

release: package posters validate
	mkdir -p releases
	cd build/zutat-font-v0.6 && zip -q -r ../../releases/ZutatSans-Family-0.6.zip .
	cd packages/zutat-font && npm pack --pack-destination ../../releases
