#!/bin/bash
#SBATCH --job-name=gauge_download
#SBATCH --output=logs/download_%A_%a.out
#SBATCH --error=logs/download_%A_%a.err
#SBATCH --time=04:00:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=1
#SBATCH --array=0-6
#
# GaugePredict Data Download - SLURM Submission Script
#
# This script submits download jobs as a SLURM array.
# Each array task downloads data for one HUC region.
#
# HUC codes (array indices):
#   0 = HUC 05
#   1 = HUC 06
#   2 = HUC 07
#   3 = HUC 08
#   4 = HUC 09
#   5 = HUC 10
#   6 = HUC 11
#
# Usage:
#   sbatch submit_download.sh              # Run all HUC codes as array
#   sbatch --array=0-2 submit_download.sh  # Run only HUC 05, 06, 07
#   sbatch --array=3 submit_download.sh    # Run only HUC 08
#
# To run all at once (not as array):
#   sbatch --array=0 submit_download.sh --all
#

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Create logs directory if it doesn't exist
mkdir -p "${SCRIPT_DIR}/logs"

# Print job info
echo "=========================================="
echo "SLURM Job ID: ${SLURM_JOB_ID}"
echo "SLURM Array Task ID: ${SLURM_ARRAY_TASK_ID}"
echo "Running on host: $(hostname)"
echo "Start time: $(date)"
echo "Working directory: ${PROJECT_DIR}"
echo "=========================================="

# Change to project directory
cd "${PROJECT_DIR}"

# Load required modules (adjust for your HPC environment)
# Common module systems - uncomment/modify as needed:
#
# For systems using Environment Modules:
# module purge
# module load python/3.11
# module load gdal
#
# For systems using Lmod:
# module purge
# module load Python/3.11
# module load GDAL
#
# For conda-based environments:
# source ~/.bashrc
# conda activate gaugepredict

# Activate virtual environment if it exists
if [ -d "${PROJECT_DIR}/.venv" ]; then
    echo "Activating virtual environment..."
    source "${PROJECT_DIR}/.venv/bin/activate"
fi

# Check if running with --all flag
if [[ "$1" == "--all" ]]; then
    echo "Running all HUC codes in single job..."
    python "${SCRIPT_DIR}/downloader_slurm.py" --all --skip-target
else
    # Run for specific array index
    echo "Processing array index: ${SLURM_ARRAY_TASK_ID}"
    python "${SCRIPT_DIR}/downloader_slurm.py" \
        --array-index "${SLURM_ARRAY_TASK_ID}" \
        --skip-target
fi
uv run examples/scripts/downloader_slurm.py --data_dir = data

echo "=========================================="
echo "Finished at: $(date)"
echo "=========================================="
