import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# Read bucket name from environment variable or default to project bucket
S3_BUCKET_NAME = os.getenv("TRACEDATA_S3_BUCKET", "tracedata-evidence-vault")

def upload_file_to_s3(local_file_path: str, bucket_name: str = S3_BUCKET_NAME, s3_key: str = None) -> bool:
    """
    Uploads a local dataset to an AWS S3 bucket.
    If no AWS credentials exist, simulates the upload for local testing.
    """
    if not os.path.exists(local_file_path):
        print(f"❌ Upload failed: Local file '{local_file_path}' does not exist.")
        return False

    if s3_key is None:
        s3_key = os.path.basename(local_file_path)

    # Check for AWS credentials in environment
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    if not aws_access_key or not aws_secret_key:
        print(f"⚠️ AWS credentials not detected. [DRY-RUN] Simulating S3 upload: {local_file_path} ➔ s3://{bucket_name}/{s3_key}")
        return True

    try:
        s3_client = boto3.client("s3")
        print(f"☁️ Uploading '{local_file_path}' to AWS S3 bucket '{bucket_name}'...")
        s3_client.upload_file(local_file_path, bucket_name, s3_key)
        print(f"✅ Successfully uploaded to s3://{bucket_name}/{s3_key}")
        return True
    except NoCredentialsError:
        print("❌ AWS credentials not found. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in environment.")
        return False
    except ClientError as e:
        print(f"❌ AWS S3 ClientError: {e}")
        return False

def sync_case_evidence_to_s3():
    """
    Uploads both raw evidence and processed datasets to the S3 bucket vault.
    """
    print("\n-------------------------------------------------------")
    print("☁️ AWS S3 CLOUD SYNC — TRACEDATA EVIDENCE VAULT")
    print("-------------------------------------------------------")

    raw_file = "data/raw/transactions.csv"
    processed_file = "data/processed/clean_transactions.csv"

    upload_file_to_s3(raw_file, s3_key="raw/case_001_transactions.csv")
    upload_file_to_s3(processed_file, s3_key="processed/case_001_clean_transactions.csv")

if __name__ == "__main__":
    sync_case_evidence_to_s3()