#!/usr/bin/env python3
#coding: utf-8

#
# pyplot-timeline2 - Vertical layout of timeline and plot using matplotlib
#

import io, sys, os
import re
import argparse
#from turtle import left, right
import numpy as np
import pandas as pd
import datetime
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
plt.rcParams['ps.fonttype'] = 42

_version = "Sun Mar 5 16:26:06 JST 2023"
_code    = "MyCommands(LINUX/PYTHON3/UTF-8)"

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

def mydatetime(date_str):
    # str -> date 型変換関数
    try:
        return datetime.date.fromisoformat(date_str)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e) + " Date must be in ISO format. ex. 2020-01-01")

def mydatetime2(date_str):
    try:
        #return datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(date_str)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e) + " DateTime format ex. 2020-01-01 10:20:30")


def get_args():
    help_desc_msg ="""pyplot-timeline2 - Vertical layout of timeline and plot using matplotlib

    Read two types of time series files (date-text and date-value formats) and plot them vertically.

    reference:
        https://matplotlib.org/stable/gallery/lines_bars_and_markers/timeline.html
    
    usage:
        pyplot-timeline2.py <date-label.txt> <date-value.txt> --delim " "
    
        The delimiters in the timeline and dateval files should be the same.
        When reading data from standard input, hyphenate the filename "-".
        Requires data with headers.
        The leftmost column of input data must be in date format as follows:
            yyyy/m/d
            yyyy-m-d
            yyyy/m
            yyyy-m
        
        Columns with dtype == 'object' are skipped.
        To suppress this behavior, specify the --notskipobject switch.

    input-data1 : date-label.txt
        date version
        2020-02-26 v2.2.4
        2020-02-26 v3.0.3
        2019-11-10 v3.0.2
        2019-11-10 v3.0.1
        2019-09-18 v3.0.0
        2019-08-10 v2.2.3
        2019-03-17 v2.2.2
        2019-03-16 v2.2.1
        2019-03-06 v2.2.0
        2019-01-18 v2.1.2
        2018-12-10 v2.1.1
        2018-10-07 v2.1.0
        2018-05-10 v2.0.2
        2018-05-02 v2.0.1
        2018-01-17 v2.0.0

    input-data2 : date-value.txt
        date val1 val2
        2018-01 107.3 272.1
        2018-02 98.1 262.1
        2018-03 304.2 490.9
        2018-04 455.4 631.2
        2018-05 576.5 731.8
        2018-06 670.5 807.6
        2018-07 875.9 1004.1
        2018-08 888.6 1048.4
        2018-09 687.1 803.4
        2018-10 556.2 720.9
        2018-11 376.7 555.8
        2018-12 231.6 387.3
        2019-01 153.4 325.8
        2019-02 177.5 320.0
        2019-03 281.7 460.3
        2019-04 386.7 570.1
        2019-05 596.7 785.9
        2019-06 680.6 827.4
        2019-07 799.2 913.8
        2019-08 872.0 1009.7
        2019-09 762.1 914.0
        2019-10 608.2 754.6
        2019-11 366.5 540.3
        2019-12 238.8 397.2
        2020-01 221.0 381.3
        2020-02 190.9 357.2
        2020-03 304.8 484.4
        2020-04 366.5 544.1
        2020-05 605.8 770.3
        2020-06 706.9 836.6

    examples:
        python pyplot-timeline2.py date-label.txt date-value.txt --delim " "

        cat date-value.txt | python pyplot-timeline2.py date-label.txt - --delim " "

        python pyplot-timeline2.py date-label.csv date-value.csv -d "," --rot 90 --minterval 3 --grid --xrs 1 --dformat "%Y-%m`n(%a)"

    options:
        --vline 2019-08-01,2020-02-01
            Draw a vertical line: comma-separated dates in ISO format

        --levels 5,-5,3,-3,1,-1
           or -l 5,-5,3,-3,1,-1
            Specify the vertical axis value (y-value) of the label.
            Label y-values are applied in a loop from left to right.

        --dformat "%Y-%m`n(%a)"
            --yinterval <int>: year interval
            --minterval <int>: month interval
            --dinterval <int>: day interval
            --winterval <int>: weekday interval
            
        --tcolor 'tab:red'
            Specify vertical line color for timeline
        
        --acolor 'tab:red'
            Specify font color for timeline
        
        --asize 9
            Specify font size of the timeline
        
        --afont 'Meiryo'
            Specify font type for timeline
        
        --colorful
            Different color text and lines on the timeline
        
        -ccolor color1,color2,color3,...
            Specify loop color

    """
    help_epi_msg = """EXAMPLES:
    cat date-value.txt | python pyplot-timeline2.py date-label.txt -d " "
    cat date-value.txt | python pyplot-timeline2.py date-label.txt -d " " --vline 2019-08-01,2020-02-01 --vlinecolor 'tab:purple'
    cat date-value.txt | python pyplot-timeline2.py date-label.txt -d " " --grid --colorful
    cat date-value.txt | python pyplot-timeline2.py date-label.txt -d " " --grid --colorful --ccolor g,r,b,k,c
    cat date-value.txt | python pyplot-timeline2.py date-label.txt -d " " --grid --colorful --ccolor tab:red,tab:green,tab:blue,tab:brown
    cat date-value.txt | python pyplot-timeline2.py date-label.txt -d " " --rot 90 --minterval 3 --grid --xrs 1 --dformat "%Y-%m`n(%a)"
    cat date-value.txt | python pyplot-timeline2.py date-label.txt -d " " -l 5,-5,3,-3,1,-1
    """
    parser = argparse.ArgumentParser(description=help_desc_msg,
                    epilog=help_epi_msg,
                    formatter_class=argparse.RawDescriptionHelpFormatter)

    tp  = lambda x:list(map(int, x.split(',')))
    ts  = lambda x:list(map(str, x.split(',')))
    tps = lambda x:list(map(int, x.split(' ')))
    tpd = lambda x:list(map(mydatetime, x.split(',')))

    parser.add_argument('timeline', help='timeline file: "date,label"', type=str)
    parser.add_argument('dateval', help='data file: "date,val,val,..."', type=str)

    parser.add_argument('-l', '--levels', help='Choose some nice levels (default=-5 5 3 -3 -1 1)', type=tps)
    parser.add_argument('--x', help='plot single column', type=int)
    parser.add_argument('--xrs', help='plot X-Rs line', type=int)
    parser.add_argument('--xspan', help='set x tick span', type=int)
    parser.add_argument('--linewidth', help='line width', default=1, type=float)
    parser.add_argument('--hlinewidth', help='horizon line width', default=1, type=float)

    parser.add_argument('--outval', help='output values', action="store_true")
    parser.add_argument('-d', '--delim', help='data separator(delimiter)', default=r' ',
        choices=[r' ', r',', r'\t'])
    parser.add_argument("-o", "--output", help="output file name", type=str)
    parser.add_argument('--dpi', help='output dpi', default=100, type=int)
    
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

    parser.add_argument('--colorful', help="colurful annotation", action="store_true")
    parser.add_argument('--ccolor', help="colurful annotation colors", default="tab:green,tab:blue,tab:brown", type=ts)
    parser.add_argument("--tcolor", help="annotation vline color", default="tab:blue", type=str)
    parser.add_argument("--acolor", help="annotation font color", type=str)
    parser.add_argument("--asize", help="annotation font size", type=int)
    parser.add_argument("--afont", help="annotation font", default="Meiryo", type=str)

    parser.add_argument('--vline', help="Date must be in ISO format. For example: 2020-01-01.", type=tpd)
    parser.add_argument("--vlinecolor", help="vline color", default='tab:red', type=str)

    parser.add_argument("--notskipobject", help="do not skip object dtype", action="store_true")
    parser.add_argument("--mtype", help="marker type", type=str)

    parser.add_argument("--line", help="graph type: line", action="store_true")
    parser.add_argument("--step", help="graph type: line + step", action="store_true")
    parser.add_argument("--bar", help="graph type: bar plot", action="store_true")
    parser.add_argument("--barh", help="graph type: bar plot", action="store_true")

    parser.add_argument("--grep", help="Only bar, barh, color the bar of the label hit.", type=str)
    parser.add_argument("--gcolor", help="Color of the bar that matches regex", default = "red", type=str)
    parser.add_argument("--gcolor2", help="Color of the bar that not matches regex", type=str)

    parser.add_argument("--noheader", help="noheader data", action="store_true")
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
    parser.add_argument("--ylab", help="y axis label", type=str)
    tpf = lambda x:list(map(float, x.split(',')))
    parser.add_argument("--xlim", help="x axis limit", type=tpf)
    parser.add_argument("--ylim", help="y axis limit", type=tpf)
    parser.add_argument("--ymin", help="y axis min", type=float)
    parser.add_argument("--ymax", help="y axis max", type=float)
    parser.add_argument("--grid", help="grid", action="store_true")
    parser.add_argument('--rot', help="xlab rotate", type=int)
    parser.add_argument("--seaborn", help="pair plot", action="store_true")
    parser.add_argument("--monochrome", help="monochrome line", action="store_true")
    parser.add_argument("--debug", help="output dataframe", action="store_true")
    #parser.print_help()
    #parser.add_argument("-V", "--version", help="version", action="version", version=_version)
    args = parser.parse_args()
    return(args)

