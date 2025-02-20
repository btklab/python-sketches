#!/usr/bin/env python3
#coding: utf-8

#
# Calc-ChemMassPercent
#

import io, sys, os
import re
import argparse

_version = "Sat Jan 27 19:48:18 TST 2024"
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
    help_desc_msg ="""Calc-ChemMassPercent - Recalculate the mass percent concentration

    Synopsis:
        Calculate mass percent concentration when mixing multiple solutions.
    
        python Calc-ChemMassPercent.py -f "100 mL : 0.3 NaCl, 0.03 T-N + 100 mL : 3.0% T-N +200 mL" -r 2

            Type          : Solution.1
            Formula       : 100mL:0.3NaCl,0.03T-N
            Volume        : 100 mL
            NaCl          : 30.0 g / 100 mL = 0.30 (30.00 w/v%)
            T-N           : 3.0 g / 100 mL = 0.03 (3.00 w/v%)

            Type          : Solution.2
            Formula       : 100mL:3.0%T-N
            Volume        : 100 mL
            T-N           : 3.0 g / 100 mL = 0.03 (3.00 w/v%)

            Type          : Solution.3
            Formula       : 200mL
            Volume        : 200 mL

            Type          : Product
            Formula       : 100mL:0.3NaCl,0.03T-N + 100mL:3.0%T-N + 200mL
            Total_Volume  : 400.0 mL
            Total_NaCl    : 30.0 g / 400.0 mL = 0.07 (7.50 w/v%)
            Total_T-N     : 6.0 g / 400.0 mL = 0.01 (1.50 w/v%)
            Total_Solid   : 36.0 g / 400.0 mL = 0.09 (9.00 w/v%)
    
    Usage:
        'solution.1 + solution.2 + ...' | python Calc-ChemMassPercent.py
        python Calc-ChemMassPercent.py -f 'solution.1 + solution.2 + ...'

    Expression pattern:
        Basic:
            Weight             -> 100
            Weight : Percent % -> 100 : 3 %
            Weight : Ratio     -> 100 : 0.03

            <Rule>
            - Allows specification of solute only
              (Example at the top of the list)

        With Unit:
            Volume [unit]                 -> 100 mL
            Volume [unit] : w/v Percent % -> 100 mL : 3 %
            Volume [unit] : Ratio         -> 100 mL : 0.03
            
            Weight [unit]                 -> 100 kg
            Weight [unit] : w/w Percent % -> 100 kg : 3 %
            Weight [unit] : Ratio         -> 100 kg : 0.03
            
            <Note>
            - The Solute units must be the same throughout the formula.
              (If a unit difference detected, an error will be returned)
        
        With Solvent name:
            Volume : Percent % Name -> 100 : 3 % NaCl
            Volume : Ratio Name     -> 100 : 0.03 NaCl

        Volume with density:
            density=1.17 g/ml, Volume = 1000 ml, 35w/w% HCl
                -> 1.17 * 1000 g : 35% HCl
        
        Mix Multiple Solutions with different concentrations (use the '+'):
            -> 100:3% + 100:1%
            -> 100mL:3%NaCl + 100mL:1%NaCl

            <Note>
            - Add up solvents with the same name.
            - If the solvents name is omitted, the names
              M1, M2, ... are automatically assigned from the left.
        
        Solutions containing multiple Solvents (use ",")
            -> 100 : 10%, 3%
            -> 100 mL : 10% NaCl, 3% T-N

            <Note>
            - You can add as many Solvents as you want.
        
        Solvent can be specified by solid content.
            -> 100 mL + 0 mL : 15.0 NaCl (add 15g of NaCl)
            -> 100 mL + 0 : 15.0 (add 15g of Something)

            <Note>
            In this case, if the total volume of aqueous solution
            in the formula is zero, a "div/0" error will be returned.

        Molarity mode (-m, --molar) syntax:
            Required: liquid volume unit, molecule name
            Optional: density
            
            1. With volume unit and molecule name:
            -> echo "1000 ml : 35% HCl" | python Calc-ChemMassPercent.py --molar

                Type          : Solution.1
                Formula       : 1000ml:35%HCl
                Volume        : 1000 ml
                HCl           : 350.0 g / 36.461 amu / 1.0 L = 9.599 mol/L (M)

                Type          : Product
                Formula       : 1000ml:35%HCl
                Total_Volume  : 1000.0 ml
                Total_HCl     : 350.0 g / 36.461 amu / 1.0 L = 9.599 mol/L (M)
            
            2. With density (density * volume):
            -> 1.17 g/ml, 1000 ml, 35w/w% HCl
            -> echo "1.17 * 1000 g : 35% HCl" | python Calc-ChemMassPercent.py --molar

                Type          : Solution.1
                Formula       : 1.17*1000g:35%HCl
                Weight        : 1170.0 g (1.000 L)
                HCl           : 409.5 g / 36.461 amu / 1.0 L = 11.231 mol/L (M)

                Type          : Product
                Formula       : 1.17*1000g:35%HCl
                Total_Weight  : 1170.0 g (1.000 L)
                Total_HCl     : 409.5 g / 36.461 amu / 1.0 L = 11.231 mol/L (M)
            
            <Note>
            - If the solvent unit is liquid volume rather than mass, 
              the concentration of the solvent will be w/v% instead of w/w%.
                - 1st examples unit: solution = "ml", solvent = "w/v %"
                - 2nd examples unit: solution = "g",  solvent = "w/w %"
            - By specifying the density, the molarity (mol/L) can be calculated.
            - Density must be written to the left of the liquid volume.
            - When specifying density, the liquid volume unit is mass.
        
        Practice:
            <Q.1>
            Dilute 100mL of 3w/v% NaCl solution
            to double volume with water.

                100 mL : 3% NaCl + 100 mL
                100 mL : 0.03 NaCl + 100 mL
                100 : 3% + 100
                100 : 0.03 + 100

            <Q.2>
            An aqueous solution weighing 100g containing
            10w/w% NaCl and 3w/w%T-N as a solvent.

                100 g : 10% NaCl, 3% T-N
                100 g : 0.1 NaCl, 0.03 T-N
                100 : 10%, 3%
                100 : 0.1, 0.03

                "/","*" can be used for concentration term,
                but do not use "+" because it is used to
                express mixtures of Solutions:

                100 : 10%, 3% = 100 : 10/100, 3/100*1.0

            <Q.3>
            Calculate the molar concentration (mol/L)
            of CH3COOH
            with a density of 1.05 g/mL at 20 degrees
            and a purity of 100 w/w%.

                echo "1.05 * 1000 g : 100% CH3COOH" | python Calc-ChemMassPercent.py --molar

                    Type          : Solution.1
                    Formula       : 1.05*1000g:100%CH3COOH
                    Weight        : 1050.0 g (1.000 L)
                    CH3COOH       : 1050.0 g / 60.052 amu / 1.0 L = 17.485 mol/L (M)

                    Type          : Product
                    Formula       : 1.05*1000g:100%CH3COOH
                    Total_Weight  : 1050.0 g (1.000 L)
                    Total_CH3COOH : 1050.0 g / 60.052 amu / 1.0 L = 17.485 mol/L (M)
                        
            <Q.4>
            Calculate the factor(molar concentration ratio) of HCl/N,
            1000 ml : 4.21 w/v% of N and 12.34 w/v% of HCl

                echo "1000ml: 4.21% N, 12.34% HCl" | python Calc-ChemMassPercent.py --molar --expression 'print("Total_Volume = {} {}".format(Prod.volume, Prod.unit));print( "factor = {:.4f} HCl/N molar concentration ratio".format(HCl.molar / N.molar))' --verbose

                    Type          : Solution.1
                    Formula       : 1000ml:4.21%N,12.34%HCl
                    Volume        : 1000 ml
                    N             : 42.1 g / 14.007 amu / 1.0 L = 3.006 mol/L (M)
                    HCl           : 123.39999999999999 g / 36.461 amu / 1.0 L = 3.384 mol/L (M)

                    Type          : Product
                    Formula       : 1000ml:4.21%N,12.34%HCl
                    Total_Volume  : 1000.0 ml
                    Total_N       : 42.1 g / 14.007 amu / 1.0 L = 3.006 mol/L (M)
                    Total_HCl     : 123.39999999999999 g / 36.461 amu / 1.0 L = 3.384 mol/L (M)

                    Set_Variable  : Prod = Product(name, volume, unit)
                    Set_Variable  : N = Material(name, volume, unit, mol, molar, molar_unit)
                    Set_Variable  : HCl = Material(name, volume, unit, mol, molar, molar_unit)

                    exec_end      : print("Total_Volume = {} {}".format(Prod.volume, Prod.unit))
                    return        : Total_Volume = 1000.0 ml

                    exec_end      : print( "factor = {:.4f} HCl/N molar concentration ratio".format(HCl.molar / N.molar))
                    return        : factor = 1.1260 HCl/N molar concentration ratio

            <Q.5>
            Calculate mass molarity of
            d=1.2 g/ml, 1000 ml, 20 w/w% NaOH

                echo "1.2*1000 g : 20% NaOH" | python Calc-ChemMassPercent.py -mm
                echo "1.2*1000 g : 20% NaOH" | python Calc-ChemMassPercent.py --massmolarity

                    Type          : Solution.1
                    Formula       : 1.2*1000g:20%NaOH
                    Weight        : 1200.0 g (1.000 L)
                    NaOH          : 240.0 g / 39.997 amu / 0.96 kg = 6.250 mol/kg
                    
                    Type          : Product
                    Formula       : 1.2*1000g:20%NaOH
                    Total_Weight  : 1200.0 g (1.000 L)
                    Total_NaOH    : 240.0 g / 39.997 amu / 0.96 kg = 6.250 mol/kg

    
    Thanks:
        MathPython
        https://wiki3.jp/MathPython/page/34
    
    Links:
        Calc-ChemMassPercent.py, Calc-ChemWeightLR.py,
        Get-PeriodicTable.py, Get-MolecularMass.py,
        Calc-ChemMassPercent.py

    """
    help_epi_msg = """EXAMPLES:

    # Dilute a solvent with a weight of 100
    # in which 15 w/w% of something (M1) is dissolved
    # with the same weight of water.
    
    python Calc-ChemMassPercent.py -f "100:0.15+100"

        Type          : Solution.1
        Formula       : 100:0.15
        Weight        : 100
        M1            : 15.0 / 100 = 0.150 (15.000 %)

        Type          : Solution.2
        Formula       : 100
        Weight        : 100

        Type          : Product
        Formula       : 100:0.15 + 100
        Total_Weight  : 200.0
        Total_M1      : 15.0 / 200.0 = 0.075 (7.500 %)
        Total_Solid   : 15.0 / 200.0 = 0.075 (7.500 %)
    
    # Dissolve 15.0g of salt in 100g of saline solution
    # with a concentration of 10 w/w%

    python Calc-ChemMassPercent.py -f "100 g : 10% NaCl + 0 g : 15.0 NaCl"

        Type          : Solution.1
        Formula       : 100g:0.1NaCl
        Weight        : 100 g
        NaCl          : 10.0 g / 100 g = 0.100 (10.000 w/w%)
        
        Type          : Solution.2
        Formula       : 0g:15.0NaCl
        Weight        : 0 g
        NaCl          : 15.0 g
        
        Type          : Product
        Formula       : 100g:0.1NaCl + 0g:15.0NaCl
        Total_Weight  : 100.0 g
        Total_NaCl    : 25.0 g / 100.0 g = 0.250 (25.000 w/w%)
        Total_Solid   : 25.0 g / 100.0 g = 0.250 (25.000 w/w%)

    # Calculate mass percent concentration when mixing multiple solutions.
    echo "100 L : 3.0% NaCl + 100 L : 9.0% NaCl + 200" | python Calc-ChemMassPercent.py
    # or
    python Calc-ChemMassPercent.py -f "100 L : 3.0% NaCl + 100 L : 9.0% NaCl + 200"
    
        Type          : Solution.1
        Formula       : 100L:3.0%NaCl
        Volume        : 100 L
        NaCl          : 3.0 kg / 100 L = 0.030 (3.000 w/v%)

        Type          : Solution.2
        Formula       : 100L:9.0%NaCl
        Volume        : 100 L
        NaCl          : 9.0 kg / 100 L = 0.090 (9.000 w/v%)

        Type          : Solution.3
        Formula       : 200
        Volume        : 200

        Type          : Product
        Formula       : 100L:3.0%NaCl + 100L:9.0%NaCl + 200
        Total_Volume  : 400.0 L
        Total_NaCl    : 12.0 kg / 400.0 L = 0.030 (3.000 w/v%)
        Total_Solid   : 12.0 kg / 400.0 L = 0.030 (3.000 w/v%)
    
    # -v, --verbose option: Output total solvent weight for each step
    python Calc-ChemMassPercent.py -f "100 L : 3.0% NaCl + 100 L : 9.0% NaCl + 200" -v

        Type          : Solution.1
        Formula       : 100L:3.0%NaCl
        Volume        : 100 L
        NaCl          : 3.0 kg / 100 L = 0.030 (3.000 w/v%)
        Total_Volume  : 100.0 L
        Total_Solid   : 3.0 kg / 100.0 L = 0.030 (3.000 w/v%)
        Total_NaCl    : 3.0 kg / 100.0 L = 0.030 (3.000 w/v%)

        Type          : Solution.2
        Formula       : 100L:9.0%NaCl
        Volume        : 100 L
        NaCl          : 9.0 kg / 100 L = 0.090 (9.000 w/v%)
        Total_Volume  : 200.0 L
        Total_Solid   : 12.0 kg / 200.0 L = 0.060 (6.000 w/v%)
        Total_NaCl    : 12.0 kg / 200.0 L = 0.060 (6.000 w/v%)

        Type          : Solution.3
        Formula       : 200
        Volume        : 200
        Total_Volume  : 400.0 L
        Total_Solid   : 12.0 kg / 400.0 L = 0.030 (3.000 w/v%)
        Total_NaCl    : 12.0 kg / 400.0 L = 0.030 (3.000 w/v%)

        Type          : Product
        Formula       : 100L:3.0%NaCl + 100L:9.0%NaCl + 200
        Total_Volume  : 400.0 L
        Total_NaCl    : 12.0 kg / 400.0 L = 0.030 (3.000 w/v%)
        Total_Solid   : 12.0 kg / 400.0 L = 0.030 (3.000 w/v%)
    
    # Simple expression: Mix 100g of 3w/w% saline and 100g of 9w/w% saline:
    python Calc-ChemMassPercent.py -f "100g:3% + 100g:9%"

        Type          : Solution.1
        Formula       : 100g:3%
        Weight        : 100 g
        M1            : 3.0 g / 100 g = 0.030 (3.000 w/w%)

        Type          : Solution.2
        Formula       : 100g:9%
        Weight        : 100 g
        M1            : 9.0 g / 100 g = 0.090 (9.000 w/w%)

        Type          : Product
        Formula       : 100g:3% + 100g:9%
        Total_Weight  : 200.0 g
        Total_M1      : 12.0 g / 200.0 g = 0.060 (6.000 w/w%)
        Total_Solid   : 12.0 g / 200.0 g = 0.060 (6.000 w/w%)
    
    # Mixing multiple solutions containing multiple solvents
    python Calc-ChemMassPercent.py -f "100 mL : 0.3 NaCl, 0.03 T-N + 100 mL : 3.0% T-N +200 mL" -r 2
    
        Type          : Solution.1
        Formula       : 100mL:0.3NaCl,0.03T-N
        Volume        : 100 mL
        NaCl          : 30.0 g / 100 mL = 0.30 (30.00 w/v%)
        T-N           : 3.0 g / 100 mL = 0.03 (3.00 w/v%)
        
        Type          : Solution.2
        Formula       : 100mL:3.0%T-N
        Volume        : 100 mL
        T-N           : 3.0 g / 100 mL = 0.03 (3.00 w/v%)
        
        Type          : Solution.3
        Formula       : 200mL
        Volume        : 200 mL
        
        Type          : Product
        Formula       : 100mL:0.3NaCl,0.03T-N + 100mL:3.0%T-N + 200mL
        Total_Volume  : 400.0 mL
        Total_NaCl    : 30.0 g / 400.0 mL = 0.07 (7.50 w/v%)
        Total_T-N     : 6.0 g / 400.0 mL = 0.01 (1.50 w/v%)
        Total_Solid   : 36.0 g / 400.0 mL = 0.09 (9.00 w/v%)
"""

    parser = argparse.ArgumentParser(description=help_desc_msg,
                    epilog=help_epi_msg,
                    formatter_class=argparse.RawDescriptionHelpFormatter)
    #parser = argparse.ArgumentParser(description='calc matrix using numpy')
    #parser.print_help()
    ts = lambda x:list(map(str, x.split(';')))
    parser.add_argument("-f", "--formula", help="molecular formula", type=ts)
    parser.add_argument("-m", "--molar", help="calc molar concentration", action="store_true")
    parser.add_argument("-mm", "--massmolarity", help="calc mass molarity", action="store_true")
    parser.add_argument("-r", "--round", help="round", default="3", type=str)
    parser.add_argument("-e", "--expression", help="execute expression", type=str)
    parser.add_argument("-v", "--verbose", help="verbose output", action="store_true")
    parser.add_argument("--mvar", help="Use M# in expression", action="store_true")
    parser.add_argument("-d", "--debug", help="debug", action="store_true")
    parser.add_argument("-V", "--version", help="version", action="version", version=_version)
    args = parser.parse_args()
    return(args)

