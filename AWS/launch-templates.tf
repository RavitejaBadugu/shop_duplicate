##streamlitandfastapi##
resource "aws_security_group" "auto-scaling-sg-web" {
    count = length(var.web-services-template-params)
    name = "auto-scaling-sg-web-${count.index}"
    vpc_id = data.aws_vpc.shop-vpc.id
    ingress {
        description = "for in"
        protocol = "tcp"
        from_port = var.web-services-template-params[count.index].port
        to_port = var.web-services-template-params[count.index].port
        cidr_blocks = ["0.0.0.0/0"]
    }
    ingress {
        description = "for in"
        protocol = "tcp"
        from_port = 22
        to_port = 22
        cidr_blocks = [data.aws_vpc.shop-vpc.cidr_block]
    }
    egress {
        description = "allow all"
        protocol = "-1"
        from_port = 0
        to_port = 0
        cidr_blocks = ["0.0.0.0/0"]
        ipv6_cidr_blocks = ["::/0"]
    }
    tags = {
      "Name" = "auto-scaling-sg-web-${count.index}"
    }
  
}
############################
##models##
resource "aws_security_group" "auto-scaling-sg-ec2" {
    count = length(var.service-template-params)
    name = "auto-scaling-sg-ec2-${count.index}"
    vpc_id = data.aws_vpc.shop-vpc.id
    ingress {
        description = "for in"
        protocol = "tcp"
        from_port = var.service-template-params[count.index].port
        to_port = var.service-template-params[count.index].port
        cidr_blocks = [data.aws_vpc.shop-vpc.cidr_block]
    }
    ingress {
        description = "for in"
        protocol = "tcp"
        from_port = 22
        to_port = 22
        cidr_blocks = [data.aws_vpc.shop-vpc.cidr_block]
    }
    egress {
        description = "allow all"
        protocol = "-1"
        from_port = 0
        to_port = 0
        cidr_blocks = ["0.0.0.0/0"]
        ipv6_cidr_blocks = ["::/0"]
    }
    tags = {
      "Name" = "auto-scaling-sg-ec2-${count.index}"
    }
  
}
#######################
##for knn##
resource "aws_security_group" "auto-scaling-knn-sg-ec2" {
    name = "auto-scaling-knn-sg-ec2"
    vpc_id = data.aws_vpc.shop-vpc.id
    dynamic "ingress" {
        for_each=var.knn-template-params.ports #5000 and 5002
        content {
            protocol = "tcp"
            from_port = ingress.value
            to_port = ingress.value
            cidr_blocks = [data.aws_vpc.shop-vpc.cidr_block]
        }
    }
    ingress {
        description = "for in"
        protocol = "tcp"
        from_port = 22
        to_port = 22
        cidr_blocks = [data.aws_vpc.shop-vpc.cidr_block]
    }
    egress {
        description = "allow all"
        protocol = "-1"
        from_port = 0
        to_port = 0
        cidr_blocks = ["0.0.0.0/0"]
        ipv6_cidr_blocks = ["::/0"]
    }
    tags = {
      "Name" = "auto-scaling-knn-sg-ec2"
    }
  
}
#################################
##streamlit and fastapi launch templates##
resource "aws_launch_template" "streamlit-services" {
    name = var.web-services-template-params[0].name
    image_id = var.web-services-template-params[0].image_id
    instance_type = var.web-services-template-params[0].instance
    key_name = "terra-keypair"
    vpc_security_group_ids = [aws_security_group.auto-scaling-sg-web[0].id]
    user_data = base64encode(templatefile("${path.module}/${var.web-services-template-params[0].tmpl_file_path}",
                                        {nlbdns = aws_lb.private-nlb.dns_name,port= 8000}
                                     )
    )
}
resource "aws_launch_template" "fastapi-services" {
    name = var.web-services-template-params[1].name
    image_id = var.web-services-template-params[1].image_id
    instance_type = var.web-services-template-params[1].instance
    key_name = "terra-keypair"
    iam_instance_profile {
        arn = var.iam_instance_profile.arn
    }
    vpc_security_group_ids = [aws_security_group.auto-scaling-sg-web[1].id]
    user_data = base64encode(templatefile("${path.module}/${var.web-services-template-params[1].tmpl_file_path}",
                                        {albdns = aws_lb.private-alb.dns_name,db_host = var.rds_endpoint}
                                     )
    )
}
###################################
##model templates##
resource "aws_launch_template" "templates" {
    count = length(var.service-template-params)
    name = var.service-template-params[count.index].name
    image_id = var.service-template-params[count.index].image_id
    instance_type = var.service-template-params[count.index].instance
    key_name = "terra-keypair"
    vpc_security_group_ids = [aws_security_group.auto-scaling-sg-ec2[count.index].id]
}
###################################
##Knn templates##
resource "aws_launch_template" "knn-template" {
    name = "knn-template"
    image_id = var.knn-template-params.image_id
    instance_type = var.knn-template-params.instance
    key_name = "terra-keypair"
    vpc_security_group_ids = [aws_security_group.auto-scaling-knn-sg-ec2.id]
}