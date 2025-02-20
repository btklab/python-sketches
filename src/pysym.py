#!/usr/bin/env python3
#coding: utf-8

#
# pysym.py - sympy oneliner
#

import io, sys, os
import re
import argparse
import math
import numpy as np
#import pandas as pd
import sympy
from sympy import sin, cos, tan, atan, log, I, pi, E, exp, sqrt
from sympy import symbols
from sympy import Eq, solve, diff, integrate, factorial, factor, summation
from sympy import Matrix, plot 
from sympy.printing.dot import dotprint
#from sympy.abc import x

_version = "Wed 01 Mar 2023 21:55:00 JST"
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
    help_desc_msg ="""pysym.py -- sympy oneliner using exec

    Usage: 
        pysym.py 'x**2 - 2*x - 15' [--latex|--simplify|--dot] [--sympify]
        pysym.py 'sympy.factor(x**2 - 2*x - 15)' [--latex|--simplify|--dot] [--sympify]
        -> 数式をsympyが解釈して出力。--latexでlatex数式変換
        -> --sympifyで数式を文字列として渡す。ただし数式中に=がある場合はうまく動作しない

    Option:
        -v '<val1>=<str>;<val2>=<str>;...' 変数の宣言と代入

    Default settings:
        sympy.init_printing(use_unicode=True)
        x, y, z = sympy.symbols('x y z')
        a, b, c = sympy.symbols('a b c')

        import sympy
        from sympy import symbols
        from sympy import Eq, solve, diff, integrate, factorial, factor, summation
        from sympy import sin, cos, tan, atan, log, I, pi, E, exp, sqrt
        from sympy import Matrix, plot
        from sympy.printing.dot import dotprint
        import io, sys, os, re
        import numpy as np
        import math
        import matplotlib.pyplot as plt
    """
    help_epi_msg = """EXAMPLES:

    === 電卓として使う ===
    pysym.py '1+2'
    # 電卓として使う: 3

    pysym.py '1.2e2'
    # 電卓として使う: 120.0

    pysym.py 'sympy.factorial(10)'
    # 電卓として使う: 3628800

    pysym.py "sympy.expand('(x+y)*(x-y)')"
    # 多項式の展開: x**2 - y**2

    pysym.py 'type(1.2e2)'
    # pythonコマンドの実行: <class 'float'>
    # 内部でevalを用いているので、こういうことができる


    === 数式の演算・シンプル化・LaTeX形式変換 ===

    pysym.py 'x**2 + 2*x + 1'
    # 数式表示: x**2 + 2*x + 1

    pysym.py 'x**2 + 2*x + 1' --latex (-l)
    # latex変換: x^{2} + 2 x + 1

    pysym.py '(x**2 + 2*x + 1).subs(x,1)'
    # 値の代入: 4

    pysym.py '(x**2 + 2*x + 1 + y**2).subs([(x,1),(y,2)])'
    # 複数の値の代入はタプルを用いる: 8

    === LaTeX形式の式と代入結果の同時出力 ===

    python pysym.py '(x**2 + 2*x + 1 + y**2).subs([(x,1),(y,2)])' --eq
    \begin{align}
    x^{2} + 2 x + y^{2} + 1 &= 8 \\
    \end{align}

    === 変数オプション-vを活用する ===

    pysym.py 'x**2 + 2*x + 1 + X*Y' -v "X,Y=sympy.symbols('X Y')"
    # 記号の追加は-vオプションでできる: X*Y + x**2 + 2*x + 1

    pysym.py 'x**2 + 2*x + 1 + X*Y*Z' -v "X, Y=sympy.symbols('X Y');Z=sympy.symbols('Z')"
    # -vオプションはセミコロン;区切りで複数指定可能: X*Y*Z + x**2 + 2*x + 1

    pysym.py 'f(x)' -v 'def f(x): return x**2'
    # python式に関数定義: x**2

    pysym.py 'sympy.solve(sympy.Eq(f(x), g(x)), x)' -v 'def f(x): return x**2 - 1; def g(x): return 4*x - 5'
    # y = x**2 -1 と y = 4*x - 5 が交差または接している点の x 座標: [2]
    ↓
    # 解が一つなので1点で接している。その座標は？
    pysym.py '2,f(2)' -v 'def f(x): return x**2 - 1; def g(x): return 4*x - 5;'
    # (2, 3)
    ↓
    # 接線の傾き
    pysym.py 'sympy.diff(f(x), x).subs(x, 2)' -v 'def f(x): return x**2 - 1; def g(x): return 4*x - 5;'
    # 4

    # 2次方程式の解の公式
    pysym.py 'sympy.Eq(a*x**2+b*x+c, (-b + sympy.sqrt(-4*a*c + b**2))/(2*a))' --latex
    # normal: Eq(a*x**2 + b*x + c, (-b + sqrt(-4*a*c + b**2))/(2*a))
    # latex:  a x^{2} + b x + c = \frac{- b + \sqrt{- 4 a c + b^{2}}}{2 a}


    === いろいろな演算 ===

    pysym.py 'sympy.solve([3*x + 5*y -29, x + y - 7])'
    # 連立方程式を解く: {x: 3, y: 4}

    pysym.py 'sympy.summation(k, (k, 1, 10) )' -v "k=sympy.symbols('k', integer = True)"
    # 総和を求める: 55

    pysym.py 'sympy.factor(sympy.summation(k, (k, 1, N) ))' -v "k, N=sympy.symbols('k N', integer = True)"
    # 総和。上限を文字にしてもいい: N*(N + 1)/2

    pysym.py 'f(x)' -v 'def f(x): return x**2'
    # python式に関数定義: x**2

    pysym.py 'sympy.factor(x**2 + 2*x + 1)'
    # 因数分解: (x + 1)**2

    pysym.py 'sympy.diff(x**2 - 2*x - 15)'
    # 微分: 2*x - 2

    pysym.py 'sympy.integrate(x**2 - 2*x - 15)'
    # 積分: x**3/3 - x**2 - 15*x

    pysym.py 'sympy.integrate(x**2 - 2*x - 15, (x, 0, 10))'
    # 定積分: 250/3

    pysym.py 'sympy.solve([x + 5*y - 2, -3*x + 6*y - 15], [x, y])'
    # 方程式の求解: {x: -3, y: 1}

    ## calc matrix: 行列の演算
    ## thanks: https://atatat.hatenablog.com/entry/sympy10_matrix

    pysym.py 'sympy.Matrix([[a, b], [c, d]])' -v 'a,b,c=sympy.symbols("a b c"); d,e,f=sympy.symbols("d e f")'
    # 行列の定義: Matrix([[a, b], [c, d]])

    pysym.py 'sympy.Matrix([x, y])'
    # 列ベクトルの定義: Matrix([[x], [y]])

    pysym.py 'sympy.Matrix([[x, y]])'
    # 行ベクトルの定義: Matrix([[x, y]])

    pysym.py 'A*B' -v 'd=sympy.symbols("d");A=sympy.Matrix([[a, b], [c, d]]);B=sympy.Matrix([x, y])'
    # Matrix([[a*x + b*y], [c*x + d*y]])

    pysym.py 'A+B' -v 'A=sympy.Matrix([[1,2], [3,4]]);B=sympy.Matrix([[3, 4],[5,6]])'
    # 行列の和: Matrix([[4, 6], [8, 10]])

    pysym.py 'A.shape' -v 'd=sympy.symbols("d");A=sympy.Matrix([[a, b], [c, d]])'
    # 行列の数を取得: (2, 2)

    pysym.py 'A.row(0)' -v 'd=sympy.symbols("d");A=sympy.Matrix([[a, b], [c, d]])'
    # 行列の成分を取得: Matrix([[a, b]])

    pysym.py 'A.col(1)' -v 'd=sympy.symbols("d");A=sympy.Matrix([[a, b], [c, d]])'
    # 行列の成分を取得: Matrix([[b], [d]])

    pysym.py 'A.transpose()' -v 'd=sympy.symbols("d");A=sympy.Matrix([[a, b], [c, d]])'
    # 行列の転置: Matrix([[a, c], [b, d]])

    pysym.py 'A.det()' -v 'd=sympy.symbols("d");A=sympy.Matrix([[a, b], [c, d]])'
    # 行列式（determinant）: a*d - b*c

    pysym.py 'A.inv()' -v 'd=sympy.symbols("d");A=sympy.Matrix([[a, b], [c, d]])'
    pysym.py 'A**(-1)' -v 'd=sympy.symbols("d");A=sympy.Matrix([[a, b], [c, d]])'
    # 逆行列: Matrix([[d/(a*d - b*c), -b/(a*d - b*c)], [-c/(a*d - b*c), a/(a*d - b*c)]])

    pysym.py 'A.eigenvals()' -v 'd=sympy.symbols("d");A=sympy.Matrix([[a, b], [c, d]])'
    # 固有値: {a/2 + d/2 - sqrt(a**2 - 2*a*d + 4*b*c + d**2)/2: 1, a/2 + d/2 + sqrt(a**2 - 2*a*d + 4*b*c + d**2)/2: 1}

    pysym.py 'A.eigenvects()' -v 'd=sympy.symbols("d");A=sympy.Matrix([[a, b], [c, d]])'
    # 固有ベクトル:
    # [(a/2 + d/2 - sqrt(a**2 - 2*a*d + 4*b*c + d**2)/2, 1, [Matrix([
    # [-d/c + (a/2 + d/2 - sqrt(a**2 - 2*a*d + 4*b*c + d**2)/2)/c],
    # [                                                         1]])]), (a/2 + d/2 + sqrt(a**2 - 2*a*d + 4*b*c + d**2)/2, 1, [Matrix([
    # [-d/c + (a/2 + d/2 + sqrt(a**2 - 2*a*d + 4*b*c + d**2)/2)/c],
    # [                                                         1]])])]

    pysym.py 'A.rref()' -v 'd=sympy.symbols("d");A=sympy.Matrix([[5, -2, 5], [1, 1, 8]])'
    # 階段行列:
    # (Matrix([
    # [1, 0, 3],
    # [0, 1, 5]]), (0, 1))


    === Matplotlibを用いたplot（グラフ描画） ===

    pysym.py "sympy.plot(sin(x), (x, -2*pi, 2*pi))"
    pysym.py "sympy.plot(sin(x), (x, -2*pi, 2*pi), title='タイトル', xlabel='横軸')"
    # サインカーブ

    pysym.py 'plt.plot(s,t);plt.show()' -v 's=[i for i in range(6)];t=[i**2 for i in s]'
    [<matplotlib.lines.Line2D object at 0x7fe4c0a20670>]
    # plt.show()

    pysym.py 'sympy.plot_parametric(cos(x), sin(x), (x, 0, 2*pi))' --size 5,5
    # グラフサイズの指定


"""
    parser = argparse.ArgumentParser(description=help_desc_msg,
                    epilog=help_epi_msg,
                    formatter_class=argparse.RawDescriptionHelpFormatter)
    tp = lambda x:list(map(str, x.split(',')))
    sp = lambda x:list(map(str, x.split(';')))
    parser.add_argument("formula", help="python script", type=str)
    parser.add_argument("-l", "--latex", help="output latex formula", action="store_true")
    parser.add_argument("-u", "--unicode", help="use unicode print", action="store_true")
    parser.add_argument("-s", "--simplify", help="simplify", action="store_true")
    parser.add_argument("--sympify", help="sympify", action="store_true")
    parser.add_argument("--dot", help="output dot file format", action="store_true")
    parser.add_argument("--eq", help="output formula = answer", action="store_true")
    parser.add_argument("-d", "--delimiter", help="line separator(delimiter)", default=r' ',
        choices=[r" ", r",", r"\t"])
    parser.add_argument("-m", "--module", help='<modules>,...', type=tp)
    parser.add_argument("-v", "--variable", help='<variable>=<string>;...', type=sp)
    parser.add_argument("-i", "--inputfile", help='input from data file', type=str)
    parser.add_argument('--size', help='graph size: w inch, h inch', type=tp)
    parser.add_argument("--debug", help="output dataframe", action="store_true")
    #parser.print_help()
    args = parser.parse_args()
    return(args)

