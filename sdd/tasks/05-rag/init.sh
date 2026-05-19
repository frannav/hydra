#!/bin/bash
# Setup script for HYDRA RAG mission
# Idempotent — safe to run multiple times

set -e

cd backend

# Ensure data directories exist
mkdir -p data/fixtures
mkdir -p data/outputs

# Ensure .gitkeep files exist
touch data/fixtures/.gitkeep
touch data/outputs/.gitkeep

echo "Setup complete"
