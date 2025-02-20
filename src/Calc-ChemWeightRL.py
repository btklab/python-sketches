#!/usr/bin/env python3
#coding: utf-8

#
# Calc-ChemWeightRL
#

import io, sys, os
import re
import argparse
import json
from pymatgen.core import Composition

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
    help_desc_msg ="""Calc-ChemWeightRL - Chemical weighing calculator using pymatgen

    Synopsis:
        Calculate the weight(gram) of each term in the chemical formula
        from the first term on the Right side to the Left side (R -> L)

    Usage:
        'comp1 + comp2 -> product' | python Calc-ChemWeightRL.py
        python Calc-ChemWeightRL.py -f 'comp1 + comp2 -> product'

    Example:
        # Calculate Grams of Methane(CH4) and Oxygen(O2)
        # required to obtain 44g of carbon dioxide(CO2)
        "CH4 + 2 O2 -> CO2 + 2 H2O" | python Calc-ChemWeightRL.py -g 44.0

        Formula  :      CH4       +      2O2       ->      CO2       +      2H2O
        Molratio :       1        :       2        :        1        :       2
        Molmass  :     16.04      +   2 * 32.00    ->     44.01      +   2 * 18.02
        Weight   :    16.039 g    +    63.984 g    ->    44.000 g    +    36.023 g
    
    Notes:
        - Calculate by default to get 1g of the first term on the Right compound
        - Spaces in expressions are ignored
        - The number at the beginning of each compound is considered the number of moles

    Dependency:
        pymatgen
        https://pymatgen.org/

        GitHub - materialsproject/pymatgen
        https://github.com/materialsproject/pymatgen
        https://pymatgen.org/pymatgen.core.html
    
    Install pymatgen module:
        python -m pip install pymatgen
        https://github.com/materialsproject/pymatgen#installation
    
    Links:
        Calc-ChemMassPercent.py, Calc-ChemWeightLR.py,
        Get-PeriodicTable.py, Get-MolecularMass.py,
        Calc-ChemMassPercent.py

    """
    help_epi_msg = """EXAMPLES:

    # Calculate Grams of Methane(CH4) and Oxygen(O2) required to obtain 44g of carbon dioxide(CO2)
    "CH4 + 2 O2 -> CO2 + 2 H2O" | python Calc-ChemWeightRL.py -g 44.0

        Formula  :      CH4       +      2O2       ->      CO2       +      2H2O
        Molratio :       1        :       2        :        1        :       2
        Molmass  :     16.04      +   2 * 32.00    ->     44.01      +   2 * 18.02
        Weight   :    16.039 g    +    63.984 g    ->    44.000 g    +    36.023 g

    # verbose output (-v option)
    "CH4 + 2 O2 -> CO2 + 2 H2O" | python Calc-ChemWeightRL.py -g 44.0 -v
    
        Type     : Product
        Name     : CO2 * 1.0
        Weight   : 44.00000000 (g)
        Ratio    : 0.99978414 (ratio)
        Mol_mass : CO2 = 44.0095 (g/mol)
        Formula  : 1 / gram_per_mol / mol * target_gram = 1 / 44.010 / 1.0 * 44.000

        Type     : Product
        Name     : H2O * 2.0
        Weight   : 36.02278235 (g)
        Ratio    : 0.99978414 (ratio)
        Mol_mass : H2O = 18.01528 (g/mol)
        Formula  : gram_per_mol * mol * mol_ratio = 18.015 * 2.0 * 1.000

        Type     : Material
        Name     : CH4 * 1.0
        Weight   : 16.03899703 (g)
        Ratio    : 0.99978414 (ratio)
        Mol_mass : CH4 = 16.04246 (g/mol)
        Formula  : gram_per_mol * mol * mol_ratio = 16.042 * 1.0 * 1.000

        Type     : Material
        Name     : O2 * 2.0
        Weight   : 63.98378532 (g)
        Ratio    : 0.99978414 (ratio)
        Mol_mass : O2 = 31.9988 (g/mol)
        Formula  : gram_per_mol * mol * mol_ratio = 31.999 * 2.0 * 1.000
    """

    parser = argparse.ArgumentParser(description=help_desc_msg,
                    epilog=help_epi_msg,
                    formatter_class=argparse.RawDescriptionHelpFormatter)
    #parser = argparse.ArgumentParser(description='calc matrix using numpy')
    #parser.print_help()
    ts = lambda x:list(map(str, x.split(',')))
    tf = lambda x:list(map(float, x.split(',')))
    parser.add_argument("-f", "--formula", help="molecular formula", type=ts)
    parser.add_argument("-g", "--gram", help="product weight", default=1.0, type=float)
    parser.add_argument("-p", "--padding", help="debug padding", default=20, type=int)
    parser.add_argument("-wf", "--wformat", help="weight format", default='.3f', type=str)
    parser.add_argument("-wp", "--wpadding", help="weight padding", default=14, type=int)
    parser.add_argument("-d", "--debug", help="debug", action="store_true")
    parser.add_argument("-kg", "--kg", help="kilogram", action="store_true")
    parser.add_argument("-mg", "--mg", help="milligram", action="store_true")
    parser.add_argument("-v", "--verbose", help="verbose output", action="store_true")
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

