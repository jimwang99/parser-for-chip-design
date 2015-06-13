
import os
import re

from netlist import *

################################################################

def spice_netlist_parser (ls_spice_netlist_fpath, nmos='NCH_MAC', pmos='PCH_MAC'):
    """
    >> class design_t()
    """
    design = design_t()

    ls_nmos = nmos.lower().split()
    ls_pmos = pmos.lower().split()

    #===========================================================
    # read all spice netlist file into memory (ls_raw)
    #   and remove comment, concate lines
    ls_raw = list() # content = (line, fpath_idx, line_idx)

    for (fpath_idx, fpath) in enumerate(ls_spice_netlist_fpath):
        assert os.path.isfile(fpath), 'Cannot find spice netlist file %s' % fpath
        f = open(fpath, 'r')

        for (line_idx, line) in enumerate(f):
            # remove spice style comment
            line = re.sub(r'\*.*', '', line.strip())
            line = re.sub(r'\$.*', '', line.strip())

            if (len(line) == 0):
                continue

            ls_raw.append((line.strip(), fpath_idx, line_idx))

        f.close()

    #===========================================================
    # concate lines into full statement and save into memory (ls_stmt)
    ls_stmt = list() # content = (stmt, fpath_idx, begin_line_idx, end_line_idx)

    stmt = ''
    for (line, fpath_idx, line_idx) in reversed(ls_raw):
        if (line[0] == r'+'):
            line = ' ' + line[1:]
            if (len(stmt) == 0):
                # no previous found continue line
                end_line_idx = line_idx
                stmt = line
            else:
                # with previous found continue line
                stmt = line + stmt
        else:
            # current line is not a continue line
            begin_line_idx = line_idx
            if (len(stmt) == 0):
                # no previous found continue line
                end_line_idx = line_idx
                stmt = line
            else:
                # with previous found continue line
                stmt = line + stmt

            ls_stmt.append((stmt, fpath_idx, begin_line_idx, end_line_idx))

            stmt = ''

    ls_stmt.reverse()

    #===========================================================
    # parse statement
    module = None
    for (stmt, fpath_idx, begin_line_idx, end_line_idx) in ls_stmt:
        stmt = stmt.replace(r"'", " ' ")
        stmt = stmt.replace(r'=', ' = ')
        stmt = re.sub(r'\s+', ' ', stmt)

        ls_tk = stmt.lower().split()

        first = ls_tk[0]
        #-------------------------------------------------------
        # parse subckt title
        if (first == '.subckt'):
            module_name = ls_tk[1]
            ls_port_name = ls_tk[2:]

            assert module == None
            module = module_t(module_name)
            design.modules[module.name] = module

            module.ls_port_name = ls_port_name # preserve the order of ports
            for port_name in ls_port_name:
                port = port_t(port_name, module, 'bidirection')
                module.ports[port.name] = port

        #-------------------------------------------------------
        # parse module end
        elif (first == '.ends'):
            assert module != None
            module = None

        #-------------------------------------------------------
        # parse instance
        elif (first[0] == 'x') or (first[0] == 'm'):
            instance_name = ls_tk[0]

            try:
                idx = ls_tk.index('=') - 2
            except:
                idx = -1

            instance = instance_t(instance_name, module)
            instance.master_module_name = ls_tk[idx]
            instance.ls_pin_connection = ls_tk[1:idx]

            module.instances[instance.name] = instance

        #-------------------------------------------------------
        # parse special
        elif (first[0] == '.'):
            #TODO param, option, global
            if (first[0] == '.global'):
                pass
            elif (first[0] == '.param'):
                pass
            elif (first[0] == '.option'):
                pass
            else:
                print 'Warning: Statement is not supported at line (%d to %d) in file (%s) \"%s\"' % (begin_line_idx+1, end_line_idx+1, ls_spice_netlist_fpath[fpath_idx], stmt)

        #-------------------------------------------------------
        else:
            print 'Warning: Statement is not supported at line (%d to %d) in file (%s) \"%s\"' % (begin_line_idx+1, end_line_idx+1, ls_spice_netlist_fpath[fpath_idx], stmt)

    #===========================================================
    # solve instance reference and pin connection
    for module in design.modules.values():
        for instance in module.instances.values():
            # instance's master module
            if (instance.master_module_name in ls_nmos):
                instance.is_mos = True
            elif (instance.master_module_name in ls_pmos):
                instance.is_mos = True
            else:
                instance.master_module = design.modules[instance.master_module_name]
            del instance.master_module_name

            # instance's pin connection
            assert len(instance.ls_pin_connection) == len(instance.master_module.ls_port_name), ' (PIN) %s\n((PORT)%s' % (instance.ls_pin_connection, instance.master_module.ls_port_name)

            for (pin_connection, port_name) in zip(instance.ls_pin_connection, instance.master_module.ls_port_name):
                pin = pin_t(instance.master_module.ports[port_name], instance)
                instance.pins[pin.name] = pin

    return design


if __name__ == '__main__':
    ram1 = spice_netlist_parser(['./test/ram.spi'], nmos='TN', pmos='PN')
    ram2 = spice_netlist_parser(['./test/ram.spi'], nmos='TN', pmos='PN')

    if (ram1 == ram2):
        print 'equal'
