import boto3
import argparse
import subprocess
from botocore.exceptions import ClientError

# --- Step 1: Parse repository name from CLI ---
parser = argparse.ArgumentParser()
parser.add_argument("repository_name", help="Name of the ECR repository")
args = parser.parse_args()

repo_name = args.repository_name
region = "us-east-1"
session = boto3.Session()  # picks up AWS creds from env vars
ecr = session.client("ecr", region_name=region)

# --- Step 2: Create or fetch ECR repository ---
try:
    response = ecr.create_repository(
        repositoryName=repo_name,
        imageScanningConfiguration={"scanOnPush": True}
    )
    print("Repository created.")
    uri = response["repository"]["repositoryUri"]
except ClientError as e:
    if e.response["Error"]["Code"] == "RepositoryAlreadyExistsException":
        print(f"Repository '{repo_name}' already exists.")
        response = ecr.describe_repositories(repositoryNames=[repo_name])
        uri = response["repositories"][0]["repositoryUri"]
    else:
        raise e

print(f"[INFO] ECR URI: {uri}")

# --- Step 3: Build Docker image ---
image_tag = "latest"
local_image = f"{repo_name}:{image_tag}"
full_ecr_image = f"{uri}:{image_tag}"

print(f"[INFO] Building local image: {local_image}")
subprocess.run(["docker", "build", "-t", local_image, "."], check=True)

# --- Step 4: Tag image with ECR URI ---
print(f"[INFO] Tagging image as: {full_ecr_image}")
subprocess.run(["docker", "tag", local_image, full_ecr_image], check=True)

# --- Step 5: Login to ECR ---
print(f"[INFO] Logging in to ECR ({region})...")
login_cmd = [
    "aws", "ecr", "get-login-password",
    "--region", region
]
login_proc = subprocess.Popen(login_cmd, stdout=subprocess.PIPE)
subprocess.run([
    "docker", "login",
    "--username", "AWS",
    "--password-stdin", uri.split('/')[0]
], stdin=login_proc.stdout, check=True)

# --- Step 6: Push to ECR ---
print(f"[INFO] Pushing image to ECR: {full_ecr_image}")
subprocess.run(["docker", "push", full_ecr_image], check=True)

print("Docker image successfully pushed to ECR.")
