provider "aws" {
  region = var.region
}

$ export AWS_ACCESS_KEY_ID="AKIAZHSKUQLIFNRO6OWG"
$ export AWS_SECRET_ACCESS_KEY="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"
$ export AWS_DEFAULT_REGION="us-east-1"

variable "region" {
  description = "The AWS region to create resources in."
  default     = "us-east-1"
}

