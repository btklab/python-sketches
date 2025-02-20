#!/usr/bin/env python3
#coding: utf-8

#
# Calc-LPpulp
#

import io, sys, os
import argparse
import re
import pulp as pl

_version = "Sun Jan 21 13:31:48 TST 2024"
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
    help_desc_msg ="""Calc-LPpulp - Solve Linear Problem with matrix using PULP

    Linear Problem optimizer that expresses objective variables and
    constraints in a matrix.

    input.txt:
        0.013  0.008, "Total Cost of Ingredients per can"
        1      1      == 100, "PercentagesSum"
        0.100  0.200  >= 8.0, "ProteinRequirement"
        0.080  0.100  >= 6.0, "FatRequirement"
        0.001  0.005  <= 2.0, "FibreRequirement"
        0.002  0.005  <= 0.4, "SaltRequirement"

    script:

        python ./Calc-LPpulp.py --lbound 0 --category "Integer"

            Status  = Optimal (Minimize)
            Name    = objective
            Option  = {'lowBound': 0.0, 'upBound': None, 'cat': 'Integer'}
            x1      = 34.0
            x2      = 66.0
            Obj_Val = 0.97

    input data format:
        - basic
            - Express the objective function and constraints as a
              numeric matrix separated by spaces
            - The variable names are automatically assigned, but
              you can also specify any variable names (see below)
            - Multiple spaces will be replaced with a single space,
              so you can format it for easier reading
        
        - skip line
            - The following lines of input data are skipped
                - Lines beginning with "#"
                - Empty lines
        
        - Space handling
            - Multiple consecutive spaces in input data are
              recognized as single space. (This is convenient
              when formatting input data to make it easier for
              human to read)
            - Extra spaces at the beginning and end of each line
              in the input data is removed.
        
        - title line
            - The first line beginning with "#" is interpreted as title
        
        - set variable symbols
            - Variables can be declared on the first line,
              excluding the title line, separated by spaces
            - If no variables are specified, x1, x2,... will be automatically
              assigned in order from the left column of the matrix
            - Variable names can also be specified with the --names option,
              but it is recommended to write variable names on
              the input data as much as possible. (This is because if
              you write the data and variable name separately, one
              is likely to be lost.)
            - If the number of variables is less than the number of
              columns in the objective function, the columns of the
              objective function to which variables are not assigned are
              simply considered as numbers to be summed

                example : case where the number of variables is
                          less than the number of columns of the
                          objective function

                    x  y
                    1  1 1
                    3  5 0 <= 15
                    2  1   >= 4
                    1 -1 1 == 1

                 output

                    1*x + 1*y + 1
                    _C1: 3 x + 5 y <= 15
                    _C2: 2 x + y >= 4
                    _C3: x - y = 0
        
        - set objective function
            - The first line starting with a number is
              considered the objective function
            - The specification of the objective function can be
              skipped. For example, it is not necessary to use an
              objective function to derive a solution to a quadratic
              function

                example without objective function

                    1 1 == 100
                    2 4 == 272

                how to specify variable names when
                there is no objective function

                    x y
                    1 1 == 100
                    2 4 == 272

        - set constraints
            - Data lines containing operators "<=, ==, >=" are
              considered constraints
            - Multiple constraints can be specified

        - misc
            - If you specify the "-d (--debug)" option, it shows
              the description of the problem. It can be used to verify
              the answer
            - If you specify the "-o (--output <filepath>)", it output
              the python script into a file. It can be used when you
              want to add more complex processing
        
        - what this script cannot do
            - Variable assignment statements cannot be written in
              input data
            - Variables cannot be automatically generated from a
              two-dimensional table
    
    References:
        GitHub - coin-or/pulp: A python Linear Programming API
            https://github.com/coin-or/pulp

        Optimization with PuLP - PuLP documentation
            https://coin-or.github.io/pulp/

        About LP
            http://www.nct9.ne.jp/m_hiroi/light/pulp01.html
            https://www.miyamotolab.org/lectures/autumn_winter
            https://web.tuat.ac.jp/~miya/fujie_ORSJ.pdf
    
    Links:
        Calc-LPpulp.py

    """
    help_epi_msg = """EXAMPLES:

    Solve a Blending Problem
        https://coin-or.github.io/pulp/CaseStudies/a_blending_problem.html

    input.txt:

        ```input.txt
        # title  --category "Integer" --lbound 0
        ## objective
        0.013 0.008 0.010 0.002 0.005 0.001, "Total Cost of Ingredients per can"

        ## constraints
        1 1 1 1 1 1 == 100
        0.100 0.200 0.150 0.000 0.040 0.000 >= 8.0, "proteinPercent"
        0.080 0.100 0.110 0.010 0.010 0.000 >= 6.0, "fatPercent"
        0.001 0.005 0.003 0.100 0.150 0.000 <= 2.0, "fibrePercent"
        0.002 0.005 0.007 0.002 0.008 0.000 <= 0.4, "saltPercent"
        ```

    solve:

        python Calc-LPpulp.py -f input.txt --category "Integer" --lbound 0 [-d]
        cat input.txt | python Calc-LPpulp.py --category "Integer" --lbound 0 [-d]
        
            Status  = Optimal (Minimize)
            Name    = title
            Option  = --cat "Integer" --lbound 0
            x1      = 0.0
            x2      = 60.0
            x3      = 0.0
            x4      = 0.0
            x5      = 0.0
            x6      = 40.0
            Obj_Val = 0.5

    Simplest example:

        0.013 0.008 0.010 0.002 0.005 0.001
        1 1 1 1 1 1 == 100
        0.100 0.200 0.150 0.000 0.040 0.000 >= 8.0
        0.080 0.100 0.110 0.010 0.010 0.000 >= 6.0
        0.001 0.005 0.003 0.100 0.150 0.000 <= 2.0
        0.002 0.005 0.007 0.002 0.008 0.000 <= 0.4

    solve:
        python Calc-LPpulp.py -f input.txt --lbound 0

            Status  = Optimal (Minimize)
            Name    = Problem
            Option  = {'lowBound': 0.0, 'upBound': None, 'cat': 'Continuous'}
            x1      = 0.0
            x2      = 60.0
            x3      = 0.0
            x4      = 0.0
            x5      = 0.0
            x6      = 40.0
            Obj_Val = 0.52

    Add title and comment

        # this is title

        ## objective
        0.013 0.008 0.010 0.002 0.005 0.001
    
        ## constraints
        1 1 1 1 1 1 == 100
        0.100 0.200 0.150 0.000 0.040 0.000 >= 8.0
        0.080 0.100 0.110 0.010 0.010 0.000 >= 6.0
        0.001 0.005 0.003 0.100 0.150 0.000 <= 2.0
        0.002 0.005 0.007 0.002 0.008 0.000 <= 0.4

    solve:
        python Calc-LPpulp.py -f input.txt --lbound 0

            Status  = Optimal (Minimize)
            Name    = this_is_title
            Option  = {'lowBound': 0.0, 'upBound': None, 'cat': 'Continuous'}
            x1      = 0.0
            x2      = 60.0
            x3      = 0.0
            x4      = 0.0
            x5      = 0.0
            x6      = 40.0
            Obj_Val = 0.52

    Add variable names within input data

        # this is title

        ## objective
        CHICKEN  BEEF MUTTON  RICE WHEAT   GEL
          0.013 0.008  0.010 0.002 0.005 0.001
    
        ## constraints
        1 1 1 1 1 1 == 100
        0.100 0.200 0.150 0.000 0.040 0.000 >= 8.0
        0.080 0.100 0.110 0.010 0.010 0.000 >= 6.0
        0.001 0.005 0.003 0.100 0.150 0.000 <= 2.0
        0.002 0.005 0.007 0.002 0.008 0.000 <= 0.4

    solve:
        python Calc-LPpulp.py -f input.txt --lbound 0 -c 'Integer'

            Status  = Optimal (Minimize)
            Name    = this_is_title
            Option  = {'lowBound': 0.0, 'upBound': None, 'cat': 'Integer'}
            BEEF    = 60.0
            CHICKEN = 0.0
            GEL     = 40.0
            MUTTON  = 0.0
            RICE    = 0.0
            WHEAT   = 0.0
            Obj_Val = 0.5

    output debug mode:
    python Calc-LPpulp.py -f input.txt --lbound 0 -c 'Integer' -d

    output python script to file:
    python Calc-LPpulp.py -f input.txt --lbound 0 -c 'Integer' -o out.py

    all input format:
    
        ```input.txt
        # title  --category "Integer" --lbound 0
        
        ## objective
        CHICKEN BEEF   MUTTON RICE  WHEAT GEL
        0.013   0.008  0.010  0.002 0.005 0.001, "Total Cost of Ingredients per can"
        
        ## constraints
        1 1 1 1 1 1 == 100
        0.100 0.200 0.150 0.000 0.040 0.000 >= 8.0, "proteinPercent"
        0.080 0.100 0.110 0.010 0.010 0.000 >= 6.0, "fatPercent"
        0.001 0.005 0.003 0.100 0.150 0.000 <= 2.0, "fibrePercent"
        0.002 0.005 0.007 0.002 0.008 0.000 <= 0.4, "saltPercent"
        ```
"""

    parser = argparse.ArgumentParser(description=help_desc_msg,
                    epilog=help_epi_msg,
                    formatter_class=argparse.RawDescriptionHelpFormatter)
    #parser = argparse.ArgumentParser(description='calc matrix using numpy')
    #parser.print_help()
    ts = lambda x:list(map(str, x.split(' ')))
    parser.add_argument("-f", "--file", help="input file", type=str)
    parser.add_argument("-t", "--title", help="title label of the problem", type=str)
    parser.add_argument("-o", "--output", help="output *.py", type=str)
    parser.add_argument("-o2", "--output2", help="output *.lp", type=str)
    parser.add_argument("-max", "--max", help="sense of the problem", action="store_true")
    parser.add_argument("-min", "--min", help="sense of the problem", action="store_true")
    parser.add_argument("-c", "--category", help="category of the variable", default="Continuous", type=str,
        choices=['Continuous', 'Binary', 'Integer'])
    parser.add_argument("-p", "--padding", help="ljust of display", default=7, type=int)
    parser.add_argument("-low", "--lbound", help="lowBound", default=None, type=float)
    parser.add_argument("-up", "--ubound", help="upBound", default=None, type=float)
    parser.add_argument("-s", "--symbol", help="symbol of variable", default="x", type=str)
    parser.add_argument("-n", "--names", help="Specify variable names", type=ts)
    parser.add_argument("-d", "--debug", help="debug", action="store_true")
    parser.add_argument("-V", "--version", help="version", action="version", version=_version)
    args = parser.parse_args()
    return(args)

