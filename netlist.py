
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
            return None
        m = module_t(module_name)
        self.modules(m.name) = m
        return m

class module_t:
    def __init__(self, name):
        self.name = name

        self.ports = dict()
        self.ls_port = list() # port in order
        self.wires = dict()
        self.instances = dict()

        self.params = dict()

        self.is_hierarchical = True

        self.full_name = self.name

    def add_port(self, port_name, direction):
        if (port_name in self.ports.keys()):
            print 'Error: port (%s) in module (%s) already exists' % (port_name, self.full_name)
            return None
        p = port_t(port_name, self, direction)
        self.ports(p.name) = p
        self.ls_port.append(p)
        return p

    def add_wire(self, wire_name):
        if (wire_name in self.wires.keys()):
            print 'Error: wire (%s) in module (%s) already exists' % (wire_name, self.full_name)
            return None
        w = wire_t(wire_name, self)
        self.wires(w.name) = w
        return w

    def add_instance(self, instance_name):
        if (instance_name in self.instances.keys()):
            print 'Error: instance (%s) in module (%s) already exists' % (instance_name, self.full_name)
            return None
        n = instance_t(instance_name, self)
        self.instances(n.name) = n
        return n

    def add_param(self, param, default_value):
        if (param in self.params.keys()):
            print 'Error: param (%s) in module (%s) already exists' % (param, self.full_name)
            return 0
        self.params(param) = default_value
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
        self.params = dict()

        self.full_name =  '%s.%s' % (self.parent_module.name, self.name)

        for master_port in self.parent_module.ports.values():
            p = pin_t(master_port, self)
            self.pins[p.name] = p

    def connect_pin(self, pin_name, connect_name):
        # find connect
        m = self.parent_module
        if (connect_name in m.ports.keys()):
            connect = m.ports(connect_name)
        elif (connect_name in m.wires.keys()):
            connect = m.wires(connect_name)
        else:
            print 'Error: cannot find connect (%s) in module (%s) for instance (%s)' % (connect_name, m.name, self.name)

        self.pins[pin_name].ls_connect.append(connect)
        connect.ls_connect.append(self)

    def add_param(self, param, value):
        assert param in self.parent_module.params.keys(), 'Error: param (%s) doesnot exist in module (%s)' % (param, self.parent_module.name)
        self.params(param) = value

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
