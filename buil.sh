#!/bin/bash
set -e

echo "==> Upgrading pip, setuptools, wheel..."
pip install --upgrade pip setuptools wheel

echo "==> Installing dependencies with precompiled wheels only..."
pip install --only-binary :all: -r requirements.txt || {
    echo "==> Precompiled wheels unavailable, installing normally..."
    pip install -r requirements.txt
}

echo "==> Build complete!"