variable "aws_region" {
    description = "aws region"
    type = string
    default = "ap-south-1"
}

variable "availability_zone" {
    description = "aws availability zone"
    type = string
    default = "ap-south-1a"
}

variable "project_name" {
    description = "Project Name"
    type = string
    default = "cuia"
}

variable "instance_type" {
    description = "EC2 type"
    type = string
    default = "t3.small"
}