def open_file(mode = 'r'):
    if args.file:
        if os.name == 'nt':
            readfile = re.sub(r'\\', '/', args.file)
        try:
            readfile = open(readfile, mode, encoding="utf-8")
        except:
            raise_error("{}: {}".format("Could not open file"), readfile)
    else:
        readfile = sys.stdin
    return readfile

def out_file(olist, ofile, mode = 'w'):
    try:
        if os.name == 'nt':
            ofile = re.sub(r'\\', '/', ofile)
            with open(ofile, mode, encoding="utf-8") as outfile:
                outfile.write('\n'.join(str(i) for i in olist))
        else:
            with open(ofile, mode, encoding="utf-8") as outfile:
                outfile.write('\n'.join(str(i) for i in olist))
    except:
        raise_error("{}: {}".format("Could not output file"), ofile)

if __name__ == '__main__':
    # get args
    args = get_args()
    
    # set varriable name
    var_name = args.symbol
    #print(var_name)
    # set sense
    if args.min:
        sense = pl.LpMinimize
        optStr = r'Minimize'
        sense_str = "pl.LpMinimize"
    elif args.max:
        sense = pl.LpMaximize
        optStr = r'Maximize'
        sense_str = "pl.LpMaximize"
    else:
        sense = pl.LpMinimize
        optStr = r'Minimize'
        sense_str = "pl.LpMinimize"
    # set category
    cat = args.category
    if cat == r'Continuous':
        category = pl.LpContinuous
        category_str = "pl.LpContinuous"
    elif cat == r'Binary':
        category = pl.LpBinary
        category_str = "pl.LpBinary"
    elif cat == r'Integer':
        category = pl.LpInteger
        category_str = "pl.LpInteger"
    else:
        category = pl.LpContinuous
        category_str = "pl.LpContinuous"
        
    # read from file
    lineCnt = 0
    debug_pad = 15
    reg_replace_duplicated_spaces = re.compile(r'  *')
    reg_title   = re.compile(r'^# (..*)$')
    reg_comment = re.compile(r'^#|^\s*$')
    reg_set_var = re.compile(r'^[a-zA-Z0-9_]+\s*=\s*')
    reg_set_constraint = re.compile(r'([^\s]+)\s*([\<\=\>]=)\s*([^\s]+)')
    reg_separate_constraint = re.compile(r'^(..*)\s*([\<\=\>]=)\s*(..*)$')
    appendVarName = 'prob'
    nam_list = []
    con_list = []
    obj_list = []
    var_list = []
    scr_list = []
    isInit = False
    isVar = False
    isObjective = False
    isFirstConst = True
    var_length = 0
    inline_title = r''
    # splatting
    opt_dict = {}
    opt_dict["lowBound"] = args.lbound
    opt_dict["upBound"]  = args.ubound
    opt_dict["cat"]      = category
    # append function to const_list
    readFile = open_file()
    for line in readFile:
        line = line.rstrip('\r\n').strip()
        line = re.sub(reg_replace_duplicated_spaces, ' ', line)
        # skip comment or empty line
        if lineCnt == 0 and re.search(reg_title, line):
            inline_title = reg_title.sub(r'\1', line).strip()
        # Create the 'prob' variable to contain the problem data
        if not isInit:
            isInit = True
            if args.title:
                title_str = args.title
                plname = re.sub(r' \-.*$', r'', title_str).strip()
                plopt  = title_str.replace(plname, '').strip()
            elif not inline_title == '':
                # replace option
                title_str = inline_title
                plname = re.sub(r' \-.*$', r'', title_str).strip()
                plopt  = title_str.replace(plname, '').strip()
            else:
                plname = r"Problem"
                plopt  = r''
            if plname == r'':
                plname = r"Problem"
                plopt  = r''
            if re.search(" ", plname):
                plname = plname.replace(" ", "_")
            prob = pl.LpProblem(name=plname, sense=sense)
            # show script
            if args.debug or args.output:
                scr_list.append(r'#!/usr/bin/env python3')
                scr_list.append(r'#coding: utf-8')
                scr_list.append(r"")
                scr_list.append(r"import pulp as pl")
                scr_list.append(r"")
                scr_list.append(r'# Init problem (sense : choice [pl.LpMinimize (default), pl.LpMaximize)]')
                scr_list.append(r'prob = pl.LpProblem(name="Problem", sense={})'.format(sense_str))
                scr_list.append(r"")
        if re.search(reg_comment, line):
            continue
        # read line
        lineCnt += 1
        if re.search(reg_set_var, line):
            # set variables: output as-is:
            if True:
                raise_error("{} : {}".format("Variable definition not allowed", line))
            if lineCnt == 1:
                raise_error("{} : {}".format("first line must be objective", line))
            var_list.append(line)
            if args.debug or args.output:
                scr_list.append(r"# Set Variable")
                scr_list.append(r"{}".format(line))
        elif re.search(reg_set_constraint, line):
            # set constraints
            #if lineCnt == 1:
            #    raise_error("{} : {}".format("first line must be objective", line))
            l = re.sub(reg_separate_constraint, r'\1', line).strip()
            c = re.sub(reg_separate_constraint, r'\2', line).strip()
            r = re.sub(reg_separate_constraint, r'\3', line).strip()
            operator = c
            split_l  = l.split()
            if not isVar:
                # set variables
                if args.names:
                    # variable names from option
                    var_length = len(args.names)
                    var_fml = r''
                    var_fml = var_fml + r'[ pl.LpVariable(name="'
                    var_fml = var_fml + r'{}".format(args.names[i].strip()), **opt_dict) for i in range(var_length) ]'
                else:
                    # auto variable names
                    var_length = len(split_l)
                    var_fml = r''
                    var_fml = var_fml + r'[ pl.LpVariable(name="{}'.format(var_name)
                    var_fml = var_fml + r'{}".format(i+1), **opt_dict) for i in range(var_length) ]'
                var_exec = r'{} = '.format(var_name) + var_fml
                exec(var_exec)
                isVar = True
                # show description
                scr_list.append(r"# Set Variables")
                scr_list.append(r"# x = pl.LpVariable(name, lowBound=None, upBound=None, cat='Continuous')")
                scr_list.append(r"# cat : choice [pl.LpContinuous (default), pl.LpBinary, pl.LpInteger]")
                scr_list.append(r"opt_dict = {}".format(opt_dict))
                if args.names:
                    scr_list.append(r'name_list = {}'.format(args.names))
                    var_fml = r''
                    var_fml = var_fml + r'[ pl.LpVariable(name="'
                    var_fml = var_fml + r'{}".format(name_list[i].strip()), **opt_dict) for i in range(var_length) ]'
                else:
                    var_fml = r''
                    var_fml = var_fml + r'[ pl.LpVariable(name="{}'.format(var_name)
                    var_fml = var_fml + r'{}".format(i+1), **opt_dict) for i in range(var_length) ]'
                var_fml = var_fml.replace(r"range(var_length)", r"range({})".format(var_length))
                var_exec = r'{} = '.format(var_name) + var_fml
                scr_list.append(r"{}".format(var_exec))
                scr_list.append(r'#name_list = {}'.format(eval(var_name)))
                scr_list.append(r"")
            if var_length == 0:
                var_length = len(split_l)
            sum_vals = []
            if var_length < len(split_l):
                #raise_error("len(names) less than len(objective) : {}".format(args.names))
                diff = var_length - len(split_l)
                sum_vals = l.split()[diff:]
                l = " ".join(l.split()[0:var_length])
                split_l  = l.split()
            # compare length between objective and constraints
            assert_str = "assert len(split_l) <= len({})".format(var_name)
            exec(assert_str)
            if len(sum_vals) > 0:
                sum_val_str = ' + '.join(sum_vals)
                line = 'pl.lpDot( [{}], {} ) + {} {} {}'.format(l.replace(' ', ', '), var_name, sum_val_str, operator, r)
            else:
                line = 'pl.lpDot( [{}], {} ) {} {}'.format(l.replace(' ', ', '), var_name, operator, r)
            line = "{} += {}".format(appendVarName, line)
            con_list.append(line)
            if args.debug or args.output:
                if isFirstConst:
                    isFirstConst = False
                    #scr_list.append(r'')
                    scr_list.append(r'# Set Constraints')
                    scr_list.append(r'#assert len(c) == len(x) == len(a)')
                scr_list.append(r"{}".format(line))
        else:
            # set variable
            if re.search(r',\s*[\'"](..*)[\'"]\s*$', line):
                # label specified
                fml = re.sub(r'^([^,]+),\s*([\'"](..*)[\'"])\s*$', r'\1', line).strip()
                lab = re.sub(r'^([^,]+),\s*([\'"](..*)[\'"])\s*$', r'\2', line).strip()
            else:
                fml = line
                lab = r''
            if lineCnt == 1 and re.search(r'^[a-zA-Z_]', fml):
                # set variable name from first line of input data
                nam_list = fml.split()
            var_length = len(fml.split())
            sum_vals = []
            if args.names:
                # variable names from option
                if len(args.names) < var_length:
                    #raise_error("len(names) less than len(objective) : {}".format(args.names))
                    diff = len(args.names) - var_length
                    sum_vals = fml.split()[diff:]
                    fml = " ".join(fml.split()[0:len(args.names)])
                var_length = len(args.names)
                var_fml = r''
                var_fml = var_fml + r'[ pl.LpVariable(name="'
                var_fml = var_fml + r'{}".format(args.names[i].strip()), **opt_dict) for i in range(var_length) ]'
            elif len(nam_list) > 0:
                # variable names from first line of input data
                if len(nam_list) < var_length:
                    #raise_error("len(names) less than len(objective): {}".format(nam_list))
                    diff = len(nam_list) - var_length
                    sum_vals = fml.split()[diff:]
                    fml = " ".join(fml.split()[0:len(nam_list)])
                var_length = len(nam_list)
                var_fml = r''
                var_fml = var_fml + r'[ pl.LpVariable(name="'
                var_fml = var_fml + r'{}".format(nam_list[i].strip()), **opt_dict) for i in range(var_length) ]'
            else:
                # auto variable names
                var_fml = r''
                var_fml = var_fml + r'[ pl.LpVariable(name="{}'.format(var_name)
                var_fml = var_fml + r'{}".format(i+1), **opt_dict) for i in range(var_length) ]'
            var_exec = r'{} = '.format(var_name) + var_fml
            exec(var_exec)
            isVar = True
            if args.debug or args.output:
                scr_list.append(r"# Set Variables")
                scr_list.append(r"# x = pl.LpVariable(name, lowBound=None, upBound=None, cat='Continuous')")
                scr_list.append(r"# cat : choice [pl.LpContinuous (default), pl.LpBinary, pl.LpInteger]")
                scr_list.append(r"opt_dict = {}".format(opt_dict))
                var_fml = r''
                if args.names:
                    scr_list.append(r'name_list = {}'.format(args.names))
                    var_fml = var_fml + r'[ pl.LpVariable(name="'
                    var_fml = var_fml + r'{}".format(name_list[i].strip()), **opt_dict)'
                elif len(nam_list) > 0:
                    scr_list.append(r'name_list = {}'.format(nam_list))
                    var_fml = var_fml + r'[ pl.LpVariable(name="'
                    var_fml = var_fml + r'{}".format(name_list[i].strip()), **opt_dict)'
                else:
                    var_fml = var_fml + r'[ pl.LpVariable(name="{}'.format(var_name)
                    var_fml = var_fml + r'{}".format(i+1), **opt_dict)'
                var_fml = var_fml + r' for i in range({}) ]'.format(len(fml.split()))
                var_exec = r'{} = '.format(var_name) + var_fml
                scr_list.append(r"{}".format(var_exec))
                if not args.names and not len(nam_list) > 0:
                    scr_list.append(r'#name_list = {}'.format(eval(var_name)))
                scr_list.append(r"")
            if lineCnt == 1 and re.search(r'^[a-zA-Z_]', fml):
                # read next row
                lineCnt = lineCnt - 1
                continue
            # set objective function
            if lab == r'':
                line = "pl.lpDot( [{}], {} )".format( fml.replace(' ', ', '), var_name)
            else:
                # label specified
                line = "pl.lpDot( [{}], {} ), {}".format( fml.replace(' ', ', '), var_name, lab)
            if len(sum_vals) > 0:
                sum_val_str = ' + '.join(sum_vals)
                line = "{} += {} + {}".format(appendVarName, line, sum_val_str)
            else:
                line = "{} += {}".format(appendVarName, line)
            obj_list.append(line)
            isObjective = True
            if args.debug or args.output:
                scr_list.append(r"# Set Objective")
                scr_list.append(r"{}".format(line))
    
    # test function
    if lineCnt == 0: raise_error("Empty file.")
    if not isVar: raise_error("Variables not set.")
    if args.debug or args.output:
        scr_list.append(r"")
        scr_list.append(r"# Show description")
        scr_list.append(r'print(prob)')
        scr_list.append(r"")
        scr_list.append(r"# Solve problem")
        scr_list.append(r'status = prob.solve(pl.PULP_CBC_CMD(msg=0))')
        scr_list.append(r"")
        scr_list.append(r"# Show result")
        scr_list.append(r'pad = {}'.format(args.padding))
        scr_list.append(r'stat = pl.LpStatus[prob.status]')
        scr_list.append(r'if stat == "Optimal":')
        scr_list.append(r'    print("{} = {}".format(r"Status".ljust(pad), stat))')
        scr_list.append(r'    print("{} = {}".format(r"Name".ljust(pad), "Project"))')
        scr_list.append(r'    print("{} = {}".format(r"Option".ljust(pad), opt_dict))')
        scr_list.append(r'    for v in prob.variables():')
        scr_list.append(r'        print("{} = {}".format(v.name.ljust(pad), v.varValue))')
        if isObjective:
            scr_list.append(r'    print("{} = {}".format(r"Obj_Val".ljust(pad), pl.value(prob.objective)))')
        else:
            scr_list.append(r'    #print("{} = {}".format(r"Obj_Val".ljust(pad), pl.value(prob.objective)))')
        scr_list.append(r'else:')
        scr_list.append(r'    print("{} = Error :  {} ({})".format(r"Status".ljust(pad), stat))')

    # exec function
    if len(obj_list) > 0:
        for f in obj_list: exec(f)
    if len(con_list) > 0:
        for f in con_list: exec(f)
    # The problem data is written to an .lp file
    if args.output:
        out_file(scr_list, args.output)
    if args.output2:
        outputFile = re.sub(r'\\', '/', args.output2)
        prob.writeLP(outputFile)
    # The problem is solved using PuLP's choice of Solver
    status = prob.solve(pl.PULP_CBC_CMD(msg=0))
    # The status of the solution is printed to the screen
    pad = args.padding
    stat = pl.LpStatus[prob.status]
    # The optimised objective function value is printed to the screen
    # debug
    if args.debug or args.output:
        print(r'Script:')
        print(r'```python')
        for p in scr_list:
            print(p)
        print(r"```")
        print(r"")
        if True:
            print(prob)
    if stat == 'Optimal':
        if plopt == r'':
            print("{} = {} ({})".format(r"Status".ljust(pad), stat, optStr))
            print("{} = {}".format(r"Name".ljust(pad), plname))
            print("{} = {}".format(r"Option".ljust(pad), opt_dict))
        else:
            print("{} = {} ({})".format(r"Status".ljust(pad), stat, optStr))
            print("{} = {}".format(r"Name".ljust(pad), plname))
            print("{} = {}".format(r"Option".ljust(pad), plopt))
        # Each of the variables is printed with it's resolved optimum value
        for v in prob.variables():
            print("{} = {}".format(v.name.ljust(pad), v.varValue))
        # show objective value
        if len(obj_list) > 0:
            print("{} = {}".format(r"Obj_Val".ljust(pad), pl.value(prob.objective)))
    else:
        print("{} = Error :  {} ({})".format(r"Status".ljust(pad), stat, optStr))
        if plopt == r'':
            print("{} = {}".format(r"Name".ljust(pad), plname))
            print("{} = {}".format(r"Option".ljust(pad), opt_dict))
        else:
            print("{} = {}".format(r"Name".ljust(pad), plname))
            print("{} = {}".format(r"Option".ljust(pad), plopt))
        raise_error("{} = {} ({})".format(r"Status", stat, optStr))
        sys.exit(1)
    
    sys.exit(0)
