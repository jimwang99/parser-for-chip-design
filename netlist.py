
# Parent tree
# design
# |---> module
#       |-----> port/wire
#       |-----> instance
#               |-----> pin

class design_t:
    def __init__(self):
        self.modules = dict()

    def add_module(self, module_name):
        if (module_name in self.modules.keys()):
            print 'Error: module (%s) already exisits' % module_name
            return 0
        m = module_t(module_name)
        self.modules(m.name) = m
        return 1

class module_t:
    def __init__(self, name):
        self.name = name

        self.ports = dict()
        self.ls_port = list() # port in order
        self.wires = dict()
        self.instances = dict()

        self.parameters = dict()

        self.is_hierarchical = True

        self.full_name = self.name

    def add_port(self, port_name, direction):
        if (port_name in self.ports.keys()):
            print 'Error: port (%s) in module (%s) already exists' % (port_name, self.full_name)
            return 0
        p = port_t(port_name, self, direction)
        self.ports(p.name) = p
        self.ls_port.append(p)
        return 1

    def add_wire(self, wire_name):
        if (wire_name in self.wires.keys()):
            print 'Error: wire (%s) in module (%s) already exists' % (wire_name, self.full_name)
            return 0
        w = wire_t(wire_name, self)
        self.wires(w.name) = w
        return 1

    def add_instance(self, instance_name):
        if (instance_name in self.instances.keys()):
            print 'Error: instance (%s) in module (%s) already exists' % (instance_name, self.full_name)
            return 0
        w = instance_t(instance_name, self)
        self.instances(w.name) = w
        return 1

    def add_parameter(self, parameter, default_value):
        if (parameter in self.parameters.keys()):
            print 'Error: parameter (%s) in module (%s) already exists' % (parameter, self.full_name)
            return 0
        self.parameters(parameter) = default_value
        return 1

#     def __eq__(self, other):
#         equal = True
#         if not (self.name == other.name):
#             equal = False
#         if not __eq_dict__(self.ports, other.ports):
#             equal = False
#         if not __eq_dict__(self.instances, other.instances):
#             equal = False
#         if not __eq_dict__(self.wires, other.wires):
#             equal = False
# 
#         if not equal:
#             print 'Error: modules (%s != %s) donot match' % (self, other)
# 
#         return equal

class instance_t:
    'instance of module'
    def __init__(self, name, parent_module):
        self.name = name
        self.parent_module = parent_module
        self.pins = dict()

        self.master_module = None
        self.parameters = dict()

        self.full_name =  '%s.%s' % (self.parent_module.name, self.name)

    def add_pin(self, pin_name):
        assert pin_name in self.parent_module.ports.keys(), 'Error: port (%s) doesnot exist in module (%s)' % (pin_name, self.parent_module.name)
        master_port = self.parent_module.ports(pin_name)
        p = pin_t(master_port, self)
        self.pins[p.name] = p

    def connect_pin(self, pin_name, target_name):
        # find target
        m = self.parent_module
        if (target_name in m.ports.keys()):
            target = m.ports(target_name)
        elif (target_name in m.wires.keys()):
            target = m.wires(target_name)
        else:
            print 'Error: cannot find connection (%s) in module (%s) for instance (%s)' % (target_name, m.name, self.name)

        self.pins[pin_name].ls_connect.append(target)
        target.ls_connect.append(self)

    def add_parameter(self, parameter, value):
        assert parameter in self.parent_module.parameters.keys(), 'Error: parameter (%s) doesnot exist in module (%s)' % (parameter, self.parent_module.name)
        self.parameters(parameter) = value

#     def __eq__(self, other):
#         equal = True
#         if (not self.name == other.name) or (not self.parent_module.name == other.parent_module.name) or (not self.master_module.name == other.master_module.name):
#             equal = False
#         if not __eq_dict__(self.pins, other.pins):
#             equal = False
# 
#         if not equal:
#             print 'Error: instances (%s != %s) donot match' % (self, other)
# 
#         return equal

class net_t:
    'basic class for wire/port/pin'
    def __init__(self, name):
        self.name = name
        self.ls_connect = list()

class wire_t(net_t):
    'wire in module, connect to internal pin'
    def __init__(self, name, parent_module):
        net_t.__init__(self, name)
        self.parent_module = parent_module
        self.ls_fanin = list()
        self.ls_fanout = list()

class port_t(net_t):
    'port of module, connect to internal pin'
    def __init__(self, name, parent_module, direction):
        net_t.__init__(self, name)
        self.parent_module = parent_module
        assert direction in 'input output bidirection', direction
        self.direction = direction
        self.full_name = '%s.%s' % (self.parent_module.name, self.name)

#     def __eq__(self, other):
#         if (not self.name == other.name) or (not self.parent_module.name == other.parent_module.name) or (not self.direction == other.direction):
#             print 'Error: ports (%s != %s) donot match' % (self, other)
#             return False
#         else:
#             return True

class pin_t(port_t):
    'pin of instance, connect to external port/wire'
    def __init__(self, master_port, parent_instance):
        net_t.__init__(self, master_port.name)
        self.master_port = master_port
        self.parent_instance = parent_instance

        self.full_name = '%s.%s.%s' % (self.parent_instance.parent_module.name, self.parent_instance.name, self.name)

#     def __eq__(self, other):
#         if (not self.name == other.name) or (not self.master_port.name == other.master_port.name) or (not self.parent_instance.name == other.parent_instance.name):
#             print 'Error: pins (%s != %s) donot match' % (self, other)
#             return False
#         else:
#             return true

################################################################
# compare 2 design/module
################################################################

def __eq_dict__(dict1, dict2):
    if (len(set(dict1.keys()) ^ set(dict2.keys())) > 0):
        return False

    for key in dict1.keys():
        if not (dict1[key] == dict2[port_name]):
            return False

    return True
