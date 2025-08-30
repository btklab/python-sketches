#!/usr/bin/env python3
#coding: utf-8

#
# pyplot - plot using matplotlib
#

import io, sys, os
import re
import argparse
import numpy as np
import pandas as pd
import datetime
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
## --> font <--
#del matplotlib.font_manager.weight_dict['roman']
#matplotlib.font_manager._rebuild()
plt.rcParams['font.family'] = 'sans-serif'
## switch stdio by platform
if os.name == 'nt':
    ## on windows
    plt.rcParams['font.sans-serif'] = ['IPAexGothic', 'BIZ UDGothic', 'MS Gothic', 'Yu Gothic', 'Noto Sans CJK JP']
elif os.name == 'posix':
    ## on linux
    plt.rcParams['font.sans-serif'] = ['IPAexGothic', 'Noto Sans CJK JP']
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype']  = 42
#plt.rcParams['font.family'] = 'Times New Roman' #全体のフォントを設定
#plt.rcParams["mathtext.fontset"] = "stix"
#plt.rcParams["font.size"] = 10
## --> ticks <--
plt.rcParams['xtick.direction'] = 'in' # x axis in
plt.rcParams['ytick.direction'] = 'in' # y axis in
plt.rcParams['axes.linewidth']  = 1.0 # axis line width
#plt.rcParams['axes.grid'] = True # make grid
## --> legend <--
plt.rcParams["legend.fancybox"] = False # 丸角
#plt.rcParams["legend.framealpha"] = 1 # 透明度の指定、0で塗りつぶしなし
plt.rcParams["legend.edgecolor"] = 'black' # edgeの色を変更
#plt.rcParams["legend.handlelength"]  = 1  # 凡例の線の長さを調節
#plt.rcParams["legend.labelspacing"]  = 5. # 垂直方向（縦）の距離の各凡例の距離
#plt.rcParams["legend.handletextpad"] = 3. # 凡例の線と文字の距離の長さ
#plt.rcParams["legend.markerscale"]   = 2  # 点がある場合のmarker scale

_version = "Thu Jan 12 04:22:40 JST 2023"
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

def date_type(date_str):
    # str -> date 型変換関数
    try:
        return datetime.date.fromisoformat(date_str)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e) + " Date must be in ISO format. ex. 2020-01-01")

def date_type2(date_str):
    try:
        #return datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(date_str)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e) + " DateTime format ex. 2020-01-01 10:20:30")

