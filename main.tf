locals {
  ctrl_ipv6_ips = [
    for ipv6 in var.wan_name_ip_net_gw : format(
      "%s:%x:%x:0:0:0:0:",
      var.ctrl_ipv6_high_hex,
      split(".", ipv6[1])[0] * 256 + split(".", ipv6[1])[1],
      split(".", ipv6[1])[2] * 256 + split(".", ipv6[1])[3]
    )
  ]

  vm_pairs = ceil(length(var.wan_name_ip_net_gw) / var.wan_ips_per_vm)

  lan_start_ip_int = split(".", var.lan_start_ip)[0] * 16777216 + split(".", var.lan_start_ip)[1] * 65536 + split(".", var.lan_start_ip)[2] * 256 + split(".", var.lan_start_ip)[3]
}

resource "vcd_network_isolated_v2" "control_net" {
  count         = local.vm_pairs
  org           = var.vcd_org
  name          = "${var.ctrl_name_prefix}-${count.index}"
  gateway       = "${var.ctrl_ipv6_high_hex}:0:0:0:0:0:0:1"
  prefix_length = 16

  dynamic "static_ip_pool" {
    for_each = slice(
      local.ctrl_ipv6_ips,
      count.index * var.wan_ips_per_vm,
      min((count.index + 1) * var.wan_ips_per_vm, length(local.ctrl_ipv6_ips))
    )
    content {
      start_address = format("%s2", static_ip_pool.value)
      end_address   = format("%s3", static_ip_pool.value)
    }
  }
}

resource "null_resource" "script-ct" {
  count = local.vm_pairs

  triggers = {
    dest_file = ".script-files/script-ct.sh.${count.index}"
  }

  provisioner "local-exec" {
    command = <<EOT
mkdir -p .script-files ;
mkdir -p .vm-nacl-keys/key-pair.${count.index}/etc ;
nacl genkey > .vm-nacl-keys/key-pair.${count.index}/vg-endpoint.json ;
nacl pubkey < .vm-nacl-keys/key-pair.${count.index}/vg-endpoint.json > .vm-nacl-keys/key-pair.${count.index}/etc/vg-router.json ;
cat script-ct.sh.init > .script-files/script-ct.sh.${count.index} ;
sed -i 's#{ipv6_input}#${join("2,", slice(local.ctrl_ipv6_ips, count.index * var.wan_ips_per_vm, min((count.index + 1) * var.wan_ips_per_vm, length(local.ctrl_ipv6_ips))))}2#' .script-files/script-ct.sh.${count.index} ;
sed -i 's#{apt_proxy}#${var.lan_mgmt_ip}#g' .script-files/script-ct.sh.${count.index} ;
sed -i 's#{rsyslog_remote}#${var.lan_mgmt_ip}#g' .script-files/script-ct.sh.${count.index} ;
sed -i 's#{keydesk_repo}#${var.keydesk_deb_repo_string}#g' .script-files/script-ct.sh.${count.index} ;
sed -i 's#{zabbix_server}#${var.zabbix_server}#g' .script-files/script-ct.sh.${count.index} ;
sed -i 's#{endpoint_ipv6}#${format("%s3", local.ctrl_ipv6_ips[count.index * var.wan_ips_per_vm])}#g' .script-files/script-ct.sh.${count.index} ;
tar czp -C setup-files-ct/ --exclude='.git' . -C ../.vm-nacl-keys/key-pair.${count.index}/ etc/vg-router.json | base64 >> .script-files/script-ct.sh.${count.index}
EOT
  }

  provisioner "local-exec" {
    when    = destroy
    command = <<EOT
rm -f ${self.triggers.dest_file}
EOT
  }
}

data "local_file" "script-ct_file" {
  count    = local.vm_pairs
  filename = null_resource.script-ct[count.index].triggers.dest_file
}