def open_file():
    if args.inputfile == "-":
        readfile = sys.stdin
    else:
        readfile = re.sub(r'\\', '/', args.inputfile)
    return readfile

def __get_values(vals):
    equations = []
    for val in vals:
        equations.append(str(val).strip())
    return equations

def output(ans, simplify=False, latex=False):
    if latex is True:
        if simplify is True:
            print(sympy.latex(sympy.simplify(ans)))
        else:
            print(sympy.latex(ans))
    else:
        if simplify is True:
            print(sympy.simplify(ans))
        else:
            print(ans)

def rad2deg(x):
    return float(x * 180/pi)

if __name__ == '__main__':

    # get args
    args = get_args()

    # import matplotlib
    if re.search(r'plot|plt', args.formula):
        import matplotlib.pyplot as plt
        from matplotlib import rcParams
        rcParams['font.family'] = 'sans-serif'
        rcParams['font.sans-serif'] = ['IPAexGothic','MS Gothic', 'Yu Gothic']
        plt.rcParams['pdf.fonttype'] = 42
        plt.rcParams['ps.fonttype'] = 42
        ## set figure size
        if args.size:
            if len(args.size) == 1:
                w_inch = args.size[0]
                h_inch = args.size[0]
            else:
                w_inch = args.size[0]
                h_inch = args.size[1]
            plt.rcParams['figure.figsize'] = (w_inch, h_inch)
            debStr = "plt.rcParams['figure.figsize'] = ({}, {})".format(w_inch, h_inch)
            if args.debug: print(debStr)

    # import modules
    if args.module:
        for mod in args.module:
            try:
                #mod = re.search(r'\'[^\']+\'', str(mod)).strip("'")
                if re.search(r'^import|^from', mod):
                    ## as is module str
                    exec(mod, globals())
                else:
                    ## if module name only
                    exec('import ' + mod, globals())
            except NameError:
                raise_error("Module Name Error")

    ## sympy settings
    sympy.init_printing(use_unicode=args.unicode)
    x, y, z = sympy.symbols('x y z')
    a, b, c = sympy.symbols('a b c')
    #if args.sympify:
    #    set_sympify = re.compile(r' *= *(.*)$')

    #This for loop sets variables given by -v options.
    if args.variable:
        for eq in __get_values(args.variable):
            #token = eq.split("=")
            #locals()[token[0]] = token[1]
            #valStr = str(token[0]).strip() + "=" + str(token[1]).strip()
            valStr = str(eq).strip()
            exec(valStr)

    # read data
    if args.inputfile:
        readfile = open_file()
        data = np.loadtxt(readfile, delimiter=args.delimiter)
        print(data)

    ## set formula
    fmls = str(args.formula).split(";")
    for fml in fmls:
        ans = str(fml).strip()
        if args.sympify:
            ans = "sympy.sympify('" + ans + "')"
        ans = eval(ans)
        ## output
        if args.dot:
            print(dotprint(sympy.simplify(ans)))
        else:
            if args.eq:
                fm = re.sub(r'\.subs.*$', r'', fml)
                su = re.sub(r'^.*\.subs\((..*)\).*$', r'\1', fml)
                if args.sympify:
                    fm = "sympy.sympify('" + fm + "')"
                fm = eval(fm)
                ofm = sympy.latex(fm)
                oline = ofm + r" &= " + str(ans)
                #print(su)
                print(r"\begin{align}")
                print(oline + r" \\")
                print(r"\end{align}")
            else:
                output(ans, simplify=args.simplify, latex=args.latex)

    sys.exit(0)

