import os
import sys

# Ensure the project root is on sys.path so that `pages`, `config`, and
# `utils` packages are importable regardless of the working directory from
# which pytest is invoked.
sys.path.insert(0, os.path.dirname(__file__))