resource "vcd_vm" "control" {
  count         = local.vm_pairs
  depends_on    = [vcd_network_isolated_v2.control_net]
  name          = "${var.vm_name_prefix}ct-${count.index}"
  catalog_name  = var.vcd_templates_catalog
  template_name = var.vcd_template
  memory        = 1024
  cpus          = 1

  lifecycle {
    ignore_changes = [
      template_name,
    ]
  }

  override_template_disk {
    bus_type        = "paravirtual"
    size_in_mb      = "10240"
    bus_number      = 0
    unit_number     = 0
    iops            = 0
    storage_profile = "spCLOUD"
  }

  guest_properties = {
    "hostname"    = "${var.vm_name_prefix}ct-${count.index}"
    "public-keys" = file(var.ssh_key_file)
    "user-data"   = base64encode(data.local_file.script-ct_file[count.index].content)
  }

  network {
    type               = "org"
    name               = var.lan_name
    ip_allocation_mode = "MANUAL"
    ### BASH reference: sft=$(( ((intip & 0xFF) + 2 * ( i + 1 + ((intip & 0xFF) + 2 * (i + 1)) / 256 * 2 )) / 256 * 2)) ; echo $((intip+2*(i+sft)))
    ip = format("%d.%d.%d.%d", floor((local.lan_start_ip_int + 2 * (count.index +
      floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1 + floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1)) / 256) * 2)) / 256) * 2
      )) / 16777216),
      floor(((local.lan_start_ip_int + 2 * (count.index +
        floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1 + floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1)) / 256) * 2)) / 256) * 2
      )) % 16777216) / 65536),
      floor(((local.lan_start_ip_int + 2 * (count.index +
        floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1 + floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1)) / 256) * 2)) / 256) * 2
      )) % 65536) / 256),
      (local.lan_start_ip_int + 2 * (count.index +
        floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1 + floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1)) / 256) * 2)) / 256) * 2
    )) % 256)
    is_primary = true
  }

  network {
    type               = "org"
    name               = "${var.ctrl_name_prefix}-${count.index}"
    ip_allocation_mode = "MANUAL"
    ip                 = format("%s2", local.ctrl_ipv6_ips[count.index * var.wan_ips_per_vm])
    is_primary         = false
  }

  connection {
    host        = self.network[0].ip
    user        = "ubuntu"
    private_key = file(replace(var.ssh_key_file, ".pub", ""))
  }

  provisioner "remote-exec" {
    script = "scripts/wait-cloud-init.sh"
  }
}

resource "null_resource" "script-ep" {
  count      = local.vm_pairs
  depends_on = [data.local_file.script-ct_file]

  triggers = {
    dest_file = ".script-files/script-ep.sh.${count.index}"
  }

  provisioner "local-exec" {
    command = <<EOT
mkdir -p .script-files ;
cat script-ep.sh.init > .script-files/script-ep.sh.${count.index} ;
sed -i 's#{ip_wan_input}#${join(",", [for ip in slice(var.wan_name_ip_net_gw, count.index * var.wan_ips_per_vm, min((count.index + 1) * var.wan_ips_per_vm, length(var.wan_name_ip_net_gw))) : format("%s/%d|%s", ip[1], ip[2], ip[3])])}#' .script-files/script-ep.sh.${count.index} ;
sed -i 's#{ipv6_input}#${join("3,", slice(local.ctrl_ipv6_ips, count.index * var.wan_ips_per_vm, min((count.index + 1) * var.wan_ips_per_vm, length(local.ctrl_ipv6_ips))))}3#' .script-files/script-ep.sh.${count.index} ;
sed -i 's#{apt_proxy}#${format("%s2", local.ctrl_ipv6_ips[count.index * var.wan_ips_per_vm])}#g' .script-files/script-ep.sh.${count.index} ;
sed -i 's#{keydesk_repo}#${var.keydesk_deb_repo_string}#g' .script-files/script-ep.sh.${count.index} ;
sed -i 's#{control_ipv6_list}#${join("2,", slice(local.ctrl_ipv6_ips, count.index * var.wan_ips_per_vm, min((count.index + 1) * var.wan_ips_per_vm, length(local.ctrl_ipv6_ips))))}2#' .script-files/script-ep.sh.${count.index} ;
tar czp -C setup-files-ep/ --exclude='.git' . -C ../.vm-nacl-keys/key-pair.${count.index}/ vg-endpoint.json | base64 >> .script-files/script-ep.sh.${count.index}
EOT
  }

  provisioner "local-exec" {
    when    = destroy
    command = <<EOT
rm -f ${self.triggers.dest_file}
EOT
  }
}

