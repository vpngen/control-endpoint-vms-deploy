terraform {
  required_providers {
    vcd = {
      source = "vmware/vcd"
    }
  }
}

variable "vcd_user" {
  type = string
}

variable "vcd_pass" {
  type = string
  sensitive = true
}

variable "vm_name_prefix" {
  type = string
  sensitive = true
}

variable "ssh_key_file" {
  type = string
  sensitive = true
}

variable "ctrl_name_prefix" {
  type = string
  sensitive = true
}

variable "ctrl_ipv6_high_hex" {
  type = string
}

variable "wan_ips_per_vm" {
  type = number
}

variable "wan_name_ip_net_gw" {
  type = list
}

variable "lan_name" {
  type = string
  sensitive = true
}

variable "lan_mgmt_ip" {
  type = string
}

variable "lan_start_ip" {
  type = string
}

variable "endpoint_lan_interfaces" {
  type = list
}

# Configure the VMware Cloud Director Provider
provider "vcd" {
  user                 = var.vcd_user
  password             = var.vcd_pass
  auth_type            = "integrated"
  org                  = "highload"
  vdc                  = "vdc_highload"
  url                  = "https://my.wolkee.cloud/api"
#  max_retry_timeout    = var.vcd_max_retry_timeout
  allow_unverified_ssl = true
}

locals {
  ctrl_ipv6_ips = [for ipv6 in var.wan_name_ip_net_gw : format("%s:%x:%x:0:0:0:0:",
    var.ctrl_ipv6_high_hex, split(".", ipv6[1])[0] * 256 + split(".", ipv6[1])[1],
      split(".", ipv6[1])[2] * 256 + split(".", ipv6[1])[3])]
  vm_pairs = ceil(length(var.wan_name_ip_net_gw) / var.wan_ips_per_vm)
  lan_start_ip_int = split(".", var.lan_start_ip)[0] * 16777216 + split(".", var.lan_start_ip)[1] * 65536 + split(".", var.lan_start_ip)[2] * 256 + split(".", var.lan_start_ip)[3]
}

resource "vcd_network_isolated_v2" "control_net" {
  for_each      = toset([for vm_num in range(0, local.vm_pairs) : tostring(vm_num)])
  org           = "highload"
  name          = "${var.ctrl_name_prefix}-${each.value}"
  gateway       = "${var.ctrl_ipv6_high_hex}:0:0:0:0:0:0:1"
  prefix_length = 16

  dynamic "static_ip_pool" {
    for_each = slice(local.ctrl_ipv6_ips, each.value * var.wan_ips_per_vm, min((each.value + 1) * var.wan_ips_per_vm, length(local.ctrl_ipv6_ips)))
    content {
      start_address = format("%s2", static_ip_pool.value)
      end_address   = format("%s3", static_ip_pool.value)
    }
  }
}

resource "null_resource" "script-ct" {
  for_each = toset([for vm_num in range(0, local.vm_pairs) : tostring(vm_num)])

  triggers = {
    dest_file   = "script-ct.sh.${each.value}"
  }

  provisioner "local-exec" {
    command = <<EOT
cat script-ct.sh.init > script-ct.sh.${each.value} ;
sed -i 's#{ipv6_input}#${join("2,", slice(local.ctrl_ipv6_ips, each.value * var.wan_ips_per_vm, min((each.value + 1) * var.wan_ips_per_vm, length(local.ctrl_ipv6_ips))))}2#' script-ct.sh.${each.value} ;
sed -i 's#{apt_proxy}#${var.lan_mgmt_ip}#g' script-ct.sh.${each.value} ;
tar czp -C setup-files-ct/ --exclude='.git' . | base64 >> script-ct.sh.${each.value}
EOT
  }
}

data "local_file" "script-ct_file" {
  for_each = toset([for vm_num in range(0, local.vm_pairs) : tostring(vm_num)])

  filename = null_resource.script-ct[each.value].triggers.dest_file
}


