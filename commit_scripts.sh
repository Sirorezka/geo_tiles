black .
black --ipynb *.ipynb
isort .
echo "Running pydocstyle..."
pydocstyle .
echo "Running pylint..."
pylint src/*.py
echo "Running mypy..."
mypy src/*.py