def open_file(ifile=None):
    if ifile == "-":
        readfile = sys.stdin
    elif ifile:
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
    tfile = open_file(args.timeline)
    dfile = open_file(args.dateval)

    if args.noheader:
        df  = pd.read_csv(dfile, sep=args.delim, index_col=0, header=None, parse_dates=False)
        tdf = pd.read_csv(tfile, sep=args.delim, index_col=0, header=None, parse_dates=False)
    else:
        df  = pd.read_csv(dfile, sep=args.delim, index_col=0, parse_dates=False)
        tdf = pd.read_csv(tfile, sep=args.delim, index_col=0, parse_dates=False)
    df.index = pd.to_datetime(df.index)
    tdf.index = pd.to_datetime(tdf.index)

    if args.debug:
        print(tdf)

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
        rcParams['figure.figsize'] = (8.0, 6.0)

    if args.style:
        plt.style.use(args.style)

    ## test fields num
    if len(tdf.columns) < 1:
        raise_error("Required at least one row other than the index row.")

    ## set series
    dates = tdf.index.values
    annotations = tdf[tdf.columns[0]]

    # Choose some nice levels
    if args.levels:
        levels = np.tile(args.levels,
                         int(np.ceil(len(dates)/6)))[:len(dates)]
    else:
        levels = np.tile([-5, 5, -3, 3, -1, 1],
                         int(np.ceil(len(dates)/6)))[:len(dates)]

    ## ax1
    #fig = plt.figure()
    fig, ax = plt.subplots(2, 1, sharex=True, constrained_layout=False)

    if args.colorful:
        colors = np.tile(args.ccolor,
                        int(np.ceil(len(dates)/len(args.ccolor))))[:len(dates)]
        ax[0].vlines(dates, 0, levels, color=colors)  # The vertical stems.
        ax[0].plot(dates, np.zeros_like(dates), "-o",
                color="k", markerfacecolor="w")  # Baseline and markers on it.
    else:
        ax[0].vlines(dates, 0, levels, color=args.tcolor)  # The vertical stems.
        ax[0].plot(dates, np.zeros_like(dates), "-o",
                color="k", markerfacecolor="w")  # Baseline and markers on it.

    # annotate lines
    sdict = {}
    sdict["textcoords"] = "offset points"
    sdict["horizontalalignment"] = "right"
    if args.asize:
        sdict["size"] = args.asize
    if os.name == 'nt':
        sdict["font"] = args.afont
    if args.colorful:
        for d, l, r, c in zip(dates, levels, annotations, colors):
            ax[0].annotate(r, xy=(d, l),
                        xytext=(-3, np.sign(l)*3),
                        verticalalignment="bottom" if l > 0 else "top",
                        color = c,
                        **sdict)
    else:
        if args.acolor:
            sdict["color"] = args.acolor
        for d, l, r in zip(dates, levels, annotations):
            ax[0].annotate(r, xy=(d, l),
                        xytext=(-3, np.sign(l)*3),
                        verticalalignment="bottom" if l > 0 else "top",
                        **sdict)
    # remove y axis and spines
    ax[0].yaxis.set_visible(False)
    ax[0].spines[["left", "top", "right"]].set_visible(False)
    ax[0].margins(y=0.1)


    ## ax2
    #ax2 = fig.add_subplot(212, sharex=ax[0])
    ## set colnums range
    if args.xrs:
        startcol = args.xrs - 1
        colnums = startcol + 1
    elif args.x:
        startcol = args.x - 1
        colnums = startcol + 1
    else:
        startcol = 0
        colnums = len(df.columns)
        if colnums < 1:
            raise_error("Required at least one row other than the index row.")
    x = df.index.values
    cnt = 0
    #print(x)
    for colnum in range(startcol, colnums):
        cnt = cnt + 1
        sdict = {}
        ## set dataframe
        yname = df.columns[colnum]
        y = df[yname]
        if cnt == 1:
            ymax = max(y)
            ymin = min(y)
        if cnt > 1 and max(y) > ymax:
            ymax = max(y)
        if cnt > 1 and min(y) < ymin:
            ymin = min(y)
        if args.notskipobject:
            pass
        else:
            if y.dtypes == 'object':
                continue
        if args.bar or args.barh:
            sdict["label"] = yname
            sdict["align"] = 'center'
            if args.bar:
                sdict["width"] = 0.8
                sdict["bottom"] = None
                bar_list = ax[1].bar(x, height=y, **sdict)
            else:
                sdict["height"] = 0.8
                sdict["left"] = None
                bar_list = ax[1].barh(x, width=y, **sdict)
        else:
            sdict["label"] = yname
            if args.mtype:
                sdict["marker"] = args.mtype
            if args.linewidth:
                sdict["linewidth"] = args.linewidth
            if args.step:
                ax[1].step(x, y, **sdict)
            else:
                ax[1].plot(x, y, **sdict)

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
        adict["linestyle"] = "dashed"
        adict["linewidth"] = args.hlinewidth
        ax[1].axhline(X_UCL, color="tab:red", **adict)
        ax[1].axhline(X_CL,  color="tab:gray", **adict)
        ax[1].axhline(X_LCL, color="tab:red", **adict)

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
            ## an another way
            #for ax in plt.gcf().axes:
            #    plt.sca(ax)
            #    plt.xlabel(ax.get_xlabel(), rotation=90)

    ## set ylabels
    #ax[0].set_ylabel(ser_x_name)
    if args.ylab:
        ax[1].set_ylabel(args.ylab)
    else:
        ax[1].set_ylabel(yname)
    ## grep color
    if args.grep and (args.bar or args.barh):
        xlabelcnt = 0
        for xlabelstr in x:
            if re.search(args.grep, str(xlabelstr)):
                bar_list[xlabelcnt].set_color(args.gcolor)
            else:
                if args.gcolor2:
                    bar_list[xlabelcnt].set_color(args.gcolor2)
            xlabelcnt = xlabelcnt + 1
    
    ## set axis options
    #if args.xlim:
    #    ax[0].set_xlim(args.xlim)
    if args.ylim:
        ax[1].set_ylim(args.ylim)
    if args.ymin and not args.ylim:
        ax[1].set_ylim(args.ymin, ymax)
    if args.ymax and not args.ylim:
        ax[1].set_ylim(ymin, args.ymax)
    ## vertical line
    if args.vline:
        for d in args.vline:
            ax[0].axvline(d, color=args.vlinecolor, linewidth=1)
            ax[1].axvline(d, color=args.vlinecolor, linewidth=1)
    if args.grid:
        ax[0].grid(axis='x', linestyle='dotted')
        ax[1].grid(axis='x', linestyle='dotted')
    ## set legend
    if args.legend:
        ax[1].legend(loc=args.legendloc)
    ## title
    if args.title:
        plt.suptitle(args.title, fontsize=args.fontsizet)

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