resource "vcd_vm" "control" {
  for_each      = toset([for vm_num in range(0, local.vm_pairs) : tostring(vm_num)])
  depends_on    = [vcd_network_isolated_v2.control_net, data.local_file.script-ct_file]
  name          = "${var.vm_name_prefix}ct-${each.value}"
  catalog_name  = "VM Templates"
  template_name = "Ubuntu 22.04 Server (20220712)"
  memory        = 1024
  cpus          = 1

  override_template_disk {
    bus_type        = "paravirtual"
    size_in_mb      = "10240"
    bus_number      = 0
    unit_number     = 0
    iops            = 0
    storage_profile = "spCLOUD"
  }

  guest_properties = {
    "hostname"    = "${var.vm_name_prefix}ct-${each.value}"
    "public-keys" = file(var.ssh_key_file)
    "user-data"   = base64encode(data.local_file.script-ct_file[each.value].content)
  }

  network {
    type               = "org"
    name               = var.lan_name
    ip_allocation_mode = "MANUAL"
    ip                 = format("%d.%d.%d.%d", floor(local.lan_start_ip_int / 16777216),
                          floor((local.lan_start_ip_int % 16777216) / 65536),
                          floor((local.lan_start_ip_int % 65536) / 256),
                          (local.lan_start_ip_int % 256) + each.value * 2)
    is_primary         = true
  }

  network {
    type               = "org"
    name               = "${var.ctrl_name_prefix}-${each.value}"
    ip_allocation_mode = "MANUAL"
    ip                 = format("%s2", local.ctrl_ipv6_ips[each.value * var.wan_ips_per_vm])
    is_primary         = false
  }
}

resource "null_resource" "script-ep" {
  for_each = toset([for vm_num in range(0, local.vm_pairs) : tostring(vm_num)])

  triggers = {
    dest_file   = "script-ep.sh.${each.value}"
  }

  provisioner "local-exec" {
    command = <<EOT
cat script-ep.sh.init > script-ep.sh.${each.value} ;
sed -i 's#{ip_wan_input}#${join(",", [for ip in slice(var.wan_name_ip_net_gw, each.value * var.wan_ips_per_vm, min((each.value + 1) * var.wan_ips_per_vm, length(var.wan_name_ip_net_gw))) : format("%s/%d|%s", ip[1], ip[2], ip[3])])}#' script-ep.sh.${each.value} ;
sed -i 's#{ipv6_input}#${join("3,", slice(local.ctrl_ipv6_ips, each.value * var.wan_ips_per_vm, min((each.value + 1) * var.wan_ips_per_vm, length(local.ctrl_ipv6_ips))))}3#' script-ep.sh.${each.value} ;
sed -i 's#{apt_proxy}#${format("%s2", local.ctrl_ipv6_ips[each.value * var.wan_ips_per_vm])}#g' script-ep.sh.${each.value} ;
tar czp -C setup-files-ep/ --exclude='.git' . | base64 >> script-ep.sh.${each.value}
EOT
  }
}

data "local_file" "script-ep_file" {
  for_each = toset([for vm_num in range(0, local.vm_pairs) : tostring(vm_num)])

  filename = null_resource.script-ep[each.value].triggers.dest_file
}

resource "vcd_vm" "endpoint" {
  for_each      = toset([for vm_num in range(0, local.vm_pairs) : tostring(vm_num)])
  depends_on    = [vcd_network_isolated_v2.control_net, data.local_file.script-ep_file]
  name          = "${var.vm_name_prefix}ep-${each.value}"
  catalog_name  = "VM Templates"
  template_name = "Ubuntu 22.04 Server (20220712)"
  memory        = 1024
  cpus          = 1

  override_template_disk {
    bus_type        = "paravirtual"
    size_in_mb      = "10240"
    bus_number      = 0
    unit_number     = 0
    iops            = 0
    storage_profile = "spCLOUD"
  }

  guest_properties = {
    "hostname"    = "${var.vm_name_prefix}ep-${each.value}"
    "public-keys" = file(var.ssh_key_file)
    "user-data"   = base64encode(data.local_file.script-ep_file[each.value].content)
  }

  dynamic "network" {
    for_each = setintersection(var.endpoint_lan_interfaces,
        [ format("%d.%d.%d.%d", floor(local.lan_start_ip_int / 16777216),
            floor((local.lan_start_ip_int % 16777216) / 65536),
            floor((local.lan_start_ip_int % 65536) / 256),
            (local.lan_start_ip_int % 256) + each.value * 2 + 1) ])
    content {
      type               = "org"
      name               = var.lan_name
      ip_allocation_mode = "MANUAL"
      ip                 = network.value
      is_primary         = false
    }
  }

  dynamic "network" {
    for_each = slice(var.wan_name_ip_net_gw, each.value * var.wan_ips_per_vm, min((each.value + 1) * var.wan_ips_per_vm, length(var.wan_name_ip_net_gw)))
    content {
      type               = "org"
      name               = network.value[0]
      ip_allocation_mode = "MANUAL"
      ip                 = network.value[1]
      is_primary         = false
    }
  }

  network {
    type               = "org"
    name               = "${var.ctrl_name_prefix}-${each.value}"
    ip_allocation_mode = "MANUAL"
    ip                 = format("%s3", local.ctrl_ipv6_ips[each.value * var.wan_ips_per_vm])
    is_primary         = true
  }
}
