#!/usr/bin/env python3
#coding: utf-8

#
# pyplot-pandas - plot using pandas-plot and matplotlib
#

import io, sys, os
import re
import argparse
import numpy as np
import pandas as pd
import datetime
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

from matplotlib.ticker import ScalarFormatter
import matplotlib.ticker as mtick

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
    help_desc_msg ="""pyplot-pandas -- data visualization using matplotlib
    pandas df.plotを使用したグラフ描画。
    列指定は1始まりとする。

    --debugオプションでjupyter notebook貼り付け用の文字列も同時に出力する。
    ただし、すべてのオプションに対応しているわけではない。

    default behavior is to read data form stdin
    if set -i option, read data from file

    --datetimeスイッチで、1列目を日付形式のインデックスとみなす。
    このスイッチを指定した場合、追加で以下のオプションを使用できる：
        --dformat "%Y-%m`n(%a)"
            --yinterval <int>: year interval
            --minterval <int>: month interval
            --dinterval <int>: day interval
            --winterval <int>: weekday interval

    垂線を引く: カンマ区切りで値やISO形式の日付を指定
        --vline 10,20,30
        --datetime --vline 2019-08-01,2020-02-01
    """
    help_epi_msg = """EXAMPLES:
    cat iris.csv | python pyplot-pandas.py -d ","
    cat iris.csv | python pyplot-pandas.py -d "," --index
    cat date.csv | python pyplot.py -d "," --datetime --minterval 2 --rot 90 --dformat "%Y-%m`n(%a)"

    cat iris.csv | python pyplot-pandas.py -d "," --sorta 1,2
    cat date.txt | python pyplot-pandas.py --datetime

    cat iris.csv | python pyplot-pandas.py -d "," --bar
    cat iris.csv | python pyplot-pandas.py -d "," --bar --hatch 3

    cat iris.csv | python pyplot-pandas.py -d "," --line --mstyle 'k-^','r-o','k-D','k--' --msize 5 --mfillcolor None

    cat iris.csv | python pyplot-pandas.py -d "," --step
    cat iris.csv | python pyplot-pandas.py -d "," --step --where '[pre|mid|post]'

    cat iris.csv | python pyplot-pandas.py -d "," --pair --hue 5
    cat iris.csv | python pyplot-pandas.py -d "," --pair --hue 5 --seaborn

    cat iris.csv | python pyplot-pandas.py -d "," --scatter
    cat iris.csv | python pyplot-pandas.py -d "," --scatter --hue 4
    cat iris.csv | python pyplot-pandas.py -d "," --scatter --x 5 --y 2 --jitter
    cat iris.csv | python pyplot-pandas.py -d "," --scatter --x 5 --y 2 --jitter --hue 5
    cat iris.csv | python pyplot-pandas.py -d "," --hist --subplots --layout 2,2

    ## box plot
    cat iris.csv | python pyplot-pandas.py -d "," --box
    cat iris.csv | python pyplot-pandas.py -d "," --box --col 1 --by 5

    ## histogram
    cat iris.csv | python pyplot-pandas.py -d "," --hist
    cat iris.csv | python pyplot-pandas.py -d "," --hist --alpha 0.5
    cat iris.csv | python pyplot-pandas.py -d "," --hist --col 1 --by 5

    ## line
    cat iris.csv | python pyplot-pandas.py -d "," --line
    cat iris.csv | python pyplot-pandas.py -d "," --line --y 1
    cat iris.csv | python pyplot-pandas.py -d "," --line --subplots

    ## kde
    cat iris.csv | python pyplot-pandas.py -d "," --kde

    ## hexbin
    cat iris.csv | python pyplot-pandas.py -d "," --hexbin
    cat iris.csv | python pyplot-pandas.py -d "," --hexbin --gridsize 10

    ## pie chart
    cat iris.csv | head -n 5 | python pyplot-pandas.py -d "," --pie --x 2 --pielabel 1
    cat iris.csv | head -n 5 | python pyplot-pandas.py -d "," --pie --x 2 --piepercent "%1.1f%%"

    python pyplot-pandas.py -i iris.csv -d ","
    python pyplot-pandas.py -i iris.csv -d "," --monochrome
    python pyplot-pandas.py -i iris.csv -d ',' --y2 1

    ## 水平線を引く
    python pyplot-pandas.py -i iris.csv -d ',' --hline 1 --hlinecolor "tab:red"
    python pyplot-pandas.py -i iris.csv -d ',' --hline 3.0,2.0 --hlinecolor tab:red,tab:green
      -> 水平線を引く。カンマ区切りで複数引けるが、その際は
         hline, hlinecolorの引数の数を一致させる必要がある、
         vlineも同じ。

    cat iris.csv | python pyplot-pandas.py -d "," --joint --jointkind scatter
     -> seaborn jointplotの例
    cat iris.csv | python pyplot-pandas.py -d "," --scatter --x 1 --y 3 --lm
    cat iris.csv | python pyplot-pandas.py -d "," --scatter --x 1 --y 3 --lm --printinfo
      -> 散布図に最小二乗法を適用し回帰直線をプロット。同時に線形回帰式及びR^2値を凡例に表示

    cat iris.csv | python pyplot-pandas.py -d "," --xrs 1
    cat iris.csv | python pyplot-pandas.py -d "," --xrs 1 --hlinewidth 1.2
      -> 1列目のデータを用いてX-Rs線を引く

    ## fill range
    cat iris.csv | python pyplot-pandas.py -d ","  --vspan 60,80 --vspancolor gray

    ## format template:
    cat iris.csv | python pyplot-pandas.py --xfmt '%.1f' ## x軸format
    cat iris.csv | python pyplot-pandas.py --x10n 2 ## x軸を10^n表記にformat
    cat iris.csv | python pyplot-pandas.py --xlim 0,40 --xstep 10 --xstep2 1 --grid2 ## 補助目盛+グリッド

    cat datetime.txt | python pyplot-pandas.py --datetime
    cat datetime.txt | python pyplot-pandas.py --datetime --datetimelocate sunday --dformat '%H-%M\\n(%a)' --rot 45 --grid
    cat datetime.txt | python pyplot-pandas.py --datetime --datetimelocate day --datetimeinterval 5

    ## legend locate
    cat iris.csv | python pyplot-pandas.py --legendloc2 1,1,1 ## 凡例を外に。
    """
    parser = argparse.ArgumentParser(description=help_desc_msg,
                    epilog=help_epi_msg,
                    formatter_class=argparse.RawDescriptionHelpFormatter)
    tp = lambda x:list(map(int,   x.split(',')))
    tf = lambda x:list(map(float, x.split(',')))
    ts = lambda x:list(map(str,   x.split(',')))
    td1 = lambda x:list(map(date_type,  x.split(',')))
    td2 = lambda x:list(map(date_type2, x.split(',')))

    parser.add_argument('-d', '--delimiter', help='line separator(delimiter)', default=r' ',
        choices=[r' ', r',', r'\t'])
    parser.add_argument("-o", "--output", help="output file name", type=str)
    parser.add_argument("-i", "--inputfile", help="input file name", type=str)
    parser.add_argument('--dpi', help='output dpi', default=100, type=int)
    
    ## graph type
    parser.add_argument("--scatter", help="graph type: scatter", action="store_true")
    parser.add_argument("--line", help="graph type: line", action="store_true")
    parser.add_argument("--step", help="graph type: line + step", action="store_true")
    parser.add_argument("--where", help="graph type: line + step config", type=str, choices=[
        'pre','post','mid'])
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
    
    ## graph opts
    parser.add_argument('--x', help="x colnum", type=int)
    parser.add_argument('--y', help="y colnum", type=int)
    parser.add_argument('--hue', help="hue colnum", type=int)
    parser.add_argument('--y2', help="secondary y axis columns", type=int)
    
    parser.add_argument('--xname', help="x colname", type=str)
    parser.add_argument('--yname', help="y colname", type=str)
    parser.add_argument('--huename', help="hue colname", type=str)
    parser.add_argument('--y2name', help="y2 colname", type=str)
    
    parser.add_argument('--col', help="box colnum: box", type=int)
    parser.add_argument('--by', help="box group by: box", type=int)
    parser.add_argument('--colname', help="box colname: box", type=str)
    parser.add_argument('--byname', help="box group by: box", type=str)
    parser.add_argument('--gridsize', help="gridsize: hexbin", type=int)
    parser.add_argument('--color', help="color", type=str)
    
    ## font
    parser.add_argument('--anzu', help="font: anzu", action="store_true")
    parser.add_argument('--natsume', help="font: natsume", action="store_true")
    parser.add_argument('--natsumeo', help="font: natsume osae", action="store_true")
    parser.add_argument('--nofont', help="do not set font", action="store_true")
    
    ## pie chart
    parser.add_argument('--pielabel', help="label column in pie plot", type=int)
    parser.add_argument('--piepercent', help="add perent label in pie plot", type=str)
    parser.add_argument('--pieborder', help="border width in pie plot", default=.5, type=float)
    parser.add_argument('--pieradius', help="radius of pie plot", default=1.0, type=float)
    parser.add_argument('--pierev', help="reverse label clock in pie plot", action="store_true")
    parser.add_argument('--piestartangle', help="start angle in pie plot", default=90, type=int)
    
    ## least square
    parser.add_argument("--lm", help="set least square line in scatter plot", action="store_true")
    parser.add_argument("--printinfo", help="print corr and formula", action="store_true")
    
    ## theme
    parser.add_argument('--theme', help="set seaborn theme", type=str, choices=[
        'darkgrid','dark','whitegrid','white','ticks'], default='whitegrid')
    parser.add_argument('--context', help="set seaborn context", type=str, choices=[
        'paper','notebook','talk','poster'])
    parser.add_argument('--palette', help="set seaborn palette", type=str, choices=[
        'deep','muted','pastel','bright','dark','colorblind','hls','husl'])
    parser.add_argument('--color_codes', help="color_codes", action="store_true")
    parser.add_argument('--font_scale', help="font scale", type=float)
    
    parser.add_argument('--size', help='w inch, h inch', type=tp)
    parser.add_argument('--layout', help='subplot layout', type=tp)
    parser.add_argument("--noheader", help="noheader data", action="store_true")
    parser.add_argument("--index", help="set df.columns[0] as index", action="store_true")
    parser.add_argument('--alpha', help='alpha betw 0 and 1', type=float)
    parser.add_argument('--sorta', help='sort by ascending', type=tp)
    parser.add_argument('--sortd', help='sort by descending', type=tp)
    
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
    parser.add_argument("--style", help="graph style", choices=[
        'bmh','classic','dark_background','fast','fivethirtyeight','ggplot','grayscale',
        'seaborn-bright','seaborn-colorblind','seaborn-dark-palette','seaborn-dark','seaborn-darkgrid',
        'seaborn-deep','seaborn-muted','seaborn-notebook','seaborn-paper','seaborn-pastel',
        'seaborn-poster','seaborn-talk','seaborn-ticks','seaborn-white','seaborn-whitegrid',
        'seaborn','Solarize_Light2','tableau-colorblind10','_classic_test'])
    
    ## graph opts
    parser.add_argument("--jitter", help="jitter scatter plot using seaborn", action="store_true")
    parser.add_argument("--swarm", help="jitter scatter plot using seaborn", action="store_true")
    parser.add_argument("--jointkind", help="seaborn jointplot kind", default="scatter", choices=[
        "scatter","reg","resid","kde","hex"])
    
    parser.add_argument('--mstyle', help='line marker style', type=ts)
    parser.add_argument('--msize', help='marker size', type=int)
    parser.add_argument('--mfillcolor', help='marker fill', type=str)
    parser.add_argument('--medge', help='marker edge width', type=float)
    parser.add_argument('--medgecolor', help='marker edge color', type=str)
    parser.add_argument('--colormap', help='colormap', type=str)
    parser.add_argument("--mycolormap", help="my color map", action="store_true")
    parser.add_argument("--offcolorbar", help="colorbar switch", action="store_true")
    parser.add_argument('--hatch', help="add hatch in bar plot", type=int)
    parser.add_argument('--linewidth', help='line widths', default=1, type=float)

    parser.add_argument('--hline', help="horizon lines", type=tf)
    parser.add_argument('--hlinewidth', help='horizon line widths', default=0.8, type=float)
    parser.add_argument('--hlinecolor', help="horizon line colors", default='tab:red', type=ts)
    parser.add_argument("--hline0", help="add y zero line", action="store_true")

    parser.add_argument('--vline', help="vertical lines", type=ts)
    #parser.add_argument('--vlined', help="date vertical lines. Date must be in ISO format. ex. 2020-01-01", type=td1)
    #parser.add_argument('--vlinedt', help="datetime vertical lines. ex: 2020-01-01 00:00:00", type=td2)
    parser.add_argument('--vlinecolor', help="vertical line colors", default='tab:red', type=ts)
    parser.add_argument('--vlinewidth', help='vertical line widths', default=0.8, type=float)
    parser.add_argument('--hspan', help='fill h-range', type=tf)
    parser.add_argument('--hspancolor', help='fillcolor h-range', default="coral", type=str)
    parser.add_argument('--hspanalpha', help='fillcolor alpha h-range', default=0.5, type=float)
    parser.add_argument('--vspan', help='fill v-range', type=tf)
    parser.add_argument('--vspancolor', help='fillcolor v-range', default="coral", type=str)
    parser.add_argument('--vspanalpha', help='fillcolor alpha v-range', default=0.5, type=float)
    parser.add_argument("--today", help="add today vline", action="store_true")
    parser.add_argument("--now", help="add now datetime vline", action="store_true")
    parser.add_argument("--legend", help="legend switch", action="store_true")
    parser.add_argument("--offlegend", help="legend switch", action="store_true")
    parser.add_argument("--legendloc", help="legend location", choices=[
        "best","upper right","upper left","lower left","lower right","right",
        "center left","center right","lower center","upper center","center"],
        default="best", type=str)
    parser.add_argument('--legendloc2',  help='legend location', type=tf)
    parser.add_argument('--adjust',  help='space adjust. eg: 0.1,0.8', type=tf)
    
    parser.add_argument("--title", help="title", type=str)
    parser.add_argument("--xlab", help="x axis label", type=str)
    parser.add_argument("--ylab", help="y axis label", type=str)
    parser.add_argument('--xlim', help='x axis min, max', type=tf)
    parser.add_argument('--ylim', help='y axis min, max', type=tf)
    parser.add_argument('--xstep',  help='x axis major interval', type=float)
    parser.add_argument('--ystep',  help='y axis major interval', type=float)
    parser.add_argument('--xstep2', help='x axis minor interval', type=float)
    parser.add_argument('--ystep2', help='y axis minor interval', type=float)
    parser.add_argument('--xticks', help='x axis ticks', type=tf)
    parser.add_argument('--yticks', help='y axis ticks', type=tf)
    parser.add_argument('--xfmt', help='x axis format', type=str)
    parser.add_argument('--yfmt', help='y axis format', type=str)
    parser.add_argument('--x10n', help='x axis format 10^n', type=int)
    parser.add_argument('--y10n', help='y axis format 10^n', type=int)
    parser.add_argument("--grid",  help="add major grid", action="store_true")
    parser.add_argument("--grid2", help="add major and minor grid", action="store_true")
    parser.add_argument('--xrs', help='add x-Rs hline', type=int)
    parser.add_argument('--xrsname', help='add x-Rs hline', type=str)
    parser.add_argument("--subplots", help="subplots", action="store_true")
    parser.add_argument("--reverse", help="reverse y axis", action="store_true")
    parser.add_argument("--sharex", help="subplots share x axis", action="store_true")
    parser.add_argument("--sharey", help="subplots share y axis", action="store_true")
    parser.add_argument("--logx", help="logx", action="store_true")
    parser.add_argument("--logy", help="logy", action="store_true")
    parser.add_argument("--logxy", help="logxy", action="store_true")
    parser.add_argument("--stacked", help="bar or area stacking", action="store_true")
    parser.add_argument('--rot', help="xlab rotate", type=int)
    parser.add_argument('--fontsize', help="fontsize", type=float)
    parser.add_argument('--fontsizet', help="title fontsize", default=14, type=float)
    parser.add_argument("--seaborn", help="pair plot", action="store_true")
    parser.add_argument("--monochrome", help="monochrome line", action="store_true")
    parser.add_argument("--xkcd", help="xkcd", action="store_true")
    
    parser.add_argument("--debug", help="output plot option", action="store_true")
    #parser.add_argument("-q", "--quiet", help="print as it is", action="store_true")
    #parser.add_argument("-t", "--dtype", help="array data type", default='float', type=str)
    #parser.add_argument("-V", "--version", help="version", action="version", version=_version)
    #parser.print_help()
    args = parser.parse_args()
    return(args)

