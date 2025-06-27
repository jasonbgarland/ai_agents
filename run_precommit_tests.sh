#!/bin/bash
set -e

# Run all unit tests
.venv/bin/python -m unittest discover -s tests