def open_file(mode = 'r'):
    out_lines = []
    readfile = sys.stdin
    for line in readfile:
        line = line.rstrip('\r\n')
        for l in line.split(";"):
            out_lines.append(str(l).strip())
    return out_lines

def strip_formulas(formulas):
    out_lines = []
    for f in formulas:
        out_lines.append(str(f))
    return out_lines

def isNumber(string):
    test_str = str(string)
    try:
        float(test_str)
    except ValueError:
        return False
    else:
        return True

def remove_illegal_chars_from_variable_name(name):
    return re.sub(r'[^0-9a-zA-Z_]+', '', name)

def splitTermToNumAndUnit(term, compiled_regex):
    str_num  = compiled_regex.sub(r'\1', term)
    str_num  = str_num.replace(',', '').replace('_', '').rstrip('-/*')
    str_unit = compiled_regex.sub(r'\2', term)
    split_density = None
    split_vol = None
    if re.search(r'\*|\/', str_num):
        # split d, vol
        split_num = str_num.lstrip(r'*').rstrip(r'*').split(r'*')
        if len(split_num) > 1:
            split_density = split_num[0].strip()
            split_vol = split_num[-1].strip()
        str_num = str(eval(str_num))
    if str_unit == '':
        pass
    elif not isNumber(str_num):
        raise_error("Could not get Volume from '{}'.".format(term))
        sys.exit(1)
    return str_num, str_unit, split_density, split_vol

