terraform {
  backend "s3" {
    bucket = "poc-tf-state-163081953997-ap-south-1-an"
    key    = "cuia/terraform.tfstate"
    region = "ap-south-1"
  }
}