# Run the FastAPI app with auto-reload
run:
	uvicorn app.main:app --reload

# Run tests with correct PYTHONPATH
test:
	PYTHONPATH=. pytest tests/

# Run install to install all requirements
install:
	pip freeze > requirements.txt

# Run freeze to update requirements.txt
freeze:
	pip freeze > requirements.txt