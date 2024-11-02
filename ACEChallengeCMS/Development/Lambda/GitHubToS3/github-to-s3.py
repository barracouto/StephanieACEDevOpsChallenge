import boto3
import zipfile
import os
import tempfile

s3_client = boto3.client('s3')
codepipeline_client = boto3.client('codepipeline')

def lambda_handler(event, context):
    # Extract CodePipeline Job ID
    job_id = event['CodePipeline.job']['id']
    
    # Set destination S3 bucket directly in the code
    destination_bucket = "scouto-ace-devops-msc"  # Replace with your actual bucket name

    # Get CodePipeline artifact details
    artifact = event['CodePipeline.job']['data']['inputArtifacts'][0]
    artifact_bucket = artifact['location']['s3Location']['bucketName']
    artifact_key = artifact['location']['s3Location']['objectKey']
    
    # Download the artifact (zip file) from the source bucket
    with tempfile.TemporaryFile() as tmp_file:
        s3_client.download_fileobj(artifact_bucket, artifact_key, tmp_file)
        tmp_file.seek(0)

        # Unzip and upload each file to the destination bucket with the full path preserved
        with zipfile.ZipFile(tmp_file, 'r') as zip_ref:
            for file_name in zip_ref.namelist():
                # Skip directories
                if not file_name.endswith('/'):
                    with zip_ref.open(file_name) as file_data:
                        # Use the full path from file_name directly as the S3 key
                        # This will preserve the folder structure from GitHub in S3
                        s3_client.upload_fileobj(file_data, destination_bucket, file_name)

    # Notify CodePipeline of job success
    codepipeline_client.put_job_success_result(jobId=job_id)

    return {'status': 'Templates synced to S3 successfully'}
