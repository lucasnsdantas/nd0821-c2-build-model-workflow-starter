#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact.
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    logger.info(f"Downloading {args.input_artifact}.")
    artifact_local_path = run.use_artifact(args.input_artifact).file()
    df = pd.read_csv(artifact_local_path)

    logger.info("Filtering listings with prices between $10 - $350.")
    idx = df["price"].between(args.min_price, args.max_price)
    df = df[idx].copy()

    logger.info("Filtering listings withing specific geographic area.")
    idx = df["longitude"].between(args.min_longitude, -args.max_longitude) & df[
        "latitude"
    ].between(args.min_latitude, args.max_latitude)
    df = df[idx].copy()

    logger.info("Converting last_review from string to datetime.")
    df["last_review"] = pd.to_datetime(df["last_review"])

    logger.info("Saving clean_sample.csv file.")
    df.to_csv(args.output_artifact, index=False)

    logger.info(f"Creating artifact.")
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file(local_path=args.output_artifact)
    run.log_artifact(artifact)
    artifact.wait()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")

    parser.add_argument(
        "--input_artifact", type=str, help="Input data to be cleaned.", required=True
    )

    parser.add_argument(
        "--output_artifact", type=str, help="Cleaned data.", required=True
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help="The type for the output artifact.",
        required=True,
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="The description of the output artifact.",
        required=True,
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="The minimum rental price to consider.",
        required=True,
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="The maximum rental price to consider.",
        required=True,
    )

    args = parser.parse_args()

    go(args)
