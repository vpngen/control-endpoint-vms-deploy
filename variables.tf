variable "vcd_org" {
  type = string
}

variable "vcd_vdc" {
  type = string
}

variable "vcd_user" {
  type = string
}

variable "vcd_pass" {
  type      = string
  sensitive = true
}

variable "vcd_template" {
  type = string
}

variable "vcd_templates_catalog" {
  type = string
}
variable "vm_name_prefix" {
  type      = string
  sensitive = true
}

variable "ssh_key_file" {
  type      = string
  sensitive = true
}

variable "ctrl_name_prefix" {
  type      = string
  sensitive = true
}

variable "ctrl_ipv6_high_hex" {
  type = string
}

variable "wan_ips_per_vm" {
  type = number
}

variable "wan_name_ip_net_gw" {
  type = list(any)
}

variable "lan_name" {
  type      = string
  sensitive = true
}

variable "lan_mgmt_ip" {
  type = string
}

variable "lan_start_ip" {
  type = string
}

variable "endpoint_lan_interfaces" {
  type = list(any)
}

variable "keydesk_deb_repo_string" {
  type      = string
  sensitive = true
}

variable "zabbix_server" {
  type      = string
  sensitive = true
}

variable "endpoint_cpu_cores" {
  type = number
}

variable "endpoint_ram_size" {
  type = number
}
