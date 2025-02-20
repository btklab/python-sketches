#!/usr/bin/env python3
#coding: utf-8

#
# pycalc - python one-liner
#

import io, sys, os
import re
import argparse
import datetime
import numpy as np
import pandas as pd
import unicodedata

_version = "Mon Jun 1 16:48:17 JST 2024"
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
    help_desc_msg ="""pycalc.py -- python oneliner

    pycalc.py <formula;formura;...>
    cat iris.csv | pycalc.py -d "," "df.describe()"

    標準入力を df=pd.read_csv(sys.stdin, sep=delimiter)にて読み込む
    -i <file>でファイル入力も可能

    <formula>はセミコロン区切りで複数指定可能
    formulaに"="が含まれておればexec(formula),
    含まれないならans=eval(formula)が実行される
    ただし、()の中だけにイコールがある場合はevalになる。
    たとえば"df.describe(include='all')"はeval

    -v '<val1>=<str>;<val2>=<str>;...'で変数に代入できる

    デフォルトでimportするモジュール: io, sys, os, re, datetime
    デフォルトでimportするモジュール: numpy, pandas


    """
    help_epi_msg = """EXAMPLES:
    ## describe
    cat iris.ssv | python pycalc.py "df.dtypes"
    cat iris.ssv | python pycalc.py "df.describe()"
    cat iris.ssv | python pycalc.py "df.describe()" --nowrap
    cat iris.ssv | python pycalc.py "df[df.columns[0:2]].describe()"

    ## parse date examples
    cat date.txt | python pycalc.py "df" --datetime
    cat date.txt | python pycalc.py "df['date']=pd.to_datetime(df['date']);df['date2']=pd.to_datetime(df['date2']);df['diff']=df['date']-df['date2'];df.dropna()"
    cat date.txt | python pycalc.py "df['date']=pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d.%a');df"
    cat date.txt | python pycalc.py "df['date']=pd.to_datetime(df['date']);df['timedelta_row']=df['date'].diff();df"
    cat date.txt | python pycalc.py "df['date']=pd.to_datetime(df['date']);df['adddate']=df['date']+datetime.timedelta(days=31);df"
    cat date.txt | python pycalc.py "df['date']=pd.to_datetime(df['date']);df['adddate']=df['date']-datetime.datetime.now();df"
    cat date.txt | python pycalc.py "df['date']=pd.to_datetime(df['date']);df['add_date']=df['date']+pd.to_timedelta(df['val'], unit='d');df"

    ## normalise using str.unicodedata.normalize('NKFC')
    cat date.txt | python pycalc.py "df" --normalize
    cat date.txt | python pycalc.py "df=df.applymap(lambda x: unicodedata.normalize('NFKC',x));df"
    cat date.txt | python pycalc.py "df['ten']=df['ten'].str.normalize('NFKC');df"
    cat date.txt | python pycalc.py "df['extract']=df['ten'].str.extract('(?P<city>新橋|日本橋)').dropna();df"
    cat date.txt | python pycalc.py "df['address'] = df['address'].str.replace('〒[0-9]{3}\-[0-9]{4}', '')"

    ## use apply
    cat date.txt | python pycalc.py "df['len']=df['ten'].apply(len);df"
    cat date.txt | python pycalc.py "df['len']=df['ten'].apply(lambda x: len(x));df"


    ## output csv
    cat iris.ssv | python pycalc.py -d " " "df.describe().to_csv()" | grep .

    ## fillna and output csv
    cat iris.csv | python pycalc.py -d "," "df.fillna('NaN').to_csv()" | grep .

    ## rename column name and print df
    cat iris.csv | python pycalc.py -d "," "df.columns=['sl','sw','pl','pw','species']; df.head()"
    cat iris.csv | python pycalc.py -d "," "df.columns=['sl','sw','pl','pw','species']; df.groupby('species').size()"
    cat iris.csv | python pycalc.py -d "," "df.columns=['sl','sw','pl','pw','species']; df.groupby('species').mean()"
    cat iris.csv | python pycalc.py -d "," "df.columns=['sl','sw','pl','pw','species']; a=df.groupby('species'); a.sum()"
    cat iris.csv | python pycalc.py -d "," "df.columns=['sl','sw','pl','pw','species']; a=df.groupby('species'); a.std()"
    cat iris.csv | python pycalc.py -d "," "df.columns=['sl','sw','pl','pw','species']; a=df.groupby('species'); a.var()"

    ## groupby and aggregate
    cat iris.csv | python pycalc.py -d "," "df.columns=['sl','sw','pl','pw','species']; df.groupby('species').agg('mean')"
    cat iris.csv | python pycalc.py -d "," "df.columns=['sl','sw','pl','pw','species']; df.groupby('species').agg(lambda x: max(x) - min(x))"
    cat iris.csv | python pycalc.py -d "," "df.columns=['sl','sw','pl','pw','species']; df.groupby('species').agg({'sl':'mean', 'sw':max, 'pl':np.min, 'pw':np.min})"

    cat iris.csv | python pycalc.py -d "," "df.columns=['sl','sw','pl','pw','species']; df.groupby('species').describe()['sl']"
    ## describe & include
    cat iris.ssv | python pycalc.py "df.describe(include='all')"
    cat iris.ssv | python pycalc.py "df.describe(include='object')"
    cat iris.ssv | python pycalc.py "df.describe(include=[np.object, np.number])"

    ## describe & exclude
    cat iris.ssv | python pycalc.py "df.describe(exclude=np.number)"
    cat iris.ssv | python pycalc.py "df.describe(exclude=np.number).to_csv()" | grep .

    ## describe & percentiles
    cat iris.ssv | python pycalc.py "df.describe(percentiles=[0.1,0.2,0.5])" # 10%,20%,50%
    
    ## 「species」列のカテゴリごとに要約統計量を出力
    1..4 | %{ cat iris.csv | self $_ NF `
        | python pycalc.py "df.groupby('species').describe()" --nowrap -d "," }

    cat iris.csv | python pycalc.py "df[df.columns[:]].groupby('species').describe()" -d "," --nowrap

    === 変数の活用 ===
    echo 1 | python pycalc.py 's,t' -v 's=[i for i in range(6)];t=[i**2 for i in s]'
    ([0, 1, 2, 3, 4, 5], [0, 1, 4, 9, 16, 25])

    === Matplotlibを用いたグラフ描画 ===
    ## formulaに"plot"または"plt"をみつけるとimport matplotlib as pltを読み込む
    cat iris.csv | python pycalc.py -d "," "ax=df.groupby('species').max().plot.bar(rot=0);plt.show()"

    echo 1 | python pycalc.py 'plt.plot(s,t);plt.show()' -v 's=[i for i in range(6)];t=[i**2 for i in s]'
    [<matplotlib.lines.Line2D object at 0x7f96395f19a0>]
    # 式をセミコロンで区切ると複数の式を記述できる

    === create dataframe ===
    echo 1 | python pycalc.py "df=pd.DataFrame({'city': ['osaka', 'osaka', 'osaka', 'osaka', 'tokyo', 'tokyo', 'tokyo'],'food': ['apple', 'orange', 'banana', 'banana', 'apple', 'apple', 'banana'],'price': [100, 200, 250, 300, 150, 200, 400],'quantity': [1, 2, 3, 4, 5, 6, 7]});df"
    echo 1 | python pycalc.py "df=...; df.groupby('city').mean()"
    echo 1 | python pycalc.py "df=...; df.groupby('city').mean().T"
    echo 1 | python pycalc.py "df=...; df.groupby('city').size()"
    echo 1 | python pycalc.py "df=...; df.groupby('city').size()['osaka']"

    echo 1 | python pycalc.py "df=...; df.groupby(['city','food']).mean()"
    echo 1 | python pycalc.py "df=...; df.groupby(['city','food'],as_index=False).mean()"

    echo 1 | python pycalc.py "df=...; df.groupby('city').agg(np.mean)"
    echo 1 | python pycalc.py "df=...; df.groupby('city').agg({'price': np.mean, 'quantity': np.sum})"

    === query ===
    cat iris.csv | python pycalc.py -d "," "df.columns=['sl','sw','pl','pw','species'];df.query('sl < 5.0' )"
    cat iris.csv | python pycalc.py -d "," "df.columns=['sl','sw','pl','pw','species'];df.query('4.9 <= sl < 5.0' )"
    cat iris.csv | python pycalc.py -d "," "df.columns=['sl','sw','pl','pw','species'];df.query('sl > sw / 3' )"
    cat iris.csv | python pycalc.py -d "," "df.columns=['sl','sw','pl','pw','species'];df.query('species == \'setosa\'')"
    cat iris.csv | python pycalc.py -d "," "df.columns=['sl','sw','pl','pw','species'];df.query('species in [\'setosa\']')"

    cat iris.csv | python pycalc.py -d "," "df.columns=['sl','sw','pl','pw','species'];df.query('index % 2 == 0')"

    cat iris.csv | python pycalc.py -d "," "df.columns=['sl','sw','pl','pw','species'];df.query('sl > 5.0 & sw < 2.5')"
    cat iris.csv | python pycalc.py -d "," "df.columns=['sl','sw','pl','pw','species'];df.query('sl > 5.0 and sw < 2.5')"

    === solve simultaneous equations ===
    echo 1 | python pycalc.py 'L=[[3/4,5/2], [-2,1]];R=[-6,-7];np.linalg.solve(L, R)'
    [ 2. -3.]
    """
    parser = argparse.ArgumentParser(description=help_desc_msg,
                    epilog=help_epi_msg,
                    formatter_class=argparse.RawDescriptionHelpFormatter)
    tp = lambda x:list(map(str, x.split(',')))
    sp = lambda x:list(map(str, x.split(';')))
    parser.add_argument("formula", help="python script", type=str)
    parser.add_argument("-i", "--inputfile", help="input file name", type=str)
    parser.add_argument("-d", "--delimiter", help="line separator(delimiter)", default=r' ',
        choices=[r" ", r",", r"\t"])
    parser.add_argument("-m", "--module", help='import modules', type=tp)
    parser.add_argument("-v", "--variable", help='<variable>=<string>', type=sp)
    parser.add_argument("-n", "--noheader", help="no header", action="store_true")
    parser.add_argument("-q", "--quiet", help="print as it is", action="store_true")
    parser.add_argument("--index", help="col[0] as index", action="store_true")
    parser.add_argument("--datetime", help="set df.columns[0] as datetime", action="store_true")
    parser.add_argument("--nowrap", help="human readable for terminal", action="store_true")
    parser.add_argument("--normalize", help="normalize data using unicodedata.normalize('NFKC')", action="store_true")
    parser.add_argument("--csv", help="output df as csv to stdout", action="store_true")
    parser.add_argument("--tsv", help="output df as tsv to stdout", action="store_true")
    parser.add_argument("--ssv", help="output df as ssv to stdout", action="store_true")
    parser.add_argument("--max_rows", help="max rows", default=None, type=int)
    parser.add_argument("--max_columns", help="max colmnss", default=None, type=int)
    parser.add_argument("--max_colwidth", help="max column width", default=None, type=int)
    parser.add_argument('--size', help='graph size: w inch, h inch', type=tp)
    parser.add_argument("--debug", help="output dataframe", action="store_true")
    #parser.print_help()
    args = parser.parse_args()
    return(args)

