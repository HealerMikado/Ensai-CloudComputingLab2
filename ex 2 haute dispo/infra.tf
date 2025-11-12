

########################################
# Launch Template
########################################

resource "aws_launch_template" "ubuntu_template" {
  name_prefix   = "ubuntu-template-"
  image_id      = "ami-0ecb62995f68bb549"
  instance_type = 
  key_name      = 

  vpc_security_group_ids = 

  block_device_mappings {
    device_name = "/dev/sda1"

    ebs {
      volume_size = 8
      volume_type = "gp3"
    }
  }

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "ubuntu-autoscaling-instance"
    }
  }
}

########################################
# Auto Scaling Group
########################################
resource "aws_autoscaling_group" "web_asg" {
  desired_capacity     = 
  max_size             = 
  min_size             = 
  vpc_zone_identifier  = data.aws_subnets.default.ids
  health_check_type    = "EC2"
  target_group_arns    = [aws_lb_target_group.web_tg.arn]

  launch_template {
    id      = 
    version = 
  }

  tag {
    key                 = "Name"
    value               = "web-asg-instance"
    propagate_at_launch = true
  }
}

########################################
# Load Balancer (ALB)
########################################
# resource "aws_lb" "web_alb" {
#   name               = "web-alb"
#   internal           = false
#   load_balancer_type = 
#   security_groups    =
#   subnets            = data.aws_subnets.default.ids

#   tags = {
#     Name = "web-alb"
#   }
# }

########################################
# Target Group (pour le Load Balancer)
########################################
# resource "aws_lb_target_group" "web_tg" {
#   name     = "web-tg"
#   port     = 
#   protocol = 
#   vpc_id   = data.aws_vpc.default.id


#   tags = {
#     Name = "web-tg"
#   }
# }

########################################
# Listener pour le Load Balancer
########################################
# resource "aws_lb_listener" "http_listener" {
#   load_balancer_arn = aws_lb.web_alb.arn
#   port              = 
#   protocol          = ""

#   default_action {
#     type             = 
#     target_group_arn = 
#   }
# }

########################################
# Outputs
########################################
output "load_balancer_dns_name" {
  description = "Nom DNS du load balancer"
  value       = aws_lb.web_alb.dns_name
}

output "security_group_id" {
  description = "ID du security group créé"
  value       = aws_security_group.web_sg.id
}