def getSolventUnit(unit):
    if unit == '':
        ret = [unit, None]
    elif unit.lower() == r'kL'.lower():
        ret = [r't', float(1*1000*1000)]
    elif unit.lower() == r'L'.lower():
        ret = [r'kg', float(1*1000)]
    elif unit.lower() == r'mL'.lower():
        ret = [r'g', float(1*1)]
    elif unit.lower() == r't'.lower():
        ret = [unit, float(1*1000*1000)]
    elif unit.lower() == r'kg'.lower():
        ret = [unit, float(1*1000)]
    elif unit.lower() == r'g'.lower():
        ret = [unit, float(1*1)]
    elif unit.lower() == r'mg'.lower():
        ret = [unit, float(1/1000)]
    else:
        ret = [unit, float(1*1)]
    return ret

def getSolutionUnit(unit):
    # ret = [str("unit"), float(Volume/Weight), str("Volume/Weight")]
    # convert to g/ml
    if unit == '':
        ret = [unit, None, None]
    elif unit.lower() == r'kL'.lower():
        ret = [unit, float(1*1000), r'Volume']
    elif unit.lower() == r'L'.lower():
        ret = [unit, float(1), r'Volume']
    elif unit.lower() == r'mL'.lower():
        ret = [unit, float(1/1000), r'Volume']
    elif unit.lower() == r't'.lower():
        ret = [unit, float(1*1000), r'Weight']
    elif unit.lower() == r'kg'.lower():
        ret = [unit, float(1*1), r'Weight']
    elif unit.lower() == r'g'.lower():
        ret = [unit, float(1/1000), r'Weight']
    elif unit.lower() == r'mg'.lower():
        ret = [unit, float(1/1000/1000), r'Weight']
    else:
        ret = [unit, float(1*1), None]
    return ret

