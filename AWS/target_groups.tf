resource "aws_lb_target_group" "public-nlb-target-grps" {
    name = "streamlit-target"
    target_type = "instance"
    port = 8505
    protocol = "TCP"
    vpc_id = data.aws_vpc.shop-vpc.id
    health_check {
      healthy_threshold = 3
      interval = 10
      unhealthy_threshold = 3

    }
}


resource "aws_lb_target_group" "private-nlb-target-grps" {
    name = "fastapi-target"
    target_type = "instance"
    port = 8000
    protocol = "TCP"
    vpc_id = data.aws_vpc.shop-vpc.id
    health_check {
      path="/ping"
      healthy_threshold = 3
      interval = 10
      unhealthy_threshold = 3
      
    }
}

resource "aws_lb_target_group" "private-alb-target-grps" {
  count = length(local.ports)
  name = "alb-target-group-for-port-${local.ports[count.index]}"
  target_type = "instance"
  slow_start = count.index < 2 ? 200 : 30
  port = local.ports[count.index]
  protocol = "HTTP"
  vpc_id = data.aws_vpc.shop-vpc.id
  health_check {
    path = var.private-alb-subnet-params.paths[count.index]
    healthy_threshold = 3
    interval = 30
    timeout = 20
    unhealthy_threshold = 5
    }
}