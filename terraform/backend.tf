terraform {
  backend "s3" {
    bucket = "poc-tf-state-087607092654-ap-south-1-an"
    key    = "cuia/terraform.tfstate"
    region = "ap-south-1"
  }
}