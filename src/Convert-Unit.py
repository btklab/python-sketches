#!/usr/bin/env python3
#coding: utf-8

#
# Convert-Unit.py
#

import io, sys, os
import argparse
from sympy import simplify
from sympy.physics import units as u
from sympy.physics.units import joule, kilogram

# === Custom units ===
calorie = 4.184 * joule
kilocalorie = 4184 * joule
BTU = 1055.06 * u.joule

sievert = joule / kilogram  # 1 Sv = 1 J/kg
gray = joule / kilogram  # 1 Gy = 1 J/kg


from sympy.physics.units import candela, steradian
lumen = candela * steradian

from sympy.physics.units import meter
lux = lumen / meter**2


# Categorized units for help display
UNIT_CATEGORIES = {
    "Length": {
        'm': u.meter, 'meter': u.meter, 'km': u.kilometer, 'cm': u.centimeter,
        'mm': u.millimeter, 'um': u.micrometer, 'nm': u.nanometer,
        'inch': u.inch, 'in': u.inch, 'ft': u.foot, 'foot': u.foot, 'yd': u.yard,
        'mile': u.mile, 'nmi': u.nautical_mile,
        #'km/h': u.kilometer / u.hour,
        #'m/s': u.meter / u.second,
    },
    "Time": {
        's': u.second, 'sec': u.second, 'ms': u.millisecond, 'us': u.microsecond,
        'ns': u.nanosecond, 'min': u.minute, 'h': u.hour, 'hr': u.hour,
        'day': u.day,
        #'week': u.week,
        'year': u.year,
    },
    "Mass": {
        'kg': u.kilogram, 'g': u.gram, 'gram': u.gram, 'mg': u.milligram,
        'ug': u.microgram, 'lb': u.pound,
        #'oz': u.ounce,
    },
    "Area": {
        'm2': u.meter**2, 'km2': u.kilometer**2, 'cm2': u.centimeter**2,
        #'acre': u.acre,
        'hectare': u.hectare,
    },
    "Volume": {
        'm3': u.meter**3, 'cm3': u.centimeter**3, 'mm3': u.millimeter**3,
        'l': u.liter,
        'L': u.liter,
        'liter': u.liter,
        'ml': u.milliliter,
        'mL': u.milliliter,
        'kl': 1000 * u.liter,
        'kL': 1000 * u.liter,
        'kiloliter': 1000 * u.liter,
        #'gallon': u.1000 * gallon,
        'quart': u.quart,
    },
    "Speed": {
        'm/s': u.meter / u.second, 'km/h': u.kilometer / u.hour,
        'kmph': u.kilometer / u.hour, 'mph': u.mile / u.hour,
        'ft/s': u.foot / u.second,
        #'knot': u.knot,
    },
    "Force & Pressure": {
        'N': u.newton, 'Pa': u.pascal, 'kPa': 1000 * u.pascal,
        'MPa': 1_000_000 * u.pascal, 'bar': u.bar, 'atm': u.atm, 'psi': u.psi,
    },
    "Energy": {
        'J': u.joule, 'kJ': 1000 * u.joule, 'MJ': 1_000_000 * u.joule,
        'cal': calorie, 'kcal': kilocalorie, 'BTU': BTU,
    },
    "Power": {
        'W': u.watt, 'kW': 1000 * u.watt, 'MW': 1_000_000 * u.watt,
    },
    "Electricity": {
        'V': u.volt, 'A': u.ampere, 'Ohm': u.ohm, 'Ω': u.ohm,
        'C': u.coulomb, 'F': u.farad, 'H': u.henry, 'S': u.siemens,
    },
    "Frequency": {
        'Hz': u.hertz, 'kHz': 1000 * u.hertz, 'MHz': 1_000_000 * u.hertz,
    },
    "Temperature": {
        'K': u.kelvin,
        'kelvin': u.kelvin,
        #'degC': u.degree_Celsius,
        #'C': u.degree_Celsius,
        #'°C': u.degree_Celsius,
        #'degF': u.degree_Fahrenheit,
        #'F': u.degree_Fahrenheit,
        #'°F': u.degree_Fahrenheit,
    },
    "Luminous": {
        "cd": u.candela,
        "sr": u.steradian,
        "lm": u.candela * u.steradian,
        "lx": (u.candela * u.steradian) / u.meter**2,
    },
    "Radiation": {
        "Sv": joule / u.kilogram,  # sievert
        "Gy": joule / u.kilogram,  # gray
        'Bq': u.becquerel,
        # "Bq": 1 / u.second,      # Optional: becquerel
    },
    "Other": {
        'mol': u.mole, 'cd': u.candela, 'rad': u.radian, 'sr': u.steradian,
        'kat': u.katal,
    }
}

