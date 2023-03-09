
variable "do_token" {}

variable "port" {
  default = "3128"
}
variable "user" {
  default = "example"
}
variable "pass" {
  default = "example"
}

output "ips" {
  value = [for p in digitalocean_droplet.proxies[*].ipv4_address : "http://${var.user}:${var.pass}@${p}:${var.port}"]
}

provider "digitalocean" {
  token = var.do_token
}

resource digitalocean_droplet "proxies" {
  name   = "proxy-droplet-${count.index + 1}"
  count  = 20
  region = "fra1"
  size   = "s-1vcpu-1gb"
  image  = "docker-20-04"

  ssh_keys = [
    "6c:b6:6e:a7:a2:ef:48:96:b0:d4:8b:31:3e:75:f7:1f"
  ]

  connection {
    type = "ssh"
    host = self.ipv4_address
    user = "root"
  }

  provisioner "remote-exec" {
    inline = [
      <<-EOF
            sleep 5
            ufw --force reset
            ufw default deny incoming
            ufw default allow outgoing
            ufw allow ssh
            ufw allow ${var.port}
            ufw --force enable
            docker run --restart=always -d -p ${var.port}:3128 \
            -e SQUID_USER=${var.user} \
            -e SQUID_PASS=${var.pass} \
            bukowa/squidproxy
            EOF
    ]
  }
}

#  user_data = <<-EOF
#            #!/bin/bash
#            sleep 5
#            ufw --force reset
#            ufw default deny incoming
#            ufw default allow outgoing
#            ufw allow ssh
#            ufw allow http
#            ufw allow https
#            ufw allow 3128
#            ufw --force enable
#            docker run --restart=always -d -p 3128:3128 \
#            -e SQUID_USER=${var.user} \
#            -e SQUID_PASS=${var.pass} \
#            bukowa/squidproxy
#            EOF
#}

#
#provider "docker" {
#  host = "ssh://root@${digitalocean_droplet.nginx_proxy.ipv4_address}:22"
#  ssh_opts = ["-o", "StrictHostKeyChecking=no"]
#}

#
#resource "docker_container" "squid" {
#  image = "bukowa/squidproxy"
#  name  = "proxy"
#  restart = "always"
#  network_mode = "host"
#  env = [
#    "SQUID_USER=${var.user}",
#    "SQUID_PASS=${var.pass}",
#  ]
#}
#

terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
#    docker = {
#      source  = "kreuzwerker/docker"
#      version = "~> 3.0.1"
#    }
  }
}