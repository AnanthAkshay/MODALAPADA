# Makefile for Gaade Kosha (Problem 2, Modalapada 2.0)
# Department of CSE&E, Ramaiah Institute of Technology

.PHONY: all install build index run dev test validate submission docker-build docker-run clean help

PYTHON ?= python
NPM ?= npm
PORT ?= 8000

help:
	@echo "Gaade Kosha - Available Commands:"
	@echo "  make install     - Install Python & Node.js dependencies"
	@echo "  make build       - Build React frontend production assets"
	@echo "  make index       - Rebuild precomputed TF-IDF / BM25 search index"
	@echo "  make run         - Run unified application on http://localhost:8000 (API + UI)"
	@echo "  make dev         - Run FastAPI backend in reload mode on port 8000"
	@echo "  make test        - Run backend test suite (pytest)"
	@echo "  make validate    - Run full 6-phase system validation suite"
	@echo "  make submission  - Run validation and generate submission/ package with checksums"
	@echo "  make docker-build- Build Docker container image"
	@echo "  make docker-run  - Run Docker container on port 8000"

install:
	$(PYTHON) -m pip install -r requirements.txt
	$(NPM) --prefix frontend install

build:
	$(NPM) --prefix frontend run build

index:
	$(PYTHON) scripts/build_index.py --backend tfidf

run:
	$(PYTHON) -m uvicorn backend.app.main:app --host 0.0.0.0 --port $(PORT)

dev:
	$(PYTHON) -m uvicorn backend.app.main:app --reload --port $(PORT)

test:
	$(PYTHON) -m pytest backend/tests -v

validate:
	$(PYTHON) scripts/run_full_validation.py

submission:
	$(PYTHON) scripts/build_submission.py

docker-build:
	docker build -t gaade-kosha .

docker-run:
	docker run -p $(PORT):8000 gaade-kosha

clean:
	rm -rf frontend/dist submission/ .pytest_cache/

