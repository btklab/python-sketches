#!/usr/bin/env python3
#coding: utf-8

#
# pymatcalc - Calculate matrix
#

import io, sys, os
import re
import argparse
import numpy as np

_version = "Wed Mar 8 06:53:17 JST 2023"
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
    help_desc_msg ="""pymatcalc - Calc matrix using numpy.ndarray

    If the input has multiple rows, it will be a matrix.
    If it has only one row, it will be a vector.
    By connecting multiple pipelines, operation results can be reused.

    Inspired by:
        Ryuichi Ueda and CIT Autonomous Robot Lab
        https://b.ueda.tech/?post=00674
        GitHub - ryuichiueda/PMAT: Pipe Oriented Matrix Calculator
        https://github.com/ryuichiueda/PMAT

    Usage:
        pymatcalc '[<key>=]<formula>'

        good: pymatcalc 'A@B'
        good: pymatcalc 'C=A@B'

        When using "=" in formula, need to specify key.

        good: pymatcalc 'C=np.eye(1, dtype=int)'
        ng:   pymatcalc 'np.eye(1, dtype=int)'

    Input format:
        label val val ...
        label val val ...
        label val val ...

        e.g.
            A 1 1
            A 2 4
            B 4 3
            B 2 1

    Functions:
        - Scalar product: pymatcalc 'C=A*B'
        - Hadamard product (element-wise multiplication): pymatcalc 'C=np.multiply(A, B)'
        - Identity matrix (method 1): pymatcalc 'C=np.eye(n, dtype=int)'
        - Identity matrix (method 2): pymatcalc 'C=np.identity(n, dtype=int)'
        - Transpose matrix: pymatcalc 'C=A.T'
        - Determinant: pymatcalc 'C=np.linalg.det(A)*np.eye(1)'
          - When the result is a scalar, multiply by an identity matrix for consistent output shape
        - Inverse matrix: pymatcalc 'np.linalg.inv(A)'
        - Eigenvalues: pymatcalc 'np.linalg.eig(A)[0]'
        - Eigenvectors: pymatcalc 'np.linalg.eig(A)[1]'
        - Dot product (inner product): pymatcalc 'np.dot(A, B)'
        - Matrix multiplication (method 1): pymatcalc 'A@B'
        - Matrix multiplication (method 2): pymatcalc 'np.matmul(A, B)'
        - Vector inner product: pymatcalc 'np.inner(A, B)'
        - Vector outer product: pymatcalc 'np.outer(A, B)'
        - Generate a random matrix: 'C=np.random.randint(-10,10,size=(3,3))'
        - Solve a system of linear equations: pymatcalc 'C=np.linalg.inv(L)@R'
    """
    help_epi_msg = """EXAMPLES:
    input example:
    $ cat matrix
    A 1 1
    A 2 4
    B 4 3
    B 2 1

    calc example:
    $ cat matrix | python pymatcalc.py 'A*B'
    A 1 1
    A 2 4
    B 4 3
    B 2 1
    A*B 4.0 3.0
    A*B 4.0 4.0

    $ cat matrix | python pymatcalc.py 'A@B'
    $ cat matrix | python pymatcalc.py 'np.matmul(A, B)'
    A 1 1
    A 2 4
    B 4 3
    B 2 1
    A@B 6.0 4.0
    A@B 16.0 10.0

    $ cat matrix | python pymatcalc.py'C=np.eye(3,dtype=int)'
    $ cat matrix | python pymatcalc.py'C=np.identity(3,dtype=int)'
    A 1 1
    A 2 4
    B 4 3
    B 2 1
    C 1 0 0
    C 0 1 0
    C 0 0 1

    add new label to ans:
    $ cat matrix | python pymatcalc.py 'C=A*B'
    A 1 2
    A 3 4
    B 4 3
    B 2 1
    C 4.0 3.0
    C 4.0 4.0

    determinant:
    $ cat matrix | python pymatcalc.py 'C=np.linalg.det(A)*np.eye(1)'
    A 2 -6 4
    A 7 2 3
    A 8 5 -1
    C -144.0

    invert:
    $ cat matrix | python pymatcalc.py 'C=np.linalg.inv(A)'
    A -4 2
    A 7 2
    C -0.0909090909090909 0.09090909090909091
    C 0.3181818181818182 0.1818181818181818

    test invert
    $ cat matrix | python pymatcalc.py 'C=np.dot(A, np.linalg.inv(A))'
    A -4 2
    A 7 2
    C 1.0 -5.551115123125783e-17
    C 1.1102230246251565e-16 1.0

    chain calc using pipe:
    $ cat matrix | python pymatcalc.py 'C=A@B' | python pymatcalc.py 'D=A@C'
    A 1 2
    A 3 4
    B 4 3
    B 2 1
    C 8.0 5.0
    C 20.0 13.0
    D 48.0 31.0
    D 104.0 67.0

    $ cat matrix | python pymatcalc.py 'C=A@(A@B)'
    A 1 2
    A 3 4
    B 4 3
    B 2 1
    C 48.0 31.0
    C 104.0 67.0

    solve simultaneous equations
    $ cat matrix
    L 1 1
    L 2 3
    R 2
    R 5

    invert Left and @ Right

    $ cat matrix | python pymatcalc.py 'ANS = np.linalg.inv(L) @ R'
    L 1 1
    L 2 4
    R 9
    R 22
    ANS 7.0
    ANS 2.0

    or use np.linalg.solve(Left, Right)

    $ cat matrix | python pymatcalc.py 'ANS = np.linalg.solve(L, R)'
    L 1 1
    L 2 4
    R 9
    R 22
    ANS 7.0
    ANS 2.0

    """
    parser = argparse.ArgumentParser(description=help_desc_msg,
                    epilog=help_epi_msg,
                    formatter_class=argparse.RawDescriptionHelpFormatter)
    #parser = argparse.ArgumentParser(description='calc matrix using numpy')
    #parser.print_help()
    parser.add_argument("formula", help="numpy formula", type=str)
    parser.add_argument("-i", "--inputfile", help="input file name", type=str)
    parser.add_argument("-q", "--quiet", help="print as it is", action="store_true")
    parser.add_argument("-t", "--dtype", help="array data type", default='float', type=str)
    parser.add_argument("-d", "--delimiter", help="line separator(delimiter)", default=r' ',
        choices=[r" ", r",", r"\t"])
    parser.add_argument("-V", "--version", help="version", action="version", version=_version)
    args = parser.parse_args()
    return(args)

