# types of load balancers
#1) Public
resource "aws_lb" "public-nlb" {
    name = "aws-public-nlb"
    internal = false
    load_balancer_type = "network"
    subnets = aws_subnet.public-nlb-subnets[*].id
    tags = {
      "Name" = "aws-public-nlb"
    }
}
#2) Private NLB
resource "aws_lb" "private-nlb" {
    name = "aws-private-nlb"
    internal = true
    load_balancer_type = "network"
    subnets = aws_subnet.private-nlb-subnet[*].id
    tags = {
      "Name" = "aws-private-nlb"
    }
}
#3) Private ALB
locals {
  ports = [8501,8502,5000,5002]
}
resource "aws_security_group" "albsecuritygrp" {
  name = "albsecuritygrp"
  vpc_id = data.aws_vpc.shop-vpc.id
  dynamic "ingress" {
    for_each=local.ports
    content {
    protocol = "tcp"
    from_port = ingress.value
    to_port = ingress.value
    cidr_blocks = [data.aws_vpc.shop-vpc.cidr_block]
    }
  }
  egress {
    description = "allow all"
    protocol = "-1"
    from_port = 0
    to_port = 0
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
  tags={
    "Name" = "private-alb-sg"
  }
}

resource "aws_lb" "private-alb" {
    name = "aws-private-alb"
    internal = true
    load_balancer_type = "application"
    security_groups = [aws_security_group.albsecuritygrp.id]
    subnets = aws_subnet.private-alb-subnet[*].id
    tags = {
      "Name" = "aws-private-alb"
    }
}
####################################################################

#1) Public-NLB-Listener
resource "aws_lb_listener" "public-nlb-listener" {
    load_balancer_arn = aws_lb.public-nlb.arn
    port = "8505"
    protocol = "TCP"
    default_action {
      type= "forward"
      target_group_arn = aws_lb_target_group.public-nlb-target-grps.arn
    }
}
#2) Private-NLB-Listener
resource "aws_lb_listener" "private-nlb-listener" {
    load_balancer_arn = aws_lb.private-nlb.arn
    port = "8000"
    protocol = "TCP"
    default_action {
      type= "forward"
      target_group_arn = aws_lb_target_group.private-nlb-target-grps.arn
    } 
}

#3) Private-ALB-Lsitener
resource "aws_lb_listener" "private-alb-listener" {
    count=length(local.ports)
    load_balancer_arn = aws_lb.private-alb.arn
    port = local.ports[count.index]
    protocol = "HTTP"
    default_action {
      type = "forward"
      target_group_arn = aws_lb_target_group.private-alb-target-grps[count.index].arn
    }
}
