echo "Generating documentation with pdoc..."
pdoc integration_file_processor_async --html --output-dir docs

echo "Adding docs/ to Git..."
git add docs/
git commit -m "docs: update generated documentation"
git push

echo "Documentation published at:"
echo "https://krumyakimov.github.io/Integration-File-Processor-Async/"
