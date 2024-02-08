output "calc-networks" {
  value = local.ctrl_ipv6_ips
}
output "ep-networks" {
  value = [for v in vcd_vm.endpoint: v.network]
}
output "ct-networks" {
  value = [for v in vcd_vm.control: v.network]
}