class FixedOrderFormatter(ScalarFormatter):
    '''任意の桁数で軸の値の10のN乗表記するために必要なクラス

    (1) import必要
        from matplotlib.ticker import ScalarFormatter
    (2) 参照サイト
        http://villageofsound.hatenadiary.jp/entry/2014/11/06/155824
    '''
    def __init__(self, order_of_mag=0, useOffset=True, useMathText=True):
        self._order_of_mag = order_of_mag
        ScalarFormatter.__init__(self, useOffset=useOffset, 
                                    useMathText=useMathText)
    def _set_orderOfMagnitude(self, range):
        self.orderOfMagnitude = self._order_of_mag

def open_file():
    if args.inputfile:
        readfile = re.sub(r'\\', '/', args.inputfile)
    else:
        readfile = sys.stdin
    return readfile

if __name__ == '__main__':
    ## get args
    args = get_args()

    ## set theme
    themeDict = {}
    if args.theme:       themeDict["style"] = args.theme
    if args.palette:     themeDict["palette"] = args.palette
    if args.context:     themeDict["context"] = args.context
    if args.font_scale:  themeDict["font_scale"] = args.font_scale
    if args.color_codes: themeDict["color_codes"] = True

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

    ## xkcd
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
            themeDict["font"] = 'BIZ UDGothic'

    if args.fontsize:
        plt.rcParams['font.size'] = args.fontsize

    ## read file
    readfile = open_file()

    if args.noheader:
        if args.index:
            df = pd.read_csv(readfile, sep=args.delimiter, index_col=0, header=None)
            debStr = "df = pd.read_csv(<readfile>, sep='{}', index_col=0, header=None)".format(args.delimiter)
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
        lt = 1
        ly = 1

    ## init argdict for seaborn
    sdict = {}
    isSetPlotType = False

    ## get columns name
    flag_x = False
    if args.xname:
        flag_x = True
        sdict["x"] = args.xname
        xcolname   = args.xname
    elif args.x:
        flag_x = True
        sdict["x"] = df.columns[args.x-1]
        xcolname   = df.columns[args.x-1]

    flag_y = False
    if args.yname:
        flag_y = True
        sdict["y"] = args.yname
        ycolname   = args.yname
    elif args.y:
        flag_y = True
        sdict["y"] = df.columns[args.y-1]
        ycolname   = df.columns[args.y-1]

    flag_hue = False
    if args.huename:
        flag_hue = True
        if args.scatter:
            sdict["hue"] = args.huename
        else:
            sdict["c"] = args.huename
        huecolname = args.huename
    elif args.hue:
        flag_hue = True
        if args.scatter:
            sdict["hue"] = df.columns[args.hue-1]
        else:
            sdict["c"] = df.columns[args.hue-1]
        huecolname = df.columns[args.hue-1]

    flag_xrs = False
    if args.xrsname:
        flag_xrs = True
        ycolname = args.xrsname
        sdict["kind"] = "line"
        sdict["y"] = ycolname
    elif args.xrs:
        flag_xrs = True
        ycolname = df.columns[args.xrs-1]
        sdict["kind"] = "line"
        sdict["y"] = ycolname

    flag_y2 = False
    if args.y2name:
        flag_y2 = True
        sdict["secondary_y"] = args.y2name
    elif args.y2:
        flag_y2 = True
        sdict["secondary_y"] = df.columns[args.y2-1]

    if args.colname:
        sdict["column"] = args.colname
    elif args.col:
        sdict["column"] = df.columns[args.col-1]

    if args.byname:
        sdict["by"] = args.byname
    elif args.by:
        sdict["by"] = df.columns[args.by-1]

    ## other opts
    if args.mstyle:     sdict["style"]           = args.mstyle
    if args.msize:      sdict["markersize"]      = args.msize
    if args.mfillcolor: sdict["markerfacecolor"] = args.mfillcolor
    if args.alpha:      sdict["alpha"]           = args.alpha
    if args.colormap:   sdict["colormap"]        = args.colormap
    if args.medge:      sdict["markeredgewidth"] = args.medge
    if args.medgecolor: sdict["markeredgecolor"] = args.medgecolor
    if args.xlim:       sdict["xlim"]            = args.xlim
    if args.ylim:       sdict["ylim"]            = args.ylim
    if args.xticks:     sdict["xticks"]          = args.xticks
    if args.yticks:     sdict["yticks"]          = args.yticks
    if args.title:      sdict["title"]           = args.title
    if args.legend:     sdict["legend"]          = True
    if args.offlegend:  sdict["legend"]          = False
    if args.grid:       sdict["grid"]            = args.grid
    if args.logx:       sdict["logx"]            = args.logx
    if args.logy:       sdict["logy"]            = args.logy
    if args.logxy:      sdict["loglog"]          = args.logxy
    #if args.rot:        sdict["rot"]             = args.rot
    if args.stacked:    sdict["stacked"]         = args.stacked
    if args.fontsize:   sdict["fontsize"]        = args.fontsize
    if args.alpha:      sdict["alpha"]           = args.alpha
    if args.subplots:   sdict["subplots"]        = True
    if args.gridsize:   sdict["gridsize"]        = args.gridsize
    if args.color:      sdict["color"]           = args.color

    if layoutflag:
        sdict["subplots"] = layoutflag
        sdict["layout"]   = (lt, ly)
        sdict["sharex"]   = args.sharex
        sdict["sharey"]   = args.sharey

    ## set data
    #sdict["data"] = df

    ## type == scatter
    if args.scatter or args.lm:
        isSetPlotType = True
        if not args.hue:
            sdict["kind"] = "scatter"

        ## test
        if not flag_x: raise_error("scatter requires an x and y column")
        if not flag_y: raise_error("scatter requires an x and y column")

        ## set dataframe
        x = df[sdict["x"]]
        y = df[sdict["y"]]

        if args.hue:
            import seaborn as sns
            ## set theme
            if any(themeDict): sns.set_theme(**themeDict)
            else: sns.set_theme()
            sdict["data"] = df
            ax = sns.relplot(**sdict)
            sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
            plt.legend(loc=2)
        elif args.jitter:
            import seaborn as sns
            if any(themeDict): sns.set_theme(**themeDict)
            else: sns.set_theme()
            sdict["data"] = df
            sdict["jitter"] = True
            ax = sns.catplot(**sdict)
        elif args.swarm:
            import seaborn as sns
            if any(themeDict): sns.set_theme(**themeDict)
            else: sns.set_theme()
            sdict["data"] = df
            ax = sns.swarmplot(**sdict)
        else:
            ax = df.plot(**sdict)
            ## calc least square
            if args.lm:
                #print(x.count())
                putx = (x.min() + x.max()) / 2
                puty_scale = (y.min() + y.max()) / 50
                puty = y.min()
                ## 散布図に相関係数を表示
                corr = np.corrcoef(x, y) # ピアソンの積率相関係数の計算
                #print(corr)
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
                ## put text
                equation = f'y={a}x+{b}' if b >= 0 else f'y={a}x-{-b}'
                rtext = f'{name_ls}\n{name_corr}'
                plt.text(x.max(), y.min(), rtext, verticalalignment='bottom', horizontalalignment='right')
                #plt.text(putx, puty + puty_scale * 2, name, fontsize=10, color='k') # 回帰式を表示
                if args.printinfo:
                    print(rtext.replace(' ','').replace('\n',' ; ').replace('=',' = ').replace('+',' + '))

    if args.bar:
        isSetPlotType = True
        sdict["kind"] = "bar"
        ax = df.plot(**sdict)

    if args.barh:
        isSetPlotType = True
        sdict["kind"] = "barh"
        ax = df.plot(**sdict)

    if args.box:
        isSetPlotType = True
        sdict["kind"] = "box"
        ax = df.plot(**sdict)

    if args.hexbin:
        isSetPlotType = True
        sdict["kind"] = "hexbin"
        ax = df.plot(**sdict)

    if args.hist:
        isSetPlotType = True
        sdict["kind"] = "hist"
        ax = df.plot(**sdict)

    if args.kde:
        isSetPlotType = True
        sdict["kind"] = "kde"
        ax = df.plot(**sdict)

    if args.joint:
        isSetPlotType = True
        import seaborn as sns
        if any(themeDict): sns.set_theme(**themeDict)
        else: sns.set_theme()
        #sns.set()
        if args.jointkind != 'kde':
            sns.jointplot(
                x=df.columns[args.x-1],
                y=df.columns[args.y-1],
                kind=args.jointkind,
                data=df,
                edgecolor='w'
            )
        else:
            sns.jointplot(
                x=df.columns[args.x-1],
                y=df.columns[args.y-1],
                kind='scatter',
                data=df,
                color='k',
                edgecolor='w'
            ).plot_joint(
                sns.kdeplot,
                zorder=0,
                n_levels=6
            )

    if args.pair:
        isSetPlotType = True
        if args.seaborn:
            import seaborn as sns
            if any(themeDict): sns.set_theme(**themeDict)
            else: sns.set_theme()
            if args.debug: print("import seaborn as sns")
            if flag_hue:
                ax = sns.pairplot(df, hue=huecolname)
                debStr = 'ax = sns.pairplot(df, hue=df[{}])'.format(huecolname)
            else:
                ax = sns.pairplot(df)
                debStr = "ax = sns.pairplot(df)"
        else:
            ## do not use seaborn, only use pandas
            ax = pd.plotting.scatter_matrix(df)
            debStr = "ax = pd.plotting.scatter_matrix(df)"
        if args.debug: print(debStr)

    if args.pie:
        isSetPlotType = True
        sdict["x"] = df[df.columns[args.x-1]]        
        print(sdict)
        if args.pierev:
            ## 反時計まわり
            sdict["counterclock"] = True
        else:
            ## 時計回り
            sdict["counterclock"] = False
        if args.pielabel:
            lcolname = df.columns[args.pielabel-1]
            sdict["labels"] = df[lcolname]
        else:
            sdict["labels"] = None
        if args.piestartangle:
            sdict["startangle"] = args.piestartangle
        if args.piepercent:
            sdict["autopct"] = args.piepercent
        if args.pieradius:
            sdict["radius"] = args.pieradius
        if args.pieborder:
            sdict["wedgeprops"] = {"lw" : args.pieborder, "ec" : "k"}

        xcolname = df.columns[args.x-1]
        x = df[xcolname]

        fig = plt.figure()
        fig.patch.set_facecolor('white')


        if args.title:
            del sdict["title"]
            plt.title(args.title, fontsize=args.fontsizet)
        ax = plt.pie(**sdict)

    if args.line:
        isSetPlotType = True
        sdict["kind"] = "line"
        ax = df.plot(**sdict)

    if args.step:
        isSetPlotType = True
        sdict["kind"] = "line"
        if args.where:
            dstyle = 'steps-' + args.where
        elif args.where == 'pre':
            dstyle = 'steps'
        else:
            dstyle = 'steps'
        sdict["drawstyle"] = dstyle
        ax = df.plot(**sdict)

    if not isSetPlotType:
        ## default plot
        sdict["kind"] = "line"
        ax = df.plot(**sdict)

    if args.debug: print(sdict)



    # hatch
    if (args.bar or args.barh) and (args.hatch):
        hatch_cnt = args.hatch
        hatch_pat = [ "/", "x", "\\", "-", "|", "+", "o", "O", ".", "*" ]
        bars = ax.patches
        hatches = ''.join(h * len(df) for h in hatch_pat)
        cnt = 1
        for bar, hatch in zip(bars, hatches):
            bar.set_hatch(hatch * hatch_cnt)
            cnt = cnt + 1
        if args.y2:
            h1, l1 = ax.get_legend_handles_labels()
            h2, l2 = ax.right_ax.get_legend_handles_labels()
            handles = h1 + h2
            labels  = l1 + l2
            ax.legend(handles, labels) # don't work, need fix
        else:
            ax.legend()

    #主目盛の設定
    #xmin:x軸の主目盛の開始位置、xmax:x軸の主目盛の終了位置
    #つまり、主目盛はxminからスタートし、xmaxで終わる。
    #xstep:x軸の主目盛の間隔。
    #
    #なお、ax.set_xticks(np.linspace(xmin, xmax, n_x))とは
    #xmin～xmaxの範囲を(n_x - 1)分割した位置に主目盛を表示する。
    #したがって、(xmax - xmin)/xstep が整数になるような値を指定しなければ、
    #想定通りの目盛を表示できない。
    #
    #xmin～xmaxは実際にグラフで表示する範囲よりも大きめに設定しないと、
    #目盛が表示されない範囲ができてしまう。
    #
    #np.arange()は、stepが小数の場合、目盛の最後の数値が表示されないことが
    #　あるため、np.linspace()で主目盛の位置を指定する。
    if args.xstep:
        if not args.xlim:
            raise_error("xstepを指定する場合はxlimで最小最大値のセットが必要です")
        xmin  = args.xlim[0]
        xmax  = args.xlim[1]
        xstep = args.xstep
        n_x   = int((xmax - xmin) / xstep) + 1
        ax.set_xticks(np.linspace(xmin, xmax, n_x))
        debStr = "ax.set_xticks(np.linspace({}, {}, {}))".format(xmin, xmax, n_x)
        if args.debug: print(debStr)
    if args.ystep:
        if not args.ylim:
            raise_error("ystepを指定する場合はylimで最小最大値のセットが必要です")
        ymin  = args.ylim[0]
        ymax  = args.ylim[1]
        ystep = args.ystep
        n_y   = int((ymax - ymin) / ystep) + 1
        ax.set_yticks(np.linspace(ymin, ymax, n_y))
        debStr = "ax.set_yticks(np.linspace({}, {}, {}))".format(ymin, ymax, n_y)
        if args.debug: print(debStr)

    ##補助目盛の設定
    if args.xstep2:
        if not args.xlim:
            raise_error("xstep2を指定する場合はxlimで最小最大値のセットが必要です")
        xmin  = args.xlim[0]
        xmax  = args.xlim[1]
        xstep = args.xstep2
        n_x   = int((xmax - xmin) / xstep) + 1
        ax.set_xticks(np.linspace(xmin, xmax, n_x), minor = 'True')
        debStr = "ax.set_xticks(np.linspace({}, {}, {}), minor = 'True')".format(xmin, xmax, n_x)
        if args.debug: print(debStr)
    if args.ystep2:
        if not args.ylim:
            raise_error("ystep2を指定する場合はylimで最小最大値のセットが必要です")
        ymin  = args.ylim[0]
        ymax  = args.ylim[1]
        ystep = args.ystep2
        n_y   = int((ymax - ymin) / ystep) + 1
        ax.set_yticks(np.linspace(ymin, ymax, n_y), minor = 'True')
        debStr = "ax.set_yticks(np.linspace({}, {}, {}), minor = 'True')".format(ymin, ymax, n_y)
        if args.debug: print(debStr)

    if args.grid2:
        if args.grid:
            raise_error("grid2とgridは同時にセットできません")
        #主目盛線の書式
        ax.grid(which='major',color='black', linestyle='--', linewidth=0.5)
        debStr = "ax.grid(which='major',color='black', linestyle='--', linewidth=0.5)"
        if args.debug: print(debStr)
        #補助目盛線の書式
        ax.grid(which='minor',color='black', linestyle='--', linewidth=0.3)
        debStr = "ax.grid(which='minor',color='black', linestyle='--', linewidth=0.3)"
        if args.debug: print(debStr)

    ## -----(軸目盛の数値の書式設定)------
    #y軸の値を10のN乗表記にする
    #「class FixedOrderFormatter」が必要
    if args.x10n:
        xn10 = args.x10n #10のN乗のNを指定
        ax.xaxis.set_major_formatter(FixedOrderFormatter(xn10, useMathText=True))
        ax.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    if args.y10n:
        yn10 = args.y10n #10のN乗のNを指定
        ax.yaxis.set_major_formatter(FixedOrderFormatter(yn10, useMathText=True))
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    #x軸の値を少数第1位まで表示する
    #　　その他の書式指定
    #    例1: %表示にする場合は　　'%.1f%%'
    #    例2: π表示　　'%.0fπ'
    if args.xfmt:
        #xfmt = '%.1f'
        #「import matplotlib.ticker as mtick」が必要
        xticks = mtick.FormatStrFormatter(args.xfmt)
        ax.xaxis.set_major_formatter(xticks)
    if args.yfmt:
        yticks = mtick.FormatStrFormatter(args.yfmt)
        ax.yaxis.set_major_formatter(yticks)
    #指数表示部分のフォントサイズ
    #ax.yaxis.offsetText.set_fontsize(16)
    #x軸y軸の数値のフォントサイズ　　
    #ax.tick_params(labelsize = 16)

    ## xaxis datetime format
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


    ## title and label
    #if args.title: plt.title(args.title)
    #if args.legendloc: plt.legend(loc=args.legendloc)
    if args.scatter:
        if not args.title:
            strtitle = xcolname + ' vs. ' + ycolname
            plt.title(strtitle, fontsize=args.fontsizet)
        plt.xlabel(xcolname)
        plt.ylabel(ycolname)
        if args.debug:
            print('plt.xlabel(r"{}")'.format(xcolname))
            print('plt.ylabel(r"{}")'.format(ycolname))

    if args.xlab:
        plt.xlabel(args.xlab)
        print('plt.xlabel(r"{}")'.format(args.xlab))
    if args.ylab:
        plt.ylabel(args.ylab)
        print('plt.ylabel(r"{}")'.format(args.ylab))
    ## hline, vline
    if args.hline:
        for i in range(len(args.hline)):
            ax.axhline(args.hline[i], color=args.hlinecolor[i], linestyle='dashed', linewidth=args.hlinewidth)
            print("ax.axhline({}, color={}, linestyle='dashed', linewidth={})".format(args.hline[i], args.hlinecolor[i], args.hlinewidth))
    ## plot zero line
    if args.hline0:
        ax.axhline(y=0, color='k', ls='-', lw=0.4)
        print("ax.axhline(y=0, color='k', ls='-', lw=0.4)")
    if args.vline:
        if args.datetime:
            vmap = list(map(date_type, args.vline))
        else:
            vmap = list(map(float, args.vline))
        for i in vmap:
            ax.axvline(i, color=args.vlinecolor[0], linewidth=args.vlinewidth)
            print("ax.axvline({}, color={}, linewidth={})".format(i, args.vlinecolor[0], args.vlinewidth))
    if args.today and args.datetime:
        today = datetime.date.today()
        ax.axvline(today, color=args.vlinecolor[0], linestyle='dashed', linewidth=args.vlinewidth)
        print("ax.axvline({}, color={}, linestyle='dashed', linewidth={})".format(today, args.vlinecolor[0], args.vlinewidth))
    if args.now and args.datetime:
        now = datetime.datetime.now()
        ax.axvline(now, color=args.vlinecolor, linestyle='dashed', linewidth=args.vlinewidth)
        print("ax.axvline({}, color={}, linestyle='dashed', linewidth={})".format(now, args.vlinecolor[0], args.vlinewidth))
    if args.xrs:
        ## calc X-CL,UCL,LCL
        #ycolname = df.columns[args.xrs - 1]
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
        ax.axhline(X_UCL, color='r', linestyle='dashed', linewidth=args.hlinewidth)
        ax.axhline(X_CL,  color='k', linestyle='dashed', linewidth=args.hlinewidth)
        ax.axhline(X_LCL, color='r', linestyle='dashed', linewidth=args.hlinewidth)
        if args.debug:
            print("ax.axhline({}, color='r', linestyle='dashed', linewidth={})".format(X_UCL, args.hlinewidth))
            print("ax.axhline({}, color='k', linestyle='dashed', linewidth={})".format(X_CL, args.hlinewidth))
            print("ax.axhline({}, color='r', linestyle='dashed', linewidth={})".format(X_LCL, args.hlinewidth))
    if args.vspan:
        ax.axvspan(args.vspan[0], args.vspan[1], color=args.vspancolor, alpha=args.vspanalpha )
        print("ax.axvspan({}, {}, color={}, alpha={} )".format(args.vspan[0], args.vspan[1], args.vspancolor, args.vspanalpha))
    if args.hspan:
        ax.axhspan(args.hspan[0], args.hspan[1], color=args.hspancolor, alpha=args.hspanalpha )
        print("ax.axhspan({}, {}, color={}, alpha={} )".format(args.hspan[0], args.hspan[1], args.hspancolor, args.hspanalpha))

    ## x axis label rotation
    if args.rot:
        if args.rot == 0 or args.rot == 90:
            plt.xticks(rotation=args.rot)
        else:
            labels = ax.get_xticklabels()
            plt.setp(labels, rotation=args.rot, ha="right")

    ## 凡例描画(位置指定)
    if args.legendloc2:
        if len(args.legendloc2) == 2:
            ax.legend(bbox_to_anchor=(args.legendloc2[0], args.legendloc2[1]))
            print("ax.legend(bbox_to_anchor=({}, {}))".format(args.legendloc2[0], args.legendloc2[1]))
        elif len(args.legendloc2) == 3:
            ax.legend(bbox_to_anchor=(args.legendloc2[0], args.legendloc2[1]), borderaxespad=args.legendloc2[2])
            print("ax.legend(bbox_to_anchor=({}, l{}), borderaxespad=l{})".format(args.legendloc2[0], args.legendloc2[1], args.legendloc2[2]))
    ## サイズ調整
    if args.adjust:
        if len(args.adjust) != 2:
            raise_error("--adjust はカンマ区切りで2つ数値を指定してください")
        plt.subplots_adjust(left=args.adjust[0], right=args.adjust[1])
        print("plt.subplots_adjust(left={}, right={})".format(args.adjust[0], args.adjust[1]))

    ## etc settings
    if args.reverse:
        plt.gca().invert_yaxis()
        print("plt.gca().invert_yaxis()")
    plt.tight_layout()
    if args.debug: print("plt.tight_layout()")

    if args.output:
        ofile = re.sub(r'\\', '/', args.output)
        #print(ofile)
        #plt.savefig(ofile, dpi=args.dpi, bbox_inches='tight')
        plt.savefig(ofile, dpi=args.dpi)
        plt.close('all')
        if args.debug:
            print("plt.savefig({}, dpi={})".format(ofile, args.dpi))
            print("plt.close('all')")
    else:
        plt.show()
        plt.close('all')
        if args.debug:
            print("plt.show()")
            print("plt.close('all')")