class TotalVolume:

    def __init__(self, solute_volume = 0, unit = None, name = None, split_volume = None):
        self.name = name
        self.unit = unit
        self.solute_volume = solute_volume
        self.split_volume = split_volume
        if split_volume != None:
            self.is_split_volume = True
        else:
            self.is_split_volume = False
    
    def isSplitVolume(self):
        return self.is_split_volume

    def resetIsSplitVolume(self, flag):
        self.is_split_volume = flag

    def sumSoluteVolume(self, add_volume, unit):
        # test unit
        if self.testUnit(unit):
            self.solute_volume += add_volume
        else:
            raise_error("Deferent unit detected. '{}' and '{}'".format(unit, self.unit))

    def sumSplitVolume(self, add_volume, unit):
        if self.testUnit(unit):
            self.split_volume += add_volume
        else:
            raise_error("Deferent unit detected. '{}' and '{}'".format(unit, self.unit))

    def getSoluteVolume(self):
        return self.solute_volume

    def getSplitVolume(self):
        return self.split_volume

    def testUnit(self, unit):
        if unit == None or unit == '':
            return True
        elif unit.lower() == self.unit.lower():
            return True
        else:
            return False

class Material:

    def __init__(self, name=None, weight=None, volume=None, unit=None, mol=None, ratio=None, ratio_unit=None):
        self.name       = name
        self.weight     = weight
        self.volume     = volume
        self.unit       = unit
        self.mol        = mol
        self.ratio      = ratio
        self.ratio_unit = ratio_unit
        self.molar      = ratio
        self.molar_unit = ratio_unit
    
