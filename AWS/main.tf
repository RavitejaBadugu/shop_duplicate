terraform {
  required_providers {
    aws={
        source = "hashicorp/aws"
        version ="~> 3.0"
    }
  }
  backend "s3" {
    bucket = "shop-duplicate-terraform-state-store"
    key = "terraform-state"
    region = "us-east-2"
    profile = "shop-user"
  }
}

provider "aws" {
    region = var.aws-region
    profile = "shop-user"
}
data "aws_vpc" "shop-vpc" {
  filter {
    name = "tag:Name"
    values = ["shop-vpc"]
  }
}

resource "aws_subnet" "public-nlb-subnets" {
    count = 2
    vpc_id = data.aws_vpc.shop-vpc.id
    availability_zone = var.public-nlb-params[count.index].az
    cidr_block = var.public-nlb-params[count.index].cidr_block
    tags = {
      Name = "public-shop-nlb-${count.index}"
    }
}

data "aws_internet_gateway" "igw" {
  filter {
    name = "attachment.vpc-id"
    values = [data.aws_vpc.shop-vpc.id]
  }
}
resource "aws_route_table" "public-route-table" {
  vpc_id = data.aws_vpc.shop-vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = data.aws_internet_gateway.igw.id
  }
  tags = {
    Name = "public-route-table"
  }
}

resource "aws_route_table_association" "public-route-association" {
  count = 2
  route_table_id = aws_route_table.public-route-table.id
  subnet_id = aws_subnet.public-nlb-subnets[count.index].id
}


resource "aws_route_table" "fastapi-route-table" {
  vpc_id = data.aws_vpc.shop-vpc.id
  tags = {
    Name = "fastapi_route_table"
  }
}

resource "aws_subnet" "services-subnets" {
    count = 5
    vpc_id = data.aws_vpc.shop-vpc.id
    availability_zone = var.serives-params
    cidr_block = "10.0.${count.index+2}.0/24"
    tags = {
      Name = "services-${count.index}"
    }
}

resource "aws_route_table_association" "fastapi-route-tableassociation" {
  route_table_id = aws_route_table.fastapi-route-table.id
  subnet_id = aws_subnet.services-subnets[1].id
}

resource "aws_subnet" "private-nlb-subnet" {
  count=2
  vpc_id = data.aws_vpc.shop-vpc.id
  availability_zone = var.private-nlb-subnet-params.az[count.index]
  cidr_block = "10.0.${count.index+7}.0/24"
  tags = {
    Name = "private-nlb-subnet-${count.index}"
  }
  }

resource "aws_subnet" "private-alb-subnet" {
  count=2
  vpc_id = data.aws_vpc.shop-vpc.id
  availability_zone = var.private-alb-subnet-params.az[count.index]
  cidr_block = "10.0.${count.index+9}.0/24"
  tags = {
    Name = "private-alb-subnet-${count.index}"
  }
  }