def get_args():
    help_desc_msg = r"""pyplot -- data visualization using matplotlib

    default behavior is to read data form stdin
    if set -i option, read data from file

    In the Linux(Ubuntu) environment, if you want to use Japanese fonts for column name or title, install the fonts in advance.

    bash
    $ sudo apt install fonts-ipaexfont

    pandasのplotを使用せずにplotする。
    微修正や拡張がよりしやすいはず。

    列指定は1始まりとする
    dtype == 'object'となる列はスキップされる
    この挙動を抑制する場合は--notskipobjectスイッチを指定する
    pyplotとの違いは、pandasのdf.plotを使わない点
    (pandasのdataframe自体は使う。)

    垂線を引く: カンマ区切りで値やISO形式の日付を指定
        --vline 10,20,30
        --datetime --vline 2019-08-01,2020-02-01

    --datetimeスイッチで、1列目を日付形式のインデックスとみなす。
    このスイッチを指定した場合、追加で以下のオプションを使用できる：
        --dformat "%Y-%m`n(%a)"
            --yinterval <int>: year interval
            --minterval <int>: month interval
            --dinterval <int>: day interval
            --winterval <int>: weekday interval
    #    --dformat '%Y-%m-%d\\n%H-%M-%S(%a)'
    #    --datetimelocate 'year','month','day','hour','minute','auto','monday','tuesday','wednesday','thursday','friday','saturday','sunday'
    #    --datetimeinterval

    --y2 スイッチで最右列がY2軸でライン、その他はY1軸でBarになる。
    """
    help_epi_msg = r"""EXAMPLES:
    cat iris.csv | python pyplot.py -d ","
    cat iris.csv | python pyplot.py -d "," --index
    cat date.csv | python pyplot.py -d "," --datetime --minterval 2 --rot 90 --dformat "%Y-%m`n(%a)"
    cat iris.csv | python pyplot.py -d "," --sorta 1,2
    cat iris.csv | python pyplot.py -d "," --pair --hue 5
    cat iris.csv | python pyplot.py -d "," --pair --hue 5 --seaborn
    cat iris.csv | python pyplot.py -d "," --scatter --x 1 --y 3
    cat iris.csv | python pyplot.py -d "," --scatter --x 1 --y 3 --hue 5
      -> 層別（分類別）に色分けした散布図を描画。
    cat iris.csv | python pyplot.py -d "," --scatter --x 1 --y 3 --lm
      -> 散布図に最小二乗法を適用し回帰直線をプロット。同時に線形回帰式及びR^2値を凡例に表示
    cat iris.csv | self 1 | python pyplot.py -d "," --xrs 1
      -> 1列目のデータを用いてX-Rs線を引く

    ## fill range
    cat iris.csv | python pyplot.py -d ","  --vspan 60,80 --vspancolor gray

    cat iris.csv | python pyplot.py -d "," --hist --subplots --layout 2,2
    python pyplot.py -i iris.csv -d ","
    python pyplot.py -i iris.csv -d "," --spines "zero"
        -> グラフ交点ticksをy=0にセット。 --spines "center"で交点を中央にセット。
    python pyplot.py -i iris.csv -d "," --monochrome
    python pyplot.py -i iris.csv -d ',' --y2 --y2color "tab:red"

    ## 水平線を引く
    python pyplot.py -i iris.csv -d ',' --hline 1.3
    python pyplot.py -i iris.csv -d ',' --hline 3.0,2.0 --hlinecolor r,g
      -> 水平線を引く。カンマ区切りで複数引けるが、その際は
         hline, hlinecolorの引数の数を一致させる必要がある、
         vlineも同じ。

    cat datetime.txt | python pyplot.py --datetime
    cat datetime.txt | python pyplot.py --datetime --datetimelocate sunday --dformat '%H-%M\\n(%a)' --rot 45 --grid
    cat datetime.txt | python pyplot.py --datetime --datetimelocate day --datetimeinterval 5

    ## legend locate
    cat iris.csv | python pyplot.py --legendloc2 1,1,1 ## 凡例を外に。
    """
    parser = argparse.ArgumentParser(description=help_desc_msg,
                    epilog=help_epi_msg,
                    formatter_class=argparse.RawDescriptionHelpFormatter)
    tp = lambda x:list(map(int,   x.split(',')))
    tf = lambda x:list(map(float, x.split(',')))
    ts = lambda x:list(map(str  , x.split(',')))
    td = lambda x:list(map(date_type, x.split(',')))
    td2 = lambda x:list(map(date_type2, x.split(',')))

    parser.add_argument('-d', '--delimiter', help='line separator(delimiter)', default=r' ',
        choices=[r' ', r',', r'\t'], type=str)
    parser.add_argument("-o", "--output", help="output file name", type=str)
    parser.add_argument("-i", "--inputfile", help="input file name", type=str)
    parser.add_argument('--dpi', help='output dpi', default=100, type=int)
    parser.add_argument('--x', help="x columns in scatter plot", default=1, type=int)
    parser.add_argument('--y', help="y columns in scatter plot", default=2, type=int)
    parser.add_argument('--size', help='w inch, h inch', type=tp)
    parser.add_argument('--layout', help='subplot layout', type=tp)
    parser.add_argument('--fontsize', help="fontsize", type=float)
    parser.add_argument('--fontsizet', help="title fontsize", default=14, type=float)

    parser.add_argument('--anzu', help="font: anzu", action="store_true")
    parser.add_argument('--natsume', help="font: natsume", action="store_true")
    parser.add_argument('--natsumeo', help="font: natsume osae", action="store_true")
    parser.add_argument('--nofont', help="do not set font", action="store_true")

    parser.add_argument('--self', help='select fields', type=tp)
    parser.add_argument('--delf', help='delete fields', type=tp)
    parser.add_argument('--sorta', help='sort by ascending', type=tp)
    parser.add_argument('--sortd', help='sort by descending', type=tp)
    parser.add_argument("--noheader", help="noheader data", action="store_true")
    parser.add_argument("--notskipobject", help="do not skip object dtype", action="store_true")
    parser.add_argument("--index", help="set df.columns[0] as index", action="store_true")
    parser.add_argument("--datetime", help="set df.columns[0] as datetime", action="store_true")

    parser.add_argument("--dformat", help="xaxis datetime formatter", type=str)
    parser.add_argument("--yinterval", help="year interval", type=int)
    parser.add_argument("--minterval", help="month interval", type=int)
    parser.add_argument("--dinterval", help="day interval", type=int)
    parser.add_argument("--winterval", help="weekday interval", type=int)
    parser.add_argument("--datetimelocate", help="xaxis datetime locater",
        choices=['year','month','day','hour','minute','auto',
        'monday','tuesday','wednesday','thursday','friday','saturday','sunday'], type=str)
    parser.add_argument('--datetimeinterval', help='xaxis date interval', default=1, type=int)
    #loclist = lambda x:list(map(int, x.split(',')))
    #parser.add_argument('--datetimeintervalrange', help='xaxis date interval by range (ex. 0,24,4)', type=loclist)
    parser.add_argument("--mtype", help="marker type", type=str)

    parser.add_argument("--scatter", help="graph type: scatter", action="store_true")
    parser.add_argument("--line", help="graph type: line", action="store_true")
    parser.add_argument("--step", help="graph type: line + step", action="store_true")
    parser.add_argument("--bar", help="graph type: bar plot", action="store_true")
    parser.add_argument("--barh", help="graph type: bar plot", action="store_true")
    parser.add_argument("--hist", help="graph type: histogram", action="store_true")
    parser.add_argument("--box", help="graph type: box plot", action="store_true")
    parser.add_argument("--kde", help="graph type: Kernel density estimation", action="store_true")
    parser.add_argument("--area", help="graph type: area", action="store_true")
    parser.add_argument("--pie", help="graph type: pie chart", action="store_true")
    parser.add_argument("--hexbin", help="graph type: hexbin", action="store_true")
    parser.add_argument("--joint", help="graph type: Plotting joint and marginal distributions", action="store_true")
    parser.add_argument("--pair", help="graph type: pair plot", action="store_true")

    parser.add_argument("--style", help="graph style", choices=[
        'bmh','classic','dark_background','fast','fivethirtyeight','ggplot','grayscale',
        'seaborn-bright','seaborn-colorblind','seaborn-dark-palette','seaborn-dark','seaborn-darkgrid',
        'seaborn-deep','seaborn-muted','seaborn-notebook','seaborn-paper','seaborn-pastel',
        'seaborn-poster','seaborn-talk','seaborn-ticks','seaborn-white','seaborn-whitegrid',
        'seaborn','Solarize_Light2','tableau-colorblind10','_classic_test'], type=str)
    parser.add_argument("--lm", help="set least square methods line in scatter plot", action="store_true")
    parser.add_argument('--hue', help="hue label columns", default=-1, type=int)
    parser.add_argument("--offlegend", help="legend switch", action="store_true")
    parser.add_argument("--legendloc", help="legend location", choices=[
        "best","upper right","upper left","lower left","lower right","right",
        "center left","center right","lower center","upper center","center"],
        default="best", type=str)
    parser.add_argument('--legendloc2',  help='legend location', type=tf)
    parser.add_argument('--adjust',  help='space adjust. eg: 0.1,0.8', type=tf)
    parser.add_argument("--title", help="title", default='', type=str)
    parser.add_argument("--offtitle", help="disable scatter plot title", action="store_true")
    parser.add_argument("--spines", help="set spines(ticks location)", choices=[
        'zero','center'], type=str)
    parser.add_argument("--reverse", help="reverse y axis", action="store_true")
    parser.add_argument("--xlab", help="x axis label", type=str)
    parser.add_argument("--ylab", help="y axis label", type=str)
    parser.add_argument("--xlim", help="x axis limit", type=tf)
    parser.add_argument("--ylim", help="y axis limit", type=tf)
    parser.add_argument("--ymin", help="y axis min", type=float)
    parser.add_argument("--ymax", help="y axis max", type=float)
    parser.add_argument("--grid", help="grid", action="store_true")
    parser.add_argument("--gridx", help="grid x-axis", action="store_true")
    parser.add_argument("--gridy", help="grid y-axis", action="store_true")
    #parser.add_argument("--subplots", help="subplots", action="store_true")
    #parser.add_argument("--sharex", help="subplots share x axis", action="store_true")
    #parser.add_argument("--sharey", help="subplots share y axis", action="store_true")
    parser.add_argument("--logx", help="logx", action="store_true")
    parser.add_argument("--logy", help="logy", action="store_true")
    parser.add_argument("--logxy", help="logxy", action="store_true")
    #parser.add_argument("--stacked", help="bar or area stacking", action="store_true")
    parser.add_argument('--rot', help="xlab rotate", default=0, type=int)
    parser.add_argument('--linewidth', help='line width', default=1, type=float)
    parser.add_argument('--hline', help="horizon lines", type=tf)
    parser.add_argument('--hlinewidth', help='horizon line width', default=1, type=float)
    parser.add_argument('--hlinecolor', help="horizon line colors", default='tab:red', type=ts)
    parser.add_argument("--hline0", help="add y zero line", action="store_true")
    parser.add_argument('--vline', help="vertical lines", type=ts)
    #parser.add_argument('--vlined', help="date vertical line. Date must be in ISO format. For example: 2020-01-01.", type=td)
    #parser.add_argument('--vlinedt', help="datetime vertical line. ex: 2020-01-01 00:00:00", type=td2)
    parser.add_argument('--vlinecolor', help="vertical line colors", default='tab:red', type=ts)
    parser.add_argument('--vlinewidth', help='vorizon line width', default=1, type=float)
    parser.add_argument('--hspan', help='fill h-range', type=tf)
    parser.add_argument('--hspancolor', help='fillcolor h-range', default="coral", type=str)
    parser.add_argument('--hspanalpha', help='fillcolor alpha h-range', default=0.5, type=float)
    parser.add_argument('--vspan', help='fill v-range', type=tf)
    parser.add_argument('--vspancolor', help='fillcolor v-range', default="coral", type=str)
    parser.add_argument('--vspanalpha', help='fillcolor alpha v-range', default=0.5, type=float)
    parser.add_argument("--today", help="add today vline", action="store_true")
    parser.add_argument("--now", help="add now datetime vline", action="store_true")
    parser.add_argument("--seaborn", help="pair plot", action="store_true")
    parser.add_argument("--monochrome", help="monochrome line", action="store_true")
    parser.add_argument("--mycolormap", help="my color map", action="store_true")
    parser.add_argument("--debug", help="output dataframe", action="store_true")
    parser.add_argument('--y2', help="secondary y axis columns", action="store_true")
    parser.add_argument("--y2lim", help="y2 axis limit", type=tf)
    parser.add_argument("--logy2", help="logy2", action="store_true")
    parser.add_argument("--y2lab", help="y2 axis label", type=str)
    parser.add_argument("--y2color", help="y2 axis color", default="red", type=str)
    parser.add_argument("--grep", help="bar, barhのみ、ヒットしたラベルのバーに色付けする", type=str)
    parser.add_argument("--gcolor", help="ヒットしたバーの色", default = "tab:red", type=str)
    parser.add_argument("--gcolor2", help="ヒットしなかったバーの色", type=str)
    parser.add_argument('--xrs', help='add x-Rs hline', type=int)
    parser.add_argument('--xkcd', help="xkcd", action="store_true")

    #parser.print_help()
    #parser.add_argument("formula", help="numpy formula", type=str)
    #parser.add_argument("-q", "--quiet", help="print as it is", action="store_true")
    #parser.add_argument("-t", "--dtype", help="array data type", default='float', type=str)
    #parser.add_argument("-V", "--version", help="version", action="version", version=_version)
    args = parser.parse_args()
    return(args)