class Product:

    def __init__(self, name=None, weight=None, volume=None, unit=None):
        self.name       = name
        self.weight     = weight
        self.volume     = volume
        self.unit       = unit
    
class Solution:

    def __init__(self, percent, solute_weight, name = None, calc_molmass = False):
        self.name = name
        self.percent = percent
        self.solute_weight = solute_weight
        self.solvent_weight = self.initSolventWeight()
        if calc_molmass:
            comp = Composition(name)
            self.molmass = comp.weight
        else:
            self.molmass = None

    def initSolventWeight(self):
        if self.solute_weight == 0:
            ret = (self.percent) * 1
        else:
            ret = (self.percent) * self.solute_weight
            
        return ret
        
    def getMolMass(self):
        if self.molmass == None:
            return None
        else:
            return float(self.molmass)
    
    def getSoluteWeight(self):
        ret = self.solute_weight - self.getSolventWeight()
        return ret
    
    def sumSolventWeight(self, percent, solute_weight):
        if solute_weight == 0:
            self.solvent_weight += percent * 1
        else:
            self.solvent_weight += percent * solute_weight

class Solid:

    def __init__(self, percent, solute_weight, sub = 0):
        self.name = "Solid"
        self.percent = percent
        self.solute_weight = solute_weight
        self.solvent_weight = self.initSolidWeight(sub)

    def initSolidWeight(self, sub = 0):
        if self.solute_weight == 0:
            ret = (self.percent * 1) - sub
        else:
            ret = (self.percent * self.solute_weight) - sub
        return ret
    
    def getSolventWeight(self):
        return self.solvent_weight
    
    def getCurrentSolventWeight(self, percent, solute_weight, sub = 0):
        ret = (percent * solute_weight) - sub
        return ret
    
    def sumSolventWeight(self, percent, solute_weight, sub = 0):
        if solute_weight == 0:
            self.solvent_weight += (percent * 1) - sub
        else:
            self.solvent_weight += (percent * solute_weight) - sub
    