data "local_file" "script-ep_file" {
  for_each = toset([for vm_num in range(0, local.vm_pairs) : tostring(vm_num)])

  filename = null_resource.script-ep[each.value].triggers.dest_file
}

resource "vcd_vm" "endpoint" {
  count         = local.vm_pairs
  depends_on    = [vcd_network_isolated_v2.control_net]
  name          = "${var.vm_name_prefix}ep-${count.index}"
  catalog_name  = var.vcd_templates_catalog
  template_name = var.vcd_template
  memory        = var.endpoint_ram_size
  cpus          = var.endpoint_cpu_cores

  lifecycle {
    ignore_changes = [
      template_name,
    ]
  }

  override_template_disk {
    bus_type        = "paravirtual"
    size_in_mb      = "10240"
    bus_number      = 0
    unit_number     = 0
    iops            = 0
    storage_profile = "spCLOUD"
  }

  guest_properties = {
    "hostname"    = "${var.vm_name_prefix}ep-${count.index}"
    "public-keys" = file(var.ssh_key_file)
    "user-data"   = base64encode(data.local_file.script-ep_file[count.index].content)
  }

  dynamic "network" {
    for_each = setintersection(
      (var.endpoint_lan_interfaces[0] == "all")
      ? [
        format("%d.%d.%d.%d", floor((local.lan_start_ip_int + 2 * (count.index +
          floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1 + floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1)) / 256) * 2)) / 256) * 2
          )) / 16777216),
          floor(((local.lan_start_ip_int + 2 * (count.index +
            floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1 + floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1)) / 256) * 2)) / 256) * 2
          )) % 16777216) / 65536),
          floor(((local.lan_start_ip_int + 2 * (count.index +
            floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1 + floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1)) / 256) * 2)) / 256) * 2
          )) % 65536) / 256),
          (local.lan_start_ip_int + 2 * (count.index +
            floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1 + floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1)) / 256) * 2)) / 256) * 2
        )) % 256 + 1)
      ]
      : var.endpoint_lan_interfaces,
      [
        format("%d.%d.%d.%d", floor((local.lan_start_ip_int + 2 * (count.index +
          floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1 + floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1)) / 256) * 2)) / 256) * 2
          )) / 16777216),
          floor(((local.lan_start_ip_int + 2 * (count.index +
            floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1 + floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1)) / 256) * 2)) / 256) * 2
          )) % 16777216) / 65536),
          floor(((local.lan_start_ip_int + 2 * (count.index +
            floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1 + floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1)) / 256) * 2)) / 256) * 2
          )) % 65536) / 256),
          (local.lan_start_ip_int + 2 * (count.index +
            floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1 + floor(((local.lan_start_ip_int % 256) + 2 * (count.index + 1)) / 256) * 2)) / 256) * 2
        )) % 256 + 1)
    ])
    content {
      type               = "org"
      name               = var.lan_name
      ip_allocation_mode = "MANUAL"
      ip                 = network.value
    }
  }

  network {
    type               = "org"
    name               = "${var.ctrl_name_prefix}-${count.index}"
    ip_allocation_mode = "MANUAL"
    ip                 = format("%s3", local.ctrl_ipv6_ips[count.index * var.wan_ips_per_vm])
  }

  dynamic "network" {
    for_each = slice(
      var.wan_name_ip_net_gw,
      count.index * var.wan_ips_per_vm, min((count.index + 1) * var.wan_ips_per_vm, length(var.wan_name_ip_net_gw))
    )

    content {
      type               = "org"
      name               = network.value[0]
      ip_allocation_mode = "MANUAL"
      ip                 = network.value[1]
      is_primary         = false
    }
  }


  connection {
    host        = self.network[0].ip
    user        = "ubuntu"
    private_key = file(replace(var.ssh_key_file, ".pub", ""))
  }

  provisioner "remote-exec" {
    script = "scripts/wait-cloud-init.sh"
  }
}