def open_file():
    if args.inputfile:
        readfile = re.sub(r'\\', '/', args.inputfile)
    else:
        readfile = sys.stdin
    return readfile

def check_self(colnum):
    flg = False
    if args.self:
        for col in args.self:
            if colnum == col - 1:
                flg = True
    else:
        flg = True
    return flg

def check_delf(colnum):
    flg = True
    if args.delf:
        for col in args.delf:
            if colnum == col - 1:
                flg = False
    return flg

if __name__ == '__main__':
    ## get args
    args = get_args()

    if args.seaborn:
        import seaborn as sns

    if args.monochrome:
        from cycler import cycler
        monochrome = (cycler('color', ['k']) *
            #cycler('marker', ['h' ,'2', 'v', '^', 's', '<', '>', '1', '3', '4', '8', 'p', '*', 'H', '+', ',', '.', 'x', 'o', 'D', 'd', '|', '_']) *
            cycler('marker', ['', '.']) *
            cycler('linestyle', ['-', '--', ':', '-.']))
        plt.rc('axes', prop_cycle=monochrome)

    if args.mycolormap:
        ## thanks:
        ##   https://qiita.com/nobolis/items/cb84394fbf0ce26cb1f7
        ##   https://matplotlib.org/examples/color/colormaps_reference.html
        import matplotlib.cm as cm  # グラフに使う色を細かく指定するためのクラス
        colors = [cm.RdBu(0.85), cm.RdBu(0.7), cm.PiYG(0.7), cm.Spectral(0.38), cm.Spectral(0.25)]
        print(colors[0])

    ## apply xkcd
    if args.xkcd:
        plt.xkcd()

    ## font
    ## switch stdio by platform
    if os.name == 'nt':
        ## on windows
        if args.natsume:
            plt.rcParams["font.family"] = "Natsume"
        elif args.natsumeo:
            plt.rcParams["font.family"] = "Natsumemozi-o"
        elif args.anzu:
            plt.rcParams["font.family"] = "apricotJapanesefont"
        elif args.nofont:
            pass
        else:
            plt.rcParams["font.family"] = 'BIZ UDGothic'

    if args.fontsize:
        plt.rcParams['font.size'] = args.fontsize

    ## read file
    readfile = open_file()

    if args.noheader:
        if args.index:
            df = pd.read_csv(readfile, sep=args.delimiter, index_col=0, header=None)
            debStr = "df = pd.read_csv(readfile, sep='{}', index_col=0, header=None)".format(args.delimiter)
        elif args.datetime:
            df = pd.read_csv(readfile, sep=args.delimiter, index_col=0, header=None, parse_dates=False)
            df.index = pd.to_datetime(df.index)
            debStr = "df = pd.read_csv(<readfile>, sep='{}', index_col=0, header=None, parse_dates=True)".format(args.delimiter)
        else:
            df = pd.read_csv(readfile, sep=args.delimiter, header=None)
            debStr = "df = pd.read_csv(<readfile>, sep='{}', header=None)".format(args.delimiter)
    else:
        if args.index:
            df = pd.read_csv(readfile, sep=args.delimiter, index_col=0)
            debStr = "df = pd.read_csv(<readfile>, sep='{}', index_col=0)".format(args.delimiter)
        elif args.datetime:
            df = pd.read_csv(readfile, sep=args.delimiter, index_col=0, parse_dates=False)
            df.index = pd.to_datetime(df.index)
            debStr = "df = pd.read_csv(<readfile>, sep='{}', index_col=0, parse_dates=True)".format(args.delimiter)
        else:
            df = pd.read_csv(readfile, sep=args.delimiter)
            debStr = "df = pd.read_csv(<readfile>, sep='{}')".format(args.delimiter)
    if args.debug:
        print("import numpy as np")
        print("import pandas as pd")
        print("import datetime")
        print("import matplotlib.pyplot as plt")
        print("plt.rcParams['font.family'] = 'sans-serif'")
        print("plt.rcParams['font.sans-serif'] = ['BIZ UDGothic', 'MS Gothic', 'Yu Gothic']")
        print("plt.rcParams['pdf.fonttype'] = 42")
        print("plt.rcParams['ps.fonttype'] = 42")
        print(debStr)

    # sort dataframe
    if args.sorta:
        # ascending
        colnames = []
        for colnum in args.sorta:
            colnames.append(df.columns[colnum-1])
        df = df.sort_values(by=colnames)
        debStr = "df = df.sort_values(by={})".format(colnames)
        if args.debug: print(debStr)
    if args.sortd:
        # descending
        colnames = []
        for colnum in args.sortd:
            colnames.append(df.columns[colnum-1])
        df = df.sort_values(by=colnames, ascending=False)
        debStr = "df = df.sort_values(by={}, ascending=False)".format(colnames)
        if args.debug: print(debStr)

    ## set figure
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
    else:
        plt.rcParams['figure.figsize'] = (6.0, 6.0)
        debStr = "plt.rcParams['figure.figsize'] = (6.0, 6.0)"
        if args.debug: print(debStr)

    if args.style:
        plt.style.use(args.style)
        debStr = "plt.style.use({})".format(args.style)
        if args.debug: print(debStr)

    if args.layout:
        layoutflag = True
        if len(args.layout) != 2:
            raise_error("--layoutは2,2など2つの値を指定してください")
        else:
            lt = (args.layout)[0]
            ly = (args.layout)[1]
    else:
        layoutflag = False
        lt = ly = 1


    ## set figure
    #fig = plt.figure(figsize=(6.0, 6.0))
    fig = plt.figure()
    ax = fig.add_subplot(111)

    ## init argdict
    sdict = {}
    isSetPlotType = False

    ## type == scatter
    if args.scatter:
        isSetPlotType = True
        if args.x >= 1 and args.y >= 1:

            ## get columns name
            xname = df.columns[args.x-1]
            yname = df.columns[args.y-1]

            ## set axis options
            ax.set_xlabel(df.columns[args.x-1])
            ax.set_ylabel(df.columns[args.y-1])

            ## set dataframe
            x = df[xname]
            y = df[yname]

            if args.hue == -1:
                #ax.scatter(x, y)
                if args.mtype:
                    sdict["marker"] = args.mtype
                else:
                    sdict["marker"] = "o"
                ax.scatter(x, y, **sdict)
                if args.lm:
                    #print(x.count())
                    putx = (x.min() + x.max()) / 2
                    puty_scale = (y.min() + y.max()) / 50
                    puty = y.min()
                    ## 散布図に相関係数を表示
                    corr = np.corrcoef(x, y) # ピアソンの積率相関係数の計算
                    corr = corr * corr
                    name_corr = "{s:s}{f:4.3f}".format(s="R^2 = ", f=corr[1,0]) # 表示するテキスト設定
                    #plt.text(putx, puty + puty_scale, name, fontsize=10, color='k') # 相関係数を表示
                    ## 散布図に回帰式を追加する
                    ## 回帰係数aと切片bを計算し、回帰直線をプロットする
                    a = corr[1,0] * y.std() / x.std() # 回帰係数（a）
                    b = y.mean() - a * x.mean() # 切片（b）
                    x1 = np.linspace(np.floor(x.min()), np.ceil(x.max()), x.count()) # x軸データ
                    y1 = a * x1 + b # y軸データ
                    name_ls = "{s1:s}{f1:4.3f}{s2:s}{f2:4.3f}".format(s1="y = ", f1=a, s2="x + ", f2=b)
                    strlabel = name_ls + '  (' + name_corr + ')'
                    strlabel = '$' + strlabel + '$'
                    plt.plot(x1, y1, color='r', lw=args.linewidth, label=strlabel) # 回帰式のプロット
                    #plt.text(putx, puty + puty_scale * 2, name, fontsize=10, color='k') # 回帰式を表示
                    ## put text
                    equation = f'y={a}x+{b}' if b >= 0 else f'y={a}x-{-b}'
                    rtext = f'{name_ls}\n{name_corr}'
                    plt.text(x.max(), y.min(), rtext, verticalalignment='bottom', horizontalalignment='right')
                if not args.offtitle:
                    strtitle = xname + ' vs. ' + yname
                    plt.title(strtitle, fontsize=args.fontsizet)
            else:
                huename = df.columns[args.hue-1]
                labels = set(df[huename])
                dataset = [(df[df[huename]==x][xname], df[df[huename]==x][yname]) for x in labels]
                for data, label in zip(dataset, labels):
                    x, y = data
                    #ax.scatter(x, y, label=label)
                    sdict["label"] = label
                    if args.mtype:
                        sdict["marker"] = args.mtype
                    else:
                        sdict["marker"] = "o"
                    ax.scatter(x, y, **sdict)
                if not args.offtitle:
                    strtitle = xname + ' vs. ' + yname
                    plt.title(strtitle, fontsize=args.fontsizet)
        else:
            raise_error("scatter plotの列指定は、--xと--yにて1以上の整数を指定ください")

    ## type == pair
    if args.pair:
        isSetPlotType = True
        if args.seaborn:
            if args.hue >= 1:
                sns.pairplot(df, hue=df.columns[args.hue-1])
            else:
                sns.pairplot(df)
        else:
            ## do not use seaborn, only use pandas
            pd.plotting.scatter_matrix(df)

    ## type == all
    if not isSetPlotType:
        ## set colnums range
        if args.xrs:
            startcol = args.xrs - 1
            colnums = startcol + 1
        else:
            startcol = 0
            colnums = len(df.columns)
        #print(colnums)
        if args.index:
            if colnums < 1:
                raise_error("index以外に最低1列必要です")

        x = df.index.values
        cnt = 0
        #print(x)
        for colnum in range(startcol, colnums):
            if check_self(colnum) and check_delf(colnum):
                ## set dataframe
                yname = df.columns[colnum]
                y = df[yname]
                if args.notskipobject:
                    pass
                else:
                    if y.dtypes == 'object':
                        continue
                cnt = cnt + 1
                if cnt == 1:
                    ymax = max(y)
                    ymin = min(y)
                if cnt > 1 and max(y) > ymax:
                    ymax = max(y)
                if cnt > 1 and min(y) < ymin:
                    ymin = min(y)
                if args.y2 and colnum == colnums - 1:
                    ax2 = ax.twinx()
                    if args.mtype:
                        sdict["marker"] = args.mtype
                    sdict["label"] = yname
                    sdict["color"] = y2color
                    if args.step:
                        ax2.step(x, y, **sdict)
                    else:
                        ax2.plot(x, y, **sdict)
                    ## set axis options
                    if args.y2lim: ax2.set_ylim(args.y2lim)
                    if args.logy2: ax2.set_yscale("log")
                    #if args.y2lab: ax2.set_ylabel(yname)
                    ax2.set_ylabel(yname)
                else:
                    if args.y2:
                        sdict["label"] = yname
                        if args.mtype:
                            sdict["marker"] = args.mtype
                        bar_list = ax.bar(x, y, **sdict)
                    elif args.bar or args.barh:
                        sdict["label"] = yname
                        sdict["align"] = 'center'
                        if args.bar:
                            sdict["width"] = 0.8
                            sdict["bottom"] = None
                            bar_list = ax.bar(x, height=y, **sdict)
                        else:
                            sdict["height"] = 0.8
                            sdict["left"] = None
                            bar_list = ax.barh(x, width=y, **sdict)
                    else:
                        sdict["label"] = yname
                        if args.mtype:
                            sdict["marker"] = args.mtype
                        if args.linewidth:
                            sdict["linewidth"] = args.linewidth
                        if args.step:
                            ax.step(x, y, **sdict)
                        else:
                            ax.plot(x, y, **sdict)

    ## set axis options
    if args.datetime:
        import matplotlib.dates as mdates

    if args.datetimelocate:
        # 軸目盛の設定
        if args.datetimelocate == 'year':
            ax.xaxis.set_major_locator(mdates.YearLocator(base=args.datetimeinterval))
        elif args.datetimelocate == 'month':
            ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=None, interval=args.datetimeinterval, tz=None))
        elif args.datetimelocate == 'day':
            ax.xaxis.set_major_locator(mdates.DayLocator(bymonthday=None, interval=args.datetimeinterval, tz=None))
        elif args.datetimelocate == 'hour':
            ax.xaxis.set_major_locator(mdates.HourLocator(byhour=None, interval=args.datetimeinterval, tz=None))
        elif args.datetimelocate == 'minute':
            ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=None, interval=args.datetimeinterval, tz=None))
        elif args.datetimelocate == 'second':
            ax.xaxis.set_major_locator(mdates.SecondLocator(bysecond=None, interval=args.datetimeinterval, tz=None))
        elif args.datetimelocate == 'monday':
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, tz=None))
        elif args.datetimelocate == 'tuesday':
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.TU, tz=None))
        elif args.datetimelocate == 'wednesday':
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.WE, tz=None))
        elif args.datetimelocate == 'thursday':
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.TH, tz=None))
        elif args.datetimelocate == 'friday':
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.FR, tz=None))
        elif args.datetimelocate == 'saturday':
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.SA, tz=None))
        elif args.datetimelocate == 'sunday':
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.SU, tz=None))
        elif args.datetimelocate == 'auto':
            ax.xaxis.set_major_locator(mdates.AutoDateLocator(tz=None, minticks=5, maxticks=None, interval_multiples=True))
        else:
            ax.xaxis.set_major_locator(mdates.AutoDateLocator(tz=None, minticks=5, maxticks=None, interval_multiples=True))
        ## 補助目盛りを使いたい場合や時刻まで表示したい場合は以下を調整して使用
        #ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=range(0, 24, 1), tz=None))
        #ax.xaxis.set_major_formatter(mdates.Dateformatter("%Y-%m-%d\n%H:%M:%S"))

    #if args.dformat:
    #    #ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y\n%m-%d'))
    #    dtimeformatstr = args.dformat
    #    dtimeformatstr = 'ax.xaxis.set_major_formatter(mdates.DateFormatter("' + dtimeformatstr + '"))'
    #    #print(dtimeformatstr)
    #    eval(dtimeformatstr)

    if args.dformat:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter(args.dformat))
    if args.yinterval:
        plt.gca().xaxis.set_major_locator(mdates.YearLocator(base=args.yinterval))
    if args.minterval:
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=args.minterval))
    if args.dinterval:
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=args.dinterval))
    if args.winterval:
        plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=args.winterval))


    ## type == "bar", "barh"のみ、grepでヒットしたラベル文字列のバーに色付け
    if args.grep and (args.bar or args.barh):
        xlabelcnt = 0
        for xlabelstr in x:
            if re.search(args.grep, str(xlabelstr)):
                bar_list[xlabelcnt].set_color(args.gcolor)
            else:
                if args.gcolor2:
                    bar_list[xlabelcnt].set_color(args.gcolor2)
            xlabelcnt = xlabelcnt + 1

    if args.spines:
        ax.spines['bottom'].set_position(args.spines)
    if args.xlim:
        ax.set_xlim(args.xlim)
    if args.ylim:
        ax.set_ylim(args.ylim)
    if args.ymin and not args.ylim:
        ax.set_ylim(args.ymin, ymax)
    if args.ymax and not args.ylim:
        ax.set_ylim(ymin, args.ymax)

    if args.grid: ax.grid(linestyle='dotted')
    if args.gridx: ax.grid(axis='x', linestyle='dotted')
    if args.gridy: ax.grid(axis='y', linestyle='dotted')
    #if args.logy: ax.set_yscale("log", basey=10, nonposy="mask")
    if args.logy: ax.set_yscale("log")
    if args.logx: ax.set_xscale("log")
    if args.logxy:
        ax.set_xscale("log")
        ax.set_yscale("log")
    if args.hline:
        for i in range(len(args.hline)):
            adict = {}
            adict["color"]     = args.hlinecolor[i]
            adict["linestyle"] = "dashed"
            adict["linewidth"] = args.hlinewidth
            ax.axhline(args.hline[i], **adict)
    ## plot zero line
    if args.hline0:
        adict = {}
        adict["y"]     = 0
        adict["color"] = 'k'
        adict["ls"]    = '-'
        adict["lw"]    = 0.4
        ax.axhline(**adict)
    if args.vline:
        if args.datetime:
            vmap = list(map(date_type, args.vline))
        else:
            vmap = list(map(float, args.vline))
        for i in vmap:
            adict = {}
            adict["color"]     = args.vlinecolor[0]
            #adict["linestyle"] = "dashed"
            adict["linewidth"] = args.vlinewidth
            ax.axvline(i, **adict)
    if args.today and args.datetime:
        today = datetime.date.today()
        adict = {}
        adict["color"]     = args.vlinecolor[0]
        #adict["linestyle"] = "dashed"
        adict["linewidth"] = args.vlinewidth
        ax.axvline(today, **adict)
    if args.now and args.datetime:
        now = datetime.datetime.now()
        adict = {}
        adict["color"]     = args.vlinecolor[0]
        #adict["linestyle"] = "dashed"
        adict["linewidth"] = args.vlinewidth
        ax.axvline(now, **adict)
    ## set legend
    if args.offlegend:
        pass
    else:
        if args.y2:
            h1, l1 = ax.get_legend_handles_labels()
            h2, l2 = ax2.get_legend_handles_labels()
            ax.legend(h1+h2, l1+l2, loc=args.legendloc)
        else:
            if args.scatter and args.hue == -1:
                pass
            else:
                ax.legend(loc=args.legendloc)
    if args.xlab: ax.set_xlabel(args.xlab)
    if args.ylab: ax.set_ylabel(args.ylab)
    if args.y2lab: ax2.set_ylabel(args.y2lab)
    if args.xrs:
        ## calc X-CL,UCL,LCL
        ycolname = df.columns[args.xrs - 1]
        ser_x = df[ycolname]
        ser_r = df[ycolname].diff().abs()
        ser_x.index = df.index
        ser_r.index = df.index
        xstd  = ser_x.std()
        xbar  = ser_x.mean()
        rsbar = ser_r.dropna().mean()
        X_CL  = xbar
        X_UCL = xbar + 2.66 * rsbar
        X_LCL = xbar - 2.66 * rsbar
        adict = {}
        adict["color"]     = "tab:red"
        adict["linestyle"] = "dashed"
        adict["linewidth"] = args.hlinewidth
        ax.axhline(X_UCL, **adict)
        ax.axhline(X_CL,  **adict)
        ax.axhline(X_LCL, **adict)
    if args.vspan:
        adict = {}
        adict["color"] = args.vspancolor
        adict["alpha"] = args.vspanalpha
        ax.axvspan(args.vspan[0], args.vspan[1], **adict)
    if args.hspan:
        adict = {}
        adict["color"] = args.hspancolor
        adict["alpha"] = args.hspanalpha
        ax.axhspan(args.hspan[0], args.hspan[1], **adict)

    ## set plt options: title and label
    #if args.xlab: plt.xlabel(args.xlab)
    #if args.ylab: plt.ylabel(args.ylab)
    if args.title: plt.title(args.title, fontsize=args.fontsizet)
    if args.rot:
        # 軸目盛ラベルの回転
        if args.rot == 0 or args.rot == 90:
            plt.xticks(rotation=args.rot)
        else:
            labels = ax.get_xticklabels()
            plt.setp(labels, rotation=args.rot, ha="right")
    if args.reverse:
        plt.gca().invert_yaxis()

    ## 凡例描画(位置指定)
    if args.legendloc2:
        if len(args.legendloc2) == 2:
            ax.legend(bbox_to_anchor=(args.legendloc2[0], args.legendloc2[1]))
        elif len(args.legendloc2) == 3:
            ax.legend(bbox_to_anchor=(args.legendloc2[0], args.legendloc2[1]),
                        borderaxespad=args.legendloc2[2])
    ## サイズ調整
    if args.adjust:
        if len(args.adjust) != 2:
            raise_error("--adjust はカンマ区切りで2つ数値を指定してください")
        plt.subplots_adjust(left = args.adjust[0], right = args.adjust[1])

    ## etc
    plt.tight_layout()

    ## output
    if args.output:
        ofile = re.sub(r'\\', '/', args.output)
        #print(ofile)
        plt.savefig(ofile, dpi=args.dpi)
        plt.close('all')
    else:
        plt.show()
        plt.close('all')
