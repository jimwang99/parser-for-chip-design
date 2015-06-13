from verilog_netlist_parser import *

print __expand_net_single__('n0', 2, 10, 2, 10)
print __expand_net_single__('n1', 10, 2, 2, 10)
print __expand_net_single__('n2', 10, 10, 10, 10)
print __expand_net_single__('n3', 0, 0, 0, 0)


ref_bus = dict()
ref_bus['n0'] = (2, 10, 2, 10, 9)
ref_bus['n1'] = (10, 2, 2, 10, 9)
ref_bus['n2'] = (10, 10, 10, 10, 1)
ref_bus['n3'] = (0, 0, 0, 0, 1)

print __expand_net__('n0, n1, n2, n3, n7[1:3], n8[4:2]'.split(), ref_buses):
