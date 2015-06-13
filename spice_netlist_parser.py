
import os
import re

from netlist import *

################################################################

def spice_netlist_parser (ls_spice_netlist_fpath, nmos_name='NCH_MAC NCH_MAC_PSVT NCH_MAC_NSVT', pmos_name='PCH_MAC NCH_MAC_PSVT NCH_MAC_NSVT'):
    """
    >> class design_t()
    """
    design = design_t()

    ls_nmos_name = nmos_name.lower().split()
    ls_pmos_name = pmos_name.lower().split()

    for mos_name in (ls_nmos+ls_pmos):
        mos = design.add_module(mos_name)
        assert mos

        mos.is_hierarchical = False
        if (mos_name in ls_nmos_name):
            mos.is_nmos = True
            mos.is_pmos = False
        elif (mos_name in ls_pmos_name):
            mos.is_nmos = False
            mos.is_pmos = True

        mos.add_port('d', 'bidirection')
        mos.add_port('g', 'bidirection')
        mos.add_port('b', 'bidirection')
        mos.add_port('s', 'bidirection')
        mos.add_param('l', 28e-9)
        mos.add_param('w', 28e-9)
        mos.add_param('w', 28e-9)

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
            try:
                idx_equal = ls_tk.index('=')
                ls_port_name = ls_tk[2:idx_equal-1]
                ls_param_tk = ls_tk[idx_equal-1:]
            except:
                ls_port_name = ls_tk[2:]
                ls_param_tk = list()

            assert module == None
            module = module_t(module_name)
            design.modules[module.name] = module

            # port
            for port_name in ls_port_name:
                module.add_port(port_name, 'bidirection')

            # param
            for (param_name, param_value) in parse_param_token(ls_param_tk):
                module.add_param(param_name, param_value)

        #-------------------------------------------------------
        # parse module end
        elif (first == '.ends'):
            assert module != None
            module = None

        #-------------------------------------------------------
        # parse instance
        elif (first[0] == 'x') or (first[0] == 'm'):
            instance_name = ls_tk[0]
            instance = instance_t(instance_name, module)

            try:
                idx_equal = ls_tk.index('=')
                instance.master_module_name = ls_tk[idx]
                instance.ls_pin_connect = ls_tk[1:idx_equal-1]
                instance.ls_param_tk = ls_tk[idx_equal-1:]
            except:
                instance.master_module_name = ls_tk[-1]
                instance.ls_pin_connect = ls_tk[1:-1]
                instance.ls_param_tk = list()

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
    # solve instance reference and pin connect
    for module in design.modules.values():
        for instance in module.instances.values():
            # instance's master module
            instance.master_module = design.modules[instance.master_module_name]
            del instance.master_module_name

            # instance's pin connect
            assert len(instance.ls_pin_connect) == len(instance.master_module.ls_port), ' (PIN) %s\n((PORT)%s' % (instance.ls_pin_connect, instance.master_module.ports.keys())

            for (connect_name, port) in zip(instance.ls_pin_connect, instance.master_module.ls_port):
                instance.connect_pin(port.name, connect_name)

            # instance's parameter

    return design

def parse_param_token (ls_tk):
    '>> (name, value)
    ls_param = list()
    while len(ls_tk) > 0:
        name = ls_tk.pop(0)
        assert ls_tk.pop(0) == '=', ls_tk
        try:
            next_idx_equal = ls_tk.index('=')
            value = ''.join(ls_tk[:next_idx_equal-1])
            ls_tk = ls_tk[next_idx_equal-1:]
        except:
            value = ''.join(ls_tk)
            ls_tk = list()
        value = value.strip("'")

        ls_param.append((name, value))

    return ls_param


if __name__ == '__main__':
    ram1 = spice_netlist_parser(['./test/ram.spi'], nmos='TN', pmos='PN')
    ram2 = spice_netlist_parser(['./test/ram.spi'], nmos='TN', pmos='PN')

    if (ram1 == ram2):
        print 'equal'
