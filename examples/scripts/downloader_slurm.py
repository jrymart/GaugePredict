"""
GaugePredict Data Downloader - SLURM HPC Version
Download and process USGS gauge data for the Mississippi River Basin.

This script is designed to run on HPC clusters with SLURM.
It can process individual HUC codes via SLURM array jobs.

Usage:
    python downloader_slurm.py --huc 05           # Single HUC
    python downloader_slurm.py --huc 05 06 07     # Multiple HUCs
    python downloader_slurm.py --all              # All default HUCs
    python downloader_slurm.py --array-index 0    # For SLURM array jobs
"""

import argparse
import sys
import numpy as np
import pandas as pd
from dataretrieval import nwis
from GaugePredict.downloader import load_target, GaugebyHUC
from pathlib import Path

# Default configuration
DEFAULT_HUC_CODES = ["05", "06", "07", "08", "09", "10", "11"]
PARAMETER = "discharge"
PARAMETER_CODE = "00060"
TARGET_SITE = "07374000"  # Baton Rouge
START_DATE = "2005-01-02"
END_DATE = "2024-12-31"
UNITS = "metric"
PERCENT_THRESHOLD = 95
SITE_TYPE = "ST"


def setup_directories(base_dir: Path, parameter: str):
    """Setup data directories."""
    data_dir = base_dir / f"cached_data_{parameter}"
    data_dir.mkdir(parents=True, exist_ok=True)
    json_path = data_dir / f"site_dict_{parameter}.json"
    return data_dir, json_path


def download_target(full_index, target_site: str, parameter_code: str,
                    start_date: str, end_date: str, units: str):
    """Download and process target site data."""
    print(f"Downloading target site {target_site}...")
    target_df = load_target(
        target_site=target_site,
        full_index=full_index,
        parameter_code=parameter_code,
        start_date=start_date,
        end_date=end_date,
        to_units=units)

    # Create continuous daily time series
    target = (target_df
              .reindex(full_index)
              .interpolate(limit_direction="both")
              .ffill()
              .bfill())
    return target


def download_huc_data(huc_codes: list, start_date: str, end_date: str,
                      parameter_code: str, percent_threshold: int,
                      data_dir: Path, json_path: Path, site_type: str):
    """Download predictor sites for specified HUC codes."""
    print(f"Downloading predictor sites for HUC codes: {huc_codes}")

    summary = GaugebyHUC(
        start_date=start_date,
        end_date=end_date,
        huc_codes=huc_codes,
        parameter_code=parameter_code,
        percent_threshold=percent_threshold,
        data_dir=data_dir,
        json_path=json_path,
        siteType=site_type)

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Download USGS gauge data for HPC/SLURM environments")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--huc", nargs="+",
                       help="HUC code(s) to download (e.g., 05 06 07)")
    group.add_argument("--all", action="store_true",
                       help="Download all default HUC codes")
    group.add_argument("--array-index", type=int,
                       help="SLURM array task index (0-based)")

    parser.add_argument("--data-dir", type=Path, default=None,
                        help="Override data directory")
    parser.add_argument("--skip-target", action="store_true",
                        help="Skip downloading target site data")
    parser.add_argument("--start-date", default=START_DATE,
                        help=f"Start date (default: {START_DATE})")
    parser.add_argument("--end-date", default=END_DATE,
                        help=f"End date (default: {END_DATE})")

    args = parser.parse_args()

    # Determine HUC codes to process
    if args.all:
        huc_codes = DEFAULT_HUC_CODES
    elif args.array_index is not None:
        if args.array_index >= len(DEFAULT_HUC_CODES):
            print(f"Error: Array index {args.array_index} out of range "
                  f"(max: {len(DEFAULT_HUC_CODES) - 1})")
            sys.exit(1)
        huc_codes = [DEFAULT_HUC_CODES[args.array_index]]
    else:
        huc_codes = args.huc

    print(f"Processing HUC codes: {huc_codes}")
    print(f"Date range: {args.start_date} to {args.end_date}")

    # Setup directories
    script_dir = Path(__file__).parent
    examples_dir = script_dir.parent

    if args.data_dir:
        data_dir = args.data_dir
        data_dir.mkdir(parents=True, exist_ok=True)
        json_path = data_dir / f"site_dict_{PARAMETER}.json"
    else:
        data_dir, json_path = setup_directories(examples_dir, PARAMETER)

    # Create full time index
    full_index = pd.date_range(
        start=args.start_date, end=args.end_date, freq="D", tz="UTC")

    # Download target site (optional)
    if not args.skip_target:
        target = download_target(
            full_index=full_index,
            target_site=TARGET_SITE,
            parameter_code=PARAMETER_CODE,
            start_date=args.start_date,
            end_date=args.end_date,
            units=UNITS)
        print(f"Target site data shape: {target.shape}")

    # Download HUC data
    summary = download_huc_data(
        huc_codes=huc_codes,
        start_date=args.start_date,
        end_date=args.end_date,
        parameter_code=PARAMETER_CODE,
        percent_threshold=PERCENT_THRESHOLD,
        data_dir=data_dir,
        json_path=json_path,
        site_type=SITE_TYPE)

    print("\nDownload complete")
    print(f"Data saved to: {data_dir}")
    print(f"Site metadata saved to: {json_path}")
    print(f"\nSummary: {summary}")


if __name__ == "__main__":
    main()
