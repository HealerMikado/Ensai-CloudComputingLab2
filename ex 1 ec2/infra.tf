

# Création de l'instance EC2
resource "aws_instance" "ubuntu_vm" {
  ami           = ""
  instance_type = ""
  vpc_security_group_ids = []
  key_name = ""
  user_data_base64 = base64encode(file("${path.module}/user_data.sh"))

  tags = {
    Name = "ubuntu-tf-instance"
  }

  metadata_options {
    http_tokens = "optional"
  }
}