# Flatten all units into a single map
UNIT_MAP = {k: v for category in UNIT_CATEGORIES.values() for k, v in category.items()}

def convert_temperature(value, from_unit, to_unit):
    """
    Handles temperature conversion explicitly (Celsius, Fahrenheit, Kelvin).
    """
    if from_unit == 'C' and to_unit == 'K':
        return value + 273.15
    elif from_unit == 'K' and to_unit == 'C':
        return value - 273.15
    elif from_unit == 'F' and to_unit == 'C':
        return (value - 32) * 5 / 9
    elif from_unit == 'C' and to_unit == 'F':
        return value * 9 / 5 + 32
    elif from_unit == 'F' and to_unit == 'K':
        return (value - 32) * 5 / 9 + 273.15
    elif from_unit == 'K' and to_unit == 'F':
        return (value - 273.15) * 9 / 5 + 32
    elif from_unit == to_unit:
        return value
    else:
        raise ValueError(f"Unsupported temperature conversion: {from_unit} to {to_unit}")

def convert_units(value: float, from_unit: str, to_unit: str, numeric: bool = False):
    if from_unit not in UNIT_MAP or to_unit not in UNIT_MAP:
        raise ValueError(f"Unsupported unit. Use --help to view available units.")
    expr = value * UNIT_MAP[from_unit]
    target = UNIT_MAP[to_unit]
    result = simplify(expr / target)
    return result.evalf() if numeric else result


def format_unit_help(categories):
    lines = []
    for name, units in categories.items():
        unit_list = ", ".join(sorted(units.keys()))
        lines.append(f"{name}:\n  {unit_list}")
    return "\n\n".join(lines)


def main():
    help_epilog = """
Examples:
  python Convert-Unit.py 100 cm m       # Convert 100 centimeters to meters
  python Convert-Unit.py 5 cal J -n     # Convert 5 calories to joules (numerically)
  python Convert-Unit.py 10 F C         # Convert 10°F to Celsius
  python Convert-Unit.py 3 BTU kJ       # Convert 3 BTU to kilojoules
  python Convert-Unit.py 36 km/h m/s
  python Convert-Unit.py 500 lm W       # Convert 500 lumens to watts (if applicable)

Supported units (by category):
""" + format_unit_help(UNIT_CATEGORIES)

    parser = argparse.ArgumentParser(
        description="Convert physical units using sympy.physics.units",
        epilog=help_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("value", type=float, help="Numeric value to convert")
    parser.add_argument("from_unit", type=str, help="Unit to convert from (e.g. 'km')")
    parser.add_argument("to_unit", type=str, help="Unit to convert to (e.g. 'm')")
    parser.add_argument("-n", "--numeric", action="store_true", help="Evaluate the result numerically")

    args = parser.parse_args()

    try:
        if args.from_unit in ['C', 'F', 'K'] and args.to_unit in ['C', 'F', 'K']:
            result = convert_temperature(args.value, args.from_unit, args.to_unit)
            print(f"{args.value} {args.from_unit} = {result} {args.to_unit}")
        else:
            result = convert_units(args.value, args.from_unit, args.to_unit, args.numeric)
            print(f"{args.value} {args.from_unit} = {result} {args.to_unit}")
    except Exception as e:
        print(f"[Error] {e}")


if __name__ == "__main__":
    main()
    sys.exit(0)