def __get_values(vals):
    equations = []
    for val in vals:
        equations.append(str(val).strip())
    return equations

def open_file():
    if args.inputfile:
        readfile = re.sub(r'\\', '/', args.inputfile)
    else:
        readfile = sys.stdin
    return readfile

if __name__ == '__main__':

    # get args
    args = get_args()

    # import matplotlib
    if re.search(r'plot|plt', args.formula):
        import matplotlib.pyplot as plt
        from matplotlib import rcParams
        plt.rcParams['font.family'] = 'sans-serif'
        ## on windows
        if os.name == 'nt':
            plt.rcParams['font.sans-serif'] = ['IPAexGothic', 'BIZ UDGothic', 'MS Gothic', 'Yu Gothic', 'Noto Sans CJK JP']
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

    '''
    This for loop sets variables given by -v options.
    '''
    if args.variable:
        for eq in __get_values(args.variable):
            #token = eq.split("=")
            #locals()[token[0]] = token[1]
            #valStr = str(token[0]).strip() + "=" + str(token[1]).strip()
            valStr = str(eq).strip()
            exec(valStr)

    ## read file
    readfile = open_file()

    # read dataframe
    if args.noheader:
        if args.index:
            df = pd.read_csv(readfile, sep=args.delimiter, index_col=0, header=None)
        elif args.datetime:
            df = pd.read_csv(readfile, sep=args.delimiter, index_col=0, header=None, parse_dates=True)
        else:
            df = pd.read_csv(readfile, sep=args.delimiter, header=None)
    else:
        if args.index:
            df = pd.read_csv(readfile, sep=args.delimiter, index_col=0)
        elif args.datetime:
            df = pd.read_csv(readfile, sep=args.delimiter, index_col=0, parse_dates=True)
        else:
            df = pd.read_csv(readfile, sep=args.delimiter)
    if args.normalize:
        df = df.applymap(lambda x: unicodedata.normalize('NFKC',x))

    ## do not fold output
    if args.nowrap:
        pd.set_option('display.expand_frame_repr', False)
    pd.set_option('display.max_columns', args.max_columns)
    pd.set_option('display.max_rows', args.max_rows)
    pd.option_context('display.max_colwidth', args.max_colwidth)

    ## execute formula and print answer
    #print(args.formula)
    if args.debug:
        print(df)
    elif args.csv:
        df.to_csv(sys.stdout, index=True, sep=",")
    elif args.tsv:
        df.to_csv(sys.stdout, index=True, sep=r"\t")
    elif args.ssv:
        df.to_csv(sys.stdout, index=True, sep=" ")
    else:
        fmls = str(args.formula).split(";")
        for fml in fmls:
            fml = str(fml).strip()
            # if formula(tml) contains "=", run exec, otherwise run eval
            if re.search(r'^([^\(]+)=', fml):
                exec(fml)
            else:
                ans = eval(fml)
                if args.quiet:
                    pass
                else:
                    print(ans)

    sys.exit(0)

