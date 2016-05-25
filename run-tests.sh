#!/bin/sh
set -e

env PYTHONPATH=. python3 test/test_kea.py
