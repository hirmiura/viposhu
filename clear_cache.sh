#!/bin/bash

\find . | \grep -E "(__pycache__|\.pyc|\.pyo|\.mypy_cache|\.pytest_cache$)" | \xargs rm -rf