def separate_molar_and_name(target):
    res = []
    target = target.strip()
    if re.search(r'^([0-9.]+)([^0-9]..*)$', target):
        mul = str(re.sub(r'^([0-9.]+)([^0-9]..*)$', r'\1', target))
        nam = str(re.sub(r'^([0-9.]+)([^0-9]..*)$', r'\2', target))
    else:
        mul = str("1")
        nam = str(target)
    res = [mul, nam]
    return res

if __name__ == '__main__':
    # get args
    args = get_args()

    # read formula
    formulas = []
    if args.formula:
        formulas = strip_formulas(args.formula)
    else:
        formulas = open_file()

    # set variable
    line_count     = 0
    product_list   = []
    product_hash   = {}
    material_list  = []
    material_hash  = {}
    product_weight_list    = []
    product_molmass_list   = []
    product_molratio_list  = []
    material_weight_list   = []
    material_molmass_list  = []
    material_molratio_list = []
    weight_format = r'{:' + args.wformat + r"}"
    compiled_regex = re.compile(r'^(..*)(\->|=)(..*)$')
    for fml in formulas:
        # item counter
        line_count += 1
        # get formula
        fml = fml.rstrip('\r\n').replace(' ', '')
        # test formula
        if compiled_regex.search(fml):
            pass
        else:
            raise_error("syntax error: {}".format(fml))
        # get material
        fml_material = compiled_regex.sub(r'\1', fml)
        fml_material = fml_material.strip()
        if fml_material == "":
            raise_error("material is not detected: {}".format(fml))
        # get product
        fml_product = compiled_regex.sub(r'\3', fml)
        fml_product = fml_product.strip()
        if fml_product == "":
            raise_error("product is not detected: {}".format(fml))
        fml_materials = fml_material.split('+')
        fml_products  = fml_product.split('+')
        # separate each product into molar and name
        for pname in fml_products:
            mul, nam = separate_molar_and_name(str(pname))
            product_hash[nam] = mul
            product_list.append(nam)
        # separate each material into molar and name
        for mname in fml_materials:
            mul, nam = separate_molar_and_name(str(mname))
            material_hash[nam] = mul
            material_list.append(nam)
        # debug
        if args.debug:
            #print("{} : {}".format("debug: product_list".ljust(args.padding), product_list))
            print("{} : {}".format("debug: product_hash".ljust(args.padding), product_hash))
            #print("{} : {}".format("debug: material_list".ljust(args.padding), material_list))
            print("{} : {}".format("debug: material_hash".ljust(args.padding), material_hash))
        # calculate target compound weight per mol
        pad2 = 8
        product_count = 1
        for pname in product_list:
            comp_name = pname
            comp = Composition(comp_name)
            if product_count == 1:
                target_gram = float(args.gram)
            gram_per_mol = float(comp.weight)
            mol = float(product_hash[pname])
            product_molratio_list.append(product_hash[pname])
            if mol == 1.0:
                product_molmass_list.append("{:.2f}".format(gram_per_mol))
            else:
                product_molmass_list.append("{} * {:.2f}".format(product_hash[pname], gram_per_mol))
            if product_count == 1:
                mol_ratio = 1 / gram_per_mol / mol * target_gram
            if product_count > 1:
                target_gram = gram_per_mol * mol * mol_ratio
            if args.kg:
                product_weight_list.append(str(weight_format.format(target_gram / 1000)))
            elif args.mg:
                product_weight_list.append(str(weight_format.format(target_gram * 1000)))
            else:
                product_weight_list.append(str(weight_format.format(target_gram * 1)))
            if args.verbose:
                # verbose output
                if product_count > 1 or args.debug:
                    print("")
                print("{} : {}".format("Type".ljust(pad2), "Product"))
                print("{} : {} * {}".format("Name".ljust(pad2), pname, mol))
                print("{} : {:.8f} (g)".format("Weight".ljust(pad2), target_gram))
                print("{} : {:.8f} (ratio)".format("Ratio".ljust(pad2), mol_ratio))
                print("{} : {} = {} (g/mol)".format("Mol_mass".ljust(pad2), pname, gram_per_mol))
                if product_count == 1:
                    print("{} : {} = 1 / {:.3f} / {} * {:.3f}".format("Formula".ljust(pad2), "1 / gram_per_mol / mol * target_gram", gram_per_mol, mol, target_gram))
                else:
                    print("{} : {} = {:.3f} * {} * {:.3f}".format("Formula".ljust(pad2), "gram_per_mol * mol * mol_ratio", gram_per_mol, mol, mol_ratio))
            product_count += 1
        
        material_count = 0
        for mname in material_list:
            comp_name = mname
            comp = Composition(comp_name)
            gram_per_mol = float(comp.weight)
            mol = float(material_hash[mname])
            material_molratio_list.append(material_hash[mname])
            if mol == 1.0:
                material_molmass_list.append("{:.2f}".format(gram_per_mol))
            else:
                material_molmass_list.append("{} * {:.2f}".format(material_hash[mname], gram_per_mol))
            material_gram = gram_per_mol * mol * mol_ratio
            if args.kg:
                material_weight_list.append(str(weight_format.format(material_gram / 1000)))
            elif args.mg:
                material_weight_list.append(str(weight_format.format(material_gram * 1000)))
            else:
                material_weight_list.append(str(weight_format.format(material_gram * 1)))
            if args.verbose:
                # verbose output
                print("")
                print("{} : {}".format("Type".ljust(pad2), "Material"))
                print("{} : {} * {}".format("Name".ljust(pad2), mname, mol))
                print("{} : {:.8f} (g)".format("Weight".ljust(pad2), material_gram))
                print("{} : {:.8f} (ratio)".format("Ratio".ljust(pad2), mol_ratio))
                print("{} : {} = {} (g/mol)".format("Mol_mass".ljust(pad2), mname, gram_per_mol))
                print("{} : {} = {:.3f} * {} * {:.3f}".format("Formula".ljust(pad2), "gram_per_mol * mol * mol_ratio", gram_per_mol, mol, mol_ratio))
            material_count += 1
        
        if not args.verbose:
            # output formula of material
            vjust_width = 8
            print("{} : ".format("Formula".ljust(vjust_width)), end="")
            array_length = len(fml_materials)
            for i in range(array_length):
                print("{}".format(str(fml_materials[i]).center(args.wpadding)), end="")
                if i == array_length - 1:
                    print("{}".format(r' -> '), end="")
                else:
                    print("{}".format(r' + '), end="")

            # output formula of product
            array_length = len(fml_products)
            for i in range(array_length):
                print("{}".format(str(fml_products[i]).center(args.wpadding)), end="")
                if i == array_length - 1:
                    print("")
                else:
                    print("{}".format(r' + '), end="")

            # output molar ratio of material
            print("{} : ".format("Molratio".ljust(vjust_width)), end="")
            array_length = len(material_molratio_list)
            for i in range(array_length):
                out_molratio = r'{}'.format(str(material_molratio_list[i]))
                print("{}".format(str(out_molratio).center(args.wpadding)), end="")
                if i == array_length - 1:
                    print("{}".format(r' :  '), end="")
                else:
                    print("{}".format(r' : '), end="")

            # output molar ratio of product
            array_length = len(product_molratio_list)
            for i in range(array_length):
                out_molratio = r'{}'.format(str(product_molratio_list[i]))
                print("{}".format(str(out_molratio).center(args.wpadding)), end="")
                if i == array_length - 1:
                    print("")
                else:
                    print("{}".format(r' : '), end="")

            # output molar mass of material
            print("{} : ".format("Molmass".ljust(vjust_width)), end="")
            array_length = len(material_molmass_list)
            for i in range(array_length):
                out_molmass = r'{}'.format(str(material_molmass_list[i]))
                print("{}".format(str(out_molmass).center(args.wpadding)), end="")
                if i == array_length - 1:
                    print("{}".format(r' -> '), end="")
                else:
                    print("{}".format(r' + '), end="")

            # output molar nass of product
            array_length = len(product_molmass_list)
            for i in range(array_length):
                out_molmass = r'{}'.format(str(product_molmass_list[i]))
                print("{}".format(str(out_molmass).center(args.wpadding)), end="")
                if i == array_length - 1:
                    print("")
                else:
                    print("{}".format(r' + '), end="")
            
            # output weight of material
            print("{} : ".format("Weight".ljust(vjust_width)), end="")
            array_length = len(material_weight_list)
            for i in range(array_length):
                if args.kg:
                    out_waight = r'{} kg'.format(str(material_weight_list[i]))
                elif args.mg:
                    out_waight = r'{} mg'.format(str(material_weight_list[i]))
                else:
                    out_waight = r'{} g'.format(str(material_weight_list[i]))
                print("{}".format(str(out_waight).center(args.wpadding)), end="")
                if i == array_length - 1:
                    print("{}".format(r' -> '), end="")
                else:
                    print("{}".format(r' + '), end="")

            # output weight of product
            array_length = len(product_weight_list)
            for i in range(array_length):
                if args.kg:
                    out_waight = r'{} kg'.format(str(product_weight_list[i]))
                elif args.mg:
                    out_waight = r'{} mg'.format(str(product_weight_list[i]))
                else:
                    out_waight = r'{} g'.format(str(product_weight_list[i]))
                print("{}".format(str(out_waight).center(args.wpadding)), end="")
                if i == array_length - 1:
                    print("")
                else:
                    print("{}".format(r' + '), end="")
    
    sys.exit(0)
