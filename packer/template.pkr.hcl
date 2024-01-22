variable "aws_region" {
  type = string
  default = "us-west-2"
}

variable "base_ami" {
  type = string
  default = "ami-e535c59d"
}

variable "image_os" {
  type = string
  default = "amzn2"
}

variable "image_type" {
  type = string
  default = "base"
}

variable "instance_profile" {
  type = string
  default = "umcollab_standard"
}

variable "root_device" {
  type = string
  default = "/dev/xvda"
}

variable "subnet_id" {
  type = string
  default = "subnet-xxx"
}

local "satellite_rpm" {
    expression = vault("secret/satellite", "rpm")
}

local "satellite_org" {
    expression = vault("secret/satellite", "org")
}

local "satellite_key" {
    expression = vault("secret/satellite", "key")
}

source "amazon-ebs" "host" {
  ami_name = "${var.image_type}_${uuidv4()}"
  associate_public_ip_address = false
  ena_support = true
  encrypt_boot = contains(["base", "vdc_relay"], var.image_type)
  instance_type = "t3.medium"
  launch_block_device_mappings {
    delete_on_termination = true
    device_name = "${var.root_device}"
    volume_size = 15
    volume_type = "gp3"
  }
  launch_block_device_mappings {
    delete_on_termination = true
    device_name = "/dev/xvdg"
    volume_size = 3
    volume_type = "gp3"
  }
  region = "${var.aws_region}"
  source_ami = "${var.base_ami}"
  ssh_pty = true
  ssh_username = "ec2-user"
  subnet_id = "${var.subnet_id}"
  tags = {
    image_type = "${var.image_type}"
    os = "${var.image_os}"
  }
  user_data_file = "packer/userdata"
  iam_instance_profile = "${var.instance_profile}"
}

build {
  sources = ["source.amazon-ebs.host"]

  provisioner "shell" {
    script = "packer/scripts/setup.sh"
    env = {
      SATELLITE_RPM = "${local.satellite_rpm}"
      SATELLITE_ORG = "${local.satellite_org}"
      SATELLITE_KEY = "${local.satellite_key}"
    }
  }

  provisioner "ansible" {
    groups = ["Class_${var.image_type}", "Status_development", "packer"]
    host_alias = "${var.image_type}"
    playbook_file = "ansible/${var.image_type}.yml"
    use_proxy = false
  }

  provisioner "shell" {
    script = "packer/scripts/cleanup.sh"
  }
}