def print_matrix(key, mat):
    if mat.ndim == 2:
        matlist = []
        for i in range(mat.shape[0]):
            matlist.append(key)
            for j in range(mat.shape[1]):
                matlist.append(mat[i][j])
            ## print liststr
            mapped_list = map(str, matlist)
            liststr = args.delimiter.join(mapped_list)
            print(liststr)
            matlist = []
    if mat.ndim == 1:
        matlist = []
        matlist.append(key)
        for i in range(mat.shape[0]):
            matlist.append(mat[i])
        ## print liststr
        mapped_list = map(str, matlist)
        liststr = args.delimiter.join(mapped_list)
        print(liststr)

def open_file(mode = 'r'):
    if args.inputfile:
        filename = re.sub(r'\\', '/', args.inputfile)
        try:
            readfile = open(filename, mode, encoding="utf-8")
        except:
            raise_error("Could not open file: %s", filename)
    else:
        readfile = sys.stdin
    return readfile

if __name__ == '__main__':
    # get args
    args = get_args()
    tmpformula = args.formula.replace(' ','')
    eqflag = re.search(r'=', tmpformula)
    if eqflag:
        fkey    = re.sub('=.*$', '', tmpformula) 
        formula = re.sub('^.*?=', '', tmpformula) 
    else:
        fkey    = tmpformula
        formula = tmpformula
    #print(fkey, formula, sep=args.delimiter)

    ## read file
    readfile = open_file()

    lineCnt = 0
    outlist = []
    mydict = {}

    for line in readfile:
        lineCnt += 1
        ## print line
        line = line.rstrip('\r\n')
        print(line)
        ## read matrix as np.array
        splitLine = line.split(args.delimiter)
        key = splitLine.pop(0)
        tmplist = splitLine
        if lineCnt == 1:
            mydict.setdefault(key, key)
            outlist.append(tmplist)
            lastkey = key
        else:
            if key in mydict:
                outlist.append(tmplist)
            else:
                ## set np.array
                execformula = str(mydict[lastkey])
                execformula += " = np.array(outlist, dtype=" + args.dtype + ")"
                #print(execformula)
                exec(execformula)
                outlist = []
                outlist.append(tmplist)
                mydict.setdefault(key, key)
                lastkey = key
    ## set np.array
    execformula = str(mydict[lastkey])
    execformula += " = np.array(outlist, dtype=" + args.dtype + ")"
    #print(execformula)
    exec(execformula)

    ## execute formula and print answer
    ans = eval(formula)
    if args.quiet:
        pass
        #print(ans)
    else:
        print_matrix(fkey, ans)

    sys.exit(0)

