#!/usr/bin/env python3
#coding: utf-8

#
# Get-MolecularMass
#

import io, sys, os
import re
import argparse
import json
from pymatgen.core import Composition
import urllib.parse

_version = "Sat Dec 30 16:19:17 JST 2023"
_code    = "MyCommands(LINUX+WINDOWS/PYTHON3/UTF-8)"

## switch stdio by platform
if os.name == 'nt':
    ## on windows
    sys.stdin  = io.TextIOWrapper(sys.stdin.buffer,  encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
elif os.name == 'posix':
    ## on linux
    sys.stdin  = open('/dev/stdin',  'r', encoding='utf-8')

def raise_error(msg, *arg):
    scriptfile = os.path.basename(__file__)
    errorheader = "Error[" + scriptfile + "]:"
    print(errorheader, msg.format(arg), file=sys.stderr)
    sys.exit(1)

def get_args():
    help_desc_msg = r"""Get-MolecularMass - Get molecular data using pymatgen

    Usage:
        '<comp>, <comp>' | python Get-MolecularMass.py
        python Get-MolecularMass.py -f '<comp>, <comp>'

    Dependency:
        pymatgen
        https://pymatgen.org/

        GitHub - materialsproject/pymatgen
        https://github.com/materialsproject/pymatgen
        https://pymatgen.org/pymatgen.core.html
    
    Install:
        python -m pip install pymatgen
        https://github.com/materialsproject/pymatgen#installation

    Tips:
        Each molecular weight is stored in the variables "M<int>", "N<int>".
        <int> is assigned 1, 2, 3,... in the order of read molecules.

            - M<int> is Molecular weight for each record.
            - N<int> is Molecular name for each record.

        Calculations using molecular weight can be performed using
        this variable with the following options:

            --begin   "<exp;exp;...>"
            --process "<exp;exp;...>"
            --end     "<exp;exp;...>"

        In the --process, the "#" symbol is assigned 1,2,3,...
        in the order of molecules read.
    
    Links:
        Calc-ChemMassPercent.py, Calc-ChemWeightLR.py,
        Get-PeriodicTable.py, Get-MolecularMass.py,
        Calc-ChemMassPercent.py
    """
    help_epi_msg = r"""EXAMPLES:

    # Using PowerShell on Windows:
    "LiFePO4, H4O2, CH2(SO4)2" | python Get-MolecularMass.py --short

        name              : LiFePO4
        name_reduced_i    : LiFePO4, 1.0
        chem_system       : Fe-Li-O-P
        molar_mass        : 157.7574 (g/mol)
        as_dict           : {'Li': 1.0, 'Fe': 1.0, 'P': 1.0, 'O': 4.0}
        fractional_comp   : Li0.14285714 Fe0.14285714 P0.14285714 O0.57142857
        set_variable      : M1 = 157.757362 (g/mol)

        name              : H4O2
        name_reduced_i    : H2O, 2.0
        chem_system       : H-O
        molar_mass        : 36.0306 (g/mol)
        as_dict           : {'H': 4.0, 'O': 2.0}
        fractional_comp   : H0.66666667 O0.33333333
        set_variable      : M2 = 36.03056 (g/mol)

        name              : CH2(SO4)2
        name_reduced_i    : H2C(SO4)2, 1.0
        chem_system       : C-H-O-S
        molar_mass        : 206.1518 (g/mol)
        as_dict           : {'C': 1.0, 'H': 2.0, 'S': 2.0, 'O': 8.0}
        fractional_comp   : C0.07692308 H0.15384615 S0.15384615 O0.61538462
        set_variable      : M3 = 206.15177999999997 (g/mol)

    # Calculation example using molecular weight variables "M<int>"
    "LiFePO4, CH2(SO4)2" | python Get-MolecularMass.py -s --end 'print(M1 + M2)'

        name              : LiFePO4
        name_reduced_i    : LiFePO4, 1.0
        chem_system       : Fe-Li-O-P
        molar_mass        : 157.7574 (g/mol)
        as_dict           : {'Li': 1.0, 'Fe': 1.0, 'P': 1.0, 'O': 4.0}
        fractional_comp   : Li0.14285714 Fe0.14285714 P0.14285714 O0.57142857
        set_variable      : M1 = 157.757362 (g/mol)

        name              : CH2(SO4)2
        name_reduced_i    : H2C(SO4)2, 1.0
        chem_system       : C-H-O-S
        molar_mass        : 206.1518 (g/mol)
        as_dict           : {'C': 1.0, 'H': 2.0, 'S': 2.0, 'O': 8.0}
        fractional_comp   : C0.07692308 H0.15384615 S0.15384615 O0.61538462
        set_variable      : M2 = 206.15177999999997 (g/mol)

        exec_end          : print(M1 + M2)
        return            : 363.909142

    # Calculation example using molecular weight variables "M<int>"
    #   In the --process, the "#" symbol is assigned 1,2,3,... in the order of molecules read.
    "LiFePO4, H4O2" | python Get-MolecularMass.py --short --process "C# = comp.weight;print(C#)" --end "print(C1 + C2)"

        name              : LiFePO4
        name_reduced_i    : LiFePO4, 1.0
        chem_system       : Fe-Li-O-P
        molar_mass        : 157.7574 (g/mol)
        as_dict           : {'Li': 1.0, 'Fe': 1.0, 'P': 1.0, 'O': 4.0}
        fractional_comp   : Li0.14285714 Fe0.14285714 P0.14285714 O0.57142857
        set_variable      : M1 = 157.757362 (g/mol)

        exec_foreach      : C1 = comp.weight
        return            :

        exec_foreach      : print(C1)
        return            : 157.757362 amu

        name              : H4O2
        name_reduced_i    : H2O, 2.0
        chem_system       : H-O
        molar_mass        : 36.0306 (g/mol)
        as_dict           : {'H': 4.0, 'O': 2.0}
        fractional_comp   : H0.66666667 O0.33333333
        set_variable      : M2 = 36.03056 (g/mol)

        exec_foreach      : C2 = comp.weight
        return            :

        exec_foreach      : print(C2)
        return            : 36.03056 amu

        exec_end          : print(C1 + C2)
        return            : 193.787922 amu

    # replace elements using dictionary
    "Fe2O3" | python Get-MolecularMass.py -s --replace '{"Fe":{"Mn":1.0}}'

        name              : Fe2O3
        name_replaced     : Mn2O3, 1
        name_reduced_i    : Mn2O3, 1.0
        chem_system       : Mn-O
        molar_mass        : 157.8743 (g/mol)
        as_dict           : {'O': 3.0, 'Mn': 2.0}
        fractional_comp   : O0.6 Mn0.4
        set_variable      : M1 = 157.87429 (g/mol)

    "Fe2O3" | python Get-MolecularMass.py -s --replace '{"Fe":{"Mn":0.5,"Cu":0.5}}'
    
        name              : Fe2O3
        name_replaced     : MnCuO3, 1
        name_reduced_i    : MnCuO3, 1.0
        chem_system       : Cu-Mn-O
        molar_mass        : 166.4822 (g/mol)
        as_dict           : {'O': 3.0, 'Mn': 1.0, 'Cu': 1.0}
        fractional_comp   : O0.6 Mn0.2 Cu0.2
        set_variable      : M1 = 166.482245 (g/mol)

    # Calculation using M<int> and N<int> and --skip <int>
    "BaTiO3, BaCO3, TiO2" | python Get-MolecularMass.py --process 'print("{} : {:.3f} g".format(N#, 1/M1*M#*1.5))' -s -skip 1
    
        name              : BaTiO3
        name_reduced_i    : BaTiO3, 1.0
        chem_system       : Ba-O-Ti
        molar_mass        : 233.1922 (g/mol)
        as_dict           : {'Ba': 1.0, 'Ti': 1.0, 'O': 3.0}
        fractional_comp   : Ba0.2 Ti0.2 O0.6
        set_variable      : M1 = 233.19219999999999 (g/mol)
        
        name              : BaCO3
        name_reduced_i    : BaCO3, 1.0
        chem_system       : Ba-C-O
        molar_mass        : 197.3359 (g/mol)
        as_dict           : {'Ba': 1.0, 'C': 1.0, 'O': 3.0}
        fractional_comp   : Ba0.2 C0.2 O0.6
        set_variable      : M2 = 197.33589999999998 (g/mol)
        
        exec_foreach      : print("{} : {:.3f} g".format(N2, 1/M1*M2*1.5))
        return            : BaCO3 : 1.269 g
        
        name              : TiO2
        name_reduced_i    : TiO2, 1.0
        chem_system       : O-Ti
        molar_mass        : 79.8658 (g/mol)
        as_dict           : {'Ti': 1.0, 'O': 2.0}
        fractional_comp   : Ti0.33333333 O0.66666667
        set_variable      : M3 = 79.8658 (g/mol)
        
        exec_foreach      : print("{} : {:.3f} g".format(N3, 1/M1*M3*1.5))
        return            : TiO2 : 0.514 g
    """

    parser = argparse.ArgumentParser(description=help_desc_msg,
                    epilog=help_epi_msg,
                    formatter_class=argparse.RawDescriptionHelpFormatter)
    #parser = argparse.ArgumentParser(description='calc matrix using numpy')
    #parser.print_help()
    ts = lambda x:list(map(str  , x.split(',')))
    parser.add_argument("-f", "--formula", help="molecular formula", type=ts)
    parser.add_argument("-p", "--process", help="run expression for each material", type=str)
    parser.add_argument("-e", "--end", help="run expression after output all materials", type=str)
    parser.add_argument("-b", "--begin", help="run expression before read materials", type=str)
    parser.add_argument("-skip", "--skip", help="skip applying expression to first record", default=0, type=int)
    parser.add_argument("-r", "--remove_charges", help="remove charges from composition", action="store_true")
    parser.add_argument("--replace", help="replace element using dictionary", type=str)
    parser.add_argument("-s", "--short", help="short output", action="store_true")
    parser.add_argument("-pad", "--padding", help="display name padding", default=17, type=int)
    parser.add_argument("-o", "--only", help="output only expression", action="store_true")
    parser.add_argument("-V", "--version", help="version", action="version", version=_version)
    args = parser.parse_args()
    return(args)

def open_file(mode = 'r'):
    out_lines = []
    readfile = sys.stdin
    for line in readfile:
        line = line.rstrip('\r\n')
        for l in line.split(","):
            out_lines.append(str(l).strip())
    return out_lines

def strip_formulas(formulas):
    out_lines = []
    for f in formulas:
        out_lines.append(str(f).strip())
    return out_lines

if __name__ == '__main__':
    # get args
    args = get_args()

    # read formula
    formulas = []
    if args.formula:
        formulas = strip_formulas(args.formula)
    else:
        formulas = open_file()

    # run end expression
    if args.begin:
        exp_count = 0
        message = "exec_begin"
        messager = "return"
        exp = args.begin
        fmls = str(exp).split(";")
        for fml in fmls:
            exp_count += 1
            if exp_count > 1:
                print("")
            fml = str(fml).strip()
            # if fml contains "=", run exec, otherwise run eval
            print("{} : {}".format(message.ljust(args.padding), fml))
            print("{} : ".format(messager.ljust(args.padding)), end="")
            if re.search(r'^([^\(]+)=', fml):
                exec(fml)
                print("")
            else:
                ans = eval(fml)
        print("")

    exp_count  = 0
    line_count = 0
    elem_count = 0
    for line in formulas:
        # item counter
        line_count += 1
        # get formula
        line = line.rstrip('\r\n')
        #print(line)
        # set composition
        comp_name = line
        comp = Composition(comp_name)
        if args.remove_charges:
            comp = comp.remove_charges()
        if args.replace:
            rep_dict = json.loads(args.replace)
            comp = comp.replace(rep_dict)
        comp_name_reduced, factor = comp.get_reduced_formula_and_factor()
        comp_name_reduced2, factor2 = comp.get_integer_formula_and_factor()
        # set mol mass for each item
        molmass_mark = "M" + str(line_count)
        molname_mark = "N" + str(line_count)
        mol_mass_formula = molmass_mark + " = " + str(float(comp.weight))
        mol_mass_name    = molname_mark + " = " + '"' + str(comp_name) + '"'
        exec(mol_mass_formula)
        exec(mol_mass_name)
        # output
        if args.only:
            pass
        elif args.short:
            k = r"name"
            print("{} : {}".format(k.ljust(args.padding), comp_name))
            if args.replace:
                k = r"name_replaced"
                print("{} : {}, {}".format(k.ljust(args.padding), comp_name_reduced, str(factor)))
            k = r"name_reduced_i"
            print("{} : {}, {}".format(k.ljust(args.padding), comp_name_reduced2, str(factor2)))
            k = r"chem_system"
            print("{} : {}".format(k.ljust(args.padding), comp.chemical_system))
            k = r"molar_mass"
            print("{} : {:.4f} (g/mol)".format(k.ljust(args.padding), comp.weight))
            k = r"as_dict"
            print("{} : {}".format(k.ljust(args.padding), comp.as_dict()))
            k = r"fractional_comp"
            print("{} : {}".format(k.ljust(args.padding), comp.fractional_composition))
            k = r"set_variable"
            print("{} : {} (g/mol)".format(k.ljust(args.padding), mol_mass_formula))
        else:
            k = r"name"
            print("{} : {}".format(k.ljust(args.padding), comp_name))
            if args.replace:
                k = r"name_replaced"
                print("{} : {}, {}".format(k.ljust(args.padding), comp_name_reduced, str(factor)))
            k = r"name_reduced"
            print("{} : {}, {}".format(k.ljust(args.padding), comp_name_reduced, str(factor)))
            k = r"name_reduced_i"
            print("{} : {}, {}".format(k.ljust(args.padding), comp_name_reduced2, str(factor2)))
            k = r"formula"
            print("{} : {}".format(k.ljust(args.padding), comp.formula))
            k = r"formula_iupac"
            print("{} : {}".format(k.ljust(args.padding), comp.iupac_formula))
            k = r"chem_system"
            print("{} : {}".format(k.ljust(args.padding), comp.chemical_system))
            k = r"atoms_num"
            print("{} : {}".format(k.ljust(args.padding), comp.num_atoms))
            k = r"molar_mass"
            print("{} : {:.4f} (g/mol)".format(k.ljust(args.padding), comp.weight))
            k = r"mol_per_gram"
            print("{} : {:.8f} (mol/g)".format(k.ljust(args.padding), 1 / comp.weight))
            k = r"fractional_comp"
            print("{} : {}".format(k.ljust(args.padding), comp.fractional_composition))
            k = r"oxi_state_guesses"
            print("{} : {}".format(k.ljust(args.padding), comp.oxi_state_guesses()))
            k = r"as_dict"
            print("{} : {}".format(k.ljust(args.padding), comp.as_dict()))
            k = r"is_element"
            print("{} : {}".format(k.ljust(args.padding), comp.is_element))
            k = r"total_electrons"
            print("{} : {}".format(k.ljust(args.padding), comp.total_electrons))
            #print("{} : {}".format("el_amt_dict".ljust(args.padding), comp.get_el_amt_dict()))
            #print("{} : {}".format("elements".ljust(args.padding), comp.elements))
            #print("{} : {}".format("alphabetical_formula".ljust(args.padding), comp.alphabetical_formula))
            comp_name_reduced = comp_name
            k = r"reference"
            print("{} : https://pymatgen.org/pymatgen.core.html".format(k.ljust(args.padding)))
            k = r"search_bing"
            encoded_uri = r"https://www.bing.com/search?q=" + urllib.parse.quote(comp_name_reduced)
            print("{} : {}".format(k.ljust(args.padding), encoded_uri))
            k = r"search_google"
            encoded_uri = r"https://www.google.com/search?q=" + urllib.parse.quote(comp_name_reduced)
            print("{} : {}".format(k.ljust(args.padding), encoded_uri))
            k = r"search_wiki"
            encoded_uri = r"https://en.wikipedia.org/wiki/" + urllib.parse.quote(comp_name_reduced)
            print("{} : {}".format(k.ljust(args.padding), encoded_uri))
            k = r"set_variable"
            print("{} : {} (g/mol)".format(k.ljust(args.padding), mol_mass_formula))
        # run process expression
        if args.process and line_count > args.skip:
            message = "exec_foreach"
            messager = "return"
            exp = args.process
            exp = exp.replace('#', str(line_count))
            fmls = str(exp).split(";")
            for fml in fmls:
                exp_count += 1
                if exp_count > 0:
                    print("")
                fml = str(fml).strip()
                # if fml contains "=", run exec, otherwise run eval
                print("{} : {}".format(message.ljust(args.padding), fml))
                print("{} : ".format(messager.ljust(args.padding)), end="")
                if re.search(r'^([^\(]+)=', fml):
                    exec(fml)
                    print("")
                else:
                    ans = eval(fml)
        print("")

    # run end expression
    exp_count = 0
    if args.end:
        message = "exec_end"
        messager = "return"
        exp = args.end
        fmls = str(exp).split(";")
        for fml in fmls:
            exp_count += 1
            if exp_count > 1:
                print("")
            fml = str(fml).strip()
            # if fml contains "=", run exec, otherwise run eval
            print("{} : {}".format(message.ljust(args.padding), fml))
            print("{} : ".format(messager.ljust(args.padding)), end="")
            if re.search(r'^([^\(]+)=', fml):
                exec(fml)
                print("")
            else:
                ans = eval(fml)

    sys.exit(0)
