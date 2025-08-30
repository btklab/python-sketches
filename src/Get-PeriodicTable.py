#!/usr/bin/env python3
#coding: utf-8

#
# Get-PeriodicTable
#

import io, sys, os
import re
import argparse
from pymatgen.core import Element
import json
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
    help_desc_msg = r"""Get-PeriodicTable - Get Element data using pymatgen

    Dependency:
        pymatgen
        https://pymatgen.org/

        GitHub - materialsproject/pymatgen
        https://github.com/materialsproject/pymatgen
        https://pymatgen.org/pymatgen.core.html#module-pymatgen.core
    
    Install:
        python -m pip install pymatgen

        https://github.com/materialsproject/pymatgen#installation

    Usage:
        python Get-PeriodicTable.py -f "<Element>, <Element>, ..."
        "<Element>, <Element>, ..." | python Get-PeriodicTable.py
    
    Links:
        Calc-ChemMassPercent.py, Calc-ChemWeightLR.py,
        Get-PeriodicTable.py, Get-MolecularMass.py,
        Calc-ChemMassPercent.py
    """
    help_epi_msg = r"""EXAMPLES:

    # get specified items (Case sensitive)
    python Get-PeriodicTable.py -f 'Cu,Ag,H' -i "Name, Atomic mass, Boiling point"

        Name              : Copper
        Atomic mass       : 63.546
        Boiling point     : 3200 K

        Name              : Silver
        Atomic mass       : 107.8682
        Boiling point     : 2435 K

        Name              : Hydrogen
        Atomic mass       : 1.00794
        Boiling point     : 20.28 K

    # get short data
    "Fe" | python Get-PeriodicTable.py

        Atomic no         : 26
        Name              : Iron
        Atomic mass       : 55.845
        Atomic radius     : 1.4
        Boiling point     : 3134 K
        Critical temperature : no data K
        Density of solid  : 7874 kg m<sup>-3</sup>
        ICSD oxidation states : [2, 3]
        Ionization energies : [7.9024681, 16.19921, 30.651, 54.91, 75.0, 98.985, 124.976, 151.06, 233.6, 262.1, 290.9, 330.8, 361.0, 392.2, 456.2, 489.312, 1262.7, 1357.8, 1460.0, 1575.6, 1687.0, 1798.4, 1950.4, 2045.759, 8828.1879, 9277.6818]
        IUPAC ordering    : 64
        Liquid range      : 1323 K
        Melting point     : 1811 K
        Molar volume      : 7.09 cm<sup>3</sup>
        Oxidation states  : [-2, -1, 1, 2, 3, 4, 5, 6]
        Superconduction temperature : no data K
        Thermal conductivity : 80 W m<sup>-1</sup> K<sup>-1</sup>
        Van der waals radius : 2.04
        Youngs modulus    : 211 GPa

    # get pretty data
    "Fe" | python Get-PeriodicTable.py --pretty

        Atomic no         : 26
        Name              : Iron
        Atomic mass       : 55.845
        Atomic radius     : 1.4
        Boiling point     : 3134 K
        Critical temperature : no data K
        Density of solid  : 7874 kg m<sup>-3</sup>
        ICSD oxidation states : [2, 3]
        Ionization energies : [7.9024681, 16.19921, 30.651, 54.91, 75.0, 98.985, 124.976, 151.06, 233.6, 262.1, 290.9, 330.8, 361.0, 392.2, 456.2, 489.312, 1262.7, 1357.8, 1460.0, 1575.6, 1687.0, 1798.4, 1950.4, 2045.759, 8828.1879, 9277.6818]
        IUPAC ordering    : 64
        is_actinoid       : False
        is_alkali_metal   : False
        is_alkali_earth_metal : False
        is_chalcogen      : False
        is_halogen        : False
        is_lanthanoid     : False
        is_metal          : True
        is_metalloid      : False
        is_noble_gas      : False
        is_post_transition_metal : False
        is_quadrupolar    : False
        is_rare_earth_metal : False
        is_transition_metal : True
        Liquid range      : 1323 K
        Melting point     : 1811 K
        Molar volume      : 7.09 cm<sup>3</sup>
        Oxidation states  : [-2, -1, 1, 2, 3, 4, 5, 6]
        Superconduction temperature : no data K
        Thermal conductivity : 80 W m<sup>-1</sup> K<sup>-1</sup>
        Van der waals radius : 2.04
        Youngs modulus    : 211 GPa
        reference         : https://pymatgen.org/pymatgen.core.html
        search_bing       : https://www.bing.com/search?q=Iron
        search_google     : https://www.google.com/search?q=Iron
        search_wiki       : https://en.wikipedia.org/wiki/Iron

    # output all data
    "Fe" | python Get-PeriodicTable.py --all

    # Output as Json and convert to hashtable using PowerShell 7
    "Fe" | python Get-PeriodicTable.py --raw | ConvertFrom-Json -AsHashtable
    
    # Output dictionary using -m or --molmass switch
    "Fe,O" | python Get-PeriodicTable.py --molmass
    {'Fe': 55.845, 'O': 15.9994}

    # using --molmass with --item and --json and --raw
    "Fe,O" | python Get-PeriodicTable.py --molmass --item 'Oxidation states, Atomic mass' --json --raw
    {"Fe": {"Oxidation states": [-2, -1, 1, 2, 3, 4, 5, 6], "Atomic mass": 55.845}, "O": {"Oxidation states": [-2, -1, 1, 2], "Atomic mass": 15.9994}}

    # using --molmass with --item and --json
    "Fe,O" | python Get-PeriodicTable.py --molmass --item 'Oxidation states, Atomic mass' --json
    {
        "Fe": {
            "Oxidation states": [
                -2,
                -1,
                1,
                2,
                3,
                4,
                5,
                6
            ],
            "Atomic mass": 55.845
        },
        "O": {
            "Oxidation states": [
                -2,
                -1,
                1,
                2
            ],
            "Atomic mass": 15.9994
        }
    }
    """

    parser = argparse.ArgumentParser(description=help_desc_msg,
                    epilog=help_epi_msg,
                    formatter_class=argparse.RawDescriptionHelpFormatter)
    #parser = argparse.ArgumentParser(description='calc matrix using numpy')
    #parser.print_help()
    ts = lambda x:list(map(str  , x.split(',')))
    parser.add_argument("-f", "--formula", help="molecular formula", type=ts)
    parser.add_argument("--raw", help="output json as-is", action="store_true")
    parser.add_argument("--json", help="output json", action="store_true")
    parser.add_argument("-s", "--short", help="output short data", action="store_true")
    parser.add_argument("-p", "--pretty", help="output pretty data", action="store_true")
    parser.add_argument("-a", "--all", help="output all data", action="store_true")
    parser.add_argument("-m", "--molmass", help="output only molar mass", action="store_true")
    parser.add_argument("-i", "--item", help="select item", type=ts)
    parser.add_argument("-pad", "--padding", help="display name padding", default=17, type=int)
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

    ## read file
    formulas = []
    if args.molmass:
        elm_dict = {}
    if args.formula:
        formulas = strip_formulas(args.formula)
    else:
        formulas = open_file()

    line_counter = 0
    elem_counter = 0
    for line in formulas:
        line_counter += 1
        ## print line
        line = line.rstrip('\r\n')
        #print(line)
        elem_name = line
        elem_json = Element(elem_name).data
        #print(type(elem_json))
        if args.molmass:
            if args.item:
                item_dict = {}
                for i in args.item:
                    key = str(i).strip()
                    if str(key) in elem_json.keys():
                        item_dict[key] = elem_json[key]
                    else:
                        raise_error("{} could not found in dict-keys.".format(i))
                elm_dict[elem_name] = item_dict
            else:
                key = r"Atomic mass"
                elm_dict[elem_name] = elem_json[key]
        elif args.json or args.raw:
            if args.raw:
                print(elem_json)
            else:
                print(json.dumps(elem_json, indent=4))
        elif args.item:
            elem_counter += 1
            if elem_counter > 1:
                print("")
            for i in args.item:
                key = str(i).strip()
                if str(key) in elem_json.keys():
                    print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
                else:
                    raise_error("{} could not found in dict-keys.".format(i))
        else:
            elem_counter += 1
            if elem_counter > 1:
                print("")
            key = r"Atomic no"
            if str(key) in elem_json.keys() and True:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))

            key = r"Input"
            if args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_name))

            key = r"Name"
            if str(key) in elem_json.keys() and True:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))

            key = r"Atomic mass"
            if str(key) in elem_json.keys() and True:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Atomic orbitals"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Atomic radius"
            if str(key) in elem_json.keys() and True:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Atomic radius calculated"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Boiling point"
            if str(key) in elem_json.keys() and True:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))

            key = r"Brinell hardness"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Bulk modulus"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Coefficient of linear thermal expansion"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Common oxidation states"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Critical temperature"
            if str(key) in elem_json.keys() and True:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Density of solid"
            if str(key) in elem_json.keys() and True:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Electrical resistivity"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Electron affinity"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Electronic structure"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Ground level"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"ICSD oxidation states"
            if str(key) in elem_json.keys() and True:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Ionic radii"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Ionic radii hs"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Ionic radii ls"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Ionization energies"
            if str(key) in elem_json.keys() and True:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"IUPAC ordering"
            if str(key) in elem_json.keys() and True:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"is_actinoid"
            if args.all or args.pretty:
                print("{} : {}".format(key.ljust(args.padding), Element(elem_name).is_actinoid))
            
            key = r"is_alkali_metal"
            if args.all or args.pretty:
                print("{} : {}".format(key.ljust(args.padding), Element(elem_name).is_alkali))
            
            key = r"is_alkali_earth_metal"
            if args.all or args.pretty:
                print("{} : {}".format(key.ljust(args.padding), Element(elem_name).is_alkaline))
            
            key = r"is_chalcogen"
            if args.all or args.pretty:
                print("{} : {}".format(key.ljust(args.padding), Element(elem_name).is_chalcogen))
            
            key = r"is_halogen"
            if args.all or args.pretty:
                print("{} : {}".format(key.ljust(args.padding), Element(elem_name).is_halogen))
            
            key = r"is_lanthanoid"
            if args.all or args.pretty:
                print("{} : {}".format(key.ljust(args.padding), Element(elem_name).is_lanthanoid))
            
            key = r"is_metal"
            if args.all or args.pretty:
                print("{} : {}".format(key.ljust(args.padding), Element(elem_name).is_metal))
            
            key = r"is_metalloid"
            if args.all or args.pretty:
                print("{} : {}".format(key.ljust(args.padding), Element(elem_name).is_metalloid))
            
            key = r"is_noble_gas"
            if args.all or args.pretty:
                print("{} : {}".format(key.ljust(args.padding), Element(elem_name).is_noble_gas))
            
            key = r"is_post_transition_metal"
            if args.all or args.pretty:
                print("{} : {}".format(key.ljust(args.padding), Element(elem_name).is_post_transition_metal))
            
            key = r"is_quadrupolar"
            if args.all or args.pretty:
                print("{} : {}".format(key.ljust(args.padding), Element(elem_name).is_post_transition_metal))
            
            key = r"is_rare_earth_metal"
            if args.all or args.pretty:
                print("{} : {}".format(key.ljust(args.padding), Element(elem_name).is_rare_earth_metal))
            
            key = r"is_transition_metal"
            if args.all or args.pretty:
                print("{} : {}".format(key.ljust(args.padding), Element(elem_name).is_transition_metal))
            
            key = r"Liquid range"
            if str(key) in elem_json.keys() and True:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Melting point"
            if str(key) in elem_json.keys() and True:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Mendeleev no"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Metallic radius"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Mineral hardness"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Molar volume"
            if str(key) in elem_json.keys() and True:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"NMR Quadrupole Moment"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Oxidation states"
            if str(key) in elem_json.keys() and True:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Poissons ratio"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Reflectivity"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Refractive index"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Rigidity modulus"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Shannon radii"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Superconduction temperature"
            if str(key) in elem_json.keys() and True:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Thermal conductivity"
            if str(key) in elem_json.keys() and True:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Van der waals radius"
            if str(key) in elem_json.keys() and True:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Velocity of sound"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Vickers hardness"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"X"
            if str(key) in elem_json.keys() and args.all:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))
            
            key = r"Youngs modulus"
            if str(key) in elem_json.keys() and True:
                print("{} : {}".format(key.ljust(args.padding), elem_json[key]))

            key = r"reference"
            if args.all or args.pretty:
                print("{} : https://pymatgen.org/pymatgen.core.html"  .format("reference".ljust(args.padding)))

            key = r"search_bing"
            if args.all or args.pretty:
                encoded_uri = r"https://www.bing.com/search?q=" + urllib.parse.quote(elem_json["Name"])
                print("{} : {}".format(key.ljust(args.padding), encoded_uri))

            key = r"search_google"
            if args.all or args.pretty:
                encoded_uri = r"https://www.google.com/search?q=" + urllib.parse.quote(elem_json["Name"])
                print("{} : {}".format(key.ljust(args.padding), encoded_uri))

            key = r"search_wiki"
            if args.all or args.pretty:
                encoded_uri = r"https://en.wikipedia.org/wiki/" + urllib.parse.quote(elem_json["Name"])
                print("{} : {}".format(key.ljust(args.padding), encoded_uri))

    if args.molmass:
        if args.json:
            # json output
            if args.raw:
                print(json.dumps(elm_dict))
            else:
                print(json.dumps(elm_dict, indent=4))
        else:
            # raw output
            print(elm_dict)

    sys.exit(0)
