terraform {
  required_providers {
    vcd = {
      source  = "vmware/vcd"
      version = "3.7"
    }
  }
}

# Configure the VMware Cloud Director Provider
provider "vcd" {
  user      = var.vcd_user
  password  = var.vcd_pass
  auth_type = "integrated"
  org       = var.vcd_org
  vdc       = var.vcd_vdc
  url       = "https://my.wolkee.cloud/api"
  #  max_retry_timeout    = var.vcd_max_retry_timeout
  allow_unverified_ssl = true
}
