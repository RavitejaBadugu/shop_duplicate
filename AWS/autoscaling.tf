resource "aws_autoscaling_group" "web-scalers" {
    count = 2
    name = "web-scalers-${count.index}"
    max_size = 2
    min_size = 1
    desired_capacity = 1
    vpc_zone_identifier = [aws_subnet.services-subnets[count.index].id]
    target_group_arns = [count.index==0?aws_lb_target_group.public-nlb-target-grps.arn:aws_lb_target_group.private-nlb-target-grps.arn]
    launch_template {
      id = count.index==0?aws_launch_template.streamlit-services.id:aws_launch_template.fastapi-services.id
    }
}

###############################
resource "aws_autoscaling_group" "CV-end-scaler" {
    name = "CV-end-scaler"
    max_size = 2
    min_size = 1
    desired_capacity = 1
    vpc_zone_identifier = [aws_subnet.services-subnets[2].id]
    target_group_arns = [aws_lb_target_group.private-alb-target-grps[0].arn]
    launch_template {
      id = aws_launch_template.templates[0].id
    }
}
##################################
resource "aws_autoscaling_group" "nlp-end-scaler" {
    name = "nlp-end-scaler"
    max_size = 2
    min_size = 1
    desired_capacity = 1
    vpc_zone_identifier = [aws_subnet.services-subnets[3].id]
    target_group_arns = [aws_lb_target_group.private-alb-target-grps[1].arn]
    launch_template {
      id = aws_launch_template.templates[1].id
    }
}
#####################################
resource "aws_autoscaling_group" "knn-end-scaler" {
    name = "knn-end-scaler"
    max_size = 2
    min_size = 1
    desired_capacity = 1
    vpc_zone_identifier = [aws_subnet.services-subnets[4].id]
    target_group_arns = [aws_lb_target_group.private-alb-target-grps[2].arn,aws_lb_target_group.private-alb-target-grps[3].arn]
    launch_template {
      id = aws_launch_template.knn-template.id
    }
}
###########################################
# Using Scheduled Scaling
locals {
  balancer_names=toset([aws_autoscaling_group.web-scalers[0].name,aws_autoscaling_group.web-scalers[1].name,
                 aws_autoscaling_group.CV-end-scaler.name,aws_autoscaling_group.nlp-end-scaler.name,
                 aws_autoscaling_group.knn-end-scaler.name])
}
resource "aws_autoscaling_schedule" "scheduler-up" {
    for_each = local.balancer_names
    scheduled_action_name="${each.value}-scheduler-up"
    autoscaling_group_name = each.value
    min_size = -1
    max_size = 2
    desired_capacity = 2
    recurrence = "0 9 * * *"
    time_zone = "Asia/Kolkata"
    depends_on = [aws_autoscaling_group.web-scalers[0],aws_autoscaling_group.web-scalers[1],
                 aws_autoscaling_group.CV-end-scaler,aws_autoscaling_group.nlp-end-scaler,
                 aws_autoscaling_group.knn-end-scaler]
}

resource "aws_autoscaling_schedule" "scheduler-down" {
    for_each = local.balancer_names
    scheduled_action_name="${each.value}-scheduler-down"
    autoscaling_group_name = each.value
    min_size = -1
    max_size = 2
    desired_capacity = 1
    recurrence = "0 17 * * *"
    time_zone = "Asia/Kolkata"
    depends_on = [aws_autoscaling_group.web-scalers[0],aws_autoscaling_group.web-scalers[1],
                 aws_autoscaling_group.CV-end-scaler,aws_autoscaling_group.nlp-end-scaler,
                 aws_autoscaling_group.knn-end-scaler]
}