if __name__ == '__main__':
    # get args
    args = get_args()

    # read module
    if args.molar or args.massmolarity:
        molar_flag = True
    else:
        molar_flag = False
    if molar_flag:
        from pymatgen.core import Composition

    # read formula
    formulas = []
    if args.formula:
        formulas = strip_formulas(args.formula)
    else:
        formulas = open_file()

    # set variable
    solid_name = "Solid"
    solution_symbol = "Solution."
    term_symbol = "M"
    debug_ljust = 13
    line_counter = 0
    # regex
    allowed_num = r'^([-0-9.eE\*/,_]+)'
    allowed_num_and_percent = r'^([-0-9.eE\*/,_]+)%(.*)$'
    separate_num_and_unit   = r'^([-0-9.eE\*/,_]+)(.*)$'
    regex_allowed_num = re.compile(allowed_num)
    regex_allowed_num_and_percent = re.compile(allowed_num_and_percent)
    regex_separate_num_and_unit = re.compile(separate_num_and_unit)
    # lists
    solution_dict = {}
    solvent_dict  = {}
    material_list = []
    variable_list = []
    print_list    = []
    for fml in formulas:
        # formula counter
        line_counter += 1
        # get formula
        fml = fml.rstrip('\r\n')
        fml = fml.strip()
        # test formula
        if re.search('^$', fml):
            sys.exit(0)
        if not regex_allowed_num.search(fml):
            sys.exit(0)
        #if args.debug or args.verbose:
        #    print("{} : {}".format("Input".ljust(debug_ljust), fml.replace(' ', '').replace('+', ' + ')))
        #    print("")
        # split formula into solutions with "+" symbol
        solution_counter = 0
        solutions = fml.split(r'+')
        term_len = len(solutions)
        if True:
            # init solid class
            solvent_dict[solid_name] = Solid(0, 0)
        for solution in solutions:
            solution = solution.strip()
            solution_counter += 1
            solution_id = solution_symbol + str(solution_counter)
            # get Volume and mass percent concentration
            solution = solution.replace(' ', '')
            if re.search(r':', solution):
                # Volume and Concentration
                # e.g. "1000 L : 0.3 NaCl, 0.03 T-N"
                vol  = re.sub(r'^([^:]*):(.*)$', r'\1', solution).strip()
                if vol == '': vol = str(0)
                conc = re.sub(r'^([^:]*):(.*)$', r'\2', solution).strip()
            else:
                # Volume only
                # e.g. "1000 L"
                vol  = str(solution).strip()
                conc = str('')
            # set solution volume and unit
            str_vol, str_vol_unit, split_density, split_vol = splitTermToNumAndUnit(vol, regex_separate_num_and_unit)
            if str_vol_unit == "" and molar_flag:
                raise_error("Please specify solution unit (e.g. L, mL, g, mg, kg) '{}'.".format(vol))
            if solution_counter == 1:
                # init volume
                if split_vol != None:
                    total_volume = TotalVolume(float(str_vol), str_vol_unit, "Total_Volume", float(split_vol))
                    #print(total_volume.isSplitVolume())
                    #print(total_volume.getSplitVolume())
                else:
                    total_volume = TotalVolume(float(str_vol), str_vol_unit)
                if str_vol_unit == "":
                    print_solution_unit = r''
                    print_solvent_unit  = r''
                    isVolume = None
                else:
                    print_solution_unit, coef_solu_to_liter, isVolume = getSolutionUnit(str_vol_unit)
                    print_solvent_unit, coef_solv_to_gram = getSolventUnit(str_vol_unit)
            else:
                # add volume
                total_volume.sumSoluteVolume(float(str_vol), str_vol_unit)
                if isVolume == "Weight" and total_volume.isSplitVolume():
                    if split_vol == None:
                        # reset 
                        total_volume.resetIsSplitVolume(False)
                    else:
                        total_volume.sumSplitVolume(float(split_vol), str_vol_unit)
                        print(total_volume.getSplitVolume())
            # set Property name
            if isVolume == "Weight":
                propNameVolumeOrWeight = r"Weight"
            elif isVolume == "Volume":
                propNameVolumeOrWeight = r"Volume"
            else:
                propNameVolumeOrWeight = r"Weight"
                
            if True:
                print_list.append("{} : {}".format("Type".ljust(debug_ljust), solution_id))
                print_list.append("{} : {}".format("Formula".ljust(debug_ljust), solution))
                if print_solution_unit == '':
                    print_list.append("{} : {}".format(propNameVolumeOrWeight.ljust(debug_ljust), str_vol).strip())
                else:
                    if isVolume == "Weight" and total_volume.isSplitVolume():
                        if split_vol != None:
                            str_split_vol = str("{:." + args.round + "f}").format(float(split_vol) * coef_solu_to_liter)
                            str_split_vol_unit = 'L'
                        print_list.append("{} : {} {} ({} {})".format(propNameVolumeOrWeight.ljust(debug_ljust), str_vol, str_vol_unit, str_split_vol, str_split_vol_unit).strip())
                    else:
                        print_list.append("{} : {} {}".format(propNameVolumeOrWeight.ljust(debug_ljust), str_vol, str_vol_unit).strip())
            
            # get each mass percent concentration nums
            if conc == '':
                # no conc terms (Volume only)
                conc_terms = ['']
                conc_terms_len = 0
            else:
                conc_terms = conc.split(r',')
                conc_terms_len = len(conc_terms)
            # set solvent name and concentration
            term_counter = 0
            for cterm in conc_terms:
                cterm = cterm.strip()
                # test term
                if cterm == '':
                    continue
                term_counter += 1
                # interpret % symbol
                if regex_allowed_num_and_percent.search(cterm):
                    cterm = regex_allowed_num_and_percent.sub(r'\1/100\2', cterm)
                str_solv_num, str_solv_name, _, _ = splitTermToNumAndUnit(cterm, regex_separate_num_and_unit)
                if str_solv_name == r'' and molar_flag:
                    raise_error("Please specify molecule name '{}'.".format(solution))
                elif str_solv_name == r'':
                    str_solv_name = term_symbol + str(term_counter)
                if molar_flag or args.expression:
                    if re.search(r'\-', str_solv_name):
                        raise_error("Hyphen cannot be used in molecular formula: '{}'.".format(str_solv_name))
                # test duplication of term
                #print("{} : {}".format(str_solv_name, solid_name))
                if str_solv_name == solid_name:
                    raise_error("Name '{}' is already registered as a built-in variable. Please set another name.".format(solution))
                # add to dict
                if str_solv_name in solvent_dict.keys():
                    # add solvent weight
                    solvent_dict[str_solv_name].sumSolventWeight(float(str_solv_num), float(str_vol))
                else:
                    # init material_list
                    material_list.append(str_solv_name)
                    # init solvent dict
                    if molar_flag:
                        solvent_dict[str_solv_name] = Solution(float(str_solv_num), float(str_vol), str(str_solv_name), True)
                        #print(solvent_dict[str_solv_name].getMolMass())
                    else:
                        solvent_dict[str_solv_name] = Solution(float(str_solv_num), float(str_vol), str(str_solv_name))
                if True:
                    solvent_dict[solid_name].sumSolventWeight(float(str_solv_num), float(str_vol))
                # output each solvent mass percent
                if molar_flag:
                    c = str_solv_name.ljust(debug_ljust)
                    v = str_vol
                    if isVolume == r"Volume":
                        vol_unit = r" mol/L (M)"
                        v_liter = float(v) * coef_solu_to_liter
                        v_str = str("{} L").format(v_liter)
                    elif isVolume == r"Weight":
                        if args.massmolarity:
                            pass
                        elif total_volume.isSplitVolume() and split_vol != None:
                            vol_unit = r" mol/L (M)"
                            v_liter = float(split_vol) * coef_solu_to_liter
                            v_str = str("{} L").format(v_liter)
                        else:
                            vol_unit = r" mol/kg"
                            v_liter = float(v) * coef_solu_to_liter
                            v_str = str("{} kg").format(v_liter)
                    else:
                        v_str = str("{}").format(v_liter)
                        vol_unit = r''
                    n = float(str_solv_num)
                    molmass = float(solvent_dict[str_solv_name].getMolMass())
                    if float(v) == 0:
                        w = n
                        w_gram = w * coef_solv_to_gram
                        molar = w_gram / molmass
                    else:
                        w = n * float(v)
                        w_gram = w * coef_solv_to_gram
                        if args.massmolarity:
                            vol_unit = r" mol/kg"
                            v_liter = float(v) * coef_solu_to_liter - w_gram / 1000
                            v_str = str("{} kg").format(v_liter)
                        molar = w_gram / molmass / v_liter
                    w_str = str("{} g").format(w_gram)
                    m_str = str("{:." + args.round + "f} amu").format(molmass)
                    p_str = str("{:." + args.round + "f}{}").format(molar, vol_unit)
                    if print_solution_unit != r'':
                        u_solv = print_solvent_unit
                        if float(v) == 0:
                            # case Volume == 0 (only solvent)
                            print_list.append(str("{} : {} ({} {})").format(c, w_str, w, u_solv).strip())
                        else:
                            print_list.append(str("{} : {} / {} / {} = {}").format(c, w_str, m_str, v_str, p_str).strip())
                else:
                    c = str_solv_name.ljust(debug_ljust)
                    v = str_vol
                    n = float(str_solv_num)
                    p = n * 100
                    if float(v) == 0:
                        w = n
                    else:
                        w = n * float(v)
                    if isVolume == r"Volume":
                        p_unit = "w/v%"
                    elif isVolume == r"Weight":
                        p_unit = "w/w%"
                    else:
                        p_unit = "%"
                    n_str = str("{:." + args.round + "f}").format(n)
                    p_str = str("{:." + args.round + "f} {}").format(p, p_unit)
                    if print_solution_unit == '':
                        if float(v) == 0:
                            # case Volume == 0 (only solvent)
                            print_list.append(str("{} : {}").format(c, w).strip())
                        else:
                            print_list.append(str("{} : {} / {} = {} ({})").format(c, w, v, n_str, p_str).strip())
                    else:
                        u_solv = print_solvent_unit
                        u_solu = print_solution_unit
                        if float(v) == 0:
                            # case Volume == 0 (only solvent)
                            print_list.append(str("{} : {} {}").format(c, w, u_solv).strip())
                        else:
                            print_list.append(str("{} : {} {} / {} {} = {} ({})").format(c, w, u_solv, v, u_solu, n_str, p_str).strip())
            
            if args.debug or args.verbose:
                # output 
                propName = "Total_" + propNameVolumeOrWeight
                if not molar_flag:
                    if print_solution_unit == '':
                        print_list.append("{} : {}".format(propName.ljust(debug_ljust), total_volume.getSoluteVolume()).strip())
                    else:
                        print_list.append("{} : {} {}".format(propName.ljust(debug_ljust), total_volume.getSoluteVolume(), print_solution_unit).strip())
                    if len(solvent_dict) > 0:
                        for key in solvent_dict.keys():
                            c = str("Total_" + key).ljust(debug_ljust)
                            v = total_volume.getSoluteVolume()
                            w = solvent_dict[key].solvent_weight
                            r = w / v
                            p = w / v * 100
                            if isVolume == r"Volume":
                                p_unit = "w/v%"
                            elif isVolume == r"Weight":
                                p_unit = "w/w%"
                            else:
                                p_unit = "%"
                            r_str = str("{:." + args.round + "f}").format(r)
                            p_str = str("{:." + args.round + "f} {}").format(p, p_unit)
                            if print_solution_unit == '':
                                print_list.append(str("{} : {} / {} = {} ({})").format(c, w, v, r_str, p_str).strip())
                            else:
                                u_solv = print_solvent_unit
                                u_solu = print_solution_unit
                                print_list.append(str("{} : {} {} / {} {} = {} ({})").format(c, w, u_solv, v, u_solu, r_str, p_str).strip())
            if True:
                print_list.append("")
        
        # add material_list
        if not molar_flag:
            material_list.append(solid_name)
        # output product
        propName = "Total_" + propNameVolumeOrWeight
        n = propName.ljust(debug_ljust)
        v = total_volume.getSoluteVolume()
        print_list.append("{} : {}".format("Type".ljust(debug_ljust), "Product"))
        print_list.append("{} : {}".format("Formula".ljust(debug_ljust), fml.replace(' ', '').replace('+', ' + ')))
        if print_solution_unit == '':
            print_list.append("{} : {}".format(n, v).strip())
        else:
            u = print_solution_unit
            if isVolume == "Weight" and total_volume.isSplitVolume():
                vs = total_volume.getSplitVolume()
                ts = str("{:." + args.round + "f}").format(vs * coef_solu_to_liter)
                print_list.append("{} : {} {} ({} L)".format(propName.ljust(debug_ljust), v, u, ts).strip())
            else:
                print_list.append("{} : {} {}".format(propName.ljust(debug_ljust), v, u).strip())
        if args.expression:
            # set Product(name, weight, volume, unit)
            product_symbol = "Prod"
            exp_str = product_symbol + ' = Product("Product", v, v, u)'
            try: exec(exp_str)
            except: raise_error("invalid variable name: '{}'".format(product_symbol))
            if isVolume == r"Volume":
                exp_reg = product_symbol + " = Product(name, volume, unit)"
            elif isVolume == r"Weight":
                exp_reg = product_symbol + " = Product(name, weight, unit)"
            else:
                exp_reg = product_symbol + " = Product(name, weight, unit)"
            variable_list.append(exp_reg)
        # get solvent
        if len(solvent_dict) > 0:
            mat_counter = 0
            for key in material_list:
                if args.mvar:
                    mat_counter += 1
                    var_symbol = term_symbol + str(mat_counter)
                else:
                    var_symbol = key
                if args.expression:
                    var_symbol = remove_illegal_chars_from_variable_name(var_symbol)
                if molar_flag:
                    c = str("Total_" + key).ljust(debug_ljust)
                    if isVolume == r"Volume":
                        vol_unit = r" mol/L (M)"
                        v_liter = float(v) * coef_solu_to_liter
                        v_str = str("{} L").format(v_liter)
                    elif isVolume == r"Weight":
                        if args.massmolarity:
                            pass
                        elif total_volume.isSplitVolume():
                            vol_unit = r" mol/L (M)"
                            v_liter = vs * coef_solu_to_liter
                            v_str = str("{} L").format(v_liter)
                        else:
                            # split_vol == None:
                            vol_unit = r" mol/kg"
                            v_liter = float(v) * coef_solu_to_liter
                            v_str = str("{} kg").format(v_liter)
                    else:
                        v_str = str("{}").format(v_liter)
                        v_liter = float(v) * coef_solu_to_liter
                        vol_unit = r""
                    w = solvent_dict[key].solvent_weight
                    w_gram = w * coef_solv_to_gram
                    molmass = float(solvent_dict[key].getMolMass())
                    if float(v) == 0:
                        molar = w_gram / molmass
                    else:
                        if args.massmolarity:
                            vol_unit = r" mol/kg"
                            v_liter = float(v) * coef_solu_to_liter - w_gram / 1000
                            v_str = str("{} kg").format(v_liter)
                        molar = w_gram / molmass / v_liter
                    w_str = str("{} g").format(w_gram)
                    m_str = str("{:." + args.round + "f} amu").format(molmass)
                    p_str = str("{:." + args.round + "f}{}").format(molar, vol_unit)
                    if print_solution_unit != r'':
                        u_solv = print_solvent_unit
                        if float(v) == 0:
                            # case Volume == 0 (only solvent)
                            print_list.append(str("{} : {} ({} {})").format(c, w_str, w, u_solv)).strip()
                        else:
                            print_list.append(str("{} : {} / {} / {} = {}").format(c, w_str, m_str, v_str, p_str).strip())
                        # set Material(name, weight, volume, unit, mol, ratio, ratio_unit)
                        if args.expression:
                            exp_str = var_symbol + " = Material(key, w_gram, w_gram, 'g', molmass, molar, vol_unit)"
                            try: exec(exp_str)
                            except: raise_error("invalid variable name: '{}'".format(var_symbol))
                else:
                    c = str("Total_" + key).ljust(debug_ljust)
                    v = total_volume.getSoluteVolume()
                    w = solvent_dict[key].solvent_weight
                    r = w / v
                    p = w / v * 100
                    if isVolume == r"Volume":
                        p_unit = "w/v%"
                    elif isVolume == r"Weight":
                        p_unit = "w/w%"
                    else:
                        p_unit = "%"
                    r_str = str("{:." + args.round + "f}").format(r)
                    p_str = str("{:." + args.round + "f} {}").format(p, p_unit)
                    if print_solution_unit == '':
                        print_list.append(str("{} : {} / {} = {} ({})").format(c, w, v, r_str, p_str).strip())
                        if args.expression:
                            # set Material(name, weight, volume, unit, mol, ratio, ratio_unit)
                            exp_str = var_symbol + " = Material(key, w, w, None, None, p, p_unit)"
                            try: exec(exp_str)
                            except: raise_error("invalid variable name: '{}'".format(var_symbol))
                    else:
                        u_solv = print_solvent_unit
                        u_solu = print_solution_unit
                        print_list.append(str("{} : {} {} / {} {} = {} ({})").format(c, w, u_solv, v, u_solu, r_str, p_str).strip())
                        if args.expression:
                            # set Material(name, weight, volume, unit, mol, ratio, ratio_unit)
                            exp_str = var_symbol + " = Material(key, w, w, u_solv, None, p, p_unit)"
                            try: exec(exp_str)
                            except: raise_error("invalid variable name: '{}'".format(var_symbol))
                # set variable expression
                if args.expression:
                    if molar_flag:
                        if isVolume == r"Volume":
                            exp_reg = var_symbol + " = Material(name, volume, unit, mol, molar, molar_unit)"
                        elif isVolume == r"Weight":
                            exp_reg = var_symbol + " = Material(name, weight, unit, mol, molar, molar_unit)"
                        else:
                            exp_reg = var_symbol + " = Material(name, weight, unit, mol, molar, molar_unit)"
                    else:
                        if isVolume == r"Volume":
                            exp_reg = var_symbol + " = Material(name, volume, unit, mol, ratio, ratio_unit)"
                        elif isVolume == r"Weight":
                            exp_reg = var_symbol + " = Material(name, weight, unit, mol, ratio, ratio_unit)"
                        else:
                            exp_reg = var_symbol + " = Material(name, weight, unit, mol, ratio, ratio_unit)"
                    variable_list.append(exp_reg)
            
        # output variables
        if args.verbose and len(variable_list) > 0:
            print_list.append("")
            for var in variable_list:
                n = "Set_Variable".ljust(debug_ljust)
                print_list.append(str("{} : {}").format(n, var).strip())
        
        # print
        if len(print_list) > 0:
            for print_item in print_list:
                print(print_item)

        # output execute result
        exp_count = 0
        if args.expression:
            print("")
            message = "exec_end"
            messager = "return"
            exp = args.expression
            fmls = str(exp).split(";")
            for fml in fmls:
                exp_count += 1
                if exp_count > 1:
                    print("")
                fml = str(fml).strip()
                # if fml contains "=", run exec, otherwise run eval
                print("{} : {}".format(message.ljust(debug_ljust), fml))
                print("{} : ".format(messager.ljust(debug_ljust)), end="")
                if re.search(r'^([^\(]+)=', fml):
                    exec(fml)
                    print("")
                else:
                    ans = eval(fml)
        
    sys.exit(0)
