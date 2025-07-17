echo "Generating documentation with pdoc..."

pdoc \
  config \
  managers \
  resources \
  services \
  utils \
  validators \
  -o docs

echo "Adding docs/ to Git..."
git add docs/
git commit -m "docs: update full project documentation"
git push

echo "Documentation published at:"
echo "https://krumyakimov.github.io/Integration-File-Processor-Async/"
