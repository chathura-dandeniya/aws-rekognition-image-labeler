"""
AWS Rekognition Image Labeler
------------------------------
Detects and labels objects in images stored in Amazon S3 using
Amazon Rekognition. Outputs labels with confidence scores and
displays bounding boxes over the image using Matplotlib.

Usage:
    python app.py --photo <image_key> --bucket <bucket_name> [--max-labels <int>] [--region <region>]

Example:
    python app.py --photo Image_01.jpg --bucket aws-rekognition-label-images-2026

Requirements:
    See requirements.txt
"""

import argparse
import logging
import sys
from io import BytesIO

import boto3
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from botocore.exceptions import BotoCoreError, ClientError
from PIL import Image

# ========================
# Logging Configuration
# ========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


# ========================
# Core Functions
# ========================

def detect_labels(photo: str, bucket: str, max_labels: int = 10, region: str = "us-east-1") -> int:
    """
    Detects labels in an image stored in an S3 bucket using Amazon Rekognition.

    Args:
        photo      (str): The S3 object key (filename) of the image to analyse.
        bucket     (str): The name of the S3 bucket containing the image.
        max_labels (int): Maximum number of labels to return. Defaults to 10.
        region     (str): AWS region for Rekognition and S3 clients. Defaults to 'us-east-1'.

    Returns:
        int: The number of labels detected, or -1 if an error occurred.
    """

    try:
        # Initialise Rekognition client with explicit region
        rekognition_client = boto3.client("rekognition", region_name=region)

        logger.info(f"Running detect_labels on '{photo}' in bucket '{bucket}'...")

        # Call Rekognition detect_labels API
        response = rekognition_client.detect_labels(
            Image={"S3Object": {"Bucket": bucket, "Name": photo}},
            MaxLabels=max_labels
        )

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "NoSuchBucket":
            logger.error(f"S3 bucket '{bucket}' does not exist. Please check the bucket name.")
        elif error_code == "NoSuchKey":
            logger.error(f"Image '{photo}' not found in bucket '{bucket}'. Please check the file name.")
        elif error_code == "InvalidS3ObjectException":
            logger.error(f"Rekognition could not access '{photo}'. Ensure the file is a supported image format.")
        elif error_code == "AccessDeniedException":
            logger.error("Access denied. Check your IAM policy has s3:GetObject and rekognition:DetectLabels permissions.")
        else:
            logger.error(f"AWS ClientError: {e.response['Error']['Message']}")
        return -1

    except BotoCoreError as e:
        logger.error(f"BotoCoreError: {e}")
        return -1

    # Print detected labels to terminal
    print(f"\nDetected labels for: {photo}")
    print("─" * 45)
    for label in response["Labels"]:
        confidence = round(label["Confidence"], 2)
        print(f"  Label: {label['Name']:<20} | Confidence: {confidence}%")
    print("─" * 45)

    # Load and display image with bounding boxes
    display_image_with_boxes(photo, bucket, response["Labels"], region)

    return len(response["Labels"])


def display_image_with_boxes(photo: str, bucket: str, labels: list, region: str = "us-east-1") -> None:
    """
    Loads an image from S3 into memory and renders it with bounding boxes
    and confidence score labels using Matplotlib.

    Args:
        photo  (str) : The S3 object key of the image.
        bucket (str) : The S3 bucket name.
        labels (list): List of label dictionaries returned by Rekognition.
        region (str) : AWS region for the S3 client. Defaults to 'us-east-1'.
    """

    try:
        logger.info("Loading image from S3 for visualisation...")

        # Retrieve image from S3 into memory (no disk write)
        s3 = boto3.resource("s3", region_name=region)
        obj = s3.Object(bucket, photo)
        img_data = obj.get()["Body"].read()
        img = Image.open(BytesIO(img_data))

    except ClientError as e:
        logger.error(f"Failed to load image from S3: {e.response['Error']['Message']}")
        return

    except Exception as e:
        logger.error(f"Unexpected error loading image: {e}")
        return

    # Set up Matplotlib figure
    plt.imshow(img)
    ax = plt.gca()

    # Draw bounding boxes for each label instance
    for label in labels:
        for instance in label.get("Instances", []):
            bbox = instance["BoundingBox"]

            left   = bbox["Left"]   * img.width
            top    = bbox["Top"]    * img.height
            width  = bbox["Width"]  * img.width
            height = bbox["Height"] * img.height

            # Draw rectangle bounding box
            rect = patches.Rectangle(
                (left, top), width, height,
                linewidth=2,
                edgecolor="red",
                facecolor="none"
            )
            ax.add_patch(rect)

            # Add label text with confidence score
            confidence = round(label["Confidence"], 2)
            label_text = f"{label['Name']} ({confidence}%)"
            plt.text(
                left, top - 2,
                label_text,
                color="red",
                fontsize=8,
                bbox=dict(facecolor="white", alpha=0.6, edgecolor="none")
            )

    plt.title(f"Rekognition Labels: {photo}")
    plt.axis("off")
    plt.tight_layout()
    plt.show()
    logger.info("Visualisation complete.")


# ========================
# Argument Parser
# ========================

def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed argument values.
    """
    parser = argparse.ArgumentParser(
        description="Detect and label objects in an S3 image using Amazon Rekognition."
    )
    parser.add_argument(
        "--photo",
        required=True,
        help="The S3 object key (filename) of the image to analyse. Example: Image_01.jpg"
    )
    parser.add_argument(
        "--bucket",
        required=True,
        help="The name of the S3 bucket containing the image. Example: aws-rekognition-label-images-2026"
    )
    parser.add_argument(
        "--max-labels",
        type=int,
        default=10,
        help="Maximum number of labels to detect (default: 10)"
    )
    parser.add_argument(
        "--region",
        default="us-east-1",
        help="AWS region for Rekognition and S3 (default: us-east-1)"
    )
    return parser.parse_args()


# ========================
# Entry Point
# ========================

def main():
    """Main entry point — parses arguments and runs label detection."""
    args = parse_arguments()

    logger.info("Starting AWS Rekognition Image Labeler...")
    logger.info(f"  Photo      : {args.photo}")
    logger.info(f"  Bucket     : {args.bucket}")
    logger.info(f"  Max Labels : {args.max_labels}")
    logger.info(f"  Region     : {args.region}")

    label_count = detect_labels(
        photo=args.photo,
        bucket=args.bucket,
        max_labels=args.max_labels,
        region=args.region
    )

    if label_count >= 0:
        print(f"\nTotal labels detected: {label_count}")
        logger.info("Done.")
    else:
        logger.error("Label detection failed. Please review the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()