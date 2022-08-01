variable "aws-region" {
    type = string
    description = "region where to launch"
    default = "us-east-2"
}

variable "public-nlb-params" {
    type = list(object({
        az= string,
        cidr_block= string
    }))
    description = "parameters for public subnets"
}

variable "serives-params" {
    type = string
    description = "az for private subnets which will hold services"
  
}

variable "rds_endpoint" {
  type = string
  description = "endpoint of rds"
  
}
variable "private-nlb-subnet-params" {
  type = object({az=list(string)})
  description = "az's for alb deployed private subnets"
}

variable "private-alb-subnet-params" {
  type = object({az=list(string),paths=list(string)})
  description = "list containing paths to forward the traffic"
}

variable "iam_instance_profile" {
  type = object({
    arn=string,
    name=string
  })
  description = "arn and name of instance profile which gives accesee to s3 for fastapi services"
}

variable "web-services-template-params" {
  type = list(object({
    port=number,
    name=string,
    image_id=string,
    instance=string,
    tmpl_file_path=string
  }))
  description = "parameters for streamlit and fastapi services"
}


variable "service-template-params" {
    type = list(object({port=number,name=string,instance=string,image_id=string}))
    description = "parameters for services except knn services"
}

variable "knn-template-params" {
    type = object({instance=string,image_id=string,ports=list(number)})
    description = "parameters for knn services"
}