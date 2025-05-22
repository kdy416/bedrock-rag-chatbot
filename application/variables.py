import os
import boto3

KNOWLEDGE_BASE_ID="${KnowledgeBaseIdParam}" # Please update

# Resolve the AWS Region dynamically.
# Priority: environment variable AWS_REGION ▸ boto3 session default ▸ fallback.
REGION = os.environ.get("AWS_REGION") or boto3.Session().region_name or "ap-northeast-2"
MODEL_ARN="anthropic.claude-3-haiku-20240307-v1:0"
FM_GENERATION_MODEL_ARN="anthropic.claude-3-haiku-20240307-v1:0" # e.g. anthropic.claude, ai21, TitanText