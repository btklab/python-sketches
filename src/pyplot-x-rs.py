#!/usr/bin/env python3
#coding: utf-8

#
# pyplot-X-Rs - plot x-rs chart using matplotlib
#

import io, sys, os
import re
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import rcParams
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

def get_args():
    help_desc_msg = r"""pyplot-X-Rs -- data visualization using matplotlib
    X-Rs管理図の描画
    検査値が毎回の検査で一個しか得られない場合に用いる

    default behavior is to read data form stdin
    if set -i optoin, read data from file

    列指定は1始まりとする
    デフォルトで1列目が指定される

    --xspan <num>でx目盛りの間隔を指定できる
    --datetime
        --dformat "%Y-%m-%d %b`n%a"
        --yinterval <int>: year interval
        --minterval <int>: month interval
        --dinterval <int>: day interval
        --winterval <int>: weekday interval
    --ratio スイッチで変化率グラフを追加
    --rolling で差分の累積和グラフを追加
    """
    help_epi_msg = r"""EXAMPLES:
    cat dateval.txt | python pyplot-X-Rs.py
    cat dateval.txt | python pyplot-X-Rs.py --x 2 --ratio
    cat dateval.txt | python pyplot-X-Rs.py --x 2 --rolling 10
    cat dateval.txt | python pyplot-X-Rs.py --x 2 --style bmh
    cat iris.csv | python pyplot-X-Rs.py --x 2 -d ","
    """
    parser = argparse.ArgumentParser(description=help_desc_msg,
                    epilog=help_epi_msg,
                    formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--x', help='select column', default=1, type=int)
    parser.add_argument('--xspan', help='set x tick span', type=int)
    parser.add_argument('--linewidth', help='line width', default=1, type=float)
    parser.add_argument('--hlinewidth', help='horizon line width', default=1, type=float)
    parser.add_argument('--ratio', help='change ratio', action="store_true")
    parser.add_argument('--rolling', help='diff rolling window num', type=int)
    parser.add_argument('--sigma', help='calc X-UCL,LCL using 3sigma', action="store_true")
    parser.add_argument('--outval', help='output values', action="store_true")
    parser.add_argument('-d', '--delimiter', help='line separator(delimiter)', default=r' ',
        choices=[r' ', r',', r'\t'])
    parser.add_argument("-o", "--output", help="output file name", type=str)
    parser.add_argument("-i", "--inputfile", help="input file name", type=str)
    parser.add_argument('--dpi', help='output dpi', default=100, type=int)
    tp = lambda x:list(map(int, x.split(',')))
    parser.add_argument('--size', help='w inch, h inch', type=tp)
    parser.add_argument('--fontsize', help="fontsize", type=float)
    parser.add_argument('--fontsizet', help="title fontsize", default=14, type=float)

    parser.add_argument("--xkcd", help="xkcd", action="store_true")
    parser.add_argument('--anzu', help="font: anzu", action="store_true")
    parser.add_argument('--natsume', help="font: natsume", action="store_true")
    parser.add_argument('--natsumeo', help="font: natsume osae", action="store_true")

    parser.add_argument("--dformat", help="xaxis datetime formatter", type=str)
    parser.add_argument("--yinterval", help="year interval", type=int)
    parser.add_argument("--minterval", help="month interval", type=int)
    parser.add_argument("--dinterval", help="day interval", type=int)
    parser.add_argument("--winterval", help="weekday interval", type=int)

    parser.add_argument('--layout', help='subplot layout', type=tp)
    parser.add_argument("--noheader", help="noheader data", action="store_true")
    parser.add_argument("--index", help="set df.columns[0] as index", action="store_true")
    parser.add_argument("--datetime", help="set df.columns[0] as datetime", action="store_true")
    parser.add_argument("--style", help="graph style", choices=[
        'bmh','classic','dark_background','fast','fivethirtyeight','ggplot','grayscale',
        'seaborn-bright','seaborn-colorblind','seaborn-dark-palette','seaborn-dark','seaborn-darkgrid',
        'seaborn-deep','seaborn-muted','seaborn-notebook','seaborn-paper','seaborn-pastel',
        'seaborn-poster','seaborn-talk','seaborn-ticks','seaborn-white','seaborn-whitegrid',
        'seaborn','Solarize_Light2','tableau-colorblind10','_classic_test'])
    parser.add_argument("--legend", help="legend switch", action="store_true")
    parser.add_argument("--legendloc", help="legend location", choices=[
        "best","upper right","upper left","lower left","lower right","right",
        "center left","center right","lower center","upper center","center"],
        default="best", type=str)
    parser.add_argument("--title", help="title", default='', type=str)
    #parser.add_argument("--xlab", help="x axis label", type=str)
    #parser.add_argument("--ylab", help="y axis label", type=str)
    tpf = lambda x:list(map(float, x.split(',')))
    parser.add_argument("--xlim", help="x axis limit", type=tpf)
    parser.add_argument("--ylim", help="y axis limit", type=tpf)
    parser.add_argument("--grid", help="grid", action="store_true")
    #parser.add_argument("--subplots", help="subplots", action="store_true")
    #parser.add_argument("--sharex", help="subplots share x axis", action="store_true")
    #parser.add_argument("--sharey", help="subplots share y axis", action="store_true")
    parser.add_argument("--logx", help="logx", action="store_true")
    parser.add_argument("--logy", help="logy", action="store_true")
    parser.add_argument("--logxy", help="logxy", action="store_true")
    #parser.add_argument("--stacked", help="bar or area stacking", action="store_true")
    parser.add_argument('--rot', help="xlab rotate", type=int)
    #parser.add_argument('--hline', help="horizon line", type=float)
    #parser.add_argument('--vline', help="vertical line", type=float)
    parser.add_argument("--seaborn", help="pair plot", action="store_true")
    parser.add_argument("--monochrome", help="monochrome line", action="store_true")
    parser.add_argument("--debug", help="output dataframe", action="store_true")
    #parser.print_help()
    #parser.add_argument("formula", help="numpy formula", type=str)
    #parser.add_argument("-q", "--quiet", help="print as it is", action="store_true")
    #parser.add_argument("-t", "--dtype", help="array data type", default='float', type=str)
    #parser.add_argument("-V", "--version", help="version", action="version", version=_version)
    args = parser.parse_args()
    return(args)

def open_file(ifile=None):
    if ifile:
        readfile = re.sub(r'\\', '/', ifile)
    else:
        readfile = sys.stdin
    return readfile

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

    ## xkcd
    if args.xkcd:
        plt.xkcd()

    ## font
    ## switch stdio by platform
    if os.name == 'nt':
        ## on windows
        if args.natsume:    plt.rcParams["font.family"] = "Natsume"
        elif args.natsumeo: plt.rcParams["font.family"] = "Natsumemozi-o"
        elif args.anzu:     plt.rcParams["font.family"] = "apricotJapanesefont"

    if args.fontsize:
        plt.rcParams['font.size'] = args.fontsize

    ## read file
    if args.inputfile:
        readfile = open_file(args.inputfile)
    else:
        readfile = open_file()

    if args.noheader:
        if args.index:
            df = pd.read_csv(readfile, sep=args.delimiter, index_col=0, header=None)
        elif args.datetime:
            df = pd.read_csv(readfile, sep=args.delimiter, index_col=0, header=None, parse_dates=False)
            df.index = pd.to_datetime(df.index)
        else:
            df = pd.read_csv(readfile, sep=args.delimiter, header=None)
    else:
        if args.index:
            df = pd.read_csv(readfile, sep=args.delimiter, index_col=0)
        elif args.datetime:
            df = pd.read_csv(readfile, sep=args.delimiter, index_col=0, parse_dates=False)
            df.index = pd.to_datetime(df.index)
        else:
            df = pd.read_csv(readfile, sep=args.delimiter)

    if args.debug:
        print(df)

    ## set figure
    if args.size:
        if len(args.size) == 1:
            w_inch = args.size[0]
            h_inch = args.size[0]
        else:
            w_inch = args.size[0]
            h_inch = args.size[1]

        rcParams['figure.figsize'] = (w_inch, h_inch)
    else:
        rcParams['figure.figsize'] = (6.0, 6.0)

    if args.style:
        plt.style.use(args.style)

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

    ## set colnums range
    colnums = len(df.columns)
    ## test fields num
    if args.index and colnums < 1:
        raise_error("index以外に最低1列必要です")
    ## set series
    ind = df.index.values
    ycolname = df.columns[args.x-1]
    ser_x = df[ycolname]
    ser_r = df[ycolname].diff().abs()
    if args.ratio:
        if args.xkcd:
            ser_p_name = 'Ratio(Rate of change)'
        else:
            ser_p_name = 'Ratio(Rate of change)'
        ser_p = df[ycolname].pct_change().abs()
        ser_p.index = df.index
        ser_p = ser_p.rename(ser_p_name)
    if args.rolling:
        ser_p_name = 'diff_sum(window=' + str(args.rolling) + ')'
        ser_p = df[ycolname].diff().rolling(window=args.rolling).sum()
        ser_p.index = df.index
        ser_p = ser_p.rename(ser_p_name)
    #print(ser_r)
    #print(ser_p)
    ser_x.index = df.index
    ser_r.index = df.index
    if args.xkcd:
        ser_x_name = 'X(Inspection value)'
        ser_r_name = 'Rs(Moving range)'
    else:
        ser_x_name = 'X(Inspection value)'
        ser_r_name = 'Rs(Moving range)'
    ser_r = ser_r.rename(ser_r_name)

    ## calc X-CL,UCL,LCL
    xbar = ser_x.mean()
    rsbar = ser_r.dropna().mean()
    R_CL = rsbar
    R_UCL = 3.27 * rsbar
    if args.sigma:
        xstd = ser_x.std()
        X_CL = xbar
        X_UCL = xbar + 3 * xstd
        X_LCL = xbar - 3 * xstd
    else:
        X_CL = xbar
        X_UCL = xbar + 2.66 * rsbar
        X_LCL = xbar - 2.66 * rsbar

    ## output values
    if args.outval:
        str_x_cl   = "{0:.2f}".format(X_CL)
        str_x_ucl  = "{0:.2f}".format(X_UCL)
        str_x_lcl  = "{0:.2f}".format(X_LCL)
        str_rs_cl  = "{0:.2f}".format(R_CL)
        str_rs_ucl = "{0:.2f}".format(R_UCL)
        print("X-CL: "   + str_x_cl)
        print("X-UCL: "  + str_x_ucl)
        print("X-LCL: "  + str_x_lcl)
        print("Rs-CL: "  + str_rs_cl)
        print("Rs-UCL: " + str_rs_ucl)

    ## set
    #fig = plt.figure()
    if args.ratio or args.rolling:
        fig, ax = plt.subplots(3,1,sharex=True)
        ax3flag = True
    else:
        fig, ax = plt.subplots(2,1,sharex=True)
        ax3flag = False

    if ax3flag:
        ## ax1
        #ax1 = fig.add_subplot(311)
        ax[0].plot(ind, ser_x, linewidth=args.linewidth, label=ycolname)
        ax[0].axhline(X_UCL, color="r", linestyle="dashed", linewidth=args.hlinewidth)
        ax[0].axhline(X_CL,  color="k", linestyle="dashed", linewidth=args.hlinewidth)
        ax[0].axhline(X_LCL, color="r", linestyle="dashed", linewidth=args.hlinewidth)
        ## ax2
        #ax2 = fig.add_subplot(312, sharex=ax[0])
        ax[1].plot(ind, ser_r, color="g", linewidth=args.linewidth, label=ser_r_name)
        ax[1].axhline(R_UCL, color="r", linestyle="dashed", linewidth=args.hlinewidth)
        ax[1].axhline(R_CL,  color="k", linestyle="dashed", linewidth=args.hlinewidth, label="hoge")
        ## ax3
        #ax3 = fig.add_subplot(313, sharex=ax[0])
        ax[2].plot(ind, ser_p, color="m", label=ser_p_name)
    else:
        ## ax1
        #ax1 = fig.add_subplot(211)
        ax[0].plot(ind, ser_x, linewidth=args.linewidth, label=ycolname)
        ax[0].axhline(X_UCL, color="r", linestyle="dashed", linewidth=args.hlinewidth)
        ax[0].axhline(X_CL,  color="k", linestyle="dashed", linewidth=args.hlinewidth)
        ax[0].axhline(X_LCL, color="r", linestyle="dashed", linewidth=args.hlinewidth)
        ## ax2
        #ax2 = fig.add_subplot(212, sharex=ax[0])
        ax[1].plot(ind, ser_r, color="g", linewidth=args.linewidth, label=ser_r_name)
        ax[1].axhline(R_UCL, color="r", linestyle="dashed", linewidth=args.hlinewidth)
        ax[1].axhline(R_CL,  color="k", linestyle="dashed", linewidth=args.hlinewidth, label="hoge")
    ## hide tick and tick label of the big axis
    #ax1.tick_params(top=False, bottom=False, left=False, right=False)
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
    ## set x ticks
    if args.xspan:
        xticks = args.xspan
        x_labels = df.index
        x_labels_rot = 0
        if args.rot: x_labels_rot = args.rot
        plt.xticks(np.arange(0, len(x_labels), xticks), x_labels[::xticks], rotation=x_labels_rot)
    elif args.rot:
        if args.rot == 0 or args.rot == 90:
            plt.xticks(rotation=args.rot)
        else:
            labels = ax[1].get_xticklabels()
            plt.setp(labels, rotation=args.rot, ha="right")

    ## set ylabels
    ax[0].set_ylabel(ser_x_name)
    ax[1].set_ylabel(ser_r_name)
    if ax3flag: ax[2].set_ylabel(ser_p_name)
    ## set axis options
    if args.xlim: ax[0].set_xlim(args.xlim)
    if args.ylim: ax[0].set_ylim(args.ylim)
    if args.grid:
        ax[0].grid(axis='x', linestyle='dotted')
        ax[1].grid(axis='x', linestyle='dotted')
        if ax3flag: ax[2].grid(axis='x', linestyle='dotted')
    if args.logy:
        ax[0].set_yscale("log")
        ax[1].set_yscale("log")
    if args.logx:
        ax[0].set_xscale("log")
        ax[1].set_xscale("log")
    if args.logxy:
        ax[0].set_xscale("log")
        ax[0].set_yscale("log")
        ax[1].set_xscale("log")
        ax[1].set_yscale("log")
    ## set legend
    if args.legend:
        ax[0].legend(loc=args.legendloc)
        ax[1].legend(loc=args.legendloc)
        if ax3flag: ax[2].legend(loc=args.legendloc)
    ## title
    if args.title:
        plt.suptitle(args.title, fontsize=args.fontsizet)
    else:
        if args.xkcd:
            titleStr = 'X-Rs Chart -> ' + str(ycolname)
        else:
            titleStr = 'X-Rs Chart -> ' + str(ycolname)
        plt.suptitle(titleStr)

    ## output
    plt.tight_layout()
    if args.output:
        ofile = re.sub(r'\\', '/', args.output)
        #print(ofile)
        plt.savefig(ofile, dpi=args.dpi)
        plt.close('all')
    else:
        plt.show()
        plt.close('all')
