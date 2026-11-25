#!/usr/bin/env python3
"""The Benefactor - RDR2 cut calculator (desktop window).

Double-click this file (or run `python launder_app.pyw`) to open the
calculator in its own window. It uses the same prices and the same
profiles.json as launder.py, so clients saved here also show up in the
command-line version.

Keep this file in the same folder as launder.py.

Option:
    --file PATH    profiles file (default: your user data folder, shown at the bottom of the window)
"""
import argparse
import json
import math
import os
import re
import sys
import threading
import time
import traceback
import urllib.error
import urllib.request
import webbrowser
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import tkinter as tk
from tkinter import messagebox, ttk
import tkinter.font as tkfont

try:
    import launder as L
except ImportError:
    _r = tk.Tk()
    _r.withdraw()
    messagebox.showerror(
        "The Benefactor",
        "Couldn't find launder.py.\n\nPut launder_app.pyw and launder.py in the same folder.",
    )
    sys.exit(1)

# ---------- look ----------
BG, PANEL, PANEL2, LINE = "#0e1a12", "#14261a", "#1a3221", "#23452d"
TEXT, MUTED = "#ece4d6", "#a1b5a5"
FIELD = "#0f1b13"                      # text-box body colour
GOLD, GOLD2, RED, VIP = "#d4a94f", "#f0cd7a", "#d77a6a", "#c58be0"
FONT = "Segoe UI"
TYPE_COLOR = {"vip": VIP, "regular": GOLD}

# ---------- bubble look: rounded, glossy images (name: (border, width, height, PNG)) ----------
# Generated artwork; corners are baked in the colour they sit on. Big images = few tiles to paint. See setup_bubble().
BUBBLE_ASSETS = {
    "card": (22, 420, 420,
        "iVBORw0KGgoAAAANSUhEUgAAAaQAAAGkCAIAAADxLsZiAAALDklEQVR42u3dT28cx5nA4beqeno4IilaoiUk3MCb7Br7B/Eh3/9z"
        "7AK+BEaysePIkihySM5MT3fVHqg4sSMpQABHZPN5ToIA6TCHH6q6u+pNj8+exvullGqtbax5UfrHBwdPDlefHuW+WxwtU07RAuCf"
        "J0WrbX+1q8O4eXm1Pb8eLrd1P6Uu55xb+1CS0ntjl1LUVsepHCyOP3t69POTxdGy1TZtx2m3H652UaUO+KfLqT9aluWiHHQpp/3V"
        "7uqPF+vfv562+9yVyCnek7z3xC6luh9L3z3+19PHv/q09GX7+ubmxXq42NRhqrVGi7CuAz7K6i5Fzjn3pT9ZPXp+fPD00TRMl1+9"
        "vPzdq2kY86J7Z+/eHbu6n1bPjk+/OOuPD66/ubj6+ny8HlqLVFJKKVJEJD858JG0aNFaa1NLKbrD/uhfnhyenQzr7av/+Wbz3Tov"
        "yt/+m7I8Xv34v5nqJ58/f/6bz6bd+Pp//3j19Zs21lRyKm87B/DxF3gp3S6/6jBtXl7tzm8Onh5+8u/PWmvbV9cpp78TuzrW0y/O"
        "Tv/7bP2H8/Mvvx23+7woSeKAO129PG6GzYt16vKT//hZKvnm28sf9e4HsWtTPf3i7ORXn55/+af1716lFKmUaJ7NAXc+eSVHa9tX"
        "19N2/OTzZ7kvmz/9oHd/jl1KdT998vnz0//6+fmX31794U3uiwdzwD1b45W0e31T99PT//xZHafNd1epK38VuxR1X1fPjp//5rP1"
        "/52vf/8698W7VuBeFq/Lw+U2lXzyb8+25zf7q10qKSJyRERrpS+nvz4bLreXX730tTAQ9/lVbcrp8quXw+X29NdnpX/7LC6nlOq+"
        "Hn922h8vL377ok01cvZzAfdYzm2qF7990R8vjz87rfuaUsq11rJanPzy9Pqbi93FNnXeSAD3fXHXUld2F9vrby5OfnlaVotaa25j"
        "Pf7Fk7wsV1+/Sdm5CGAmwUs5rr5+k5fl+BdP2lhzXpTDs5Pt65txM6SctQ6Yy5O7PG6G7eubw7OTvCi5f3zQHS43L9atRvh6GIj5"
        "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"
        "cbEUbaqbl+vc5e5waXEH3PdlXXe4zF3evFy3qd6u4d6+lLj9DmV7frM47MvBolW9A+5n6GorB4vFYb89v7n9jvj277vv39CmnHZv"
        "bnLJy8eriJi2e8cqgPu3plst+uOD3ZvN7s1Nyun74/9lebz662MV++sh5bw8eRQRdT9Fa5IH3IvMRUrd4bI/PthdbDavrn50MOwH"
        "sXvbu83QauuPV7kvdawx1YjkxQVwdz8dbi0tSv/4oCwX29fX2zfXf3sE9sexu+3duNlPu3GxWiyOlpFzm2rcPsWzygPu1GouIpV8"
        "u6BrU735br2/2r7zsP87Ynfbu7qf9te7aG2x6rvDPi9KRLpNnm+PgfjYV5mklErfLY6Wi6NlSmm4uNm8uqrD9L5rTdLjs6cffq+R"
        "S+6PDxaHy9yXaNFqrVNr4+TnBj5O6bqSS0o5R4o6TPvr3bDe1ql++PamvxO7SBE1Wmspp9J35aDrDvpUUl50NrTAR3lAV/djm9q4"
        "HabtOA1jqy2lFDk+fO/6/wMPsHXPgbCKSwAAAABJRU5ErkJggg=="
    ),
    "inset": (12, 300, 300,
        "iVBORw0KGgoAAAANSUhEUgAAASwAAAEsCAIAAAD2HxkiAAAGOklEQVR42u3dQW8bxxmA4W9mdpcULVlxbaCN0XP//39qEPhQQLar"
        "UOTuzkwPFpy46KWOzQ3C5znrRODFN9yh9ktv/vE2PksRLXpreRqml/vxMJXdmIYcwNfqa6vnZTnO88dTm9eUc+SI/usfDF/8de15"
        "yDd/vZ9e3qQU9bwuj6e61JSSjxK+psDey1jKfrx5c7t/fTt/fDr967GtLeX0PyLsrY+H6fD2hzLk0/vj+eFYz2tE/22ywP8tRUQq"
        "u2H36rD/4TDe7o8/v1+O8+cO06fjaG99ut/fvn21Ps2/vPtQn5bI6XkAmoLwu6bh80iM1svN+OJv98PN9Pjzw/zh9KnDcnh911sf"
        "X0x3f3+1HOfHfz60paUhJ/HBNxyHKaWS2tLmj6fhMN785cX6NNe5ppRy9MhDPvx4vz4tjz89RO+pJEdQ+B4jMZUUvT/+9LA+LYcf"
        "7/OQo0fure3f3OahHN996LVHViB8z6NpTr3247sPeSj7N7e9tVymYfdyf35/XJ8WMxAuMw/Xp+X8/rh7uS/TkMe7fUQ6PxxTUiBc"
        "qsOUzg/HiDTe7fN4mOp5qfMa2ZMYuJSc6rzW8zIeplx2Yz2v0bqnoRCXvDxsvZ7XshtzGnKbq88ELq/NNQ05R5iBsOGPabofZ8PW"
        "Xw99BLBxhD1cTEBsdXXfTUJwHAURAiIEEQIiBBECIoTrjNBVPcSWF/YmITiOgggBEYIIARGCCAERgggBEcLVReh3a7AhrzwEx1Hw"
        "XxQOpLDlOw9NQnAcBRECIgQRAiIEEQIbrUYDYrubQpMQHEdBhIAIQYSAXRQQV7qL4lOEyYcBl5UshAHfCQERgghBhOHJDMSWT2Zy"
        "eNMTxJZvenIcBd8JQYSACEGEgAhBhIAIwVYmIGxlAsdRQIQgQkCEIELgMgth3FBAbHZDYRKC4yiIEBAhiBDY/JWHwCa8bQ3+QKvR"
        "TES45BVh2MoEHswAIgQRggh9BCBCECEgQhAhIEIQISBCECFgIQyEhTCA4yiIEBAhiBAQIVzHKw/dUUBsdUdhEsIfYDUasOEoNAnB"
        "gxkQISBCECEgQrj6rUxAbHBHYRKC4yiIEBAhiBAQIYgQECGIEBAhiBAQIYgQuOgrD4GtdKvRwGo08J0QECGIEBAhiBDYaCGMGwqI"
        "zW4oTEJwHAURAiIEEQIiBBECtjJB2MoEOI6CCAERgggBEcI1vfLQNQXEVv/MZBKC4yiIEBAhiBAQIVzxf1G4oYCwEAYcRwERgggB"
        "EYIIARHCtW1lAmK7m0KTEBxHQYSACEGEgAjBQhggLISBK33vKLDZKDQJwYMZECEgQhAhIEIQISBCECEgQhAhIEIQIWA1GoTVaIDj"
        "KIgQECGIEBAh/Km3MrmhgNjshuL5bWsyhM0ydBwF3wlBhIAIQYSACMFqNCCsRgPHUUCEIEJAhCBCQIQgQkCEIEJAhCBCQIRgIQwQ"
        "FsLAn/Q4ag7CltPQJAQPZkCEgAhBhMCGW5mA2O6m0CQEx1EQISBCECEgQrAQBggLYcBxFBAhiBAQIYgQECGIEBAhXMkrD/1qBmKr"
        "t/+ahOA4CiIERAi2MiUfBVxW+ryVyZNRCP9PCL4TAiIEEQIihCtdCOOGAmKzGwpbmSBsZQLfCQERgggBEYIIARGC1WhA+FcmuMJX"
        "HgKbjUKTEDyYARECIgQRAiIEEQIiBBECIgQRAhtsZQJik23ZJiE4joIIARGCCAERggiBrVajAWErEziOAlu+8tCZFDb73VqO3iMn"
        "C7MhLr8wO6foPffa0uBQCltUOOReW+5zTSVHMQnhskpKJfe55jq36L3shui+GcLFvgw+R1fnlqO1dq5lN6TBhia40OOYNOSyG9q5"
        "Rms5UqqnpbdeDpOnM3CZJzLlMPXW62mJlHJERIv1OOchD7fT81NT4DtdSUQMt1Me8nqco0U8X9an6EtbH+c8luFul0qK3qUI3/pG"
        "sKeShrtdHsv6OPelfTp7lsPru+cOa29rK9OQb8aUUrQezViEb3MATSWVm7HcTqnH+suvBUbE8Ntzal/a8u9z2Q95KnlXeu29tqjd"
        "d0X4+gFYUio5lRQ92mmtpzXaF00N//V9MXqvx6We1jyVPOY8lpgkCL/rNqLXVp9qm+tzfl8m9R+FQuEMb1gNFAAAAABJRU5ErkJg"
        "gg=="
    ),
    "fld_n": (12, 240, 32,
        "iVBORw0KGgoAAAANSUhEUgAAAPAAAAAgCAIAAACjCWLqAAADFUlEQVR42u2czXITOxCF+7SkkWXHdgJJFrDIhuL9X+kuKCqXBMj4"
        "ZyyN1M3ChBvg7uNx9bfWbKZOnVKfbjWuP76jP1AiBneOO4ZjMJMqGcarA6iINpEiUhqJEv484v+SMvl5x9ETqZTW8ihV/v7MMF4B"
        "JfbMwfl5oHknudahkNBLffqXpxE4LCMBdZvHTZaxmjUbp2fTxMGHZfQXsYtu3GQd//PcZ0GrcgxhFVuu+XHXcgWIAJg3G6eHjPXw"
        "WN02x7eL7jKNfZY8EkBE/FPNwXXrKLkO933LFQwyLRsn7NJgtFyH+15y7daRgztWekxExBzWqeW2v+9JFGxSNqagagaJ7u/7lltY"
        "J2ImIlZVvwhgHB622pRMzcaEYGjTw8MWDL8Iqspw7FM3bnLLFQ5kVaAxqdwDDi3XcZN96uCY/SwAKP0AmJqNaWr6WcB+FthFL6W2"
        "Ui1sNiZ7m6ZWqpTqomfuXCv1f5suhjEVQZNoK5U7x3BORrF/YtDkw2mBcwyQ5XTGeaR4wDGHNoxzga0jaJxTB5EBsnLQOI/S8Hjl"
        "MEUbZxN2gAGTs3EucsbxDm2KNs5F0ZZyGHRe00psIxwGnclQB4O1CUdvdaEx+b5K9NqEW2khBWIynzam683EFFJopXHbF586Hz2p"
        "zScZ06wFVX30PnVtX7jsMoHSzVLFLNqYpkGLppslgcous5RW+pyul34etZlJGxOzZ23q5zFdL0ufpTQG4/B1q01Wd2/gWG0w2piQ"
        "mkXheHX3Rpscvm7BYAJJld3np7CYXX24BbPaqiRjEmquAuarD7dhMdt9fjqu+MJxt52KxtXs4v3VuMtP/zyOuwPA4GMT0dRtnFKi"
        "oaSiqhIWs/Xd27CI20/fcn84jvXj17JGFQ3z7uL9Jbwbvmz2//Z1GFXV4jzjxEbq4FOY367SzVJr2376Pu7Lr0cqeLl9VEXZc7pe"
        "xssEonEY67605yVLhvHa7qwuBj/vQgpKlL8Pw8NGqrx8cvWboI+PDVWUOx9XqbuIbhbYO4uojZPongBSWzuMZZtzP0ipYNDvsxs/"
        "AF79ekH5QKhXAAAAAElFTkSuQmCC"
    ),
    "fld_f": (12, 240, 32,
        "iVBORw0KGgoAAAANSUhEUgAAAPAAAAAgCAIAAACjCWLqAAAElElEQVR42u3c32scVRQH8HvPzOzs7E52k2Z/pMnmB22arJY2Bps2"
        "KYIIBhI0xAdB9KH2xaoPbUEEQQo+KQgi2D7Ux6ZQJCAiVEkFIbUtiVpKbFPNJmqSJptfu2mzO9nJ7M7cudeHtMH+BdlZzud5noYv"
        "l3PvPffQSFs9eUICWnK4ZbtNUa2/M3I8WZ1sCMaqfcwVlFKC0O4RQsgSzeTs1JI5lsqNTKwvZC3NJ6kKuFzsfEZ3Ai0BNSwWD/ve"
        "72sc6Ir5JJpKF6YWCovrliJRgX8U7SpKiOOKxoj2TJOeTOi2K67ezly8triWt0OavJPpx4EGIJtbbk97+PMT7fGw75tfli7/nP5n"
        "2bQZFwLDjMom1pT6ZGitD554OfHmiw1refujy9Pj0/mqgMT5k0BLQI0t9trR2Bcn2/6YNT6+lLo7a/h94PcBYKWBygwXomjzos07"
        "9oU+O5l8bl/ow0sz3/+eCQVklwsaTzYYFutpCw+dOfRrauO9C/fyJgsHZc4Jx7UZlSWgFIBsB/Xr04e7kzVvn58cn8mHNFlSwnpt"
        "lXLx3Wf/XTHf+equVeK6JjEXs4zKeINICBckoEpWif90J3MsWTNwNDYysW4WXbBs91RvIlrlOzc0bWwxTQXmYpiRBzBXaCoYW+zc"
        "0HS0yneqN2HZLjRG/H2dtcM3lifnjFBAxjQjb2U6FJAn54zhG8t9nbWNET/0dtQqQK9cT6sqYNGMvLhHVFW4cj2tAO3tqIWu1tB0"
        "2pxd2fIrjw8+EPJSoDnxK9LsytZ02uxqDUFrXSCVLtiMAx7QIa8eehCb8VS60FoXgIiuLD20sNZAxNsX42TpoRXRFbBdIePijLxP"
        "Bmq7AggRHJdnVAm7Q0KIAM4J1huoMqoOzglwIgTBRKMKuD4UnAgQHOOMKuQ+XHACAhdoVDFLtBDABdbQqFJqaLG9QuN7FFQBqBBC"
        "AKWUMQw08jzGBKUUsoYdr1bxagURj99+x6vVrGHD7Kq1f29AkbHVDhHvNtwpMuzfG5hdtWBizmiJac0xreRwfEGIvPgcq+Tw5pjW"
        "EtMm5gy4OZWzXTHYHbcdbLhD3my1c/hgd9x2xc2pHCzn7NH7G/1Hou0JfbPIJAw18g4J6GaRtSf0/iPR0fsbyzkbVAWGx9bWDefs"
        "YIvul0sOx0wjr6S55HDdL58dbFk3nOGxNVUBKRwN5S13LmO9cTyebNRv/bVRKDK/IuH/QqR8x80QCWihyAKq9MlbBw426Z9+Nz+X"
        "LQUUoJG2eqDELPGXDlZ/8GpTKm1euDo/kzZ9CqgKpTjTDpEya9gQouQI2+FtieDpgZZkIvjlDwujf+aCKnCxMwqMErPEDzcFz/Qn"
        "9ujKtTvZH29nF7OW4wocBYbKahSYItHGqPZKV7Tv+eijgnN+JH1vwdxO81PDGrczvUeXXz8WeyEZloE+yFjza9ZaviQBxQYmtOvT"
        "Gl0u4mG1Ja41xzTGxa1U/tvfMo8KbCfNTwWaEAJAHcaLDq+r9vUcCB9qCjZH/DW67HJBCZYeaJd76SSgGwX2YL04uWCO/51fzdl+"
        "BRQZ+P/eXP0H3I4rsgZNUJIAAAAASUVORK5CYII="
    ),
    "fld_d": (12, 240, 32,
        "iVBORw0KGgoAAAANSUhEUgAAAPAAAAAgCAIAAACjCWLqAAACV0lEQVR42u3cy27cRhQE0LqPJikJ1sZZ+QP8/98mRBGHfR9ejCLJ"
        "cpBd4GFQZzGrWTUKBXaj+8of37/hkwZU1FVcRUVU0CD6/QRd3dUdVVGohnz+i/8SZejqOhRAR9WRlS3CtaTfrxtqIqa6mq5Ws+oI"
        "FD7G2j+mWVxsGxDJy8w9OgpotjPdUkcDEHG1zW0d6pr77Hivan9P81C/GzVzPh8VKRAIALYz3V5VR80/L7nHeFj8fomX2bOumda3"
        "bvZt1Mzjae9IEQGDTDdc1CLSkcfTXjN9G+KvOz29/tg2Kup42sFSptPEWgAcT3tF2Tb+znJDFxeR+XzhBzOdcas4ny8iooujoVDo"
        "0LjMimQ30xl7uiLjMnUoFKpugORLMMx03k+PfAlA1E3FpaM6E9wG0mkj3ZkdJS6qqpXJJaGzq0xVVYiguBmkk+8MAVRDRLkW9H/C"
        "QBMDTcRAEzHQRAw0MdBEDDQRA0303wa6G8qLSYTTP81SQbdWlZpxRej03WxWVdrR4ipm4LACOqsWM3HtaK1IoO3OeUGJzjvewO4c"
        "6IpUFGqWr0Pd+ASLzhhndfN11CwUFII6orvHw8onWHTG9yrjYe3uOgJyPbYr5D7VdXncXhuc6BSfGsDyuF3HzaDezqEFHR371GHL"
        "4yZu3c0tIt3yff7uFrflcdNh8WF4kt1//fJ6jpfdWbq4bUNMuhrVrGu6zVFgfr+Mh1VE8uUfR4G99fRfhy5uq9vqHdVZHNZItzas"
        "UVwB1Mx/HdZ4zX+j9qjjdZyuLm4cp0s3Nk63Lvk+Tvfntv0BI+c53rkBoXgAAAAASUVORK5CYII="
    ),
    "tab_n": (14, 60, 32,
        "iVBORw0KGgoAAAANSUhEUgAAADwAAAAgCAIAAADBiozFAAAAOElEQVR42u3OMQ0AMAgAMJgGLgTgX+JeLJC0Cpo1Hde8OEhaWlpa"
        "WlpaWlpaWlpaWlpaWlpaWnr7VwgAlMndVUwAAAAASUVORK5CYII="
    ),
    "tab_h": (14, 60, 32,
        "iVBORw0KGgoAAAANSUhEUgAAADwAAAAgCAIAAADBiozFAAAEEUlEQVR42s1Yy3IbNxDsAQb7IilLlpJDUqmKc8j//1FOOaSkilmS"
        "yN0FMNM5kLJkiY50MGlhcSH3gUZvb89Drv78BS8GzSGSlm2z6nTRaJ8kCAgIjjUICOisY6mbnO+mcj+DlBheXqtf/RLASaK9GLqr"
        "RRpakF7cNpm+g8yjoRaAEiQ2mq4W/U/Lsp2nm828HkWAHWUHQdMYUlz9ep7OO2abP29tqnAHQYCkiIgcgW2SJGR/IITYaVq1y98/"
        "tuvp/u+1F5PwuK7s5SFgpQ7N2aePEkNej7bNJEQEAhIhSNKkMYYQ+L0ZdtLMSi3mLgC4IwhxaJrznua3f/1bt1l0z3ccLlcA6NQh"
        "nX26hGO+ubepPpJKqMa+7ZKqQHbLfMcJQCAaYlIVwMwBiAggPpuNRbum/diXzezZdpDicLkCETSc/XEFYr6+h1PCXr4Ek2rftgBI"
        "B3ikuROgxgiguu03IwJn3eY4NO15n9cjHBDE4XJFcvnbRezSfLOh+VPVi4S2aXGqQSLE4O7mvn8NAjhttrRqY5fm9Sgisb9YNmdd"
        "//Myr0efKp7onWRKSTXyiKZxQOIQMbMnfwnM6Ww+dDZVm2oA0F0uPJttyzNnEZEYApxHE8WBSSKIhKceRSCIbYtn6y4XADQtGu1S"
        "Xo9039vKozYEhJ+Q5udaeYKbzno3N+d9WjSqi9bJOhcE4aE49WMAv1w6SJ2LstNFq9ori9H4MmqQdGeQH4HYD3xHdLKY9hpimzzb"
        "3t+e30x3Ezk143Qj/cBeCM8W26QioDl4ILUQotYSJeCEuAVSawWBl2olaS4C5YM3HEZF5FoabU7jegIpVs394Pf0JQ7pqw9y91yz"
        "RhWR40EXCMFq9SuH/sZQkA/z27jNinsIIYRwjCyP5C5nIvmKCZIg9Y3ckTSzt9BwAnNRPmzgFfRyZN9+w/O/CELp/lBE/W85xeOb"
        "81uuENBdfbagUeTY1dT3eBnCoNFn0zqV5qyDBPBdIwYACUFDvp20bnNz1oU22lgg8n4Rk7FTAHWbtU7F5qpDY2N552Tr0Nhc61QC"
        "iHw7hRhjl94vaDJ2KcSYbycQQYKUzVw3c7NsRd+lsknR0CzbupnLZpYgcbhciYhNRRdtaLRO9SF5es0Ej26BsjdnkebDAGK8vtud"
        "e2wh2FzTsomdeqm7ZOrHU+wMKbTnvQQZr++9Pm0hACLi1W0uOrRpaOhkdZLypSQ+JcW7bhZE+9R+GEhM13c2PzaZ9IkJimcb/7lt"
        "L4Zm1XtvdZstG9xPqXMBEIK2qkMTNNYxz5+3NH/aFtPnMcc43txr36Rlm5atEjTz4qQfn3CKhJCCxCgCyzavxzpmgTwLIHogsYXU"
        "bbYxh1a1TaGJsVU5SalIpxezca5z8bmSOLjufxm+12ea5tXNAAAAAElFTkSuQmCC"
    ),
    "tab_s": (14, 60, 32,
        "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"
        "08SOJfm6Ru7f35JQSCNLrnAAAAAASUVORK5CYII="
    ),
}

# ---------- sprites: anti-aliased pictures for buttons, tiles, tick boxes and chart dots ----------
SPRITES = {
    "btn_n_L": (
        "iVBORw0KGgoAAAANSUhEUgAAABEAAAAiCAIAAAA24aWuAAACtUlEQVR42o2V3Y/bRBTFz50Z24mzcbJJtigIpBb6Ia1aBIWqD0X8"
        "+7xRgQSlPFSVQCqU3WabL9vj+8FD0m1211n2vI5/PnOPz4xpcv9TtImIAHDDzJwkoRgOBuPh6GjsvAv7AGFmlsOj0e17dybTW2mS"
        "gFCXtTCHVqCu6uF4ePz40WR6tJjNT9+8Xc9XTWxM1QC6urcmxi+P7z387qvZv+/e/vWPN+p2u0mSbLdLuOzDTfPtD0+nn0//+PkF"
        "l3E0GockqJqZwcwA2EWGG/7m+yeDw8EvPz7P0mw8mahajBGg3cfC+Qyxjl8/e1wMi5fPf82yrCiKpmlaEwrnwO0Hd46mt17+9Jvz"
        "Pss6qmpqFw12GBHpD/t3Hz14/fsrYfHBOyJhNrQrEJGwfHF89/3JbDGbJ2liZmbGItjHCEv/sBiMhq9fvPLBmxkRieom2D2MyCef"
        "TZfzRV1WOybsyRvadxd88MWomJ+cEUFNYTAzZobHXqZ7kJOj9WIFIlMDtgyBsI/JD3JT5Yadd5sPvUkSgHOunekVB3UVVXWXAcDM"
        "zrnWJAJg3DT2QbtrIkLnJ2mX0Q9Pqxns8gCb+S772I6uLrfPUy7X+UFOBFPFzRTKZakwENnNTACEel0JS0iTWNXX9OVy36pVmfWy"
        "alW64HADM0dE70/OkjwjR6Z2EznnXbVYxyp2i1w3/f8/KweCAWd/v+sUufNeRQ2m18rB4Jwr5+vlbNmbFNsjDVwT47aFzruzN6dq"
        "2h32mHkDqLbP5/Nxf3v1gKr5Oh/1nPexrDdFM7RlsHPnQlVnf56GTuhN+gBUpDWPjz7bF5tV8zLppJ1hrqwS+epgF5ht8Q31slLR"
        "rOiEbgqYipicV9/a/iUEIoqLqlnVSS9N8jR0UxUxUWU1tbAvUHIEIC7quKx98C4LPvU+CyD6D8ZPGa6Fdz4FAAAAAElFTkSuQmCC"
    ),
    "btn_n_M": (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAiCAIAAAARTyRGAAAATElEQVR42m3JwQmAMABD0RCLRaHe6zoe3cH9l0jipSKCh8ALH8d1"
        "sm1tqm3h3jvtUBJtUTYljT9s0Xrb4yS/A0DbBMAkX8ucamFZ5xuoM0xMyDvMFgAAAABJRU5ErkJggg=="
    ),
    "btn_n_R": (
        "iVBORw0KGgoAAAANSUhEUgAAABEAAAAiCAIAAAA24aWuAAACsklEQVR42o2UW2/bRhCFZ2aXFC+i4KAwEjR1IzvXGkGAFO1T3/ra"
        "39A/XqBufJEUQRdSkiNR5O6cPrBx6oRMdMDXb86ZnRny73/+wcyrRZ4v8tWyqPZ7EQnCkIgAUJtsNshE+PjRMYt454pl8e6vi9l4"
        "ClAQBq2YiQZxPlsup7N8tiy3ZdJPnp4/f3x6Un7YrRa5sYaZP2d+/u2XLMvStJ/EiYBui81sMhWRn96eJ1n6/mpCgIjcY56+fnHn"
        "b4zEURT1ok1ejK/G35+e/Pj8yfjdjau9mE+YOT1/ho9ShVcFIYoTKK4vLtOs/+Tl2fjyxjt/52aG52f4Qqo+DAMQTceTOE2Gr85G"
        "F9cAmt7Eq7Z+zvkwCMNeb3RxDY/Xv77xtWsYc/JyiDYpPDHXdU1MxTw/eTGsyn2xKIw11ntPHRJmEECkzo3+vhq+OpvevAcg2i3v"
        "fdOcWFPMcgAPf3hUV/XXfIhIVQEQGMBiMjt+/HByObJeOxkomopQZeFNsRkcP4iz1GqnDztXq+rd7tT7qt7vs6OB9artJoBrTAAi"
        "YmZAq7JKB/32fgDo/VogEHG53SVZvyUbWi8HBMDVDtDObK3mADxgu46xgyFSPZhhhmrQC3bb3eE+ICI2ss1vD2ZALCxGtusPhzJQ"
        "jdLYObfflocxTApEg2STr73zcpCJ16AXSmA285UYsfqt+TCzKvrfDdbzlatqsVa+PkEi8rWPj1Ln3HqaizH0zZl658O4F/aj+T9T"
        "EDUb3p6t2X/1GsRh/CBZXs185Vj+OwrbdZ4EigZxrx8Xo2W1q8QKfQz0eTYoiMiEJjpKCZTfzH3l/w8QkVX/KRsLm9AGaWgCU92W"
        "u2JLRGyY7rdsTc8Sk1gjRpp6rqy381t1npuf7RdvZG0SEhGcur3za6e1h1cWYSPU8aL/AuH9LPfwQwxiAAAAAElFTkSuQmCC"
    ),
    "btn_h_L": (
        "iVBORw0KGgoAAAANSUhEUgAAABEAAAAiCAIAAAA24aWuAAADgElEQVR42o2VTWhcVRTHz7nvI/NmMvnoDPmcxElHMjRtQk2p1tZU"
        "cSHShVK0tCpuCn6sRRQrLty6cSWKuhIXIrhRBFE0GBCFgm0IUfoVNU2m2HZmksy89+a9d885LiZjp8mM4+Es7+/e//mfc+/F9OQI"
        "tAqFqBRWvMCrhd3xrvw9gwdyw4f2jXdZhtkSMA3l+qEfRAfzmeceP/TgTM5xHC1wo+hW/HAngwBKqdsb7oHc8BtnH3tgOnfh2q0v"
        "fv7r0mqpXPUjzSyCzdoQEUDKW/7LTx1768UT84trn89fKlZ1T8KJx2zTUAgACGYzICJbbvDRm2eOH9537uOF31Y3MwOp8UGLmEWE"
        "mLeVNwAAkC239uG50+NjI2ff+RqVuXd0QBPXwhAB76r2X5eKW94Hr5/KjA69+v73fd3xdH9vLQxB4O71DcYwVHHTfeHJI8dmJ196"
        "99tEzHJiXRGxiLR2VSF6tWgqO/Ta84++/ekvtVB3OzYgEmloEyYq9IPolWfnflwq/Hr1ZrrXIWYQIaYWsuqFuH44nRs6mB/7bP73"
        "pGORZhAhIiZmopZp+kF08uGpiyu314tuKhkjZgAkIlSqrbaEY8/mM1+dL9gGMrMIiLAmMgQA2niwd7jfsqzL6yXbVPVDBETrCMz2"
        "zOR4OtRcrtYSXbaI1NcREQioNvLMqYmBGyVXa4YubvRDAFCTVqKwlXWmpbDihcwM0tzDxmmIuzGTiEFYtmPXnsKyfUWaZwcFEUBA"
        "BNoNyw4z1JXrpaG+mFJYH/j/E+ry9aKlJG4bzM0i/5O5VijrKMqk40FEICDCHVNtusHKenE62+8HBFivqkMqyzC+Ob9yX7avO2Zo"
        "qjveSVu3Y124crO0UTm+f7DihYggnQ5SgCAin3y3fGJ2ONVjB6FG6FCQ4exJxmzjamFjZE/8kZnMwvLftqlAWj4Ejf4AALMkHfu9"
        "Lxdt0CePjBUrASLUHWwZRjyVbLyGsLC09vRDE/1JZ/GPsmWgoZAbo96c20z9jfYD+mm58MzcxEy2/+KfZTcg20QFsGOk7jAiYJkq"
        "COmHxbWZbN+po9lyNVy95QURGwqab8Udpo6ZhiKRhaVCxQueuH/08L0pYtnwooqv/ZAikkgz7v5/EAEBq7XIsc25/UNHpwZ7ErFS"
        "NSpWo0LZ9wLCtn+WQmap+JFtqkwqkc/05oZ7MumEUuofUJfPMrd3bjEAAAAASUVORK5CYII="
    ),
    "btn_h_M": (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAiCAIAAAARTyRGAAAAXUlEQVR42k2KMQrCUBQEH2Nj90EEwSZWYpkb5Daex9LreQghxd/d"
        "FFH4xTDDsvV+PTmdL4dPP3KfrnQZy8hCMraQjTVa++e/2SQZMEmRhErwzxm6KnzXznxrLI+2AVPXUoOlfoI9AAAAAElFTkSuQmCC"
    ),
    "btn_h_R": (
        "iVBORw0KGgoAAAANSUhEUgAAABEAAAAiCAIAAAA24aWuAAADlUlEQVR42o2VXWgcVRTHz7lzZ3b2Y7K72TYJaVJWU0o+xApipTWl"
        "EaRPaqH1oRQV6oMPfoBvFnzyQfx6EEGkLxZEURH7YqVV4ouVtpiE2qbatLKJpm2STUKy+dhkd2fuOceHSUNMJrGX8zBc5jf/c+78"
        "z7l46qOXlcLBwsT1wtiNkYmZuWXbttJJFxGJGaKWzm5rsCz1QueumI3G94dGJr76sf+XKwVmSXtxJpYNDO599hACaK28uJNvSj/e"
        "0fxEV3NxevaDz3vPXxrKenGFyPIf0Hry0IFcxst4KTfmzi2ZvlvF3oG/3bjz1omn2pqz5y8PiYCtLVmD4bFXXlx5AkBESylDPD5d"
        "8lw4eXyf5trRN08vLFUTMWe1PMXEYRCxMVT1AyJqacgS6Dc+6b1+Z/G7907UJWJVP1AKVxhiWhvMREyVmu8l4g1Z7+Mzff3DpTPv"
        "v2RryxhCRABQtA4iJmJmDozR2m7MJk+fu1aq8IevP7NY8REBAKzdezpkkwUAQRDYFl78Y+y1I3tn58sDQ3cTcUfdKyciQlIpLFf9"
        "T89effW5/V4yRsSKI5MjYiJjjIgQk+faFwbvVA0ePtBZWqxspUMUioEIMMsPv408vb/ddfSWOkREBALE7DrW74WpXNZra8lpYoLo"
        "hcYYFg5/iqXU9Hxlcq7y6O5mzRRtXhEhMgAYekYhG0OTpeWuBxo0UYSOgPCKoRkAAYAZLIX/FBe62+t1VJPIPUfiyhcABBAAFio+"
        "ImiOYta+vbolwihCxFpEIsvZmK0IIAqCbMZsPEUMDO3cnhwtlu6XYREEyCadqzfHtQj/vwYAEaTiuqHOuVaYVKE1tg4ArNSorcmr"
        "1WqFsfvMDcE3dPChxouDt+eXamprCRFBkOVqsKvJa62Pnesb8eIxzVvqIIAAGOLne/I/9Q2Pz5SzqZiGzRkBsBSWyv6Rfa1Brfrl"
        "zzfqEg6JqMiuDlvUQiiVaw/nMz2d2979pp9ZFCIIROcWTqXZsr8nnzne3fL2F5fHphdTcTucxOtzQwRErPpkiA8/tqOnK/fO1wN/"
        "js6kE87q6NahtUJLkkDNJ0PyYGPyWPdOoeDkZ5fGZsprAQDQS1UDAMSCCClXtzd73R251px7YXD821+HWSTl2usuB/1IPq0Qd9S7"
        "9Slne51NRFcKU6fOThRLy17cVqg23ib6YHtaIRZLy3/dnvr+7tzoVHmxEiRdO5N0iCXyhP4F0lvg+/xk3aEAAAAASUVORK5CYII="
    ),
    "btn_p_L": (
        "iVBORw0KGgoAAAANSUhEUgAAABEAAAAiCAIAAAA24aWuAAACvklEQVR42o2V3W/cRBTFz70zY2/sbOLU290qSAhKmyI1gIQawQtC"
        "/MM8VkIC8QAVCKlIQTwVCRVKv2iTbDcbe+z5uDzsdvPlDXs0TyP9fM+9PjNDg51tdImIAHjnvfMm0ZtbRTHYujYcKMV6GRC89z5c"
        "u16+/+HNcjQAKDh//GZia6s7gcY2RVns7n1SlFvP/376+y/749dHtrYxRolyiSE0trm9u3P33sePH/3520+/wku+ng8H14lo5vgi"
        "4xq399Xn5bD84f731Xg6HA2TJIkxxhgBQEQuMN65e19+ZrT+7utvUpNsv7MdQmjb9sJ39aKHtmk//WJPafXztw96a72yLJ1znRPi"
        "BfDenZtFWew/eGgSk+c5QAJ0Lg0ghNAvNm59tLP/48MYok6MVjrEgCXSRBR8+GD39ou/no1fHaVrKQREFGMEqNtb8GFja7O/2X/y"
        "x+MkTQQCgkgUEZHYuTj4MHr3xuG/B7aySisCvS2yrB1hZVS/2Dh6eaC1WsQsxAihJWVEZ+s5gGpyorQ+ZUJg5qUzyPpZ8CF4z1pB"
        "5rsicgWms428qa0ATCwLCJiFhUCXh6cBBOcZNHN1ViJymtyzTIwiDCK+zJzFzzEiEQDxPOerSNfTKhtlzEwAVqN0Pa1lJEqzyKqV"
        "dFNZH4Lppa5uVmWCD/W0TvPU1S0xne+2W0xEk4OxWktYzcP2v2JWbI8ra23a70mUVezx7HeNnx/q3CijADATXy0IiNkeV5PDN2az"
        "RwCIMb+XlnibZ0Px+MXYulatJxRBNLspuqWysr+IlJ1Upp+aRJMDEYPBxEvrzKAY4/ifgzq2MWfQ216vqDM7cCLSHFvR4FwTiIWY"
        "GOebO8fMz6mgPWm88zElGCIiJmacmux6SwhE1E4bV7U6MyZLjDGaFYMZzCC9bDjEBMBNW3/SWs2cKDaKjSLCf9CvbnQlNH7pAAAA"
        "AElFTkSuQmCC"
    ),
    "btn_p_M": (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAiCAIAAAARTyRGAAAAT0lEQVR42m2Juw2DUBTFzjWbkFnSsgP7C+XTPYGuKUKDlMKSLee5"
        "LuxjTNv7xWOeUeluVEyuFm0SsaXj7ysaEqmqvyQBuHkSqgoKDprP+J4cvi4vSg95YAAAAABJRU5ErkJggg=="
    ),
    "btn_p_R": (
        "iVBORw0KGgoAAAANSUhEUgAAABEAAAAiCAIAAAA24aWuAAACu0lEQVR42pWT3W8TVxDFz8y9u2sn2AJUk5jIVoSQIAgBbSr1DZ54"
        "7d/QP5Nn1L4VgYSgolIEATuQZOOPbfyxd++d6YOLYyW7kjual9XVb+ecuefS899+JaLR2WCYDobpMJ/nzBwnMQBVRVlZl+fM3O7u"
        "dO/uMnM2yj5+ODjufQM0iuNSjBqdmwAW/25cb2512p073eDDu1dvjw77cRIT0SWSnjz7eSFDVQvnJpOpl9De3dnbf3h02H/9x59E"
        "ZIxZxejx0/2LDyJmFpE0Tb2G/ae/JPXk9xcvvXPG2iVmbnW2daVERFUbjYb48OHt+/rGxt6PD/qHveADM18wV12KSC2pgejw4FNt"
        "o7b308PewWdVJSIAptXdLl2oAswskJP+8Q/tVuv2Vv9jz1oLwLQ6W6WMqDCzKxwTnx4d3310zxd+dDow1rKIlrYKABgybDh4+fvN"
        "X7v379goUlVWlcoWWVxDFEfp0Ymb59vdduEKBrSqRYJCmZmIiOjrp35rZ4sNc+UYRRBd7spG0fhsbCO72di0gvIgEuCDXwCL6/au"
        "mE1njRtNWxVeERGRVQaAm843m9cqGNWwAiwgZp5PZs1bN2wZcmFjVSszBR9U1aLMz2UAAIGIQQgituS4YieLjUP/DwMgqsWzyWxt"
        "BmBituZ8lK3NqJrIcMTT7HxdRlXjelwUPp/mazOguFnPBlnwgddwT1DYWqSMf87GbNguX3mVJhCUkFyvZ+nIO8/WVGtTKAAmiNhG"
        "kud5djJmw1CtHsIgBik4sRLhrJfq98SUa1sckwAxhQTDL2lwnvg/RbZqhiq0RoWRrD8oZgVZWgbzsh8CASoMH0nu8snXLLiwCgCw"
        "TKvaNLB6Dk58Ppzl47lCydCl6FvPAmiAComX4AtfTJ2fOvFCTAS6+lbsOM8AEh+CC+KCelFRIlo6vlr/AkMB5XoWpro6AAAAAElF"
        "TkSuQmCC"
    ),
    "btn_d_L": (
        "iVBORw0KGgoAAAANSUhEUgAAABEAAAAiCAIAAAA24aWuAAACQklEQVR42pWUS3PTUAyFj3Sv7TB20keYLtpCWECYTgv//6cwhU6z"
        "AFZQmKR24+sriYVb0zyctpo73n3SObIkej09xrYgIgAxRhHx3hdFMRwN9w/2mdn3ASIiInt7eydvTg7Hh0mSANSEICJ+KxBCGI5G"
        "H6bvx+NxWZZ/bv5WZRVjNDWDbWFCCJN3k+nH6Xw+//b1KjbROcfMaZISAcA6E2O8+HxxdHQ0u55VZZWmaZomBsDa2GBijOefzoej"
        "4eWXSwOlWQZAVNfy+s5D0zRn52d5UVxfzbxz3jsVQatmk2mB49Pjg8OD66sZMxPzvY72u8YQSEXzPJ+8m/z4/lNF2DlT3VrhoQ5B"
        "VE7fni7mi+q2dN6bKro624JFJC/yoih+/7ppJRmw+3lVHY/HVXUXQnDetelFlXZoc+zyIi8XtwBMH+np1+azVxkRLZdLAv57MLMd"
        "dQaDgarGGIm5y21AL9EyITSqxrQiZkffPACRaLAdBtYZNTU1M9PnM/fjai+pUy/rLMt2G9hg6trMQPQCpgmNiDjmGOOze6Ba17VP"
        "fF0HZnoOw0RUlZXzjuhhf58KJqJQhxhjkqaq+uRQW7fb5aIsRkWo6X7bdvaDu4NWL+tskGn3v/oXibsbUpWVmqZpoiJmMPTa48dF"
        "y0UJgk+8iZoqzKC6+VYYGO7KO3acZAkMfS1ZZQgwLKulqvrME5Oaqaquatu41wQATd2wZ3ZMbCrt4MNgBNpyrztSRVWUmIiJumk0"
        "wPqYzqCaqYFAICICAYR/wTXr0RhI6FsAAAAASUVORK5CYII="
    ),
    "btn_d_M": (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAiCAIAAAARTyRGAAAAR0lEQVR42k2LSwqAQBTDOhX84IgncuUFvP9hGheD8haB0hBdz+1+"
        "9Gk+d2/r4iQOmI9kII2/+CQWOGDVpiL9PWCVTbCa3NxelDhKGMMu4WEAAAAASUVORK5CYII="
    ),
    "btn_d_R": (
        "iVBORw0KGgoAAAANSUhEUgAAABEAAAAiCAIAAAA24aWuAAACUElEQVR42pWVT0/bQBDF5+2O85eq0FRNKFURoogjVD330k/Q76+2"
        "l6aUQCHESew49s7rwRAgcQKMZk/2T/Pm7WgWX79/EyCO43gUj+NxPs/hEEWRiJCUqtD21isAnU4HQBGK8Wjc7/ev/l2RjKKoEvO1"
        "1634Jh5eD0ejUZbNW63m/v5+t/cuy7I4jr33FczH4wNV9d47oMjzeDQeXg81ig4/HTabjcuLSxFxzj1iegd7JEUoInBOvRdgEk+u"
        "r4fdXnd3b3dwPgghPMSckfdpFswoEtUikj9//Mpm89Mvp6pqwQDcMlwNMwsBgKqe9c/SJD35fAKHhR9VTKnVTEQ00sH5hZFHx0dF"
        "UZSlHM2qkxRSSOfc2e8/2zvb3V63yAsA65kFKVKEMPh78f7DnldP0pWWbUrSOTcex0J23naKonjs22qa3RnDm5vRzpsd55yWva6L"
        "+9kBksl0a6vdaDTU1gyirAxpnud5nrfbbeV6ZumTkfk8b7Qaahu1LUWWzevNmsoGbSt1QyjEahv7WUbEyMDwsjpipHGTB0thNKc+"
        "y7IXMBQBJE1nL2AAAMjSZ9chJappCCHP8+cyRkb1KEkSM9NnVvHeAzJL0qdndNF9q1FPp2koDA4b65AC0KzeqAcLaZLCQUSe6IfB"
        "VL1XPx1PSJb7QKVSGyAiNDp1WtPpZBoe7KpqbYulo5HO0lkowgJY1sa745zzkQcwS2Zm9hAQEaWVfxICgQBw3sPBgoUilNe//JYI"
        "RETgAAEAgZAM8yAUQbUxWtp3e9lmtwsKawER+Q+2CxMUhf1saQAAAABJRU5ErkJggg=="
    ),
    "acc_n_L": (
        "iVBORw0KGgoAAAANSUhEUgAAABEAAAAiCAIAAAA24aWuAAADNElEQVR42o2VzW9bRRTF752Z956fYyfNlx0nTeKGllgECVAREgUJ"
        "RFWEoFKlglgAFVJXXVawZMcWwT/C34DYFFEJEAKFtEgJBSonaVU7cezn9zn3sHBK3MRucnS3vzmjc49meOrZWRokxawUd7pxFKd5"
        "3106Xaqdqby0PO842gwEtFbdKInj9Pmzc1cvnn/z/DMLpZEx35DEsNlhhpkUq2YrWFmq3Pz40uXXznmy1241Ow/re0ksIiCYJwEm"
        "wk47uH7lwpc33vOyxta/fwh5rj9mRiec3pFEph8AEITxN59/eP3dF+6v/x4lUhifV8YFhAAQEXDAMBMRgjD++rMPPnnr7N3fbjle"
        "sTi5CLE2DYm4/zrm/5R22+FXN69+9MaZP1d/8nIjXqGcpTERDgH7jNZqp9W9dvmVa2+vbNz52Wit3QIggGUiHEnVKOYwSmrV0hef"
        "XqzfW4NYNoaUkSyhQQARGVYcJ9mN91/3ZPdhe8d1XAERIDY7cqnHTBAmtWr50svV7fpdow0AkIi1xEJDZOIkfefCcx6CJA4dxxWA"
        "ALEJsR7K+J776srpYK/BzCIgBgFZFivt9bYxgFmYGZ+dyAWdB8QMCIGIYNOYSA31WZqbLHi820yU0nicE2xGFLEa3GBTW5xmG4sI"
        "s+7P1mYJK2Ee4Ga0YrEpBFA4tA/YlJgH9EBERCAEBgbscFAMhogE+xqy9yPMRr2RYYFAgNDJZDbqzSASpTQEw8py+Km4/6BVb4aO"
        "61qxEJxkVKcbr9575HgFsRYgnEBKa/XdL38llCNWApETMHp85tRWo1Orlhem/DjsMO+v6SmjiMkKvv1+TZxRUgY43kn7E8Wcq//e"
        "buX93IvnKt2gpfiY+HR+skhEjtG/rm/XqpXF6UIYthWr4xlmFtDttXqtOjc3kY/C4Clu+wwRGaXCxP64trlcnZ0vjUVRAAgzo1e6"
        "vjlgQOQYFaf2h9W6748sL84wSZrEBBBxP3XA9EpstMoEt+9s1RtheXpyanzUaIZkEAuAAAKeYHpuSrFr9Ppm69bq5j+PIjZ+Pl90"
        "Pd8Yl5VmrXnon6VYBEGUukaXTvlLlbFquVgtFYxW/wFAozfoUwA6VwAAAABJRU5ErkJggg=="
    ),
    "acc_n_M": (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAiCAIAAAARTyRGAAAAUklEQVR42k2KIQ6AQBADySQIBJo38DC+QoLgbRgEBoFCo49tMSS3"
        "YpJ22mZdpubZZq7zoB9GLKMoSIFUcATSiyKRevxf2xXVrOzTLhsroO3Yb39Bil0K7pdnSgAAAABJRU5ErkJggg=="
    ),
    "acc_n_R": (
        "iVBORw0KGgoAAAANSUhEUgAAABEAAAAiCAIAAAA24aWuAAADIElEQVR42pWTv28cRRTH38zO7s7e+s52zoSkcECAwEGKoERQpaEI"
        "FaKgAwoQiL8CUPhRJEU6oEWEAogQpIIIBRA4hgBR4LAT23eYOD77ZJ999v3cnfe+FOeQ2L6Lj6dvMZqZz3zfmzejTr33iqdVobj0"
        "1/zS9YXlja2mb7xsxiqlWIR6har99g4pRX7UTHBzrXV5+uan3/w6dXWeRXJxJCLYy1z97AUiUlr5JojjzNDwAS/KT05Xzpy9cOHS"
        "dG4o0koJdoCq9MO7REQgENglaXsLrpnPj2TH7v/wi1/e/OArUir0zZ15agggAEAgz4RR9mA0cmS12igWJl8+cfTc6dfiKGh1Ek/r"
        "24xwelsu4bQlLsnkDhk7OvPH1LHDdPbkS9nYtpNUa3WLEd4pEXEubZlwOBPnS7OFh8fcR2+9GPrGOVZKdZl0lyAO4oRTHcShtTf+"
        "nn1s3L7x6jPNdqJUtx7mXZJtpSAFMsaY0lzh+eMTzx5/fLPe9jytRVw/Adt3BXGr5fnXn3symwkdixZ2feUcIBBobdbXKg/eGz79"
        "xNHNeuuuDKcsLCABCGisL594asIGxgg76hMAb68KtNabtfVHxx84cuiAEenLsOtAhGi7LUnSHjXpsYcO9/UBRFzSHXZfmbAQdybu"
        "O9ibAQl2z4OU6rQaj4znDXPaAwF6OYM51doYEabBQgACMYtBryP7VAgWEDA4o0TE88PiUvV/+BBI4M38s2ogGGw/tPYaCRWKK4P6"
        "CMRmhq5XmjcqG/szIFKkmNmPhi9emd1sJkYG8BGwH0TlGi7+XoqtrzFAMEsmd8+Xk3Plaj0w3v65Mbs4N3a5WDv3/cxQFPC+/RHh"
        "IIyrHXvm8+9SFusbuTvDzIGNa5I9+fFPS6v12PosIKLd/QERqe5PgI1HNhL79ic/X1usZqOAb+3cc28QAYxvM9nRKwuN98//uLTW"
        "vBPo+vB/30prbQLrBfHyFn39ben8VMkxYmt4Zy5G+xGBlOcL6UaiF1c6U9cWLk2XKxut2PrW17zncZk/y1BKLa7VFla25sq15Wqj"
        "3kqj0OQyAQt6dvxf8wSrFjT5PDEAAAAASUVORK5CYII="
    ),
    "acc_h_L": (
        "iVBORw0KGgoAAAANSUhEUgAAABEAAAAiCAIAAAA24aWuAAADlklEQVR42oWVTUxcVRTH/+e+e2d4b4ZSKAoWKmUoUMsQq0A1Erqw"
        "remiUTQuXDRq0vix6aoLExNjXLjRdNU00bozrnRvqsZq08aItqGR1goComlLigzjzLw3772Zd+9xMQgzOBNOzurm/HL+5yuX2gd2"
        "o54JIQSR67l+4DtOYl9q4JHB9NhjY0opWReQlvR8Lwz84aGDL06+9PT4eO9DrS0OUZgxUXErQ0RCiMzaavpA+szptyaPTKjifP7+"
        "tfyvS6vFnDER2FC1NiICkMtlX3vlzffffkflb9ybuxSVA2W3SuWQsAAiQFYDzOy6hfNnPzn1wrE/fvqomLubbOuNJ21mzWyYDQDe"
        "YCoZXK9w/uyFl58ZnvnqXaXizQ8MsI6iUhFENdWud4lE9p/MuQ8/Pnk0PfPtB3F7Z3xHly4HAAME5q2MtKxMNnPq5OuvTh67/c17"
        "UtlWfAfriGtDN6t4cH+3H/h9Pb0XP/8yd/NCMbsolaOcNhIKqM9IIgrD4PQbZ1T+Rn7ldszeadgwg3UEQn3GK3oH9qePTxy6M31O"
        "KoeNZiKjoy111zBh4D97/HlVXAjclVhTi2EDZqPLRBaogTbHTjw1OpZfvk4kjTEAg1lHobDigKnP9PSkutqdwsISCcWmEsQ6KjEJ"
        "MNdVKPt6+5tjfN/PC2kzG4AAsC4DINFgg4cG0xxktIkIDMZ/ekhHJRKGSNRhpJS67BmjmVE1bwZgdJlAIEJt16XW2jAzV4ZSzRAA"
        "hgFjK0MAMzGD2YC5avZcFVrTQDG3OKdlK0hwJR2jyjes+hFyfvF3NyTLamKjAWo0x5o8S38t3F3z48kOrUuMymlt46Lg5n75bS7e"
        "2q+jsFZPQxPSUl9/dzGy95FlG7Pew22YRCI5c2v62uy95s6RqOQxaFt1AoA25rMvPqVdT5JqYV3aVqFltyWb4k2Lf84nWzpHRw4X"
        "lq8LK9boQitmObuaASgV+3n6x+GDR/fu7vT+vimspo0NasgQCWa+OnU5PXKiu6O9mJkVQgKiLrbOACyl9IPgytSV9MhzPXuHimuz"
        "rH0Saj1hZasY4E0GzKyUCsPw+x8uJdsHhx4/gXKh5C6zLoMsJmJQhdpkKpiUMtL66tTlOyvZ7oEjnXsetYTRJdeUXaNDmIhNRP//"
        "f4iIiFyvkLCdJ0YnDh8a7+9uT1iuNAXtr8IE1OjPsoTQxrheIaZinR1d/anBVE9fas/D0rL+BbbSh5KkUiRCAAAAAElFTkSuQmCC"
    ),
    "acc_h_M": (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAiCAIAAAARTyRGAAAAXUlEQVR42k2JsQmAQBAEj31MxdAKNLQC+7Av86/GHizBBgQR73YN"
        "XtRg2GHW5pzt3JY0jQl1O4AKMByigxEgHeS/OYIBxeNRfomQrCwFqUB9/kKBZuB1oGp6rHt3A1NFWCXlfvJCAAAAAElFTkSuQmCC"
    ),
    "acc_h_R": (
        "iVBORw0KGgoAAAANSUhEUgAAABEAAAAiCAIAAAA24aWuAAADf0lEQVR42o2VS2icVRTHz7nfnfkm3zfzzUyDoWpotKSp2rQoCuJO"
        "VAi+UdCFblyU7kQE3YgP6MJnF0p1oUiRIiVSk0oXDSKR0mprMKBtXjVN08zUSaY+Oi/nfc85LiaZztN4+G++xe/+7/e/556LBw8d"
        "AoCZufOzF2YXL86n09e0z+eFwohIRNCpsLR6GtHCnr58Ba/8WZiemRsdO3Jm6rQhCnthZhaRVmb2m70AqCzts91g5Obw1l06Onxm"
        "JnbgkwPfTk54XsRSipmbmPhPHwsAgICwqRarxTQA9227x9v+8KdHjr62/1VEy7btxn3iytmPrn+AQmUJm3w6DgA77t07fbn4zAtP"
        "Z7JZx3HqmGIydRFVTKVAVHUiA1oHZibfuSOaHD887nleqVRSSq0zwqZJwsLGVAo6EHW8Gy9OHR50YmNfjNt+f9UYRKz5ULMMEwkT"
        "UQWtnoDbu/zL2O6b+O23PijkcwoVAChm01lUBUQB5bPd385+/vxjDz371HOpbMqyLMVM3VWLGMUUkrNfvbTvRS/oEVFTBu0SEWGy"
        "fM5f8Z8H+9SjI0+kM6m2DBpFVSLDACwAIpnYqSdHHg/YAc1koHOhCDEbAARhZdmp5MKunffdOjCoiTs1oggikikL15pNAFW5kIpC"
        "es/wXVq6+LAwm0qjLbOR0rXh24Y7701EhA2AACDARoMiFrOJ2wd3aGplpIZgrQGBAXDdWJAqeWWh5tb/kfUAADYAqbszABnSItwS"
        "V92tYQkAUCwsjACg226hdIlemIx2ty6dW2n36YYoARAdml+c1hsnsGmRpZ08h87P/arbR0SnlkA2Jbd3aPnqPyvxpc0ZAUBAMsbp"
        "u3vy61PZXFbz5j7IpuQP9SdLke9OTgTdkJL/UYaq4e2PjE2cWE0m/H7/ZntDi8rZ8MCD00uZ0WNfhoIeEf0ngxaVsj1bhjL+3e8d"
        "fNkYCgR8zNyNQQAw5YyzZagQfeD1d99MrP3uusHaiGs+HwQBREChMjGF+u/P2XveeH///OKcF/LqM1Hz9YUFWITLTMYf7A9tGzkX"
        "y3342SuJtUQjAACaq0UAACEAVD7H9m7x9955tRwdPf79sRNHDZHrBFseFe0LDwEqFbgBtFcQ7/LfxR+PT/0wdTL5x1rQDQW0r/3y"
        "64X8TkS8cmltObawuHxhdTWey+ecHjfsRYio5RWp1b94Wa5qqk5EigAAAABJRU5ErkJggg=="
    ),
    "acc_p_L": (
        "iVBORw0KGgoAAAANSUhEUgAAABEAAAAiCAIAAAA24aWuAAADUElEQVR42o2Vy28bVRTGzzn3zsuTMW3sxA5W6zwgNLEKAgRCIoCo"
        "kEAgJBBqy64skNiwrBDs+BMQ/BUsAEWIVXlIaSWyASqUBCRKTGmbOE3zcOIZz+vew2Ic4ho75OjbzEi/Od/97j13sDj9IPQrQiTC"
        "VhAFYTyUsx46XZ6dGnviTNU0hOwLCEFBGIdh/Oj0qQsvPzX32MSIZ5ikW3vNOAp7GUQgpO1dvzY1dvmdV849Xt1av1lfvb68sen7"
        "gVJas8Zub4gIwLv77XffnPv4vVfX67//fH051qb3QMG2c0QIgIAguwFmbgXhZx++/dZzj1z5Zn6rGY6deti0HK1T1gwAAAwMIlfw"
        "MksA0ArCTz+4+NLZkS+/+EqhUameAWCVRsy6W/LflHb2gk8un3+xVpif/9odyhdL1SQJofN1vi/SLKXtveDS68+88ezUlW9/sG3L"
        "9YYZmHXKrP4rSYjtMJmZKH106dzVhQWtlGWZ0rBYpcy6705IJAyj5P0LL2w3/m5sbLg5JwtHqxQQ+jN+O56dLD9/trJ4bSHn2Fke"
        "rDUgAw9gwih5ba7W2t30fd9xbGZGANYJkoQBkMw55tMzlcb6bcMQWeLMrNIYDeyJ65Cplk8WPbl6a1dKCQCIhMg6jXnAUQQAOVUp"
        "WoLjOBHSODCDzEqlEQmjrz05Mz6ShG0GJgJm7BwQIK0SAEYUfRhBmKYJABJi13YgILJWgIzYG7lUWgMAESERdRaNANzBmJl7MZk9"
        "EWXv8bDP4XRAz6roxu17ZJhEBICDi7ol/7yzE8ZsGpL5YCT+r+hmY+duM3TdXIYcR7QfxMt/3fO8vGbu8TBIJAV999MqmTkp5XH7"
        "uLaxVN/8tb5VGD6htcZjFAGC1vz59yuWk5eGcRxGOMOebYp6oznkWE9Oj+239qU4Onfs3DuGFL/80ahNlqqj+SBoiwOMaDCDiJph"
        "cWWtNlGuFNx2FAkipCP7AIAkasfqx5W12YnS6dF8O4oBgY5mGMCQFCXq2tId17FnqiOEkCoFCAgDmOzqk4JSzYu/Nda2gnIxP3rS"
        "NQQx8MGYI8D9TGfcCE0pbqw1ry6t39r0kaTrWJYpDSmJUBDhwH8Wodbsh4kpxegJZ7KcHy9546UhSfQPLBWEziRijngAAAAASUVO"
        "RK5CYII="
    ),
    "acc_p_M": (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAiCAIAAAARTyRGAAAAXElEQVR42lXHsRGCABQE0bsVAguwAgkpgIR+rMbA1uzAFoyc4f8j"
        "0ACDndmnx/3Gej2fpsuHaV5QQvdGukmKdJE06UJHp0g3SiEFW9hg+/D6+Rv4z5IZh4Hn670DWmgrjFaGzAUAAAAASUVORK5CYII="
    ),
    "acc_p_R": (
        "iVBORw0KGgoAAAANSUhEUgAAABEAAAAiCAIAAAA24aWuAAADZElEQVR42o2VTWhcVRTHzzn3vo+ZN5NJ2iTUUMFqsCqIFEHEuLSK"
        "KF3pwpXoqnbVreBO2p0IIqjgTqEFDRHsQjfSVGyNtbGmWUxMJ5lJ08lMTDJJ5uvNvHvPcTHJkGRmcA5ncXnv/fif+86fc/CzT84T"
        "4XwmP3//4cLy2tZOxdFqIIghomWGboGzP1wkooGhY4x6u8ZzmcLVn27/9teiFUklYmxZOhg1PhIuLWf/SS/klpYa5Y0nxxLvnps4"
        "+/KZwubO/OJDz3MI8QiGU199AAAgICKNsF4plziqnh5/9LnnX/j2578/+nwKiTxHH6wTp7483zoAACKSUtba9XxWzO5rr559sIvv"
        "fPj1bjWMe24bI2bDbJgj5sjaZtSos22eOHkqnhiZnJzyw+LVy+8PBH7YjIhwjxHmQykszFGjlhwcGR595Pr0Darkr1x+z3WUMYyI"
        "AEAitluyNZEXTw2mUjO374x6zUsXzlXqDcQ9Hds1mY1SWjluPOZfn/71zRcff/uVMzvlUCkiEe6RBkCIlFJkrZ298+eFtyaSgWct"
        "99QRZmHb+qW+7+VWVkdi8vrEM9vlOoHYrilimQ0AIyEiEkJ2OfPGS0/5nu6pA8JsImFLSADiuk6huP7EieSpseNapLsRAdBGIe61"
        "BIlUGDbA1J8dH9Mitisg1jJHiLRvEQCAZlh/+rFRLV0NL2ytQcQW0GKUonKlfPrkMQ0dOiIiwq2OA0gLI0QiMpFBBzTAEacLABDR"
        "/pmgLQSAiNZavX/LdtCBJwfeIRARIgKIRiToI1rujMfjd++XNHYI9QoiIqXTuX913wi4rhOJml9a77c2yzaVTKxu1nLFbUKEPhJF"
        "ZHBwaPruSrna6Os+IpIIgq0q/zK7HMQcwj6CBYaHR368lVnbqrha/Y8OIhpjjg8NzWVL399IJ2OuFdHtaXK4GGh3PQiCqtWfTt40"
        "hn1Xs0gPHQQEMJZjMb8B3sff3MpvVALfaU3iHowIMyQTiXKDLl35Y+FBKRl32qP7ECOtrwW0dhJ+/F5u+4trc/nN2kEAAPS+EQUA"
        "FJJ2lNJOcaf53c3FazPLxkrg6yPLQTtaCwAisUA1tKvF6kx6/fd0YX27HviO71DnNtH3VnYRcXWjmi1WMms7hVKtUo9inh6Iu5aF"
        "pXP9wH+gb0zIwdzF5AAAAABJRU5ErkJggg=="
    ),
    "acc_d_L": (
        "iVBORw0KGgoAAAANSUhEUgAAABEAAAAiCAIAAAA24aWuAAAClklEQVR42o2V209TQRDGv5nd05ZeKJUilxiNQUF5QI03TEy8vfhg"
        "jP+9iZFEI4RLCYXC6Tk9uzvjwylYoKd2Mo/z2/lmdnaW2msrGGdERIRB5p335cjOt5qL7dadxbYxxo4FmClz3vuwvHDryaPVB3eX"
        "5urlSsQSMhUZwzBRPxkstVvvX21u3F9GSOLzk95RfOy9qkBhr+qBKvrp4PXm+ue3z+DOO3s/vXfMhpmtjQACRhgCVJE59+3TmxeP"
        "73YOfqVJHEWlKCqpAlBVBfQKo0Dm/NcPW09XF/78+k6EUqmsChG5Jt5edikdZF/evdy8P7/zZ9taw8aGEHIxYxhm6qfZ843VZw9X"
        "9na3mRlgFb1If4MhgnPhdmv244uNo84ONICMqozNcMmQD2Frc039WZqcGROpChGraiGTubDQaq6u3Drt7jKZPFSkOAtgfQjr95YR"
        "UuecMRbD40UnaIusuXN7Lk3OAKiOtrVYW7NerVdslp7k1zYMVyUqztOarUcGsffEI3XrhLbBtps1DU5UWEaiCFpckSUgBK+iavR6"
        "LVLA6IhhOrOqKqIALoZlCqbbiwVz+bRPusgrzHkycAFECi0q4DrTi5Ne37XKxvsM0yVi50PnJCaORESnM2ai3wddJ0ZB0zLW8nEv"
        "3usmxpRFRBX/dc5n+MdOx2ukINVcoUxwU51vGENn/YExdmG2JmFw0YnCmTPV+QYAZj46jedqtcaMFXGTGzhkCFBg/yRu1qq1co5d"
        "Tt51HzL59gmi+91+o1qtlksqoUjePybHRHS/GzOb+swMQQC5+WCvMPmCF+Cw149TX7Klko14+CrGaRtd3Iaol2aHp0kvDUEZZACj"
        "SgBBiYr/LKjCB2GmSmTqlahRtrWKZcJfWkPq+ZibMdEAAAAASUVORK5CYII="
    ),
    "acc_d_M": (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAiCAIAAAARTyRGAAAATklEQVR42lWMsQ2EUBTDniwdYoEbgQmYgwXo2JyKo2UAYpov4IrI"
        "cZHUvEyMw5d9W/l0PRpUElGbB1PkdjESgxHLf/pOtU29/p6ewO84L/1mVu2OYeAVAAAAAElFTkSuQmCC"
    ),
    "acc_d_R": (
        "iVBORw0KGgoAAAANSUhEUgAAABEAAAAiCAIAAAA24aWuAAAClElEQVR42pWSW2/TQBCFZ2bXTgmUFkoFiPulQBEVSIAEEgieeADx"
        "BxAv/F8EPFGJOwotCUndOrYTr+2dw0NQ26SNgdFI1q797TmzPvzi1XNmbnejn73NXxubw9yJyEwjZCIFaL+yt5cWidksnyo99QdF"
        "qx29Xf38ba0D1ZlGuC9mbi4fSdOtNI7cMA6lPLU4d+fGlYtnTvezYbu3aa1h5knm8YNlY6wYw8xlWaRJnCTR0dmZuzevH2w2P35b"
        "B2BEdsuZB/cuEf3ZYRZjDDNnWT9NoqsXzlw+f+79l5YrK2t2MMFYqaoCFAQhAa3vHxaa/uWzRzNhUHq/bVJUsafVe0/E1gaddmuu"
        "Ubx4+tAao6r76mwXAUoga4Ne9+firHly/1ZRVSMpAXRKAwQARkyn01q5dGLl8tncFcJcwyigRAAR1MdR+97KUiMMFBAoTWtVUiUA"
        "zJKl8XxTls6ezF0pWmcOO0/CIN26du6ktWIBpemFnexwPkwX5o7Pzx60mBLECYKIqqpsUHX86JyFog7ZlTVVwJfH5met1nqj8Zdl"
        "6RYON+t0aDzQIKiviMSCauYZXykAqNdaHdqjAwCo1aFJHWYTJYP/0QEpeCNOa//P5I2wq6i39R8MxIZx5vqD/F8ZAIE0vneiovT2"
        "HxEW08/xo7sV/DWjo0EAtcGhTz+iLC/CwNbrgIgBL/ZAezP/tL4RWAPgr/N4liAr+N2XNkAiBNA0b0xEgLLYrLCvP7czV1ojo/On"
        "eVOASILUmTdfO3HmAivbX+71BiICCSj8FZera72Bq3YDI0bHLYmSSRzWoqTVSxRkDU8ca1UFRAAr2HmkTrv9Ybc/zEtvjRimvebt"
        "euyZKXM+c1UyrIZlVXk1IiM/+w77G4viW5+AcM4NAAAAAElFTkSuQmCC"
    ),
    "sml_n_L": (
        "iVBORw0KGgoAAAANSUhEUgAAAA4AAAAcCAIAAADeNBkWAAACQ0lEQVR42n2Uy28TQQzG7ZnZ924eTVqk0kNVStpSKCBx4P8/cwIV"
        "oRYhQKCoL0oSkt3Z8dgckiZpCrHm5p/sz59nBru9bbgfiAgAta0BIG/krU57Y6sTxbFZ5RSSI2F5vLuzf9zLGzkz27Ly3psVzpa2"
        "+6h78vZ13iiu+hc/v/2oKwsCImKW+9rS7h3tH795cd2//Hx6BgKNomh1G1ppADALrrJPnj09eHl4/v7T4HaQZWmr2dZaCYtnD4Bm"
        "zu0e7O0/752++0CO4iQuskKYa08IOC1nENETtTc3eieHXz6ekyOlVRgEAuKIEBeTGAAQkYNXR1f9i9HvYRCFIqJQEZHIPXOMq93m"
        "9lYYh9/PvurAMDMisrCQrPhoEGB7d+fX5Q15ClQgIgBA5NVy7ykaZ2mQhNf9S4XI7AGQmR05o/WqgLRIPZGtrFIoLAAiAM45WO0P"
        "JmvktqyYvVJG7uqw97WIUmpZhFFGOUfCMo15gr2fjrhAmVmYWWbwYs8AfF+sYT/DWASWcg+kghkPx0mRAogww9ow1XgiIEprZsa1"
        "qKpLS85FScTeC8ia0HErQ1T5RjEe/Jlfon9X1UaPbgYsEmeJJ7+mqgJEYb7t36TtHDUy838FpJ0CEetJpQOTNLNqOJmbteKXTjsF"
        "AKBS1agM4jAuknpSzfckS2eGTp9NNZqYJEyaGTnyNYHA8pwLdEYPSwBJWpkJDJNnYrlTbx44oqpBWY9tVMRRM2XPTN47En6ATj8O"
        "8VLejtWw0pHRodZhgAr/AswOr3CP6raMAAAAAElFTkSuQmCC"
    ),
    "sml_n_M": (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAcCAIAAAAvP0KbAAAASElEQVR42k2HsQ2AMBDE0EEUkAI1mYeSGdh/ifeFIoqgsGxP13Or"
        "HGVO+6p6VtkWEcIoAkEIUICg/+jWWsf++oeHQXNelLb8Au86Q0DbQQteAAAAAElFTkSuQmCC"
    ),
    "sml_n_R": (
        "iVBORw0KGgoAAAANSUhEUgAAAA4AAAAcCAIAAADeNBkWAAACQElEQVR42oWU224TQQyG7ZnZzWETmh4oKqU0pS0KQkhIXHHNLc/A"
        "exeJKkVpaNJsNsctuzv+zUV6SiIFy5oL65PnH9tj/vbjO4BhfzCKR5NkLCJhKWRmVaVlc1E9Yqb9g33rbJbl7Z+XVxeXeV6EpXCF"
        "tkG9PBoMBze38W2s0OPz5knrrMjz+ObWBm4J/fz1S71Wj6qRYTNORt3fHQXOP7Wieu3P1bWx5gltfjxThRIFLqhWIyKK4+GwNzh8"
        "d9TY2+62O4+0PW6dKFQBAVQRhiEURZH3O73Xx4eNve1u+9o5R0T2qNXUR4NC1TBneW6MSfrx2/dNAMN+bJ0z3suTi3jvidgwK6mI"
        "tC8uTz6clqsVCIyIX3FAiAgCY+0kmaTT+ZvTt74ojKyZ9x6AqirAhnvXvb2Dl+Wo4rzISldUsQgCYOZ0Ovfeb+00nKyhIh4AExER"
        "E0H83SyNGjUn4p9zUIUIES16ujjTeVqJqssCVKHKz8WQqpIvPBteFcBEWBJO9w8E3Mr4rE4e0aI54r1bn0tavgWAC4N0ljoFNqLM"
        "pDZw02T6n6wK2MCx5XQ824gyQVDfjdLJPLvLNqEKNc6G1VLvV5cNb0Ih2Hq1PUumWZoZa5ZQfSgtEYmX2u4LQJNuvPgIDs9Qfuit"
        "qlYbNetsfNXn+zAtZ1Vd6Kvt1Nlw0hkAyvyALoaDlIjJOFuql8NKqZjn83jKi7I+rgxbckxsAmuctc5K7qc3Y8k8G17dLkGlRKrw"
        "8PP8b+ZReGJe54joHyOJuVO1qcW1AAAAAElFTkSuQmCC"
    ),
    "sml_h_L": (
        "iVBORw0KGgoAAAANSUhEUgAAAA4AAAAcCAIAAADeNBkWAAAC2ElEQVR42n2U22tUVxTG1157zxnPmZy5ZCYTEzpOsCFSbyDVeqtY"
        "VCJUoVXagih9C71AngUppW997j/Ql4IIvrRPFR9ERRgQBRu1UEgMgYyN0Um8nHPmzJy91uqDiZkZYz/Ww2bz49vfXguWKo0NQ7cQ"
        "FQA8f9UUgfffK+0YHdr9QbU/55kezmgMopYlPnlo+zenD1aGSlGb640giq3qdDUaF5eD/TtGfp78bGiweOX27I2puX8boSUmljXU"
        "aHyyHHx76sAPE5/+UZu5dO1hM+GBfLbP87RGADCdfpNffjx55uiFX2/em35S7vc3DuQQkVks0QqqNS4uBxOf7/v+q0++++Xqy6g1"
        "WMhkvIwlFksAoAAEwCCqsNneu616/utjP/5WexHGvptSaESEyKrOHwOAJf5pYvz32sxfM4sDOc8SpxGttb3NeRHEx/eOlQr+5Yt3"
        "8pl0Yq1SKMxWpBcFgbPHd125MxfGSaFPEwsAWyKlVO9oqkP5ctGv/V3f4GgiEhFitknCRES2s8yWSilo2nojcJ0U8cqjiU0EAKAr"
        "g9m+efBxI2wn5DmGV/MRiUgbEbvQbMYJ4zYxi7whBUARMTMrWEtsEksOM8iKVu8FQIkwwOsJrKLwBuxqkPQc8OHs4mAurVERM8v/"
        "yUzPL7kplfecZtuiUgzvFM4uPI+i5tZKPmpZ6IzyljT0uekUjn84cuPBQsooeWuea65Z1/nz9iMHac9o8WXURgBhXre0X86GsQ2i"
        "1rmjW2r/PG1b1mp9b+32+66j7882KiVvfFfl2tSC1krjOrT2ir4IuGlz68HjbdX8kZ3Dd6eX4oQcgwBdvPaKPgAoBSmNN+/Xd1YL"
        "XxwcmXsazjciANCoUHWjr2nH4PWpOjOdO7x5dKP/7FVrKWiFsbXECbHq2S6oVNBMitkNJz7atGesHLR4fimeb0RRi9S6iyixHMbJ"
        "QM7duqkwNpytlPu8tPkP413SX7iXjBAAAAAASUVORK5CYII="
    ),
    "sml_h_M": (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAcCAIAAAAvP0KbAAAAWUlEQVR42kXGsQkCURQF0c8IpoqggSAmBqZWsN3YzoZbnz0YCL55"
        "12TBYDgzlvnJ4XjavGrL7XKmlCppxZZSVLRWxRK7SZokdIdkrfv/CWOE9+fL47pnuu9+4OpEdpo6oAEAAAAASUVORK5CYII="
    ),
    "sml_h_R": (
        "iVBORw0KGgoAAAANSUhEUgAAAA4AAAAcCAIAAADeNBkWAAAC2UlEQVR42n2TTWxMURTHz7n3vjfvzXQ6M9pp6QdRtKn4SrQVIYRo"
        "bBAshMRCLEgt7LqysLGyImEhkRBCiERC4isSgiDREOqjVVW0TTtNUUPn891zj8XTGkP9czb35Jdz7j3nf/HEkb2epqdd/S/fD3V9"
        "GMnkvFg4qJQgMvCnVKSsXArcs3Be2FWpVPr8jY6z1zvGvqdjpcEiGps3rkNEKXFa2GlqmLF5Rb0t6PDp22eudcSjIQZgZh+Vq1tX"
        "TouEIyUhInj1YeTqw+7xDLXvXF1fW3b1wWtbSUT8hTYuXWCYmdm2rGg4pCS+6E3cfvZxR+uSZfOrL9/tDNjSh4XW5Efe8/Ke5wTc"
        "eLQkm/Pajt6qrZ5+vH3r2I+MX1g2LG7kCRnDzAyARJ4lxb3O/n1bWkjrR52fgq4tyNBkGENEGhGYUQrM5PThi0/2b1tVFS/N5bXQ"
        "REVBRADgaR12rafvEl2DY7s3NH1PZQX9JU1kjAEATcax5KX7Pa0t9TUVUUWki7bCzH7SMNuW7Bn8mkx7LY01ym9XuBQibczE2CWk"
        "s7ovkVw0t7IYZebCfRoCKaB3KNk8u1yR/o0y/BpWQQYA4Ec6F3KUIlPoCZ/jCQYYkJmBWWtSzEVm46IDs0HkvNZq0jj/FCN4mmaW"
        "h3oHPgtj+H9BRiJWx9w3H0f/VxUB8mQqo048bD17lxA8pQwijGe8tYtmvOxL9A0nxVS9gSGb15URp7kuduFOV0DJKasCcDand62t"
        "e9D56e3A16CjxD8hRBhNZrYur7VAH7vyvMS1DHPxs4TAvGdyHm1fOWtehXPg1EMpEBGZWfkz91fkaZPJU0Uk0LZ+jiv54JnHqax2"
        "bOm7R6WyHgMQsZIiXhrY1FTVNCf6pHvk5M03QqBjyUmXqcWzIlJgTZlbFXMrSu33Q98OnevoHU6GHAsRTcH11JrGGJEZ/JJ6/OrL"
        "6/6xgdFxS4lw0J74kr/1E/fTNkO1vnziAAAAAElFTkSuQmCC"
    ),
    "sml_p_L": (
        "iVBORw0KGgoAAAANSUhEUgAAAA4AAAAcCAIAAADeNBkWAAACQklEQVR42oWT209TQRDGv5ndc2nLqS0tIQomVrCgQqLhyb/c+GSi"
        "8c3ExEQNKhK8RIICpdByLrszPhzsDcEvm336Zeabb3ap3b2FaRERgDzLoZo06o32fHuxHcWRneWYXO5UZLlz+97GWlyNszTr906G"
        "w3M7w2XDtH1z4dGTrSAKdz58+vbl6/BsAFFRtZN9s2G68rD7YGvj87uP22/fi9dmo9FaahpjANgxl2arm2ud9ZVXz1782j9I6klr"
        "vmWYVURVL9CSu7u+cqfbefn0eZ7myY2kWW9C4ZwDqCzHROSdm19orW5237x67XIXRmEcxcTkxSug0PJYACK69vj+7vZu7/A4qsQq"
        "GtjAew+gbF3KFnmxsLRorPm+sxdXKqrKzABUZSZHC2Cps/xz74d4X05KRKLCfy2O0UqtakN7dHBkg6DcEwDvPRmr0Cm0Vq8VWV6k"
        "mTGm7K6q3vvSxhRardfSYaoKYiKl0RtwzhlmTNiwbI0rHBEx8UxHESXSEW3Fe2OJmUdGJ6WjC7DiRS2I6Z/opHjQH5jAGmbQf2TT"
        "wRCkNghEhOhymhNV8/OsyItoLoZe2LhKLKInv3vRXFxOdh1qrDk97BfehbUIep1hBpGK9PaPgiRkc11hC1ViHhyf2TisNWqul+KK"
        "1C4+DBvu7x8DWk2qMnAEKGF6dzDVVjL+XqcpQrJzIQlYmYhA41jGaEnnZ5n3nqoGlhjENN7NFFrSLi3yQebUi4UYVVYQQLCX7ROT"
        "es1658VpxqHhkDmwxPQHqlYS/ztpzbIAAAAASUVORK5CYII="
    ),
    "sml_p_M": (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAcCAIAAAAvP0KbAAAARklEQVR42mWIsQmAQBTF7sVJbhhbZ3B/UERstPixUGwsQkLaOE9c"
        "1zks20rvHZUqsUlVofU8RcV63SQJSQC+/kEgUMh+Hjf3UCskeMK/qgAAAABJRU5ErkJggg=="
    ),
    "sml_p_R": (
        "iVBORw0KGgoAAAANSUhEUgAAAA4AAAAcCAIAAADeNBkWAAACO0lEQVR42oWSW09TQRSF994z7fSA0KJNqeEuiGDQ+OJf8NH/4N/1"
        "wcQEI/ECRsqlUnpv6TlzZi8fiqWXICvzMMn+smbvWZvffXivqtfVWqPWaNYbmoZszjEzAJqUWdnfUKC0srz5fOvZ/ra1mUat7hNv"
        "rZ1CeX5tiZmZOZtz5dXy7sGei3JfPx0eH/10kaMxa7P35uVSoZDP542YWvXq+5ejQX9w8PZ1/nHh/KQiRu7Q0np5eHPOLSwusEj1"
        "/LJyfLq5u1V6Wjo7ORVjbtHiWhkggFQVoMjlSDiO41/fjte3N0qr5bOTyrBvU1xfHj0BAERGjPfeGHN5erHz6gUzXVdr1lrRMQFQ"
        "VRGxxooRqB5+/Ly5vx3NRxpUAJ06RCRGCJR1rlmrN67qazsb3nvBjFQDEYkIEdlMpvLj95NyMZqLrM6kAgUAEQFgre11uvEgzhcL"
        "djbANKRExLei4NFrdx8VFix0AlXo0PJfmszG9Du9xSlXEAAw81jwJMIhDSxiQROuE9wQZWFmDcFO16bXiZiZmENIH0SZSbO5bL/T"
        "t3cT3CdjTNa2/7QecgUyLsOG+63eA6gqcvm5bqsb38T/RUE2a42zzUqVhf+HAnCFqF1v+X4sRu5HFXbBxUnSumiwESKys3/OIALR"
        "vE3UNyvXo4pluUMZTEQQgqMkjdvnTVUdeVlhISIGgQmCYBA4DNqDm3qPaGIfrApAUEIgDUh91yedOCQpCxNN9GbbcZeA4IN61SRV"
        "r8Q03tVIfwEyblVgTkASpAAAAABJRU5ErkJggg=="
    ),
    "sml_d_L": (
        "iVBORw0KGgoAAAANSUhEUgAAAA4AAAAcCAIAAADeNBkWAAABv0lEQVR42o2U227TQBBAZ++mlnJBlCKqJA5IEeX//wYVpReJPjlE"
        "JLazngsPG0WO40LnyRof754Z76z6sPoM56GUAoC2bQHgKr8ajUaT6cR7by85QmLhm083i2KR57mIxBiZ2fa4GONkOrn7fpfneVmW"
        "D+uHxIGA7XGz+Wz1bbUpN0+PT8zsnLPWJiXb5eaL+fLrcv1zvd/vnXMhhPSWmY9o4m5nt4ticf/jnpDSSkTU1TumxuNxsSyeH58R"
        "0RgDACLSq9imbPGl2JSb3X7nnGNmo/UAiojT91Pn3MuvF2NM0rrkAMCCwPXH6+12S0RpawAg5lT1GRqy4Jzb/t4qpbhDDAhk7zIi"
        "ijEmKBGXSx7RGCMTa6NPWREZENBKI6KA9HYcEGBhZhaRwarPUWI2b0ObpglZeBMaD5GFtdap+f9C27ZFRGMNNjjYo1NoEKh2lfde"
        "/hdaaVVXNTFZZ0+tGEZTC6s/lQ8+Pb8Wx6N9OBy01SELdVW/ZqxPA1Pva0T0wTPzoInujmFTNUzsg0+nrPfNxXA30ThjrSUmQur+"
        "mv6VAQqoJULSRhtjBCRdAgJiB/wVAAAjgwJQoJQCBQrUXzWOlnsh1NkeAAAAAElFTkSuQmCC"
    ),
    "sml_d_M": (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAcCAIAAAAvP0KbAAAAPklEQVR42l2JwQnAMBDDLir0CBx0ob46QfYfxs4nFJKHMLLiHR9V"
        "dd1PJzORhCRs47Wyt//vi9NPJBEtoDEB3XxDCZbUyjwAAAAASUVORK5CYII="
    ),
    "sml_d_R": (
        "iVBORw0KGgoAAAANSUhEUgAAAA4AAAAcCAIAAADeNBkWAAABy0lEQVR42o3TS4/aMBAA4Jmxk0AAdYWQyrLQoh6qVf9DT/0F/fuV"
        "9lDxUMVSQiDZGJyZ6SHLY3mUtXJIrM/jyYyN33/+EJE0SVer1Xq9FpEgCBBRVeHtsI1GAxA6nQ4Z2m624/F4Mpp474MgONEm/FBP"
        "l2mySFbpChR6D73+oO+9Xy6Wxpg3tP/1s7XWGCMieZ7P53MVHX4Z1uP68+yZiA7047CnqgpKSMYYIsqyLFkk3ftuq9Wa/ZntNUk1"
        "WJiZmVXVWsvMT7+ems3m47fHsiwREQBILw0AIEOj36O79l3voVf6EhFJRU4e2GkWnk6mg0+DMApF5GpUESGiPMuLoujed7lkK2el"
        "rhwAVGsWfxftTjuchraaPaf7hhVFwczNVvMy3acBAMy8cZs4ju15r89nnHNhdCWBk5VlWUZRdCHqhWREmfl9VFVY3kWNMc65G7lW"
        "JUNCl7sbUVW1Olkbt7lFRWv1mnPOe3+DIqExJk1SRPwfVdW4EbvCVUf2KhWRqBap6Ev+Uh3tq40NwgARs3V2uNzHtHpHxMoVeQEK"
        "gDt6XFdEJEPWWGEptyXgwQGArT4QERGJCBT81qvoMXqlhLubLsDMrzvihR/9B+kNhrMHoxEvAAAAAElFTkSuQmCC"
    ),
    "stp_n": (
        "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAEWUlEQVR42q1WWW8URxCu6u459zS2cYxRiDExYJDAIKQkSv6/kicU"
        "nkhChGWwvZeP3bl6uqsqD+P4wAbZmNI8zMPW9+1XU/VV4cL6HbgsUCF5crUzgenN9Tu9Tn9hLoojEWGW/eEkn80OJ4e2ssYYExoR"
        "AJGLOOYSaEQRsUXV6XcfP39ye2UpSRJmrooSAEQAEZbuLOnAOFuP9kbv//p3MhibwGit5QIHfqIAFfraK60ebz69u3rX2Xp/MM6m"
        "ubO1CJ+kK6WCMGh12/PLi0k7He0M3/z+Os+yMIo+4ThHgAptaeeXFjZ/eQkCg60dcj6KYq01KsQzaQIgLMxU21oFeunecpQmb/54"
        "vfX3+zAO4QyFTuc7J5WpK7v6aO3Fr69GO8Ph1m6apHEcK4UNpJx5QAABlFJhGCrUk92RtdXD5xtREg22d5VSnxKgwrqy9x6uPvtp"
        "858/3xZHWX+uz8xMzHJ5cPMQC0gUxfk0Gw+G688eh3G0u/VRG3NKgIje+f7C3LOfX7x787bKy16vR97LlYOZwiisimq0N1zb+NFW"
        "dn84McacUYC4+duryd7oYDBpdTqIyHLt0EbPjmZVWa1urA0/7NW2VkopRHS2vr/xQJiHHwZBHKIIEfE1g4iEJYqiyd5odjB99PKJ"
        "MAOATubacSt58HT947ttEUFAow3IV4YjDwDZNFu+tzI7nGVHM+Od+379B1vZMi9MGIiIZ494rimvGALIzABQl9V0/2jl/t3x7tBo"
        "Y3rz/YPhBPH4fxORVkqujQ4gwEQCAIj7e+PvVlfSdsuk3ZYOdJHlgNhUzXsP2lxfADDzyaxXeSHC3Vs9Eycxed/YQzPlRNT01XUJ"
        "vPdn3slWNumkJumktrTMfELQ/FQdT/BV69OU98QUmLnMiqSVGm000WnTn+QQ0dVFXDRRESFiEwWGuZl54WOX+VLa9QQxM7FhYvnf"
        "b+BrET+jSoi8yWd52m0hQtNC3w4cTBTk08zUpQUEVEpYAL8VAaBC1MrmlbF55Z03UVDl5VkfvxE+S5hGApxPM0NE+TRLumk5y0Uh"
        "3PwrIDBz0kmrvKqKyqDC6fgoXWvpwLDnb1AlBmV0kEaT7aGw6NZi19s6TOK4nZTTDG8oAoGJO4s9AJhsj5RWCgSUUgc7YxWoqJ2Q"
        "I7lBsKOoFUeteLI9EmHAZqMpJEfkfPd231U1Ofq6QgmLCU1nqT8bH2WTmdLq/NIva6WxvdCtC8vewzXNrkHvLs/Zwh7u7J805Jmz"
        "RaHNKtQqvdVhR752cEUhAsISpGFrsevK+ujjPshp6ilB44I2K5koudXWgfa1a66SLw0sC2pM+q2ol5aHxXRweHxcfu50bMTqUKfz"
        "bR0aX7m6sOxI5DwRAiKqQAdpGMShsBSTzBUWL4wqXnpdN3AmDaN2pELd7EJ2JMfgoAKttEaF7KjOrctrYcHLNsjlqxERAcEXtS9q"
        "ZZSOjA61CvTJlFBNztVkPTk6dp7P7Kf/ALRM6ad6oPOQAAAAAElFTkSuQmCC"
    ),
    "stp_h": (
        "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"
    ),
    "stp_p": (
        "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAEdUlEQVR42q2W2W8cRRDGq6prZufYXXt37cRYQVEMhBhIYnIAihD/"
        "OBJPCCIhQYgiGZw4lx3H9nrvOXqO7uJhHGd9YMWOS/0yo+7v19X9dXXj3PVFOCmQ0JSmyHJ2ndl2q9lqzs61a15NRMTYXrcXjcaD"
        "7kBr7TjMriMiICfpHAcgoohkOmvONpdufD6/eImZM61H/ZGIAAARNVszfuiLSG9n7/k/63tvd9l1lFJVh9MASFjmBZH6+v6thSsL"
        "w97w9dMXg71+lmpjLFTjEYnI873WfPvqF9c6C/ODvf6j3/5MJpHr1Y4wDgGQMEuzzuW5Oz/ei0aTtUerWZL5ge84DiIi4kFPERGR"
        "six1ql3fvb6y3FmYf/zwr1drL13fnV4rFXQa0+pLy599++Duv3+vPnu8Vq/Xw3qoWE1LHwQRKaX8wCekjWcvo/Hk9oO7fui/fb1F"
        "REcBlfq1G0s3v1t5+POvw53e/KV5a621tprscUD131oLAGEYDrv9zVcbt3+44wXe1ss3zPwegIhlUbbm27e+X/njl9+jwbg9N2fK"
        "Ej44rLWe78eT6M2rza/u3yx03tvtVYx3GQDe+en+i9X17ddbs+0WAp4461NCRFzXHfT6ySRZvvfN7sZ2nuVEpMK5Zp7lX64sI8LT"
        "R6t+GLiOg4gAZwMACCKiwv5urzHTXLi6uLm+oZQia2zYqHcud54/eerW3Hcpn1V9PwkQcGvu+pO1oB7OLV4q8oLKovjk6mI0jpIo"
        "UcyIaC2IgLXnaAIAilWW6N5298rSpyBCirnZmelu7hzY0YoBkHM0AQEBRFTMuxvbQSP0GyEHzZCIknGsWFV1wlo7beQzeQkQEJCY"
        "kigxZTHTmWUv8Iu8MGVJrKp9rdx94uE6PYwx1ShENIXRiQ4aAQeNQMepCBDSQT2skkD4cIZYkYM5IaIFk0xiLwyYWIkIHS41+5bA"
        "s/gHYBqARNYKMbE1VpAQ6RxrMl3hj3xWNd8aw9YYYIWE8DGE40BEADCl4XgSh41QKap256IQROR4bjyOOE8zIFCsxAJclL6AYkVM"
        "WaI5i3VRlI5fy2ONSBejL+J4rgWJRxEbY+JxFDaDPM6QEOTjNwDEitf00zjViWYkHO+Nwtk6u44YeyGrpBxWvjPY2BUrTIqyWEej"
        "yG/5uhsjfSxBrNRafqazqD9RrAgEiHC41bMoHLoo+y4+Zwgo3yFP9Tf3RCwgMAAAYZmXg7e91mJHjIVSzrlQAuAgN91xd5hOElIE"
        "UgEESFEyjNlzwnZDRgWas1tWQBiwyWmcjnZGpPYNye+PhqLJzggE/JkAUqHyLAwB64AEmMV6vDWYHsdHnnWT3WGh86BTV0ycIwnC"
        "/1u3ErIgpSuWRffTpDeBwxWBj715SY/TQud+O3Q8l4XYKJJqBB46TAAGpVTGkC3zUneTIsnw2E3FJ7+rCxPtjNlznHqNXVZEhESy"
        "b2EBsGgtWGOt0aZM8iLOxQqedA/yKeW3TIsyLYiJakxM5BBUCAEpjDVis9IWRgSqen+i1H+KmqM0OF3z4QAAAABJRU5ErkJggg=="
    ),
    "stp_d": (
        "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAADs0lEQVR42q1WbVMbRwyWdnW7Z2xCSiABAoSETMeB9v//kzb51ClM"
        "QkON8dnc3d6+SP2wNDHglGLQ3Mx9uF090iPdI+HGzzuwyBCRE4cYiGiwOuj3+2tra8YWIsDM1aRq6mY6nXrvtdZEJCIL/dBC1yLi"
        "O98f9A/33m1sblprWbjrPEg+AJubm0rrGML4Ynx6ejq5nBCRUuouDN31HmNUSg2Ph9vbWzGm8fiyqZsYogjn2wiAqIhopd9bf7G+"
        "tb01Go0+/f6paRpjzC0MnKcIEb33z396fvTLkUJ1dvaXd15rrZRCxFuhiAgzp5SMNVs7W9aaj799/PL5S1EU88f0yovVb96DD7v7"
        "u8e/Hl+OJ2efz3KYqFBA7j4AoJTSWovIeHQRUzx8f2iMGf09UkrdBsixv957PfwwPPnjZFrNbGlzmD+q3vxXTVTXzbSaHbw7MMac"
        "fz3XWn8HQMSU0rO1Z8MPw5M/T5u2NcYwszzEtNbe+6qq9vZ3vffVpMoY3yk6Oj6aXE6qanq3UP/HMoZzznd+d393PBp771WuXgxx"
        "b39XRMYXYyIS5uUeTklrPbms6qv67fu31+z11gfW2v2DN+dfz1kEAe42zIPyAIC2aTdebtR10zQNpZi2d7a99851WmvOPfI4gM77"
        "q9nVq1cvJ+NL0loPVgfTaooAIoIAwrxcEgIgzAKAgNWk2tjcKHsllb1SK+1ad912ACiyPIBI/tVd1zFzf9AnY01MKcakFGZyGACX"
        "JSi/GYAjhxBsacla630nzIwKb1K5RAY4l4pzzpaWlFLMzCBqzulyVcb5iyIppUIXxMLCIiJLhn0zg2+WZYATEzOzMIjkn+BJTABA"
        "hFkSJ3KtK8tS5kr0JAAioLVyraMQguS+lKdDAEAERPSdp+BDSklrHbwHfCKSRKgoWNi1jpi5bVtjTOfc/KB4jDGLsYXvfAiBELGt"
        "W7tuF47s5Uwp1KRn1QwAKE/KznW2Z+urRj2aJRbp91diiK51iHg90YIPZa8UkRTT48gXKsiWdjadpZQQkf5ljetZ3ev3Ykyc0pJi"
        "J6K0sqVt6ib4kJ3Q/MKitLI94xrH6cGKfe29Z733mZzbixcidm0nIsYa3/kUH5CHiGjSxproY1b+H2x2CJ3rUkpkKK94IvdItwAg"
        "AhWkSXvvo4/3r44pJE5MBelCSxJOnNtXbgpnPqy1UloBQOe6hcTSQtkVkVwl1IiEKChyQ6wQMYuBiMQQ89a6kFL6b2Yl5n0aMN+e"
        "H0kMDHzv6PgHXDXzTn9N45MAAAAASUVORK5CYII="
    ),
    "tile_history_n": (
        "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"
        "YII="
    ),
    "tile_history_h": (
        "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"
    ),
    "tile_history_a": (
        "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"
    ),
    "tile_clients_n": (
        "iVBORw0KGgoAAAANSUhEUgAAAJYAAAA8CAIAAAAL5NQ9AAAQ70lEQVR42u1da4xd1XVea+99nvc5M3fGM+Px2Bjb8Qs/ACdgTCiP"
        "liopVasoJBVSk/yIkBCt5KpIaSXSSKX9E4iEEORfI5o/JRX8CBQqRQUlLcIQsI2NCXhsj43nfd/v89h7r/44M+PxeO6dsTFtJJ+l"
        "o/lx5zyu9nfW61tr7Yu5bcPQSRAYMhnKIPA5F+lsuifX29PXm+7JaKUAEGK5nkLImNduF2cL1XK1XCyFfiAMw7BMICKijih1ghAZ"
        "KqkCP8j2Zrfdsn1oZNh1XUT0PM/3fIZI8ZpfV0EAIhJCOAkXEAI/KMzmPz35yezUNBfCMIxOKK4EISIC+J6fTKduuW3Pxi2bAj+Y"
        "m5ot5Yteu62VJtJLVDCG8rrAt6CIiIwx07IyvdmB9YOZnsz0xPSJ3x6fm5q1bAsRrwRyOYSIqLUO/OCW2/bs+fL+cqF4Yex8s95A"
        "hpxzxhgiAsDijZAhxhb184nWeonuRFaTlFRaK9txhjeOjNw0en7s3Dtv/g8RCFOQpo4QIqKSinF21wNfHRwZ/Oj9DyvFimmajLOl"
        "sBER59wUphCCc4axUf1cHhC0VlKpMAxDGS4CGf3VWodB6CYTO2/drZT+9etvVisVy7IWUb8MQkRUSgkhvvbwQ0qqD989iohCiKWa"
        "S0SMMdu2TcOMngEUW9LrYUYRgCCUYdtrS6UY4mV2UakwCDfv2Dq6ZdN/vvwf+elZ07ZpAUXu9qWWwvO1h/80DILjRz4wDIMxtgw/"
        "IUTSTQhhEBFpTUQEBPHx+Y55AeKcm4ZJWksply47MBRCzE3PEtGBr94xef5is9bggl8GISL6nn/3H91jGOLDI0dNy7zM4SFGxjPp"
        "JhCRtIZFaGMIPv+xsJJEBESGYWhNUslLwQsBABiGUZjNA8D2fbvOfjJGmiJDyN2+VITfzv27N23bfOzt94UhVlJ2jJIKTRSv+RcL"
        "KJEwDKWUUgqXWFQiEqaRn57t68+tWz94/vS4EGIeQtLkJt077zv0u6MnwzCM7OfSizVpx3Y4510SzMsTnCsUdNm/YukW3wAAMMbC"
        "8FJ0swijECI/Pfulvbtq1Vq5UBJCCGTM99p7vrK/nC9WSxXLdSI/uSz+ZIwppbrhhvNogyZAAEQU7NKjlQZNQAAIwBDmQ6EYz84L"
        "iiiEiFBc9rlSevyTMzv27pwcvwgAQkmZzqbXb1z/u2MfCdMgpZatKxFxxpZg2oFXkBoZMluwhIkWJyCtL92KI0NkEGrdClUrJKmQ"
        "ITCMlbKLcMZDCJetOxEJQ8xMTK/bMLT+pg0T5y6IMAh27t8deH6r0TQta4XkHxEZi4z0yoovNXJm9DroCj/w/UatNVGXrSBoeUQE"
        "gEBkuJawTbcnaadcM+OygMJKm3wFfGn8HMtlUCHiinRMlC8WZ/Nbdm6bOHdBcM5zg/35mTkApJXo1MgWqyW55GXPITB6HEyIeqVW"
        "Gy+2S3UVqvnUlF8CR5ZDIKpNFhhnVjqRHu5N5XqEhKDQ0pKWnhnLlWu8goIKXpwtbN3Tn0inRCKVsmyrWqpw0SFaISAiTXoZrqQ0"
        "GswaTrebzblj57xKAxGZ4MIUsBBZXTpfzPNwRORXm7Olesmd6dsynNnQF841ZSNgglHsGteuoAxbjZYMwr6BPpHuSROR1/K6LOLy"
        "zxFUqIRrWsOpwrmp0rlpQBSmQQsE38rvwYIdRsGE4CqUMyfHm3OVdbs2GSb3Cw1m8Ng1LgtNqcN6IqBSqt1q9eR6RSqT9tue1poB"
        "63AjIq1h0WUhUqhF0jQGEhPHxpr5KjcFdDDZnb4aASEiN43GXMWrfTxy21arP+nN1ZnBgSjOPRaB0iv6r3kcoN1sJVJJvu32XQBQ"
        "yhe7pH2RX10MXkTCNNelJo+faRVrwja6LPfSC1cUxrkKZX2mlB7NCdMI6x4yBB2jBwBAmrokclprwzKzuT7RNdubl0s0gQYUzF6f"
        "mTg21irVhGksK3wsBS9KTjWRaRhLSyrLTDQTXEt18benNx3caQROUGmjiFGcZ1RW01IkpcQlmrVzdZ+ItNZRKTGzobcwPtXMV4Xd"
        "ET+G6Idh2/MG+voMw5iZm2OMJVxXdwhrGecqCKdPnFu/f2vY8rTUcaYBgEqpLu5pETJBa3NiSikkcPrTvueVzk5zS3TEjzHP99fl"
        "cn/9ve/de/CgbVkfnDz5/IsvfnDyZCcUiYgbolmoVSby6aFsbbyAgt3g7pBIr4oMARCQAID5slHXHhtNxBgzsvbk8TOA2InuREQ/"
        "CAb7+//9pz/dsXt3eW6u7Xl//tBD999113cOH37znXfSiYTqhKIpimenkrmMcM2w6SO/UbkbxMjsrZpaEJHWwGhVAQIALZXTl/Rq"
        "zXalyQXvRG8yxtqe91ff/e6O3bt/+dprDz7yyL3f+tZPXnghlUr93eOPu7atuoVYqEJZmSw4A2mtNREQAd1QEimW1nqBpl7tbA2k"
        "2SJI3XIAIkS0sm51qoiddQMRgzAc6Ou79+DB0tzcPz777MdjY+VK5Z+fe+69Y8f27dq1Z/v2VrvNGev0WjHBG7NlMJDbhlaa4MYq"
        "bGkirbVaMIprMLZARIJWb0IjrclM2EqpVrHGOqtgBIMhhG1ZvufVGg3XcRzHKVcqtXrdME17JQ52mRIHLc+rNK2MW58q3YDJfrQ+"
        "uLZwjggIiMG82e2ir0hKWxk3aLZVKLvcnYhMw5gpFD44eXJoZOTRRx4honKl8vBDDx08cODs+Pip06dt29arvV/tSsNM2USRR7/R"
        "TCmswYQunq1JRxHpakkFABgJqzwxu5ZXgyE+/+KL9x869Dff//5dt99erdcPHTjgJpMv/PjHs4VCNpPpkokSEeOsXWn03jTIDEE6"
        "7hlfLZwh4iM7buKGqJUqnPMu5yf607WZctjykbPu97VM88Lk5LGPPto8OnrrLbds27z5s4mJp5599l9ffjnhOHotKQxBZijnV1ta"
        "aYwzxA5hh9bacR036S6m9h0Z1ShpA4Zh00POVi21a63TyeRv3n33yNGjO7dtcyzr47GxUrWaSSbV0r6pTl+OoQykDALhmEHbZzd8"
        "grh6aj8fvF9r4QqWF5qZVKpUrSKA6zhnzp/XWkdN4KVq1XUcyzRXp/RooUUjlrWm9tQttV9jgAsAgvNKvZ5OJr9+3333Hjx4YO/e"
        "oYEBIKo2GsdPnfr1kSNvvfPOxNRUNp2OuILu9N/leWksK9ahtF4IZ66DaQaAQrn84D33/P3jjx/Ytw9su10u54tFAhjM5b79zW9+"
        "+xvfGD937rmf/exfXnrJNAzTNFclIGJZvWxHJODy0H3FM2UQkibTtUIvQLGyOwzD8AePPfa3jz7qJhJH3n//5Tfe+ODEiYmZGSLq"
        "y2b37NjxJw888Mf33POTH/3owN69Tz79dL3RMIS4Uhcj18sNEbb8qOASI9XFF0JEc68eoSgNRMI2YaUFFZwXyuUfPPbYD594ojg3"
        "9w/PPPPzV16pNxqmaUZlplKl8tGnn/7itdfuP3Ton5544i8efjiVSPzl4cNRJ+sVDwNhC8a5ClXsDlfxNdEbP/SlUc5ZrVxlvEPj"
        "BaKW2ko53DTqs+XFVv7F+KXWaPzh3Xc/8+STtWr1O4cP/9urr7qOk0wkDCEYY4wxQwjHcSzDOHX69BtvvXXXvn33HDrktdv/9fbb"
        "Cde97KGIJFVyIOtkkrXpErIYw26Rv+XYTtLhQ9s2MM4aXSCMQkREty9Vmy4tbc9AAEVkW9bzTz21aXT0h08//dKrr67r65v3s4tc"
        "w4LWJ113tlj85OzZr99331f273/r7ben5+ZMIWhpuiNVz6Z1KtDtcr2T0Y4lgtB2LMt12TxX2tXoImdetcmFsDMJLS+N+DLGms3m"
        "oQMHbtu378j77//8lVd6MhnZuVAZStmbyfz3e+/94tVXeweH/uzBB9uex5aw3kRaWIaTTTaLNUSM8evetk8EQMTmEVxtrVQovXor"
        "M9xHSi/phEKl9b133sls++U33mg0GmK1uQuttW1ZL7/+ul+r/sEdd2RSqXAxTUTUoU70Z4DQr7eQs7j9YlUIiUgAzM8qdc//kLHq"
        "ZHFg+4iZsGQwT3aHUvZkMrft2dMslT44ccIyzVX5M01kWdbY+PjpM2e23nzzzRs3fjw25jpORLUDQnakvzpVJE3EL81lxdKBatEE"
        "mmmKMFyFE0eGQdP3a+3c1hEdqqg3TWqdSiQ2j462Wq3JmRnReVeGy0YCOC9Xq9P5fHbd0LpcTkoZTdGoQGY39HNDNPJVFPwGLFNc"
        "g2gNfHDLesZYs1pn3WjuefbSr7X6Ng9Jz/eqTSY4Akgpjxw9+stf/WpieprWTNQJzj89d+61N14/+cknKmqsUtpwzOE9W4pnZ6Qf"
        "xrHo6hmFJsu2LdcRdHl1qjsFI0OZPz0xuGuTV22GfsgFl0r95t13AcB1nLVXFThjx0+dklI6th2N82ulhvdtr8+Wm117G2O5MrWP"
        "trLQa7yGCdYs1SsThZHbt3FDaKUYY6lkMpVMXlVViABcx8mkUhF+KlQj+7eqQJXOz3JTxMMVa240JQLifRvXGZbRqNaXbY7Qae0Z"
        "581SnRtG/7aR2nRJhRLZtUy0RJdopbVUI7duZYLPfHyBiXisYu293tpOusIQPDmQSfamGuXa2tWICd4s1rjBh3Zt9Ootr9ZknF+V"
        "FiIiIKogNGxzw5e3k6aZjz9jgsfAXEXJV+l0byb0A+G3fQRknGmt17qPExE3RemzubDtD++9uTZdLIxNyiBkgkd5OnXajQZxfiI4"
        "kIDQMzqQ27q+Nl0unp/txg3F0sGGcUM0qw1uppx0LqNCGXrBVcWBjDOv3m7kq+nB3p6N67jBZTsI24HWGgkAI1WD+SNq1pFKScUE"
        "Tw/2DO7YaPek8qenqtNFHuvf1UPIBU/3ZotTeaGV8pptN51oVOpr6atY6he54DIIJ0+MO9lE7+hAdmTAr7XalXqr3JB+qPyQiAAR"
        "iLhpCFM42YSTTTnZhNZUuZiv56vRqxTr31UHMkonMkklZdD2sHfLoJNwhreOTp+9GM2+XMsYnNSkyUxayb5MojclLIM06VDSksFi"
        "5ExJ1a40G4WqV2sSQax81yxKqqGbR2qFamk6LxjnrXqrVW8msqnKXIkb4qrJZQLkiJyFraBYnylemBWmwQW3knakgoAYtDwVKBmE"
        "pDUyxqLN92Llu+YaRdIBgGq+zIUQ0Wa05enC0JYNjUpdK3Utixs5P4acCQDQSmkp/ZY338VEgAwRkXEGCz2MFHddXGssSkQ9g33V"
        "uYqSShiCAQHj2G60G5V673BOKXWN/UbLKB5EJhgzOBOcGRwZLu1oivXvmgGUUmb6e7TU1Xw52uGCLQYmhYuzgJjJ9ahQXsc2q/kj"
        "luuRRWgp7YSb7EnPjE8t9mkubGaJABra9VZuwzqtyW+0b9zxvt/brROkNl2rf3Qw/9ms12gtMlmX9iNFhiqU7XorNzJAQF69FTmw"
        "2Oj9Pjg/LbWddPpHB8uThUapupSJvARhVNeVftiutdIDPaZje43WfJoRV37+X/e9IE3pXDbd31OaWI7fcggBADlTYdgsN+yUm+nP"
        "aqVCL9BK4zzdEsv/YS1Ja63Jcu3e9TkhRP5CZD/FMge34o8cAGjSmpy0m8xlEMBrtLymp0K5MMAYe8kvticGALnglms7mSRj2Co3"
        "G+UaEKxIn2GXX4vRSiOCnUokepPR7jAylCoIpZSxbf2C4GOMCcsQhuCCE0G72mxVGlpp1nkmELv/4A8QaKUBQJjCcCzTMbkheLxZ"
        "2hcXdiqtAhn6YdDypR9GM7PddzT7X/wKxKWEu+FZAAAAAElFTkSuQmCC"
    ),
    "tile_clients_h": (
        "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"
        "AIbm7wAAAABJRU5ErkJggg=="
    ),
    "tile_clients_a": (
        "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"
        "7zrl0P4AAAAASUVORK5CYII="
    ),
    "tile_progress_n": (
        "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"
        "h1FTsPfxIv8LJkcZzXfvjkgAAAAASUVORK5CYII="
    ),
    "tile_progress_h": (
        "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"
    ),
    "tile_progress_a": (
        "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"
    ),
    "tile_notes_n": (
        "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"
        "0n9QAAAAAElFTkSuQmCC"
    ),
    "tile_notes_h": (
        "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"
    ),
    "tile_notes_a": (
        "iVBORw0KGgoAAAANSUhEUgAAAJYAAAA8CAIAAAAL5NQ9AAARTklEQVR42u1da5Ac1XU+597b3dM9r53d1a6QVlpJiLW0CAkkkCAp"
        "EIg3pjCuFAE5FLbBuHASEkgqlVSqsBOb2EqqbFK4KiGxyyaOywSHOAjbQYCgjAGJh1fogV67WmmlfYy0r5mdd0/fe09+9Kx2tTs7"
        "u5IgTpX6Vv+Sdnqq7tfnnO9857s92Ni2AGZYiMAZK7oyW3QtQyxuirctql++sL51ftyTCgEhWB/fIgDBcTRTOnB8qCeZ7uobzRXL"
        "dsiIhEwi0kQzwjQThJyh66lMoXzxgrp7rl+5fsXC+ngYGKZybjrnMo5AwbZ/vAs1kW3ypjqHA2QLpQPHhv7zzQMdh5MhU4RDhp4B"
        "xioQIiIipHNuy7zog7ev2bRuWbro/aZr8GDv6Gim6CmtdIDeJ7UYouAYc6xlF8U3tM1fPj/2wcH+f/3Frt1HTsXCFmeop23+VAgZ"
        "Q6l0Jl9+6I41X75r3f7e1LaOnv6RPGcYMrjgDBEBAajyRDBEwCAizy+FUgUWRAQCAlKa3LLylKqP2tetWnjTmpZX3+/+2397i4gc"
        "S0wJoTMgZAzdsjIEe/Kh69d+asE/v7yvayAdtU1TMCKgcdiIiHNuCEMIwRhHDIri+eBHWmullCfLSkrygazEBiils0VvfsL50q2r"
        "tOf92T9t70mmo2FLKT1R8pyG6GT8bEs8/7W7LTv0zZ9+kC16cccEAK2BCACBiBCZbduhkC0MgyEDRAhi8LwqIDDGuOCmYXIhtFZK"
        "aUQkAK0BEW1TFFy5ffeJeXXhJ/7g6p37+4+fHLNDxnhAjUOICEqT4Oy5J+5OF+V3XvzQNg1TsMkxS0Sci7ATFkKQT5KIwL8RBde5"
        "XzS+GGeGYZDWUskztp2hY4mOI4Oa4K83b3hzb29yOBcyub/3FQgZ4lje/Ycv32DZ1lMv7o46JiJMYkBIQJzxsB1GRJpSUYMg/LiS"
        "qiYAMAxDE0mlACoZzo8UxzL2HBtGwC/c1L51R6eniDOsQMgZjuXdz9962W0blm/5r122KaYnR0SwbQcZatJUuecs15SHjYJrjheR"
        "4EJrpbWazDOIKGwZHd2Dq5Y0rm+b//L7Ry1TEAEPN0bLUjclnG88eN0z2w7kip7BmfZL38TSlhniXBBpqNnRI4DPWIFAaVIEmkAT"
        "IAJDRKj8VxC3s3X5wBiX0qPKpk6gaJui48jg529uP55MHzoxGrIEjzbF07nSo3evdTW+sbc/5hhTOkgC4shNw6SZszlS5XtcSQVX"
        "S0maIB5iIYGmQNvAYpmKZV0sk1LAGfHxwAwK4UzVEZFp0kqpKXyfIRbLKlv0bl27+KWdR0zBRakslzbHr1296F9ePRQOCaVoSpAQ"
        "ETMZAQDp6U8LAjAERZAvaVPgkgZx6QKjtZ6ZDARO1GRJpiZMZujASa/rlEwVlW2iyVETEARKXfVmkTEO4NGZEaWIHEu8e+jkxvb5"
        "my5f/NquHpErlr90+2WpvDcwkouHLa1pyo4iIENGWk/nLYgIQJkihS28fVXo8oW8XHb7hse2vZ9NptzeYVdqQgBN0NJgNcXNyxZH"
        "rm117mgPHRuF7QdLJ8dU2ELBsIYAeGG3G4CA08sOAkildx0duWdj2/ZdPcIS/IrlzbuODjGGfpcw5SMISACk9ZT44wzLnlaablpp"
        "r2/lx5Jj39s22nE0my0qX2I1ha82AAIMZTyl6RcdwyGDrVjo3LKm4cGrEz0p/OXeQt7Vjsl0INpVLYkING1nNIFl8L09w1fe2Law"
        "MSoWzovWRazDfWlL8JmEVKKpOZQzzLsq4bCHr43lcrm/+2nfR705wdCxeF1YVHjw6WeBwLDQj1lNdLCv8OGx3ML6kw/duOCvbmv4"
        "9/cK+/u9mM0C6bUqjNUgIYPjyVQhV5KXLW3k69ctuXLFRW/sGzAEzrSFgvMz8YNMSV3SLP50U/SX7w986797RvMyZgtTsInuYdoD"
        "dVoGMAQ6Fs+7avve0ZOp4lc2NSJn+/pcx8QAxClLaUXVMESGBVe2LYhbHMWS5mgq53pSWwYjqsosSGtdaVAIOMOxgm6/yHzgaufr"
        "z3ftODxWHxEAOPcYIgJFZHCsjxi/PpDuHDiw5f5LBDov7c7VOXx6Mb6Ql9a6egdGwBBOpootjRGxsDGayrnjsmn1RKq0ZowBAEfI"
        "uaqt2XzgGufrzx/ZdTTTGDOkIgA6W63bB7LOESNZ7/FnO//xi21SOds+ykdDTAWxeLqAzUD0iAARhjLFVS3NwpOK4RmJrsqzoBQi"
        "IkBJUp3DHtkY+/rzXbuOZuqjPn4AAFLN/PlqhZozhghSk2PxfEk+/sPO732lfShnfXCsFA2xIKP6ITjTjvp4cQRPKp96TG4sq96L"
        "mNaAKKV+5Pr6F3YM7Dg8Nh5/FfktHrYQfRBn2X7/aci7npTky+uOyVN571s/O/rE71/SM1TOFLVgGIColKq5mURECCTGVfJaUQgA"
        "RCpbgttXRwuF4o9+layPCB8/RJBSxyOhH3/19ngk5Ad47V7HU9o2xaPfef2d/f0R29SapKa4I3Z2ZrbvGbpvfeKpV0fiNrvAe0U9"
        "cxYdj0L0IRO+nAOzYehJsg38nYutLS8cYQxPi+gTURgJ1UWsdNatIbf40/6IbcTDlhA4+duUokRY/OD1ge8+HP/UfLN7yLWNC5ag"
        "IhBpredSKTVpQTA+9yOaSX9miNmiuntd3YlT+X0ncomwMYV/+oGczrn3/c3PM7nyFHgm36fgyqcf23TDVa1yyh0AOMNU3ntt9/Ad"
        "q5u+va3o96kXGngI4CNSe4xXUVKBSJPw0UOoUQpBA5kcr1pq/3D7Cc6qw+N3HZl8eSxXMk3u33L6yhXLSlFVr4YmClv8zf2pu9Y3"
        "L0yI4awyLriKSBrmzArHBwViUimsjiADKHn64qaQlqqjOxO2eA1JU3DknOVLUuupbQYRRG3TFHymYkkEpmC9o6XO/tzaVufFjlTc"
        "4aQvMEWtAgLODt948hMAFQfFjLWQQcnTaxbb/aPFTFFOz6JnclcQnN1yxSLBGU1u0gk4xz1dQycGM7X4DgEC7O/N3bCm+cUO0pou"
        "tFSKc3dCEPmzWEG68oFqulglOBjC8ibzjT2p2lYnn62YBv/czSsjtqHURDLVQLYpnvzRu0cG0jUcbxrIMti+E7nPXjM/4fCSR5xd"
        "WPNhmvOf+b4I0lr4JbEGIdUAgoElMDla5jVN3ATAGGby5Qe/+bKePt4ncEKGY4raJEVwHM16UmrH5IWyxyhoEGesg+OJdHJXSFVH"
        "U5RwhMnhxHDJEIxm79whFraqPg1EVJpNdRMMR3NyrOC11Bv9KdewWDBMrB6slcaxQmdqaTPk22EQ/PntXMTPdK40vashgqhtzCql"
        "YqWrBc4mTFTBmikQNYHwE2qt1n7839nc8DME27h26TnSmTMHm9UHV8Gq+ELJt4KLiqe3ZhRO7OlsAXSedGYyY2YYRGHtYAEC0kSC"
        "ptgYp48UEFIFz5XU0mANZsomn7Ecnj+d8dN1whHRkOgbcQ0BFMwsao+iiAScadqtuq0lV0sFzXWmnMMo73zoDABIDfGwsC2eKapK"
        "IAYT4KoIYkXLqTQVNWohIkpFJ0bdyxZHtn4wNOsxmPOhMwhYLquVLeG8S6m8FzIZBbWwRhQCkQZBp0+4zDDdIA2C4e6e/GeuiNsm"
        "r20YPIPOnPmXnLE9XYO16YyfSFctihwcKLiSHBNU0FLURpC0gDMPQFRVn0MmftRXuPeahpUtzv7evDMDkAgACCFT3H9Lu09nJvQi"
        "qtCZo8mxGnRGat0QNdoXRb7/5rDFQQcG01kFGhqXuWtMKgiAM0jl1aH+0q2XN3Z0ZyMWr0oyNIFblqlM6d6vvjSdzhCBf2BcyurS"
        "NUccK6hbr0h4hIcHio4V2C9m9SfSeC2kyceRoJr9CRwTt3aM/OWdC1oarHRBGvyMkRMiSqkjjvn0YzcqpTmvJqkgAJFU1LY4UXY9"
        "Nk2MJyRE+PS6eT/fldLkV+tg1UYQSFem9rr21J4ATIF9I+6BgdLDN7d87T+6G6LG5CqFCLYl4hFr01VLAGdpHr2SZ5hCcJziLU7l"
        "vM9uaHJCxo7DY2ErcAbPoTMkIvJl7srhpFrUT2mKhNjzO4e+ff/SG1fXv7l/tM4xpCYiYAzzJfnHT70uOFNKz+oCRUTB8ODx0ZAp"
        "fMrDEF1PL6i3vnhjy1MvD0BwgG1OUYiV1l5rmot3hgAEw2xRfveVgT+/a8nh/vxw1gtbXGnys+iOff10Nt8fsoRg6NulNFHRU09v"
        "XvHavvTunlwiLIIQnGNrT0SCISg1u4PNPxYVttiuY7mffTDy9w+0PfaDQ/mSsk0fRYg45lkNNn22yRA1Ua6knty8fDinntsxFLO5"
        "DLzAc/RSK0IE3r6yuT5qHUpm5zJI0gS2yTqOZWO28cjNLW/sGx0rSMfi+uzPI/v1ryx13lVPfu4SyzS2vNTrWCw4uz9Hm5QnqbXR"
        "jpiM18+vu3xJbO+JLGc4t3E/hC3+fnc2bPG/+Exrd7JwuD9vm9w/uj/HxRgiYDrvzYubTz24oiRhy9besMXHzcTBmjWNYcnTa1tj"
        "IxmX2w3RK5cnOpN5qTXM4dV4vuvGMfmHx3PDWfn4nYsvSli7jmbTBSk4Gr7PfprE7Z/BZwwZotaQK8mypLs3ND1xz8XvdGaf2Z4M"
        "WwwBZjnJH6xJoyal6cqlsQO9GV627WuWJ7IlNZj1pnR7tWPRNllXsvhuV2bjpYl7rmmOhvjJdPnUWLnkad8NzBn6nmGGoIikhIKr"
        "8iUVCfEbVtX/yadb2xfHnnlt4JXdo1GbBxQUzu7QGoUtvrY1+j8fDopSWR0fLqxYED4wkAODEc31bJhUELN5Ku9944Xjly4K/96G"
        "eXde1dQ1UNjfm913PDec9VI5z+erRJQIG/E6sbIlvGpxpL0l4irY+pvhdw6NIUJdWFTO9wcBOGcy6Eq9ckG44KpkysXYsvmtjfYf"
        "3bb02bcGPKXP9oVqiMAQ8q72FLU2WuuXx9YujTREDakoW5BEBIhEFLFFyGC5ktrfV9jZOdY5UFAEkRDHOUySgzXNFA85V33h2oU7"
        "Do5s2zuITSsWZovyD29uzZT1W4dTUZtrfS43BcSyp4tljQj1ESMc4q2NFmfodw69I6VMQabysiy1JVjIZIgYnK8/Ny7qenrJPHtj"
        "W92Wrd0EIIDA4PjKnqFHb2vd35ctljVjZ/1mPE3g38d0OACUPFVwZd/IxHzX4MgZ2iZzLDbeVwQK6Lm+eVbTTe2JN/aN5F0VswW3"
        "G6IGx1Nj5flxa92yWEdP1hJ4bsz+tF+JATCGlkCzcjHOxr0wZ3GQNFjTmzHIFdX1KxJhg/1kR9I/W898eulY/LmdSUZ0XVs8U1IM"
        "z6vDPu2PG78oQO781RiGkC+pi5vsKxZHvv+rPk3gt+Kn34QIUsPhZP6+q5uVpu7Boo9wsP7/xF/e1S0Ja/OGph+/nTw0kA+PT20r"
        "EBKAwXGsIA8n8/eubwaAzlNFS0y8xDl48+9vSwhliACUK+ll80Kb1ze98N7g253pqCXUlFfKjg8F2VDG29+fu6k90dpgdZ4qlpUW"
        "focetN6/DfLJEEqSPEnXtcU2tsV/suPkO13pKa6JKq9XL5WVKdjmq5uWz7d/3Zk5kCwoTZZgnMH4eyqDLvyTssPgJP2lrEgTLWsM"
        "bVoZd8v62bdPJdNuxBJTHEVVfuSAIUhNZUmrF4WvX1FnmezIYPHoUGm0oKQi/9EI1ieXOX2eEg3xJY3WqgUOR3y3O7OjK6MJQkYV"
        "M0P1nxrxhWq/T1/dEv7dS2KJsCiUdbooUwWZLqgL7djf/41s5oM0LyJitoiGmOtRx7Hce0ezBVc7FptpjIM1fvDHnz4VXA0IjRGj"
        "tcFqbTAbokbCEUpTQHA+fubCsOjqwWw5mfa6h0qDGa8stWNxjrXe9/m/ITyBXRlrjwgAAAAASUVORK5CYII="
    ),
    "nav_book_n": (
        "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"
        "/w+lxefNa0dBkgAAAABJRU5ErkJggg=="
    ),
    "nav_book_h": (
        "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"
        "eWuDrjG/pXFGM60S7B+yZPe5gFQYSzjRuDO3pnDVHRcsmF2x8rGdG95tLQwYOPGbfJAQ11CKZFUVJx53boAiMODR2ruT1/1447UX"
        "Tr/35mUHGjqeWrd33baGoxGbUTANzinlnKbrKUAcoZTCREqkhPIY/Iw5ZVdfMOuseVO21nd/+UcbuqOpooCRT7k0300GbvU8XVb6"
        "MLf6SYW6RnWNPrJ23183HLp6Wc0d1y1eee0ZW+tat+xu2bbnaHc0ebQ7rhQCEIWkJGj6Lf2kaUVnnlh+1ryKgN+zeU/nbb/edqC5"
        "p8Cn+y3tw7Nan54O75uoIsEPbSckIaQwoAuJq/625/cv1p8+q+iceaU3XLLgpuVgcNoetoVUQAAJKSmwkJB4Cuubo79/tWFzXfvR"
        "7njA0oqDhlJ4bLPRsRYy00M3HyJV+3eVkBJS5DcU4ub329bvbNUYFAfNooAxvcLvPkbOoLHdbuqwOyLJeEpyBj5TKwmYCvFDBlq/"
        "lMvt5H+E2+iREKEUEPB6uA+AIMYSIhxL7W4IZ8twGqcapx6DWSYnBJVK/wr56O6ZuH3V9JaMD5GqQzUx0gSmlBiMmjrrV2tEovpv"
        "gPhIbhUzo13oquqEplz5eUAkH9ftw72zI+mw6aNE3PFyZBo1iIg0w5PJI7eZdN77xpCPDVWPB9S583Fkkqq59hxIZlppEnE5ls5p"
        "Zhp48si5WYOTVM1DVXkm/p24NuE/o6a6hcxJpuYRoruqqiapmpuqEpItZMKkquZSHZlU1bzftTEZAOejqi5VP6pC5nGrqun2IBJC"
        "CEyaJLeuA6cAUqps52HSKqMWCqVSFAiPxJJlxZ70m4wm7UZG3TFEfKYWsVP0QHO4JGhSNlmVG5PhFGJlkdXU0cM7owlOicmZ++6Y"
        "yWPUHQp+k+9ri9P6pjAqWVXkdRxFJzVixL11UhG/oZUFjZ0H2mjETjW195w8rSApBKGTXm4kyyVTYnqFD5U81NLDKcCbda1XLZu9"
        "hjOlFJlU1uEHy5JCLZxeVNfQGbZT1GtqW/e2Aqo5UwLxpKQwydaheSqEKi/wnFgVeHF7g6kzFigNhG2HUzj3pMrNe9o0Tt0hoUnk"
        "9d18RSmN2KnLz6qORONrXq/3WzqVCv0e7aW3G4r92hkziqJxh7qviEIyeabfs0xIMiXKCjwLa0NPb9hv6BwRKUnvuJOPv7D7irOr"
        "LZM7QsEkYfuDLinU9Z+qXb/zyJ5G9xUDhFlFfiTE0Nn+pnB1ifecueVv1LXpnKbHIuGTntIzBp3R1PLF1VUh42dr3vHo7usfMu+v"
        "QYV+j7Z67fshi61YUtMeTgLJvBbwE3wyCt3R1MWnVV54cun9T+9Q6L6Ll5DsS+LT79UkZON7zZcuqi4PWTsPdXFGGYVPpkYAEArQ"
        "FUt+9tTKyxZV/eCPWw8djVoGz+7l6TUcIYRTmkjJTbtbrzmv9sQTQlv2tTtC6Zx+osZLXJM5QtlJcdmi6otPq/jBn7buORL2e7S+"
        "m8P6GQ4J0ThNOmrdzsZTagouW1zd2Gkfbrc5pZzRT4TJKEiJPXGn0K9/7TOzqkLGD5/YdvhodIDVhv6yHwoglIon5YWnTrninNpd"
        "DZEXdrS0hhOcgc4pp5D5shz8Z9FMQpBIxJQjU0KVBs0LTyk/rTb0+q7mJ9bvV0hMfYit8UN/vRQAAQKRuFMSMC85s/rk2qLWcGpT"
        "XduhdjtiO0Iio/8kEQsikQopJT6D15b7TqstnDPFX98UfmbTB/uawj6PNuRXJI3+hWaOULGEmFJkLZ1fMbc6ZJlaV9Tp6Ek1dcWj"
        "CcHgOEYdECKReA1eWWj6Ta2swCCI+5rCr+5s2tMYNjTm0dkIO15h5K/Qcz1l0lF2Unh0VllozTmhoKrYG/IZJe4LRY5n3FGAaMJp"
        "7bI7epK7DnUdbo/12ClTZx6dq9EE8f8BRUiKhOMtdwsAAAAASUVORK5CYII="
    ),
    "nav_book_a": (
        "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"
        "SUVORK5CYII="
    ),
    "nav_trophy_n": (
        "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"
    ),
    "nav_trophy_h": (
        "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"
    ),
    "nav_trophy_a": (
        "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"
    ),
    "chk_0_n": (
        "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAIAAAAC64paAAAB9ElEQVR42pWSzU8TURTF7/uaKZSZgtYaiIYYI0ZECZIYYzS48p82"
        "rEwMC12aGMNHYCFakFI+2mnn3XNctJqoIOPJ2f5yznn3mebCnDFmUAyyRn5vaSHLMwWMXCBj7bAYbH/abH/5ltRSEXH1Zl70i8WV"
        "pZev17zxGGpw3hv3p60zkCzLHq4+zmYae1u71lmTzzfvLy8ury6/X984PugkIVjnzN/RFBBljLWJdGXt6VG38+7NW3d9vvXs1fMP"
        "6xsnh8eNmTxJEhe8c855/5uDDyGkaVoUg93POw9Wl/r9vnv04omF2fm4Wc+nSEIBACAukAJ0wRW9QkRm79zytcmJ3tm5iJAA5EoZ"
        "irGmd3p+I5n1MUYvjoBGJXk1bAwAisRY+lGgglHVSCX9nACvgChJaDWYIgBUEaN6KKhCEKoUMVeR5le0Rg/AKEGCrLp51FPhx4sJ"
        "AlVgMYaAAqrqFSo6Put/JI9qE+NMkFIlWYRjWD1AjRFg9doANEYFfDksnbckQVRiRQDY4GJZ2u7BUZpN+NTHMpKj+v8woUoya00f"
        "H3Scr6ehFurX8tN2R6MShOJSR0C1dXcuTCaHu19Nc2EOQPN2ywXf3T/SYbzso5D0SchvTrvg29v7ALyIWGsP99qTjfpUq2G9u/zN"
        "DYX9k97Z95PRzX4AeB7JQDuLDpkAAAAASUVORK5CYII="
    ),
    "chk_0_h": (
        "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAIAAAAC64paAAACS0lEQVR42o2S32vNcRjHn+fz+Z7T7IfZ2dlwNlNkoUQtF9RiXEm7"
        "WElSLhShcaP8CyRK7lwqV5JELYUkubDkd5NSaCu/Gma/zvmez+f9flwcKTbOeXrdvp/38373aL674L37OjGzoqN1746Ny5bmYoTK"
        "32MiiXcTU8Wrd54Oj7zPNdWLqm9qbx7/Pn14V++5E7uVbnIqTVxGxau4P1AfgnW0tQzu2dLdlR96MJJJvGYKLQcHNh/bvXXw1LUX"
        "bz5kM1nvnchcbyEZY1zS2njmeP/o5/HB01d0Vc/Ka2cPHD11/dXbz52LcyIqYjavWlREvv+YLodw4/z+05du+0P7+mKQizceFdoX"
        "RRAAYADnAwDr6jITk7NOdWfvmqSQX/hpfFJECMCk6php4t3H8R+5pgVJGoKKMxIAWF1tTkGqShpCImZApFltWjETkgRIJAABIxkB"
        "q0GsKiRBIiKpbDEjQZjp/21FnIpZxRsJCIBmQjOS1a2d0oxABBKCAIysUD2zqP06O1bOBlkJUkNoUSMJAkwAkjAzmlkNjf0OCMRE"
        "hOVypFVaqMlZTEKMJJOpmbSlKatiZkaaVKvbqYQYFzVmi2nZ3Xs2uror19pcN1sK3omY6b9xzkIEzbb1dN1/PuYnxHXkG/rWd959"
        "PDpdDBFIy0jDPJQjZkuxFHBkYENbruHC0Ett6y4UyxjsX7c8X3/z4btvkyXvnInNCaogcwvrtvcs9xl/8vLjUhq1rbtgIsU0blq7"
        "pG99oXlB9l9/pqoBHH795daTMTHLJP4nPyLWy2k+krAAAAAASUVORK5CYII="
    ),
    "chk_1_n": (
        "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAIAAAAC64paAAADdElEQVR42nWTTWhdVRSF9znn3nfvS95LXtKXpE1K0yQY82PBpLbY"
        "+ANiqtVBI4K1NlQngg78wUlHTkQsCoKCKHUQxaIQEbQgKhacaJpgCm1iSwc2NLY2tLSSl5f3k3vvOXttB0kcpHHxTddee7NZKt/d"
        "arQqlOMdzdmRB3u2N9VZx0rRBgmR0bpUjX+cmpuZu1lXGyhFqqWnbbEUHX1s18sHB6/fKhXLsTGaNhMzcpmwsy330/Tc219MpANP"
        "Bdvzzz3a98rI7o+/O3dlYcn3fa3NpmYI2LmGbPDSyMDFq7feHPvV7OxqeeuFh06cOj9/o9jcWBcGqSBlNuKbMGVqw1Q6SJVX4t9m"
        "r40O999cqpjRkcFM6J8++1c+V+tYsJlE4ByXKrHWFPimVImVor2923RLQ01huaqImIWZmbEBAaLYpVPm2eGuKHaJZU/rxeVqQ23K"
        "S6yj0AMAMETuPFWUihN35Om+g8N3NdYFJ769CIESSaz1BGAHAI6dCCmlSEhobYpndGE5Ory/+8mhdrdiq5FNEguAATA0AGYWEecY"
        "kCRxjhkM56CIbheqj+xue/GpfqXUD2fmP/lm1jfEYGY4Zs0AMwMgknI1CnwFIHHOaCmWVu5ur3/10IDvmT/m/vlo/JxvCCKAAGB2"
        "GgCDRcRa15QL33vt4dcPD1SjpFKNszXesef3bMmFtwvVd8amKtXEaGKGQFYT19ZWRJUV+/i+jl29W594oPPY0b1R4t4Yva+vI28d"
        "jn82Nb+wlA60dbwazAxm9pjZOeWYszX+ye8vbKkPD+3vPTDU0d+Vb2vOQOSDL89OnL9enwmsYyIClAAAO3brT4IIRBt69/MppeiZ"
        "4Z6d2+rToTf+86WvT1+qW3cSkVK0drNjj0SsZREwQylKB+b42CSz7N/XMTH794dfTdeEHjOL0GrVREgE1jIArxwl+cZQRETAIK0o"
        "8PX7J6fGTs0US5HWShFB1mxEpBU5oDbUUWL19OVCSy6VTXuxZUUCQCnyPb20vGK0UoogkHWIhAGB9O/I/v7noil7QT6b2tNZd+Hq"
        "cpwwQxLHzoFBlmEdO8Z/xBaJxYHBZm30+OQNle9uTRyODG3tagpmrxTLEWtF/9NnyoTmnvZsBPXpLwuRhWrqbhWiyOLe9sz9Xdls"
        "aCByp12IFCkHmblWmbxcFCHfqH8B75x1wHZrvdoAAAAASUVORK5CYII="
    ),
    "chk_1_h": (
        "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAIAAAAC64paAAADdElEQVR42nWTTWhdVRSF9znn3nfvS95LXtKXpE1K0yQY82PBpLbY"
        "+ANiqtVBI4K1NlQngg78wUlHTkQsCoKCKHUQxaIQEbQgKhacaJpgCm1iSwc2NLY2tLSSl5f3k3vvOXttB0kcpHHxTddee7NZKt/d"
        "arQqlOMdzdmRB3u2N9VZx0rRBgmR0bpUjX+cmpuZu1lXGyhFqqWnbbEUHX1s18sHB6/fKhXLsTGaNhMzcpmwsy330/Tc219MpANP"
        "Bdvzzz3a98rI7o+/O3dlYcn3fa3NpmYI2LmGbPDSyMDFq7feHPvV7OxqeeuFh06cOj9/o9jcWBcGqSBlNuKbMGVqw1Q6SJVX4t9m"
        "r40O999cqpjRkcFM6J8++1c+V+tYsJlE4ByXKrHWFPimVImVor2923RLQ01huaqImIWZmbEBAaLYpVPm2eGuKHaJZU/rxeVqQ23K"
        "S6yj0AMAMETuPFWUihN35Om+g8N3NdYFJ769CIESSaz1BGAHAI6dCCmlSEhobYpndGE5Ory/+8mhdrdiq5FNEguAATA0AGYWEecY"
        "kCRxjhkM56CIbheqj+xue/GpfqXUD2fmP/lm1jfEYGY4Zs0AMwMgknI1CnwFIHHOaCmWVu5ur3/10IDvmT/m/vlo/JxvCCKAAGB2"
        "GgCDRcRa15QL33vt4dcPD1SjpFKNszXesef3bMmFtwvVd8amKtXEaGKGQFYT19ZWRJUV+/i+jl29W594oPPY0b1R4t4Yva+vI28d"
        "jn82Nb+wlA60dbwazAxm9pjZOeWYszX+ye8vbKkPD+3vPTDU0d+Vb2vOQOSDL89OnL9enwmsYyIClAAAO3brT4IIRBt69/MppeiZ"
        "4Z6d2+rToTf+86WvT1+qW3cSkVK0drNjj0SsZREwQylKB+b42CSz7N/XMTH794dfTdeEHjOL0GrVREgE1jIArxwl+cZQRETAIK0o"
        "8PX7J6fGTs0US5HWShFB1mxEpBU5oDbUUWL19OVCSy6VTXuxZUUCQCnyPb20vGK0UoogkHWIhAGB9O/I/v7noil7QT6b2tNZd+Hq"
        "cpwwQxLHzoFBlmEdO8Z/xBaJxYHBZm30+OQNle9uTRyODG3tagpmrxTLEWtF/9NnyoTmnvZsBPXpLwuRhWrqbhWiyOLe9sz9Xdls"
        "aCByp12IFCkHmblWmbxcFCHfqH8B75x1wHZrvdoAAAAASUVORK5CYII="
    ),
    "dot_d4a94f_s": (
        "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAABXElEQVR42l3QTyiDcRzH8c/39zz7g2fMWBimUC6o1RxGiRy4SdqB"
        "m4uLtoOLm8dcKGlujhSnlZPUTppyWSvm5C612WZm7a9ne74Opsz79PlcX0AjVlWBf4W8Xul3EwCoKkQgAH1zyTQyMT62TMLU9prS"
        "wofn8RgziAgss6oKCgT0k53ZdZd7fq/HJtvo86krnS3s99imgkSxbVWFkPYiEeQfgqPTc4sXMwsraUv32MtXKSO1ImV12Ns9Tofy"
        "tHuUeBZExM7hwZU+S7G/WilXSoW0UimkrMUKc2e7UR/oNm8AgAwAsmxpMXOGkvEzl86Q9WquRRJyDcyCBNoAQABAIlcOJ7MaSfW8"
        "opWzJp2pbjKIulbTRSZXvQYAKeT1Sv7L29fJ0c4Oh13xWBUzGQ1C6Az57vHtPngV9ft84Caegy336lBv6xoTLO8f1Rv/cfQUgMYN"
        "xh9w/nOaIwD4BuiLhPNLwlrtAAAAAElFTkSuQmCC"
    ),
    "dot_d4a94f_b": (
        "iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAAB1klEQVR42m2RP2gTYRjGn/e7P0kvV9v0kJRYUvAPTUWlCA6KYG0t"
        "itrBSewodHFyLYV+3OjapVYc3Dq4uUREkA4VrJREhRKJ6EErRW2TS5q0ueTuex1KREp/08PDb3l4gP9gZsIRMPCv7wRiZhARzz44"
        "fjV9In2NTEtUK83CzEI+ByCUEsJ1oXQAJKUkIlKL7p35s9nsVK9RcbqwA7+hMNCfeP9qxZt03c0yM0hjKcV118WzuYn5G7fv38uO"
        "jH61U+c29so/bJ1rsTODycFjVmysHeJl0Xvc0tzlZZ6Zyly5ODL89Pzlu/nq9pYlzO4oqP+2W7WN3lBpQb8TzzRbUXn2ydKKAIB0"
        "OjWaSTbZ//k5adpO0GpsWYFfciB0RFGkxU1NpZzYOADoB8uFqQnFO6XcsNa1thfulxNQ+zpDB1gRABIgAwAEAPypt9b8eigEmNq7"
        "mz2sggMZDBKkwojJ3w0LACCklOJFLv/my7fyh4Rl6LphBsyIwCoiQtu2DGPd8yvrXm2BGUTMICHADycG+m6OnXp94XTfpZgpAABR"
        "xCh61crH4vYtd/HTKkspCAA6pwwNOd2PJk9OOz3xcV2QXmu0C+9Wfz1fevu91HGOvP8wUkrRyX8B8R7M007xpQ8AAAAASUVORK5C"
        "YII="
    ),
    "dot_6fb3e0_s": (
        "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAABXklEQVR42l2QPSxDYRiFz/t9V5urbnopjbghUgYhhg6GSiQsnST+"
        "UgmbwaYSNonkugaxsYkVMdQiQdh0sHWSSC0kIg0JVVT/aHtfg3/PdE7yDCcH+MQ0WeAfoUhEfmXlQzKFZZHdOBhuae/wDzgku55v"
        "E0c7o6MxZiYiYsU0WVgW2cPz6+M9XZ0Lak19zUXW6Umn7ha1uroVIpqFaQoZjS5gK/7aGuzt3uzvC9z7al3XT7mSTAtN171GQDd8"
        "p5fLc+eCiNjnax4quw2jUHgrpDKFqmT2TS/lM6y6PbbmNSa+N6qKVF/IRbtnST+zrbwUoSpClmxmIYRwAYAAgMdk4ij/cENZrqhK"
        "v5adAnZZOhxlu1QUucf7PQCQoVBEHm5MJerb/G7dawQqNZ2k4hDMrFzFjk/i20vTqXCY6eceyw7OrI5UNzSNMZGWSyUP9pcm1wAU"
        "gQ8PAMD8q/yFAOAdHdeJ1CSbCzYAAAAASUVORK5CYII="
    ),
    "dot_6fb3e0_b": (
        "iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAAB20lEQVR42m1SS2gTYRic79/dbExSTNxW7QrV4iGkiBVKQUtBaRH0"
        "4KHYUw+CiuBZD3r7+Sn2LEXUQw/1KIInQfEFRRRUxBVWsRZKoD2kxmTr5tE8dvfz0AYDOqdhGOYwM0AXmJnwDwjo0juEmBlExEcv"
        "zo7bB+yTpq6L+mbJeXH72lMAAaQUUCrSAZCUTEQUXZhbnM/lhmbqccuqihTaVQ9pe+Dd15cPz31Tqgxm0qRkoRRh5taD+fNnJ6bG"
        "h7PLh3vja+ubW6ktGObeQ9mDu1KZCS0ee3T1u9PSlpYUj1xWY0eGR+6fHh36XCj/TiRiIizV2qmNapCmKGimLHugVfHLC3M33goA"
        "6O+3T6FvkJcLlUwmaTR/VcPEmh9YGgFhEGi6aUaJvn2TAKADgAaKsdD5Td7PuQVR9xtBshmRLsCdYoigGQAgAKDmlT61Kp5gEvSz"
        "Fuxu/TUDoCgKQ2r4ngMAQkopVp7cfb7x48t7M5HUY4bRJEQhgJBAbTPZYxRXXa+Yd++BmQjMBCH4+PSlPYNjU8/2Z4+N6rE4QEAU"
        "hiiuut66+/HM6zs3P0jJYnu4nVGsbLbnxPT1K8l07yQJTW/UfCfvvFpwHi+uSCmFUirq/sV/boGdPCk6/A/3JsZ12bBGhQAAAABJ"
        "RU5ErkJggg=="
    ),
    "dot_7fc08a_s": (
        "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAABWUlEQVR42m2QTyiDcRyHP9/f+74x7zab7aAWO1AUF3Pa3U3R0tiU"
        "g7jOQblIvV4lR0cnByeaEklJkSTJTnJRu4jlTwwv27vZ3r1fF1uS5/Q5fA5PD/CDpmkCf4gmo1J1y9WTrut210hvW0d356Aiyarx"
        "mN3fHN5MMTMREcsaa0In3R5bnBgNh8LzTr+r6bZ07zNe3hfcPu8yEU1rmiaImSk0GW6L9ceOIn0DD7DweXZ30X5jZoJW3sLV4WVk"
        "Z2l9WxARB1uCEeFXAuaXWXw3DedbwfCUzRKrHtX2NrvHa44Oqd5RkIt0kD7usW2WTct0KJJsMbMgIVQAEADw8WTs554/qIgv52cp"
        "VwdGRShSpVK2RC6b3wUAKZqMStszW5lAV2ujt7kp3OBWSVJkAYacPr8+Ta2eTCUSCabfeQZn40P+gC8OYlf+Nbe3Mbe2AqAMgGpx"
        "mZnwPwQA3yUzjUgsqHakAAAAAElFTkSuQmCC"
    ),
    "dot_7fc08a_b": (
        "iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAAB20lEQVR42m2RS2tTYRiE5/3OJdcmaaISahrBjcZFQERSpdDWWiiC"
        "FMGVuBKEWMS/8HHcCRWhLuzCX9CCICKKuwpeUqiNG2tT8FZrjDVJY3M7Jznf66IXRPqshtkMMwP8AzMT9oOx5+8KYmYQEWcmhwaT"
        "fYkh0/SKenkr//jO7DMAXUgIWFA6AJJSEhGp7N1b08dPpK50Am6sZdiw/7QRTRx4nXvy7uIH620FDNIkS2GNWLg2dWN6Ynzi0pl0"
        "ZqU/3L9W3CoFHep44kf7jvT0es51hT2X/Zh1tHlrngdvjp1Nn0zPjJwaXiqVf/n9ptfdbNSCG61KhBTs0MFI0mm4lZnb918JADgc"
        "jw+bcR9/2vjcG/GH7Gqr5v/RKMU00qBcpRkeU4UPhUYBQN9urpnQiHNri6kVT7hZd+oBhzs6MYGhiMFERAYACABo1hqL7VpTCI3o"
        "d6scdlRXp72FSSnXpeZmIw8AQkop3s8uvPi+/C1n+ry6aRg2gV2AXQAdb9Bn/CysV4vLxQdgJgKDIMADlwei6bHM80QqeVr36AAA"
        "5SoUV9erX5a+jj+9N7cgWYrt3J1TYsdiPeevXrgeiIZGhSDdrrfzhTeFh7lHL1ellMKyLLXv/f8jpRS7+i8Owse0cR7wQgAAAABJ"
        "RU5ErkJggg=="
    ),
    "dot_c58be0_s": (
        "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAABYUlEQVR42l2QPSwDcRjGn/f/v2vJtVxaTSrnm0GCoTFVwmKxiQgJ"
        "g0TEpgYWBrkeidgYJNLJYKvEIhImIhKDycRkkAtC46Mod23vNfgIftPzJM/w5Ad8wSYL/CM9kJbfWQEA0zQFWeSNtCcaW5tjvVBY"
        "s7P27uDm4AkzExGxwiYLsshbGksNx+JtyUgwGipc+8OZx9v5aFlkmYimTNMUMnmQhL3nNHV2d2x09cTvdEO7fMsWpN8J6tGQEa+K"
        "NJwurM6eCSLi+vq6vgrVMJyc+/769B5wnlw9576wHgh7lbox+vNRLZGlPkeji4NMjOEpxRxKpSILzCyEEBoACAC4ebB3b7NXJFw1"
        "4L4U/R68oip9xXwhL+6f77YBQKYH0nJ6a8JuqY2VR0NGvEzTSVV8gsHK8fn+UepwcTKRSDB967Esy5sbWumvDtcMARS8f83szKyP"
        "rwHIA5+7T+H8q/yFAOADebmF8+7P4jsAAAAASUVORK5CYII="
    ),
    "dot_c58be0_b": (
        "iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAAB4klEQVR42m2SP2hTURjFz3fffS9Jmza0UbTP2OA/SkoHUUIQBLVR"
        "EaFIwclFKXQQpIguTl4u3VyUDro41KlIwVURdFARrVSjBNQUUZQIFZKXRPPSNO/dz6GWCvqbfhzOcuAAf8HMhH8gMDbydSFmBhHx"
        "1NHpg6kB95B0pPD8SmF67tJ9AIGCEhraSACkFBMRmRtTszOZzPCZHpNMOu04Gise3P7B548X747pF7rKYLJYsTiiCdfP35k5fmp0"
        "fCQ39DGRin77tdyKi44d2e0OpWOxvlGKOvMfzhVWBWkyF4/pAzu377owuGfbp9qPeheTIZmgVhiGlt9utkfS+7L7U9lJrbURALDV"
        "dQ8PxHZw5fPPvmiv3V6ph12t5SBJAghNYEWciNmc2JIHALk2mRyLJH9/3chEeoW/2gy6uUOSiQEDAoMEWTYACACoNSuLdd8TFglq"
        "VYOECf6UARCRCcOQar5XAAChlBJzCzcfvv/69mUs2i1t226DTQhGCFAnHuuxS+WiVyoXbzEzEYNJkODTuYn+k7nxB8PpvVlHRgEA"
        "xoQolYvemy+vTlybv7LAioUkEKurSmitq++WnuXPjl2eTMY35aWwZMNvFJ6WHt2+92R2SSklSJPZuAX+d4s1lFJi3X8DLhnJpLgu"
        "p5kAAAAASUVORK5CYII="
    ),
    "dot_e07a6a_s": (
        "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAABWUlEQVR42m2QPSwDcRyG39//f8r1Wj1tKuJEfE0Sko7tYMEikUak"
        "EjaDDYPNdM5gZRMzk4ZFVDcGm0RiEo1ESGPw0aanV0fb+1lag3imd3iHJw/QgE1T4A+HqZRsbgUATNMUZFneylB0MDY8muQWn5Z3"
        "nOxcOn3FzERErHDjtLeQXBhJjG10+dvCrY+5yEvJ3oz61W0iWjMBITcuLvCVPhhKTE7sx6emX7W+/qdaqSiDjq0bYT0+EGm/Wb97"
        "uBVExH0DPTMGasa3W3HdYjHwXXjXy9UaR/xtntEeXPx1lKqmao5Nb5njmMdQ4NiqVJQaMwtBQgMAAQD50kf22fmkFtcJ1O1Sq0ei"
        "7pOiXq174rVcOQEAeZhKyeWTs3ysuzNkdITiul8lnxSCAeX8/vFy6zq3ulIoMDXzWJbl7STHZ3tD+jwRB9/K7unSUWYXQJUB+o3L"
        "zIT/IQD4AVTIiHJSd2dUAAAAAElFTkSuQmCC"
    ),
    "dot_e07a6a_b": (
        "iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAAB3UlEQVR42l2SS2sTYRSG3/PNN0lIJr2NUg0aFcTYICpUIYpSSRe6"
        "cRHQTTeCUOi6LnT3MfgPuvACInUpbgWloFBFpV5whKFaFEVrTJs2HZqSpnM9Lkq09Nmc88K7Os8BtsDMhG0QAN4c/zIAEDODiPjm"
        "4KEzub35IZlMikarbY8/fv4EQKgAYQGxBECsFBFRPDk6MlE8PDBi+uum0WrC9QPk+7pfP3w/d9GanV1hgDRWSpBl4cGVyxPlyqVK"
        "4dTZudT+g/PtP1VD99rJQv/Ofb2ZRDnB+iN7bMzXrOlptkrHTg8ePXKnWD7/cbVeS4u0EQVuwwjrtZ6QyMt1Gfmmv7Fy/e79VwIA"
        "crnd5w7ozGvfPvfqPaYXNZbSYfWXCU1DGMVaUpdxf1dmGAAkAJDUEpKZm29eDIgvznrYXM1Q4EkmsXkYBmkEHQAEADRaax9czxcC"
        "TOHSYjcFfqcMAuIojslt+zYACKWUuOX8nPpUrc9kUgmpJ3QvJooARAQKsqmk7iwsu85i7TYDRAyQAPhqqdRXKe55ejy362RKSgBA"
        "xDGchWX33Y/5CzemXr5lpQQBQEdKwTSz14ZOjO7Ipoc10mTT27Cfff99b3LG/qqUEpZlxf/fYov+7SilRGf/CxzQxMB+bRepAAAA"
        "AElFTkSuQmCC"
    ),
    "dot_5fc4bd_s": (
        "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAABYklEQVR42m2QvUsCcRjHn+e5uw7L00NNlHKICiJaokl6oRbXiNCo"
        "IegPsKGIIIifVw1tjdEQDS1hYwQOEQ5BQVNL0dBiBsFl9qqnnvc09AbRZ/oO3+HDB+ALwYLgD/F0Wvre8udLkIGG45meaO/p7hlV"
        "CZte83eZ/UTinJkREVkWzGQgOrH1lamR3r6UGvD7Lu2q//WhsOIOBjcQcQ6EICmbSsF2Pt8RG+jfHR0aNjt1X65glaWiqujecCiq"
        "tUYucqtrV4SI3NrWMlYJ+FpKFct6eH9zm1ZJr5dKrOpexx1qnvlxbFQk15Mi497NdS8zyy912yVLZDMzMUlNAAAEAPB8b2Ys08Q3"
        "QvdztaqSw3VSGupOzaZKsXgAACDF02npaH4hH+ju8mrhUNTl0ZCUBgJm+fb07OR4a2cWkknGzzqCDMNwBpcXx7VIZJKZtXLh8TC7"
        "JDYBoAYA+FuXGeF/EADgA1dMiM1Uguu7AAAAAElFTkSuQmCC"
    ),
    "dot_5fc4bd_b": (
        "iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAAB2klEQVR42m2RzUtUYRjFz/Pcj2k+YszBMSdKciE5WSDSJqIPB2II"
        "CgJr4aZVBC7C/+DlxVW2MNzUolWbFpHLioJAQskgnITGyQkCKy2zmTsf3emOc+/TQhQJf3DgcDirc4BdiAhhL3bl24ZEBEQkh2+P"
        "nulOHTwXNm12K+Xc7Pid5wBaUIqhdWACIKUUEVFw7d7dqWN96ZFaLJJwbAutahX7U11zK6+fXc5rXYIIGUoU6wsaVyYnpq5fzF49"
        "23/yU2+87etKrRJzmUOJnp5uIxwfapL5ZKxQaBozekZ6x26d7h8YfHBpYHBhzSlFYoblbzTc2GrDbaMg8KLJjiP+n3rpkR6fZQBI"
        "JQ+db3V1yseN9QOJfWFv/W8j8sWtJ0wiBH7LMEJ2EO3syACACQDEsMVgebX6rW8hZLtO04t6IibLzjAEYgsAGAA8x3m/WakyDKK1"
        "RiPeDHbKAFEQ+D55lUoOAFgpxXOPn778lV+at8MR07YsjwAfW9q0Y1GrtFwsO8uF+xAhggiBWdLDw+1Hs0MvksfTpwzb3vrL9/G7"
        "+Ln8I/ch+3Zi8p0SYRNEAqU4r3Xp5+Ji5sSNkZvhRHuG2DCb9Vru+5v5h0vT00WlFGuiYM/7/0cpxdv+H4I/yp2kwV6lAAAAAElF"
        "TkSuQmCC"
    ),
    "dot_e0b56f_s": (
        "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAABWUlEQVR42m2QPSwDcRyG39//f8ppL04FTS4VKYNIDLVVIkwmia+0"
        "CZvBpgaxmK5H0pVNrJhqkSBsDDaTpRYSkQahSlv9bu9naTuIZ3qHd3jyAHXYNAX+EIsFZWMrAGCapiDLssOz3gH/yPAMk8OZeE1f"
        "hkLHt8xMRMQK10/75vzSyOh4xONW3a2Fh673z8xWd4+2Q0TrpgkhI9fXKMWPBscmpg4Dk9MfTrfvuVr4lprM6EaPHvB59bvN6OO9"
        "ICLu9/nmDL1mlIvFYjGfcpVzSf2nUOWuDtU2urXlpqNsU1UnZSkZP/HbzAoqWVUKpcpsC0HCCQACABJvX5cvnwVq4ZyrVsq02hA1"
        "h0PWKlVbfKTzpwAgY8GgXD24SPiHPB1Grx7QtXZyKFIws3J1+3QTPYyvhcMppkYey7Ls3Y2phT5P5yKBtWQ6f76yfbYHoMIANeMy"
        "M+F/CAB+ARuGidcZWjOVAAAAAElFTkSuQmCC"
    ),
    "dot_e0b56f_b": (
        "iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAAB3UlEQVR42mWSP2hTYRTFz/3evzR/sDGhagKV4BBbpBSqoBJQWoQu"
        "DsVOHQQVwVkH3T4+pOAoRdShQx1FEDfFolBEQUV8YhRDqSjtYIxJyEua5s9733UoD4L+pnMPZ7n3HmAAZib8AwFgBg3OAEDMDCLi"
        "mxcmCpls5pRpO6Jaa7tXb68+BeBLCaEUtAmAWEoiIr1y6/zS+OGxhVSknYobLdSbfYxmh988XP1yVqmvNWaQwVIKUgoPFheWpmfP"
        "zeUnCqVI+tDmTmMrbtGOk8+NHEwmhqZtx3jkfrvSM9TaGqtLUyenJo/cHz965mOj9isq7GjQb1fjfqs87GvqZlLxUa/Vq11fXH4t"
        "ACCTPXA6NwJulktJayjZDVp/on5jMwUy4PuB4Tim3peOzgCAubu5YZuC2fv5akxEim2/48VId02GCA9DBpEFYNepNrY/1Js9IYjJ"
        "3/69h3QvDIMAHQSa6l7HBQAhpRR3n6w//1Qqv41FHdOy7K4GBQACAvUTcccqblTqxe+Ve8wgYgYJAb44f3zvXCH3bDK//1jENgEC"
        "gkCjuFGpv/+8NXvjzst3LKUgAAifks+nEtfmT1xOJ2MzhkGm1+y4L9wfyyuP3XUppVBK6YFa4L9ahEgpRaj/AhPrxZVTP3w8AAAA"
        "AElFTkSuQmCC"
    ),
    "dot_b0b0e8_s": (
        "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAABWUlEQVR42l2QP0gCcRzF3/d3Z2IqpyX+qRSiwFEjIRwc3NwiQqE2"
        "xwYDo6FBuK4hcGpoaGizRVwjEFoa2sIhBNsaogITJUHp1O6+Dfb/M70Hn+HxgE9UlQX+UalUpK8sjyVVaBqZqdTuQjQaWZVl2JvN"
        "+2omk7lhZiIillWVhaaRWSicbsZikX23OzDV601OdzovB2538IiIdlRVFdLV1T4aDSwmEvGzZHKl5fHYHt7eDIlIcfl8M/FAYP62"
        "WNy7E0TEoVBwTVFCs4PBUO/3B45+f+jS9R4ryrTp9Qaz3xsnJiQbkYPq9e4SM8vDIdmEoHdmCCGEHQAEAHQ6T9V2+5lM0+rQdcMK"
        "GIbFYjVGo5F4fW2dA4CUTlekUmnrMRxeVrzeubjT6SJZtgqA5Vrt8rpc1rZzuRzTzz2amc8fr/v98xsAnN1u6+LwMHsCYASMPQAA"
        "86/yFwKAD25SgUiO2zQkAAAAAElFTkSuQmCC"
    ),
    "dot_b0b0e8_b": (
        "iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAAB0UlEQVR42oWSP2hTYRTFz73vPZ95Sf2TFxo0VCsij2wtklJE8E8X"
        "MwgGOgmlk7OCg+PHK5UuDqUWVHATXVxbFAdLB0Ut2gyl1Ia2g0sRSZrney2x+b7rUIMdCj3Tj8Phwr33APskIoQDtN/vAIkIiEhG"
        "Rh5d7unJX7Ft5ij6VZ2cvPsGQFspxWEYGhsAKSVERGZ8/OVUsVi87brdPnMX4riBfP7cx7m5FzfDMKyLCFlKCYchYWzs1VS5fK3S"
        "13fhey7n/tjaamVEXLe3t3g2k/Gvp1LW65WVW3+s+flQRkcfXurvLz0dGAgW6/XfnuNAJ0k7E8f6hDG7Ld8vnImiqD4xUfrAAFAo"
        "nL7q++dlczM56XlWK0m012xqn0igddty3aMmlzs1BAD23s7WEWZb1te3i6kUtnd2TNoYsgEBIASAiNgBAAaAZvPn1zhuMBFTHMvx"
        "/2EAYKN1m6KoUQUAVkp4Zubxu9XVb589L2PbttUCjAZEA7SbTh9z1taWGrXa4hMRIRIRYmYZHr6XHRwsvw2CiyXHcUEEaK2xsbHU"
        "WF7+dGN6+v4XpYQJADpPCYKgq1J5cCeb7R4isuwkiaoLC++fz84+q/07vzm0FnsDhTv8F2ICzaEwcoB8AAAAAElFTkSuQmCC"
    ),
    "dot_ece4d6_s": (
        "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAABSElEQVR42m3Qv0sCcRjH8ef53tllSoRGdF4QlWNFP/6QisChraUx"
        "KNy/0VZDUUYQ/QAbCo4gwkXBrYaiyT8gtQM1VExQ4867+z4NaVT0nj7jhxdAJyJi8Cdd16XulgEAOOcMEUU0ujYxPzW3ACB8ubyR"
        "jEQiz0SEiEgyETFEFPHT2Mrk9MxWaHgo0NcrBcvl8raqqfuIuMk5Z0BEyPlG+PEhbRBZT47VSjeqRv6jlqViNkMnhzuLAAAMEWlc"
        "G1saHVE112qbbcv027Y50Gy2aDAYEFpIXf3+yCTJ2+/3YuO9NCtIyEjkRZQcAmLIJB8AAAMAKJQKyULxDXs8st91HMUVwlUUxbXb"
        "NqvUKolfBPGzg71SLkNW3SCz/krN6gvd6hf34XBY4Zx/0XXHcWx3OZW4vkneXaUuz4/WAcDTMUb4AY7wfwgA8AmnF5jawvPJKgAA"
        "AABJRU5ErkJggg=="
    ),
    "dot_ece4d6_b": (
        "iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAABy0lEQVR42n2SPWhTcRTFz73vpSlpUrUOaUgV1ErQScQPFK3BQmeX"
        "7EKRDgqiW3F4ZhCqKIgZHIyD0CJVBxFtq4IgKKjQEmMGQS0WBCkkeelHbJ55/3ccTKR08EyXe3/D4ZwLrBNJwQbJhn17EJIQEV4f"
        "u3Qsmeg7oWpruVounD0/Og3AdxxHs9ls0IIdBYDJ8Tu3Ps6+Kf/8XmK9Ms8fX+c49XjibSaT6Wk7sEmKiODBeD43kD55Kp5MlvxG"
        "Q+srlb2xaHTz0GD6aDjcMROJ/B4CLi+riATXrowe2dW/41w8ue1bvbYUMYZC6Joxxlqtr3oH9u87ePzwwBmRbKAAkOjtS/fv3M7G"
        "srvFDnV4xjQjNN5WAvB9Y3V2hoNEb3wQAGwAsCzpsC2ba/XqHhHrlzF+lwpskiAhAETVCgGAAsBiuTzrujVVVQmC5iYR2gEJAFCV"
        "wPd9cV23AABKOnozd/fFXKH4Phrtsi0r5AUBDQkjIs3u7ljoU+mzWyyWbpMUtFO6MDzc82r60YelxS/0agv0agusV+b57vVU9caY"
        "c6gVqwIAHOdvD6lUKnYvn7s48+T+s5dPJ58/nMhfHRk5vRsA2GL++xb/buvgP0wf27VEPWpgAAAAAElFTkSuQmCC"
    ),
}

APP_VERSION = "1.25"  # shown in the title bar so you can tell which build you are running
START_W, START_H = 1460, 855  # the window opens at this size every time

# ---------- logo (The Benefactor), embedded so no extra files are needed ----------
LOGO_ICON_B64 = (
    "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"
)
LOGO_HEADER_B64 = (
    "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"
)


def is_count(text):
    """Allow only blank or up to 4 digits in a quantity box."""
    return text == "" or (text.isdigit() and len(text) <= 4)


# ---------- update check (looks at the newest GitHub Release) ----------
GITHUB_REPO = "ubataz402-creator/The-Benefactor"
RELEASES_PAGE = f"https://github.com/{GITHUB_REPO}/releases"


def parse_version(text):
    """'v1.9' -> (1, 9); None if there's no number in it."""
    m = re.search(r"\d+(?:\.\d+)*", str(text or ""))
    return tuple(int(x) for x in m.group(0).split(".")) if m else None


def is_newer(remote, local):
    r, l = parse_version(remote), parse_version(local)
    if r is None or l is None:
        return False
    n = max(len(r), len(l))
    return r + (0,) * (n - len(r)) > l + (0,) * (n - len(l))


def check_latest_release(timeout=8):
    """Ask GitHub for the newest published release. Returns one of:
    ("new", tag, notes, url)  - a newer version exists
    ("current", tag)          - you already have the newest
    ("none",)                 - nothing has been published yet
    ("error", message)        - couldn't check"""
    req = urllib.request.Request(
        f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "The-Benefactor-update-check"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            info = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return ("none",)
        if e.code in (403, 429):
            return ("error", "GitHub is limiting requests right now. Try again in a few minutes.")
        return ("error", f"GitHub answered with error {e.code}.")
    except (urllib.error.URLError, OSError):
        return ("error", "Couldn't reach GitHub. Check your internet connection and try again.")
    except ValueError:
        return ("error", "GitHub's answer wasn't understood.")
    if not isinstance(info, dict):
        return ("error", "GitHub's answer wasn't understood.")
    tag = str(info.get("tag_name") or info.get("name") or "")
    if parse_version(tag) is None:
        return ("error", "The newest release has no version number in its name (use a tag like v1.9).")
    if not is_newer(tag, APP_VERSION):
        return ("current", tag)
    url = str(info.get("html_url") or "")
    if not url.lower().startswith(f"https://github.com/{GITHUB_REPO}/".lower()):
        url = RELEASES_PAGE          # only ever open pages of our own repository
    return ("new", tag, str(info.get("body") or "").strip()[:500], url)


# ---------- progress chart (drawing is computed here, then painted on a canvas) ----------
METRICS = {
    "My take": lambda h: h["sale"] - h["cut"],
    "Cut": lambda h: h["cut"],
    "Sale value": lambda h: h["sale"],
}
PALETTE = [GOLD, "#6fb3e0", "#7fc08a", VIP, "#e07a6a", "#5fc4bd", "#e0b56f", "#b0b0e8"]
COMBINED_COLOR = TEXT


def parse_when(text):
    try:
        return datetime.strptime(text, "%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return None


def whole(v):
    return "$" + format(int(round(v)), ",")


def money_short(v):
    if v >= 1_000_000:
        return f"${v / 1_000_000:g}M"
    if v >= 1000:
        return f"${v / 1000:g}k"
    return f"${v:g}"


def nice_ticks(vmax, target=5):
    """Round-number gridlines from 0 up to just above vmax."""
    if vmax <= 0:
        return [0, 1]
    raw = vmax / target
    mag = 10 ** math.floor(math.log10(raw))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw)
    n = int(math.ceil(vmax / step - 1e-9))
    return [i * step for i in range(n + 1)]


def make_series(name, color, entries, dashed=False):
    total, pts = 0, []
    for when, delta in entries:
        total += delta
        pts.append((when, total, delta))
    return {"name": name, "color": color, "points": pts, "total": total, "dashed": dashed}


def build_series(data, metric, combined=False):
    """One running-total line per client (plus an optional combined line)."""
    fn = METRICS[metric]
    colors = {n: PALETTE[i % len(PALETTE)] for i, n in enumerate(data)}  # colour stays with the client
    series, everything = [], []
    for name in sorted(data, key=str.lower):
        entries = []
        for h in data[name].get("history", []):
            when = parse_when(h.get("date"))
            if when is not None:
                entries.append((when, fn(h)))
        entries.sort(key=lambda e: e[0])
        everything += entries
        series.append(make_series(name, colors[name], entries))
    if combined and len(data) > 1:
        everything.sort(key=lambda e: e[0])
        series.append(make_series("All clients", COMBINED_COLOR, everything, dashed=True))
    return series


def tint(color, amount):
    """Mix a #rrggbb colour towards white."""
    c = color.lstrip("#")
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % tuple(int(v + (255 - v) * amount) for v in (r, g, b))


def mix(a, b, t):
    """Blend colour a towards colour b (0 = a, 1 = b); both #rrggbb."""
    a, b = a.lstrip("#"), b.lstrip("#")
    return "#%02x%02x%02x" % tuple(
        int(int(a[i:i + 2], 16) * (1 - t) + int(b[i:i + 2], 16) * t) for i in (0, 2, 4))


PLOT_BG, PLOT_DARK = "#122117", "#0d1911"


def smooth_curve(pts, step=6):
    """Smooth, never-overshooting curve (monotone cubic) through (x, y) points sorted by x."""
    xs, ys = [], []
    for x, y in pts:
        if xs and x - xs[-1] < 1e-6:
            ys[-1] = y
        else:
            xs.append(x)
            ys.append(y)
    n = len(xs)
    if n < 2:
        return list(zip(xs, ys))
    d = [(ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]) for i in range(n - 1)]
    m = [d[0]] + [0 if d[i - 1] * d[i] <= 0 else (d[i - 1] + d[i]) / 2 for i in range(1, n - 1)] + [d[-1]]
    for i in range(n - 1):
        if d[i] == 0:
            m[i] = m[i + 1] = 0
            continue
        a, b = m[i] / d[i], m[i + 1] / d[i]
        q = a * a + b * b
        if q > 9:
            t = 3 / math.sqrt(q)
            m[i], m[i + 1] = t * a * d[i], t * b * d[i]
    out = []
    for i in range(n - 1):
        h = xs[i + 1] - xs[i]
        k = max(1, int(h / step))
        for j in range(k):
            t = j / k
            t2, t3 = t * t, t * t * t
            y = ((2 * t3 - 3 * t2 + 1) * ys[i] + (t3 - 2 * t2 + t) * h * m[i]
                 + (-2 * t3 + 3 * t2) * ys[i + 1] + (t3 - t2) * h * m[i + 1])
            out.append((xs[i] + t * h, y))
    out.append((xs[-1], ys[-1]))
    return out


def area_strips(curve, bottom, color, amax=0.34, bands=12):
    """The soft fill under a line: horizontal slices that fade from the colour at the line to nothing."""
    ymin = min(y for _, y in curve)
    if bottom - ymin < 2:
        return []
    out = []
    for k in range(bands):
        y0 = ymin + (bottom - ymin) * k / bands
        y1 = ymin + (bottom - ymin) * (k + 1) / bands
        fill = mix(PLOT_BG, color, amax * (1 - (k + 0.5) / bands))
        yb = min(y1 + 1, bottom)
        run = []
        for x, y in curve + [(None, None)]:
            if x is not None and y < y1 - 0.01:      # the curve is above this slice's bottom edge
                run.append((x, min(max(y, y0), y1)))
                continue
            if len(run) >= 2:
                out.append({"t": "poly", "pts": run + [(run[-1][0], yb), (run[0][0], yb)], "fill": fill})
            run = []
    return out


def build_scene(series, w, h, selected=None):
    """Return (primitives, hits). Primitives are plain dicts a canvas can paint;
    hits are (x, y, text) points for hover tooltips."""
    prims, hits = [], []
    allpts = [p for s in series for p in s["points"]]
    if not allpts:
        if w >= 160 and h >= 40:
            prims.append({"t": "text", "x": w / 2, "y": h / 2, "anchor": "center", "color": MUTED, "size": 10,
                          "text": "No saved entries yet.\nSave an entry and your progress will show up here."})
        return prims, hits
    if w < 240 or h < 170:
        return prims, hits

    ml, mr, mb = 66, 24, 34
    # legend (wraps onto more rows when there are many clients)
    x, row = ml, 0
    for s in series:
        label = f"{s['name']}  {whole(s['total'])}"
        item_w = 26 + len(label) * 6.6 + 18
        if x > ml and x + item_w > w - mr:
            x, row = ml, row + 1
        y = 14 + row * 18
        prims.append({"t": "oval", "x": x + 5, "y": y, "r": 4.5, "fill": s["color"]})
        prims.append({"t": "text", "x": x + 16, "y": y, "anchor": "w", "color": TEXT, "size": 9, "text": label})
        x += item_w
    top = 14 + (row + 1) * 18 + 8
    left, right, bottom = ml, w - mr, h - mb
    if bottom - top < 60:
        return prims, hits

    ticks = nice_ticks(max(p[1] for p in allpts), 5)
    ymax = ticks[-1] or 1
    t0 = min(p[0] for p in allpts)
    t1 = max(p[0] for p in allpts)
    if t0 == t1:
        t0, t1 = t0 - timedelta(hours=12), t1 + timedelta(hours=12)
    else:
        pad = (t1 - t0) * 0.03
        t0, t1 = t0 - pad, t1 + pad
    span = (t1 - t0).total_seconds()

    def px(t):
        return left + (t - t0).total_seconds() / span * (right - left)

    def py(v):
        return bottom - v / ymax * (bottom - top)

    prims.append({"t": "rect", "x0": left, "y0": top, "x1": right, "y1": bottom, "fill": PLOT_BG})
    bands = 8 if right - left > 520 else 6
    for i in range(0, bands, 2):
        prims.append({"t": "rect", "x0": left + (right - left) * i / bands, "y0": top,
                      "x1": left + (right - left) * (i + 1) / bands, "y1": bottom, "fill": PLOT_DARK})
    for tv in ticks:
        y = py(tv)
        prims.append({"t": "line", "pts": [(left, y), (right, y)], "color": "#1b3724" if tv else MUTED, "width": 1, "dash": None})
        prims.append({"t": "text", "x": left - 8, "y": y, "anchor": "e", "color": MUTED, "size": 9, "text": money_short(tv)})
    n = 5 if right - left > 520 else 3
    days = span / 86400
    fmt = "%b %d, %Y" if days > 180 else ("%b %d" if days >= 2 else "%b %d %H:%M")
    for i in range(n):
        t = t0 + (t1 - t0) * (i / (n - 1))
        prims.append({"t": "text", "x": px(t), "y": bottom + 8, "anchor": "n", "color": MUTED, "size": 9,
                      "text": t.strftime(fmt)})

    ordered = [s for s in series if s["name"] != selected] + [s for s in series if s["name"] == selected]
    curves = {}
    for s in ordered:
        pts = [(px(t), py(v)) for t, v, _ in s["points"]]
        curves[s["name"]] = smooth_curve(pts) if len(pts) >= 2 else pts
    for s in ordered:                                  # soft fills first so no fill covers another line
        if len(curves[s["name"]]) >= 2 and not s["dashed"]:
            prims.extend(area_strips(curves[s["name"]], bottom, s["color"], 0.40 if s["name"] == selected else 0.30))
    for s in ordered:
        thick = s["name"] == selected
        c = curves[s["name"]]
        if len(c) >= 2:
            wd = 3.2 if thick else 2.2
            if not s["dashed"]:                        # glow
                prims.append({"t": "line", "pts": c, "color": mix(PLOT_BG, s["color"], 0.22), "width": wd + 6, "dash": None})
                prims.append({"t": "line", "pts": c, "color": mix(PLOT_BG, s["color"], 0.5), "width": wd + 3, "dash": None})
            prims.append({"t": "line", "pts": c, "color": s["color"], "width": wd,
                          "dash": (5, 4) if s["dashed"] else None})
    for s in ordered:
        r = 4.5 if s["name"] == selected else 3.5
        for (t, v, d) in s["points"]:
            prims.append({"t": "oval", "x": px(t), "y": py(v), "r": r, "fill": s["color"]})
            prims.append({"t": "shine", "x": px(t) - r * 0.3, "y": py(v) - r * 0.35, "r": r * 0.38, "fill": tint(s["color"], 0.6)})
            hits.append((px(t), py(v), f"{s['name']}\n{t.strftime('%b %d, %H:%M')}\n+{whole(d)}  \u2192  {whole(v)} total"))
    return prims, hits


MARGIN = 28                       # width of the engraved border around the window


def rosette(cx, cy, R, r, d, turns, steps=360):
    """A spirograph (hypotrochoid) rosette, like the ones engraved on banknotes."""
    pts = []
    k = (R - r) / r
    for i in range(steps * turns + 1):
        t = 2 * math.pi * i / steps
        pts.append((cx + (R - r) * math.cos(t) + d * math.cos(k * t), cy + (R - r) * math.sin(t) - d * math.sin(k * t)))
    return pts


def build_banknote(w, h, margin=MARGIN):
    """Engraved banknote border (green, with gold seals) for the window background."""
    line = mix(BG, "#5fb97a", 0.72)
    faint = mix(BG, "#5fb97a", 0.42)
    gold = "#8a7234"
    prims = [{"t": "rect", "x0": 0, "y0": 0, "x1": w, "y1": h, "fill": BG}]
    if w < 3 * margin or h < 3 * margin:
        return prims
    for inset, col in ((6, gold), (margin - 7, faint)):
        prims.append({"t": "line", "pts": [(inset, inset), (w - inset, inset), (w - inset, h - inset),
                                            (inset, h - inset), (inset, inset)], "color": col, "width": 1})
    mid = margin / 2
    amp, lam = 4.2, 46.0
    for k in range(4):                                  # ribbon of interlaced waves along each edge
        ph = k * 0.52
        col = line if k % 2 == 0 else faint
        for horiz, length, ys in ((True, w, (mid, h - mid)), (False, h, (mid, w - mid))):
            for base in ys:
                pts = []
                for i in range(int((length - 2 * margin) / 8) + 1):
                    u = margin + i * 8
                    v = base + amp * math.sin(2 * math.pi * u / lam + ph) * (0.55 + 0.45 * math.cos(math.pi * (u - length / 2) / length))
                    pts.append((u, v) if horiz else (v, u))
                prims.append({"t": "line", "pts": pts, "color": col, "width": 1})
    for cx, cy in ((mid, mid), (w - mid, mid), (mid, h - mid), (w - mid, h - mid)):   # corner seals
        prims.append({"t": "line", "pts": rosette(cx, cy, 13, 4, 8, 4, 40), "color": gold, "width": 1})
        prims.append({"t": "line", "pts": rosette(cx, cy, 9, 3, 5, 3, 32), "color": "#b99a45", "width": 1})
    prims.append({"t": "text", "x": w / 2, "y": mid, "text": "$   \u00b7   $   \u00b7   $   \u00b7   $", "color": gold, "size": 9})
    prims.append({"t": "text", "x": w / 2, "y": h - mid, "text": "$   \u00b7   $   \u00b7   $   \u00b7   $", "color": gold, "size": 9})
    return prims


def paint_scene(cv, prims):
    cv.delete("all")
    for p in prims:
        if p["t"] == "rect":
            cv.create_rectangle(p["x0"], p["y0"], p["x1"], p["y1"], fill=p["fill"], outline=p.get("outline", ""))
        elif p["t"] == "oval":
            cv.create_oval(p["x"] - p["r"], p["y"] - p["r"], p["x"] + p["r"], p["y"] + p["r"],
                           fill=p["fill"], outline=p.get("outline", ""))
        elif p["t"] == "line":
            flat = [c for pt in p["pts"] for c in pt]
            if len(flat) >= 4:
                cv.create_line(*flat, fill=p["color"], width=p["width"])
        elif p["t"] == "text":
            cv.create_text(p["x"], p["y"], text=p["text"], fill=p["color"], anchor=p.get("anchor", "center"),
                           font=p.get("font") or ("Georgia", p["size"], "bold"))


# ---------- scoreboard (pure functions) ----------
TIERS = [(100000, "Legend", "#c58be0"), (40000, "Platinum", "#7fd6d0"), (15000, "Gold", "#d4a94f"),
         (5000, "Silver", "#b8c4c0"), (0, "Bronze", "#c98a5a")]       # by total deposited
SCORE_METRICS = ["Overall score", "Total deposited", "Deposits", "Average deposit", "Frequency"]
MEDALS = {1: "#f0cd7a", 2: "#c9d3d0", 3: "#d99a66"}


def tier_for(total):
    for floor, name, color in TIERS:
        if total >= floor:
            return name, color
    return TIERS[-1][1], TIERS[-1][2]


def client_stats(name, profile, now):
    """What one client has deposited (a deposit is an entry; its amount is the entry's sale value)."""
    hist = profile.get("history", [])
    amounts = [h.get("sale", 0) for h in hist]
    when = sorted(d for d in (parse_when(h.get("date")) for h in hist) if d)
    n = len(hist)
    total = sum(amounts)
    gap = None
    if len(when) >= 2:
        span = (when[-1] - when[0]).total_seconds() / 86400
        if span > 0:
            gap = span / (len(when) - 1)             # average days between deposits
    return {"name": name, "type": profile.get("type", "regular"), "n": n, "total": total,
            "avg": total / n if n else 0, "big": max(amounts) if amounts else 0, "gap": gap,
            "per_week": 7 / gap if gap else 0.0,
            "since": (now - when[-1]).total_seconds() / 86400 if when else None,
            "take": sum(h.get("sale", 0) - h.get("cut", 0) for h in hist),
            "free": sum(1 for h in hist if h.get("free"))}


def build_scoreboard(data, metric, now):
    """Rows for every client, ranked by the chosen metric. Overall score (0-100) blends total
    deposited (50%), number of deposits (25%) and how often they deposit (25%)."""
    rows = [client_stats(n, p, now) for n, p in data.items()]
    mt = max([r["total"] for r in rows] + [0])
    mn = max([r["n"] for r in rows] + [0])
    mf = max([r["per_week"] for r in rows] + [0])
    for r in rows:
        r["score"] = round(100 * (0.5 * (r["total"] / mt if mt else 0) + 0.25 * (r["n"] / mn if mn else 0)
                                  + 0.25 * (r["per_week"] / mf if mf else 0)))
        r["tier"], r["tier_color"] = tier_for(r["total"])
    key = {"Overall score": "score", "Total deposited": "total", "Deposits": "n",
           "Average deposit": "avg", "Frequency": "per_week"}.get(metric, "score")
    rows.sort(key=lambda r: (-r[key], -r["total"], r["name"].lower()))
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    return rows


def metric_text(row, metric):
    if metric == "Total deposited":
        return whole(row["total"])
    if metric == "Deposits":
        return f"{row['n']} deposit{'' if row['n'] == 1 else 's'}"
    if metric == "Average deposit":
        return whole(row["avg"])
    if metric == "Frequency":
        return gap_text(row["gap"])
    return f"{row['score']} pts"


def gap_text(gap):
    if gap is None:
        return "\u2014"
    return f"every {gap * 24:.0f} hrs" if gap < 1 else f"every {gap:.1f} days"


def ago_text(days):
    if days is None:
        return "\u2014"
    if days < 1:
        return "today"
    d = int(days)
    return f"{d} day{'' if d == 1 else 's'} ago"


def build_podium(rows, w, h, metric):
    """Gold / silver / bronze podium for the top three."""
    prims = []
    base = h - 12
    prims.append({"t": "line", "pts": [(14, base), (w - 14, base)], "color": LINE, "width": 1})
    top3 = rows[:3]
    if not top3 or w < 260 or h < 150:
        return prims
    avail = h - 86
    gap = min(200, w / 4)
    bw = min(150, gap - 16)
    spots = {1: (w / 2, 1.0), 2: (w / 2 - gap, 0.72), 3: (w / 2 + gap, 0.54)}
    for r in top3:
        cx, frac = spots[r["rank"]]
        col = MEDALS[r["rank"]]
        bh = avail * frac
        top = base - bh
        prims.append({"t": "rect", "x0": cx - bw / 2, "y0": top, "x1": cx + bw / 2, "y1": base,
                      "fill": mix(PANEL, col, 0.22), "outline": col})
        prims.append({"t": "text", "x": cx, "y": top + min(34, bh / 2), "text": str(r["rank"]), "color": col,
                      "size": 26, "font": ("Georgia", 26, "bold")})
        prims.append({"t": "text", "x": cx, "y": top - 38, "text": r["name"], "color": TEXT,
                      "size": 12, "font": (FONT, 12, "bold")})
        prims.append({"t": "text", "x": cx, "y": top - 18, "text": metric_text(r, metric), "color": GOLD2,
                      "size": 11, "font": (FONT, 11)})
        if bh > 70:
            prims.append({"t": "text", "x": cx, "y": base - 16, "text": r["tier"], "color": r["tier_color"],
                          "size": 9, "font": (FONT, 9, "bold")})
    return prims


SPRITE_IMGS = {}
SPRITE_MIDS = {}
SPRITES_OK = [True]


def sprite(name):
    """An embedded anti-aliased picture as a Tk image (None if it can't be made: callers then draw plain shapes)."""
    img = SPRITE_IMGS.get(name)
    if img is None and SPRITES_OK[0] and name in SPRITES:
        try:
            img = SPRITE_IMGS[name] = tk.PhotoImage(data=SPRITES[name])
        except Exception:
            SPRITES_OK[0] = False
            return None
    return img


def stretched(name, n):
    """The 1-pixel-wide middle slice of a button, repeated n pixels wide."""
    key = (name, n)
    if key not in SPRITE_MIDS:
        SPRITE_MIDS[key] = sprite(name).zoom(n, 1)
    return SPRITE_MIDS[key]


TILE_GLYPHS = {"history": "clock", "clients": "people", "progress": "chart", "notes": "page"}


def load_settings(path):
    """Small app settings kept beside the client data. Anything unreadable falls back to the defaults."""
    out = {"start_screen": True}
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict) and isinstance(data.get("start_screen"), bool):
            out["start_screen"] = data["start_screen"]
    except (OSError, ValueError):
        pass
    return out


def save_settings(path, settings):
    try:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(settings, fh, indent=2)
        os.replace(tmp, path)
        return True
    except OSError:
        return False


def start_stats(data):
    """(clients, entries, my take) shown on the start screen."""
    entries = sum(len(p.get("history", [])) for p in data.values())
    take = sum(h.get("sale", 0) - h.get("cut", 0) for p in data.values() for h in p.get("history", []))
    return len(data), entries, take


class Tile(tk.Canvas):
    """A big rounded menu tile: icon, title and a small caption. Click to open its page."""

    W, H = 150, 60
    KIND = "tile"

    def __init__(self, parent, title, sub, glyph, command):
        super().__init__(parent, width=self.W, height=self.H, bg=PANEL, highlightthickness=0, bd=0, cursor="hand2")
        self.title, self.sub, self.glyph, self.command = title, sub, glyph, command
        self.active = self.hover = False
        self.bind("<Enter>", lambda e: self.flag("hover", True))
        self.bind("<Leave>", lambda e: self.flag("hover", False))
        self.bind("<ButtonRelease-1>", lambda e: self.command() if self.command else None)
        self.draw()

    def flag(self, name, value):
        if getattr(self, name) != value:
            setattr(self, name, value)
            self.draw()

    def set_sub(self, text):
        if text != self.sub:
            self.sub = text
            self.draw()

    def set_active(self, on):
        self.flag("active", bool(on))

    def draw(self):
        img = sprite(f"{self.KIND}_{self.glyph}_{'a' if self.active else ('h' if self.hover else 'n')}")
        if img is None:
            return self.draw_shapes()
        self.delete("all")
        self.create_image(0, 0, image=img, anchor="nw")
        self.draw_labels()

    def draw_labels(self):
        ink = GOLD2 if self.active else TEXT
        self.create_text(58, self.H / 2 - 8, text=self.title, anchor="w", fill=ink, font=(FONT, 11, "bold"))
        self.create_text(58, self.H / 2 + 11, text=self.sub, anchor="w", fill=MUTED, font=(FONT, 9))

    def draw_shapes(self):
        self.delete("all")
        w, h = self.W, self.H
        fill = mix(PANEL2, GOLD, 0.16) if self.active else (mix(PANEL2, "#ffffff", 0.07) if self.hover else PANEL2)
        rim = GOLD if self.active else (GOLD2 if self.hover else "#3d6a4b")
        for box, r, col in (((1, 1, w - 1, h - 1), 18, rim), ((2, 2, w - 2, h - 2), 17, fill),
                            ((14, 5, w - 14, h * 0.45), 10, mix(fill, "#ffffff", 0.07))):
            self.create_polygon(*rrect_points(*box, r), smooth=True, fill=col, outline="")
        ink = GOLD2 if self.active else TEXT
        cx, cy = 32, h / 2
        self.create_oval(cx - 19, cy - 19, cx + 19, cy + 19, fill=mix(PANEL, GOLD, 0.10 if self.active else 0.03), outline=rim)
        g = TILE_GLYPHS.get(self.glyph, "chart")
        if g == "clock":
            self.create_oval(cx - 10, cy - 10, cx + 10, cy + 10, outline=ink, width=2)
            self.create_line(cx, cy, cx, cy - 6, fill=ink, width=2)
            self.create_line(cx, cy, cx + 5, cy + 2, fill=ink, width=2)
        elif g == "people":
            self.create_oval(cx - 4, cy - 10, cx + 4, cy - 2, outline=ink, width=2)
            self.create_arc(cx - 10, cy, cx + 10, cy + 20, start=0, extent=180, style="arc", outline=ink, width=2)
        elif g == "page":
            self.create_rectangle(cx - 8, cy - 10, cx + 8, cy + 10, outline=ink, width=2)
            for dy in (-4, 1, 6):
                self.create_line(cx - 4, cy + dy, cx + 4, cy + dy, fill=ink, width=1)
        else:
            self.create_line(cx - 10, cy + 9, cx + 10, cy + 9, fill=ink, width=2)
            self.create_line(cx - 10, cy + 5, cx - 3, cy - 2, cx + 2, cy + 2, cx + 10, cy - 8, fill=ink, width=2)
        self.create_text(58, h / 2 - 8, text=self.title, anchor="w", fill=ink, font=(FONT, 11, "bold"))
        self.create_text(58, h / 2 + 11, text=self.sub, anchor="w", fill=MUTED, font=(FONT, 9))


class NavTile(Tile):
    """A tall sidebar tile: icon over a title."""

    W, H = 104, 92
    KIND = "nav"

    def draw_labels(self):
        self.create_text(self.W / 2, 73, text=self.title, fill=GOLD2 if self.active else TEXT, font=(FONT, 10, "bold"))

    def draw_shapes(self):
        self.delete("all")
        w, h = self.W, self.H
        fill = mix(PANEL2, GOLD, 0.16) if self.active else (mix(PANEL2, "#ffffff", 0.07) if self.hover else PANEL2)
        rim = GOLD if self.active else (GOLD2 if self.hover else "#3d6a4b")
        for box, r, col in (((1, 1, w - 1, h - 1), 20, rim), ((2, 2, w - 2, h - 2), 19, fill),
                            ((12, 5, w - 12, h * 0.4), 12, mix(fill, "#ffffff", 0.07))):
            self.create_polygon(*rrect_points(*box, r), smooth=True, fill=col, outline="")
        ink = GOLD2 if self.active else TEXT
        cx, cy = w / 2, 32
        self.create_oval(cx - 21, cy - 21, cx + 21, cy + 21, fill=mix(PANEL, GOLD, 0.10 if self.active else 0.03), outline=rim)
        if self.glyph == "trophy":
            self.create_polygon(cx - 9, cy - 11, cx + 9, cy - 11, cx + 7, cy + 2, cx + 2, cy + 6, cx - 2, cy + 6,
                                cx - 7, cy + 2, outline=ink, fill="", width=2)
            self.create_arc(cx - 15, cy - 9, cx - 5, cy + 1, start=90, extent=180, style="arc", outline=ink, width=2)
            self.create_arc(cx + 5, cy - 9, cx + 15, cy + 1, start=-90, extent=180, style="arc", outline=ink, width=2)
            self.create_line(cx, cy + 6, cx, cy + 10, fill=ink, width=2)
            self.create_line(cx - 6, cy + 11, cx + 6, cy + 11, fill=ink, width=2)
        else:                                                    # ledger book
            self.create_rectangle(cx - 9, cy - 11, cx + 9, cy + 11, outline=ink, width=2)
            self.create_line(cx - 4, cy - 11, cx - 4, cy + 11, fill=ink, width=2)
            for dy in (-5, 0, 5):
                self.create_line(cx, cy + dy, cx + 5, cy + dy, fill=ink, width=1)
        self.create_text(w / 2, 73, text=self.title, fill=ink, font=(FONT, 10, "bold"))


BUBBLE_ON = False


def set_bubble(flag):
    global BUBBLE_ON
    BUBBLE_ON = bool(flag)


def rrect_points(x0, y0, x1, y1, r):
    """Outline of a rounded rectangle, for a smoothed canvas polygon."""
    r = max(0, min(r, (x1 - x0) / 2, (y1 - y0) / 2))
    return [x0 + r, y0, x0 + r, y0, x1 - r, y0, x1 - r, y0, x1, y0, x1, y0 + r, x1, y0 + r, x1, y1 - r, x1, y1 - r,
            x1, y1, x1 - r, y1, x1 - r, y1, x0 + r, y1, x0 + r, y1, x0, y1, x0, y1 - r, x0, y1 - r, x0, y0 + r,
            x0, y0 + r, x0, y0]


BUTTON_KINDS = {            # fill, rim, text colour
    "btn": (PANEL2, "#2b5939", TEXT),
    "acc": (GOLD, GOLD2, "#1a1509"),
    "sml": ("#183220", "#2b5939", TEXT),
    "stp": (PANEL2, "#2b5939", TEXT),
}


def button_scene(kind, w, h, state="normal"):
    """Shapes for one bubble button; state is normal / hover / pressed / disabled."""
    fill, rim, fg = BUTTON_KINDS.get(kind, BUTTON_KINDS["btn"])
    if state == "hover":
        fill, rim = mix(fill, "#ffffff", 0.10), (GOLD2 if kind != "acc" else "#ffffff")
    elif state == "pressed":
        fill = mix(fill, "#000000", 0.18)
    elif state == "disabled":
        fill, rim, fg = mix(fill, PANEL, 0.55), mix(rim, PANEL, 0.6), MUTED
    r = h / 2
    pill = kind != "stp"
    shapes = [{"t": "rrect", "box": (1, 1, w - 1, h - 1), "r": r, "fill": rim},
              {"t": "rrect", "box": (2, 2, w - 2, h - 2), "r": r - 1, "fill": fill}]
    gloss = 0.28 if kind == "acc" else 0.12
    if state == "disabled":
        gloss = 0.03
    shapes.append({"t": "rrect", "box": (h * 0.35 if pill else 6, 4, w - (h * 0.35 if pill else 6), h * 0.48),
                   "r": h * 0.22, "fill": mix(fill, "#ffffff", gloss)})
    off = 1 if state == "pressed" else 0
    return shapes, (w / 2, h / 2 + off, fg)


class BubbleButton(tk.Canvas):
    """A rounded, glossy button drawn by hand. Supports the bits of ttk.Button the app uses:
    configure(text=...), state([...]) and a command."""

    def __init__(self, parent, text="", command=None, kind="btn"):
        self.kind, self.command, self.text = kind, command, text
        self.disabled = self.hover = self.down = False
        self.font = tkfont.Font(family=FONT, size=9 if kind == "sml" else 10,
                                weight="bold" if kind == "acc" else "normal")
        w, h = self.fit()
        super().__init__(parent, width=w, height=h, bg=PANEL, highlightthickness=0, bd=0, takefocus=1)
        self.bind("<Enter>", lambda e: self.flag("hover", True))
        self.bind("<Leave>", lambda e: (self.flag("hover", False), self.flag("down", False)))
        self.bind("<ButtonPress-1>", lambda e: self.flag("down", True))
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<space>", lambda e: self.invoke())
        self.bind("<Return>", lambda e: self.invoke())
        self.draw()

    def fit(self):
        if self.kind == "stp":
            return 32, 32
        return max(self.font.measure(self.text) + (36 if self.kind != "sml" else 28), 64), (28 if self.kind == "sml" else 34)

    def flag(self, name, value):
        if getattr(self, name) != value:
            setattr(self, name, value)
            self.draw()

    def on_release(self, e):
        was = self.down
        self.flag("down", False)
        if was and 0 <= e.x <= int(self.cget("width")) and 0 <= e.y <= int(self.cget("height")):
            self.invoke()

    def invoke(self):
        if not self.disabled and self.command:
            self.command()

    def configure(self, cnf=None, **kw):
        if "text" in kw:
            self.text = kw.pop("text")
            w, h = self.fit()
            kw.update(width=w, height=h)
        result = super().configure(cnf, **kw) if (cnf or kw) else super().configure()
        self.draw()
        return result

    config = configure

    def state(self, spec=None):
        for s in spec or []:
            if s == "disabled":
                self.disabled = True
            elif s == "!disabled":
                self.disabled = False
        self.configure(cursor="arrow" if self.disabled else "hand2")
        return ()

    def draw(self):
        self.delete("all")
        w, h = int(self.cget("width")), int(self.cget("height"))
        st = "disabled" if self.disabled else ("pressed" if self.down else ("hover" if self.hover else "normal"))
        shapes, (tx, ty, fg) = button_scene(self.kind, w, h, st)
        key = {"normal": "n", "hover": "h", "pressed": "p", "disabled": "d"}[st]
        drawn = False
        if self.kind == "stp":
            img = sprite(f"stp_{key}")
            if img:
                self.create_image(0, 0, image=img, anchor="nw")
                drawn = True
        else:
            left, mid, right = (sprite(f"{self.kind}_{key}_{part}") for part in "LMR")
            if left and mid and right and w - 2 * left.width() >= 1:
                cap = left.width()
                self.create_image(0, 0, image=left, anchor="nw")
                self.create_image(cap, 0, image=stretched(f"{self.kind}_{key}_M", w - 2 * cap), anchor="nw")
                self.create_image(w - cap, 0, image=right, anchor="nw")
                drawn = True
        if not drawn:
            for sh in shapes:
                self.create_polygon(*rrect_points(*sh["box"], sh["r"]), smooth=True, fill=sh["fill"], outline="")
        self.create_text(tx, ty, text=self.text, fill=fg, font=self.font)


class BubbleCheck(tk.Canvas):
    """A tick box with a glossy rounded square, drawn from embedded pictures."""

    def __init__(self, parent, text, variable, command=None):
        self.text, self.variable, self.command = text, variable, command
        self.hover = False
        self.font = tkfont.Font(family=FONT, size=10)
        super().__init__(parent, width=34 + self.font.measure(text), height=24, bg=PANEL, highlightthickness=0,
                         bd=0, takefocus=1, cursor="hand2")
        self.bind("<Enter>", lambda e: self.set_hover(True))
        self.bind("<Leave>", lambda e: self.set_hover(False))
        self.bind("<Button-1>", self.toggle)
        self.bind("<space>", self.toggle)
        variable.trace_add("write", lambda *a: self.draw())
        self.draw()

    def set_hover(self, on):
        self.hover = on
        self.draw()

    def toggle(self, _event=None):
        self.variable.set(not self.variable.get())
        if self.command:
            self.command()

    def draw(self):
        try:
            self.delete("all")
            on = bool(self.variable.get())
            img = sprite(f"chk_{1 if on else 0}_{'h' if self.hover else 'n'}")
            if img:
                self.create_image(2, 2, image=img, anchor="nw")
            else:
                self.create_rectangle(3, 3, 21, 21, outline=GOLD if on else LINE, fill=FIELD)
                if on:
                    self.create_line(7, 12, 11, 17, 18, 7, fill=GOLD2, width=2)
            self.create_text(30, 12, text=self.text, anchor="w", fill=GOLD2 if self.hover else TEXT, font=self.font)
        except tk.TclError:
            pass                                    # the box was closed while the variable still exists


def checkbox(parent, text, variable, command=None):
    if BUBBLE_ON:
        return BubbleCheck(parent, text, variable, command)
    return ttk.Checkbutton(parent, text=text, variable=variable, style="Card.TCheckbutton", command=command)


def button(parent, text="", command=None, style=None):
    """A bubble button when the bubble look is on, otherwise the plain ttk button."""
    if BUBBLE_ON:
        kind = {"Accent.TButton": "acc", "Danger.TButton": "sml", "Step.TButton": "stp"}.get(style, "btn")
        return BubbleButton(parent, text, command, kind)
    return ttk.Button(parent, text=text, command=command, **({"style": style} if style else {}))


class NewClientDialog:
    """Small modal window asking for a name and VIP/regular."""

    def __init__(self, parent, title="New client", name="", ctype="regular", ok_text="Create", reprice=False):
        self.result = None
        self.with_reprice = reprice
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.configure(bg=PANEL)
        self.top.resizable(False, False)
        self.top.transient(parent)

        body = ttk.Frame(self.top, style="Card.TFrame", padding=18)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="Name", style="Card.TLabel").grid(row=0, column=0, sticky="w")
        self.name = tk.StringVar(value=name)
        self.entry = ttk.Entry(body, textvariable=self.name, width=28)
        self.entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(2, 12))

        self.ctype = tk.StringVar(value=ctype)
        ttk.Radiobutton(body, text="Regular", value="regular", variable=self.ctype,
                        style="Card.TRadiobutton").grid(row=2, column=0, sticky="w")
        ttk.Radiobutton(body, text="VIP", value="vip", variable=self.ctype,
                        style="Card.TRadiobutton").grid(row=2, column=1, sticky="w")

        self.again = tk.BooleanVar(value=False)
        if reprice:
            checkbox(body, "Recalculate their past entries at the new prices", self.again).grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))
        self.error = ttk.Label(body, text="", style="Card.TLabel", foreground=RED)
        self.error.grid(row=4, column=0, columnspan=2, sticky="w", pady=(8, 0))

        btns = ttk.Frame(body, style="Card.TFrame")
        btns.grid(row=5, column=0, columnspan=2, sticky="e", pady=(12, 0))
        button(btns, text="Cancel", command=self.cancel).pack(side="left", padx=(0, 8))
        button(btns, text=ok_text, style="Accent.TButton", command=self.ok).pack(side="left")

        self.top.bind("<Return>", lambda e: self.ok())
        self.top.bind("<Escape>", lambda e: self.cancel())
        self.top.protocol("WM_DELETE_WINDOW", self.cancel)

        self.top.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.top.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.top.winfo_height()) // 3
        self.top.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        self.top.grab_set()
        self.entry.focus_set()
        if name:
            self.entry.selection_range(0, "end")

    def ok(self):
        name = self.name.get().strip()
        if not name:
            self.error.configure(text="Enter a client name.")
            return
        if len(name) > 40:
            self.error.configure(text="Name is too long (40 characters max).")
            return
        self.result = (name, self.ctype.get()) + ((self.again.get(),) if self.with_reprice else ())
        self.top.destroy()

    def cancel(self):
        self.top.destroy()

    def show(self):
        self.top.wait_window()
        return self.result


def is_money_text(text):
    """Typing filter for price boxes: digits with up to 2 decimals."""
    return re.fullmatch(r"\d{0,7}(\.\d{0,2})?", text) is not None


def show_price(v):
    return str(int(v)) if float(v) == int(v) else f"{v:.2f}"


class PricesDialog:
    """Modal window to edit the Regular / VIP prices and the sale value of each bag."""

    def __init__(self, parent):
        self.result = None
        self.top = tk.Toplevel(parent)
        self.top.title("Edit prices")
        self.top.configure(bg=PANEL)
        self.top.resizable(False, False)
        self.top.transient(parent)

        body = ttk.Frame(self.top, style="Card.TFrame", padding=18)
        body.pack(fill="both", expand=True)
        for col, head in enumerate(("", "Regular", "VIP", "Sale value"), start=0):
            ttk.Label(body, text=head, style="Head.TLabel").grid(row=0, column=col, padx=6, pady=(0, 6), sticky="e" if col else "w")
        vcmd = (self.top.register(is_money_text), "%P")
        self.vars = {}          # (column, bag) -> StringVar
        self.boxes = []
        for r, key in enumerate(L.NAMES, start=1):
            ttk.Label(body, text=L.NAMES[key], style="Bold.TLabel").grid(row=r, column=0, sticky="w", padx=(0, 14), pady=4)
            for col, which in enumerate(("regular", "vip", "sale"), start=1):
                var = tk.StringVar()
                self.vars[(which, key)] = var
                box = ttk.Entry(body, textvariable=var, width=10, justify="right", validate="key", validatecommand=vcmd)
                box.grid(row=r, column=col, padx=6, pady=4)
                self.boxes.append(box)
        self.fill(L.SALE, L.CUT)

        ttk.Label(body, text="Prices apply to new entries. Entries you already saved keep the price they\n"
                             "were saved with (editing a saved entry recalculates it at today's prices).",
                  style="Muted.TLabel", justify="left").grid(row=4, column=0, columnspan=4, sticky="w", pady=(12, 0))
        self.error = ttk.Label(body, text="", style="Card.TLabel", foreground=RED, justify="left", wraplength=420)
        self.error.grid(row=5, column=0, columnspan=4, sticky="w", pady=(8, 0))

        btns = ttk.Frame(body, style="Card.TFrame")
        btns.grid(row=6, column=0, columnspan=4, sticky="ew", pady=(14, 0))
        button(btns, text="Reset to defaults", command=self.reset).pack(side="left")
        button(btns, text="Save", style="Accent.TButton", command=self.ok).pack(side="right")
        button(btns, text="Cancel", command=self.cancel).pack(side="right", padx=(0, 8))

        self.top.bind("<Return>", lambda e: self.ok())
        self.top.bind("<Escape>", lambda e: self.cancel())
        self.top.protocol("WM_DELETE_WINDOW", self.cancel)
        self.top.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.top.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.top.winfo_height()) // 3
        self.top.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        self.top.grab_set()
        if self.boxes:
            self.boxes[0].focus_set()

    def fill(self, sale, cut):
        for key in L.NAMES:
            self.vars[("sale", key)].set(show_price(sale[key]))
            for which in ("regular", "vip"):
                self.vars[(which, key)].set(show_price(cut[which][key]))

    def reset(self):
        self.fill(L.DEFAULT_SALE, L.DEFAULT_CUT)
        self.error.configure(text="")

    def ok(self):
        sale, cut = {}, {"regular": {}, "vip": {}}
        try:
            for key in L.NAMES:
                sale[key] = float(self.vars[("sale", key)].get())
                for which in ("regular", "vip"):
                    cut[which][key] = float(self.vars[(which, key)].get())
        except ValueError:
            self.error.configure(text="Fill in every price box with a number.")
            return
        err = L.validate_prices(sale, cut)
        if err:
            self.error.configure(text=err)
            return
        self.result = (sale, cut)
        self.top.destroy()

    def cancel(self):
        self.top.destroy()

    def show(self):
        self.top.wait_window()
        return self.result


class App:
    def __init__(self, root, path, bubble=True):
        self.root = root
        self.path = path
        self.want_bubble = bubble
        self.bubble = False
        self.bubble_imgs = {}
        self.data = {}
        self.names = []
        self.cur = None
        self.saved = False
        self.edit_idx = None   # index of the history entry being edited, or None
        self.checking = False  # an update check is running
        self.update_result = None
        self.busy = False
        self._status_job = None
        self.notes_for = None      # the client whose text is in the notes box
        self.notes_dirty = False   # typed but not yet saved
        self._notes_job = None

        root.title(f"The Benefactor  v{APP_VERSION}")
        root.configure(bg=BG)
        root.minsize(860, 600)
        root.report_callback_exception = self.on_error
        self.setup_style()
        self.setup_logo()
        self.build()
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.center(START_W, START_H)
        self.refresh()
        self.settings_file = os.path.join(os.path.dirname(os.path.abspath(path)), "settings.json")
        self.settings = load_settings(self.settings_file)
        self.start = None
        if self.settings["start_screen"]:
            self.open_start()

    # ----- setup -----

    def setup_logo(self):
        """Window/taskbar icon and header logo. Never blocks the app if it fails."""
        self.logo_icon = self.logo_header = None  # keep references so Tk doesn't discard them
        try:
            self.logo_icon = tk.PhotoImage(data=LOGO_ICON_B64)
            self.logo_header = tk.PhotoImage(data=LOGO_HEADER_B64)
            self.root.iconphoto(True, self.logo_icon)
        except tk.TclError:
            self.logo_icon = self.logo_header = None

    def center(self, w, h):
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        w, h = min(w, sw - 40), min(h, sh - 90)   # never open bigger than the screen
        self.root.geometry(f"{w}x{h}+{max((sw - w) // 2, 0)}+{max((sh - h) // 3, 0)}")

    def setup_style(self):
        st = ttk.Style(self.root)
        try:
            st.theme_use("clam")
        except tk.TclError:
            pass
        bold = (FONT, 10, "bold")
        st.configure(".", background=BG, foreground=TEXT, fieldbackground=PANEL2,
                     bordercolor=LINE, lightcolor=PANEL2, darkcolor=PANEL2,
                     troughcolor=PANEL, font=(FONT, 10))
        st.configure("TFrame", background=BG)
        st.configure("Card.TFrame", background=PANEL, borderwidth=0, relief="flat")
        st.configure("TLabel", background=BG, foreground=TEXT)
        st.configure("Card.TLabel", background=PANEL, foreground=TEXT)
        st.configure("Card.TCheckbutton", background=PANEL, foreground=TEXT, focuscolor=PANEL)
        st.map("Card.TCheckbutton", background=[("active", PANEL)], foreground=[("active", GOLD2)])
        st.configure("Bold.TLabel", background=PANEL, foreground=TEXT, font=bold)
        st.configure("Muted.TLabel", background=PANEL, foreground=MUTED, font=(FONT, 9))
        st.configure("Head.TLabel", background=PANEL, foreground=MUTED, font=(FONT, 9, "bold"))
        st.configure("Gold.TLabel", background=PANEL, foreground=GOLD2, font=(FONT, 10, "bold"))
        st.configure("CardTitle.TLabel", background=PANEL, foreground=GOLD2, font=("Georgia", 16, "bold"))
        st.configure("Title.TLabel", background=BG, foreground=GOLD2, font=("Georgia", 16, "bold"))
        st.configure("Status.TLabel", background=BG, foreground=MUTED, padding=(8, 2))

        st.configure("TButton", background=PANEL2, foreground=TEXT, bordercolor=LINE,
                     padding=(12, 6), focuscolor=PANEL2)
        st.map("TButton",
               background=[("disabled", PANEL), ("active", LINE)],
               foreground=[("disabled", MUTED)],
               bordercolor=[("active", GOLD)])
        st.configure("Accent.TButton", background=GOLD, foreground="#1a1509", font=bold,
                     bordercolor=GOLD, focuscolor=GOLD)
        st.map("Accent.TButton",
               background=[("disabled", "#6b5a2c"), ("active", GOLD2)],
               foreground=[("disabled", "#2a2210")],
               bordercolor=[("disabled", "#6b5a2c"), ("active", GOLD2)])
        st.configure("Danger.TButton", padding=(8, 3), font=(FONT, 9))
        st.map("Danger.TButton",
               foreground=[("disabled", MUTED), ("active", RED)],
               bordercolor=[("active", RED)],
               background=[("disabled", PANEL), ("active", LINE)])
        st.configure("Step.TButton", padding=(0, 2), width=2)

        st.configure("TEntry", fieldbackground=PANEL2, foreground=TEXT, insertcolor=TEXT, bordercolor=LINE)
        st.configure("TSpinbox", fieldbackground=PANEL2, foreground=TEXT, background=PANEL2,
                     arrowcolor=TEXT, insertcolor=TEXT, bordercolor=LINE)
        st.configure("TCombobox", fieldbackground=PANEL2, foreground=TEXT, background=PANEL2,
                     arrowcolor=TEXT, bordercolor=LINE)
        st.map("TCombobox",
               fieldbackground=[("readonly", PANEL2), ("disabled", PANEL)],
               foreground=[("readonly", TEXT), ("disabled", MUTED)],
               selectbackground=[("readonly", PANEL2)],
               selectforeground=[("readonly", TEXT)])
        self.root.option_add("*TCombobox*Listbox.background", PANEL2)
        self.root.option_add("*TCombobox*Listbox.foreground", TEXT)
        self.root.option_add("*TCombobox*Listbox.selectBackground", GOLD)
        self.root.option_add("*TCombobox*Listbox.selectForeground", "#1a1509")

        st.configure("Card.TCheckbutton", background=PANEL, foreground=TEXT, focuscolor=PANEL)
        st.map("Card.TCheckbutton", background=[("active", PANEL)],
               indicatorcolor=[("selected", GOLD), ("!selected", PANEL2)])
        st.configure("Card.TRadiobutton", background=PANEL, foreground=TEXT, focuscolor=PANEL)
        st.map("Card.TRadiobutton", background=[("active", PANEL)],
               indicatorcolor=[("selected", GOLD), ("!selected", PANEL2)])

        st.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT,
                     rowheight=26, borderwidth=0, bordercolor=PANEL)
        st.map("Treeview", background=[("selected", PANEL2)], foreground=[("selected", GOLD2)])
        st.configure("Treeview.Heading", background=PANEL2, foreground=MUTED, relief="flat",
                     font=(FONT, 9, "bold"), padding=(6, 4))
        st.map("Treeview.Heading", background=[("active", LINE)])
        st.configure("TNotebook", background=PANEL, borderwidth=0, tabmargins=(0, 0, 0, 0))
        st.configure("Tiles.TNotebook", background=PANEL, borderwidth=0, tabmargins=(0, 0, 0, 0))
        st.layout("Tiles.TNotebook.Tab", [])     # the tiles above replace the tab strip
        st.configure("TNotebook.Tab", background=PANEL, foreground=MUTED, padding=(16, 7), borderwidth=0)
        st.map("TNotebook.Tab",
               foreground=[("selected", GOLD2)],
               background=[("selected", PANEL2), ("active", PANEL2)])
        st.configure("Vertical.TScrollbar", background=PANEL2, troughcolor=PANEL,
                     bordercolor=PANEL, arrowcolor=MUTED, lightcolor=PANEL2, darkcolor=PANEL2)
        st.map("Vertical.TScrollbar", background=[("active", LINE), ("pressed", LINE)])
        self.setup_bubble(st)

    def setup_bubble(self, st):
        """Rounded, glossy 'bubble' look from the embedded images. If anything about it fails,
        the plain flat look is put back and the app carries on as before."""
        # flat fallbacks: this is what the new card styles look like when the bubble look is off
        st.configure("Bubble.TFrame", background=PANEL, bordercolor=LINE, relief="solid", borderwidth=1)
        st.configure("Inset.TFrame", background=PANEL, bordercolor=LINE, relief="solid", borderwidth=1)
        if not self.want_bubble:
            return
        try:
            keep = {n: st.layout(n) for n in ("TFrame", "TButton", "TEntry", "TCombobox", "TNotebook.Tab")}
        except tk.TclError:
            return                                   # this theme has no such layouts: stay flat
        custom = {"Bubble.TFrame": "TFrame", "Inset.TFrame": "TFrame"}
        try:
            for name, (_b, _w, _h, data) in BUBBLE_ASSETS.items():
                self.bubble_imgs[name] = tk.PhotoImage(name="bub_" + name, data=data)

            def elem(element, pic, states=(), **opts):
                st.element_create(element, "image", "bub_" + pic, *[(*s[:-1], "bub_" + s[-1]) for s in states],
                                  sticky="nswe", **opts)

            elem("Bubble.card", "card", border=22, width=44, height=44, padding=0)
            elem("Bubble.inset", "inset", border=12, width=24, height=24, padding=0)
            elem("Bubble.field", "fld_n", [("disabled", "fld_d"), ("focus", "fld_f")],
                 border=12, width=30, height=32, padding=(8, 4))
            elem("Bubble.tab", "tab_n", [("selected", "tab_s"), ("active", "!selected", "tab_h")],
                 border=14, width=32, height=32, padding=(6, 2))

            def swap(layout, old, new):
                out = []
                for name, opts in layout:
                    opts = dict(opts)
                    if "children" in opts:
                        opts["children"] = swap(opts["children"], old, new)
                    if name == old:
                        # "-border" would make Tk paint our (opaque) image AFTER its children, hiding the text
                        opts.pop("border", None)
                    out.append((new if name == old else name, opts))
                return out

            st.layout("Bubble.TFrame", [("Bubble.card", {"sticky": "nswe"})])
            st.layout("Inset.TFrame", [("Bubble.inset", {"sticky": "nswe"})])
            st.layout("TEntry", swap(keep["TEntry"], "Entry.field", "Bubble.field"))
            st.layout("TCombobox", swap(keep["TCombobox"], "Combobox.field", "Bubble.field"))
            st.layout("TNotebook.Tab", swap(keep["TNotebook.Tab"], "Notebook.tab", "Bubble.tab"))

            # the text areas and the dropdown arrow must match the rounded field's body colour
            field = FIELD
            st.configure("TEntry", fieldbackground=field, padding=(4, 2))
            st.configure("TCombobox", fieldbackground=field, background=field, bordercolor=field,
                         lightcolor=field, darkcolor=field, arrowcolor=GOLD, padding=(4, 2))
            st.map("TCombobox", fieldbackground=[("readonly", field), ("disabled", "#112016")],
                   background=[("active", field), ("pressed", field)],
                   foreground=[("readonly", TEXT), ("disabled", MUTED)])
            st.configure("TNotebook", bordercolor=PANEL, lightcolor=PANEL, darkcolor=PANEL)
            self.check_bubble()
            self.bubble = True
            set_bubble(True)
        except Exception:
            set_bubble(False)
            for n, lay in keep.items():
                st.layout(n, lay)
            for n, src in custom.items():
                st.layout(n, keep[src])
            self.bubble_imgs = {}
            self.bubble = False

    def check_bubble(self):
        """Build one of each restyled widget now, so a broken layout fails here (and we fall back)
        instead of later while the window is being built."""
        top = tk.Toplevel(self.root)
        try:
            top.withdraw()
            f = ttk.Frame(top, style="Bubble.TFrame", padding=8)
            f.pack()
            ttk.Frame(f, style="Inset.TFrame", padding=4).pack()
            for kind in ("btn", "acc", "sml", "stp"):
                BubbleButton(f, "x", None, kind).pack()
            ttk.Entry(f).pack()
            ttk.Combobox(f, values=["a"], state="readonly").pack()
            nb = ttk.Notebook(f)
            nb.add(ttk.Frame(nb), text="t")
            nb.pack()
            top.update_idletasks()
            for w in f.winfo_children():
                w.winfo_reqwidth()
        finally:
            top.destroy()

    def card(self, parent, title):
        frame = ttk.Frame(parent, style="Bubble.TFrame", padding=16)
        if title:
            ttk.Label(frame, text=title.upper(), style="Head.TLabel").pack(anchor="w", pady=(0, 8))
        return frame

    def make_tree(self, parent, columns, heights):
        """columns: list of (id, heading, width, anchor)."""
        wrap = ttk.Frame(parent, style="Inset.TFrame", padding=5)
        tree = ttk.Treeview(wrap, columns=[c[0] for c in columns], show="headings",
                            height=heights, selectmode="browse")
        for cid, head, width, anchor in columns:
            tree.heading(cid, text=head, anchor=anchor)
            tree.column(cid, width=width, minwidth=50, anchor=anchor, stretch=(cid == columns[0][0]))
        bar = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=bar.set)
        tree.pack(side="left", fill="both", expand=True)
        bar.pack(side="right", fill="y")
        tree.tag_configure("total", foreground=GOLD2, font=(FONT, 10, "bold"))
        return wrap, tree

    def build(self):
        root = self.root
        root.columnconfigure(2, weight=1)
        root.rowconfigure(1, weight=1)
        self.bg_cv = tk.Canvas(root, bg=BG, highlightthickness=0, bd=0)    # engraved banknote border
        self.bg_cv.place(x=0, y=0, relwidth=1, relheight=1)
        self._bg_job = None
        self._bg_size = None
        root.bind("<Configure>", self.on_root_resize, add="+")

        head = ttk.Frame(root, style="Bubble.TFrame", padding=(16, 10))
        head.grid(row=0, column=0, columnspan=3, sticky="ew", padx=MARGIN, pady=(MARGIN, 8))
        if self.logo_header:
            ttk.Label(head, image=self.logo_header, style="Card.TLabel").pack(side="left", padx=(0, 12))
        ttk.Label(head, text="THE BENEFACTOR", style="CardTitle.TLabel").pack(side="left")
        self.update_btn = button(head, text="Check for updates", command=self.on_check_update)
        self.update_btn.pack(side="right")
        button(head, text="Edit prices", command=self.on_prices).pack(side="right", padx=(0, 8))
        ttk.Label(head, text=f"v{APP_VERSION}", style="Muted.TLabel").pack(side="right", padx=(0, 12))

        side = ttk.Frame(root, style="Bubble.TFrame", padding=8)
        side.grid(row=1, column=0, sticky="ns", padx=(MARGIN, 0), pady=(0, 6))
        self.nav = {}
        for key, title, glyph in (("ledger", "Ledger", "book"), ("score", "Scoreboard", "trophy")):
            tile = NavTile(side, title, "", glyph, lambda k=key: self.show_page(k))
            tile.pack(pady=(0, 10))
            self.nav[key] = tile
        # both pages sit in the same grid cell and switching just raises one: no re-layout, no redraws
        self.ledger_page = ttk.Frame(root)
        self.ledger_page.grid(row=1, column=1, columnspan=2, sticky="nsew", pady=(0, 6))
        self.ledger_page.rowconfigure(0, weight=1)
        self.ledger_page.columnconfigure(1, weight=1)
        left = ttk.Frame(self.ledger_page)
        left.grid(row=0, column=0, sticky="ns", padx=(14, 10))
        right = ttk.Frame(self.ledger_page)
        right.grid(row=0, column=1, sticky="nsew", padx=(10, MARGIN))
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        # --- client card ---
        cc = self.card(left, "Client")
        cc.pack(fill="x", pady=(0, 12))
        row = ttk.Frame(cc, style="Card.TFrame")
        row.pack(fill="x")
        self.combo = ttk.Combobox(row, state="readonly", width=24)
        self.combo.pack(side="left", fill="x", expand=True)
        self.combo.bind("<<ComboboxSelected>>", self.on_pick_client)
        button(row, text="+ New", style="Accent.TButton", command=self.on_new).pack(side="left", padx=(8, 0))
        row2 = ttk.Frame(cc, style="Card.TFrame")
        row2.pack(fill="x", pady=(10, 0))
        self.badge = ttk.Label(row2, text="", style="Bold.TLabel")
        self.badge.pack(side="left")
        self.del_btn = button(row2, text="Delete client", style="Danger.TButton", command=self.on_delete)
        self.del_btn.pack(side="right")
        self.edit_client_btn = button(row2, text="Edit client", style="Danger.TButton", command=self.on_edit_client)
        self.edit_client_btn.pack(side="right", padx=(0, 8))

        # --- bags card ---
        bc = self.card(left, "Bags")
        bc.pack(fill="x")
        grid = ttk.Frame(bc, style="Card.TFrame")
        grid.pack(fill="x")
        grid.columnconfigure(0, weight=1)
        self.vars, self.spins, self.price_lbls, self.step_btns = {}, {}, {}, []
        vcmd = (self.root.register(is_count), "%P")
        for i, key in enumerate(L.NAMES):
            ttk.Label(grid, text=L.NAMES[key], style="Bold.TLabel").grid(
                row=2 * i, column=0, sticky="w", pady=(10 if i else 0, 0))
            pl = ttk.Label(grid, text="", style="Muted.TLabel")
            pl.grid(row=2 * i + 1, column=0, sticky="w")
            self.price_lbls[key] = pl
            var = tk.StringVar(value="0")
            var.trace_add("write", self.on_change)
            self.vars[key] = var
            box = ttk.Frame(grid, style="Card.TFrame")
            box.grid(row=2 * i, column=1, rowspan=2, sticky="e", padx=(14, 0), pady=(10 if i else 0, 0))
            minus = button(box, text="−", style="Step.TButton",
                               command=lambda k=key: self.bump(k, -1))
            minus.pack(side="left")
            sp = ttk.Entry(box, textvariable=var, width=6, justify="center",
                           validate="key", validatecommand=vcmd)
            sp.pack(side="left", padx=4, ipady=3)
            plus = button(box, text="+", style="Step.TButton",
                              command=lambda k=key: self.bump(k, 1))
            plus.pack(side="left")
            self.spins[key] = sp
            self.step_btns += [minus, plus]

        self.free = tk.BooleanVar(value=False)
        self.free_chk = checkbox(bc, "Free laundry  (100% return, no cut taken)", self.free, self.on_change)
        self.free_chk.pack(anchor="w", pady=(12, 0))
        self.edit_note = ttk.Label(bc, text="", style="Gold.TLabel")   # shown only while editing
        btns = ttk.Frame(bc, style="Card.TFrame")
        btns.pack(fill="x", pady=(16, 0))
        self.btn_row = btns
        self.save_btn = button(btns, text="Save entry", style="Accent.TButton", command=self.on_save)
        self.save_btn.pack(side="left")
        self.repeat_btn = button(btns, text="Repeat last", command=self.on_repeat)
        self.repeat_btn.pack(side="left", padx=8)
        self.clear_btn = button(btns, text="Clear", command=self.on_clear)
        self.clear_btn.pack(side="left")

        # --- this entry ---
        ec = self.card(right, "This entry")
        ec.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self.calc_cols = [("item", "Item", 190, "w"), ("qty", "Qty", 50, "e"),
                          ("cut", "Regular", 110, "e"), ("sale", "Sale price", 110, "e"),
                          ("take", "My take", 110, "e")]
        wrap, self.calc_tree = self.make_tree(ec, self.calc_cols, 5)
        wrap.pack(fill="x")

        # --- history / all clients ---
        hc = self.card(right, None)
        hc.grid(row=1, column=0, sticky="nsew")
        self.tile_bar = ttk.Frame(hc, style="Card.TFrame")
        self.tile_bar.pack(fill="x", pady=(0, 6))
        self.tabs = ttk.Notebook(hc, style="Tiles.TNotebook")
        self.tabs.pack(fill="both", expand=True)
        hist_page = ttk.Frame(self.tabs, style="Card.TFrame", padding=(0, 8, 0, 0))
        all_page = ttk.Frame(self.tabs, style="Card.TFrame", padding=(0, 8, 0, 0))
        self.tabs.add(hist_page, text="History")
        self.tabs.add(all_page, text="All clients")

        prog_page = ttk.Frame(self.tabs, style="Card.TFrame", padding=(0, 8, 0, 0))
        self.tabs.add(prog_page, text="Progress")
        self.tiles = []
        for i, (title, sub, glyph) in enumerate((("History", "", "history"), ("All clients", "", "clients"),
                                                 ("Progress", "lifetime graph", "progress"),
                                                 ("Notes", "", "notes"))):
            tile = Tile(self.tile_bar, title, sub, glyph, lambda i=i: self.tabs.select(i))
            tile.pack(side="left", padx=(0, 10))
            self.tiles.append(tile)
        self.tabs.bind("<<NotebookTabChanged>>", self.on_tab_changed, add="+")

        notes_page = ttk.Frame(self.tabs, style="Card.TFrame", padding=(0, 8, 0, 0))
        self.tabs.add(notes_page, text="Notes")
        self.notes_title = ttk.Label(notes_page, text="", style="Gold.TLabel")
        self.notes_title.pack(anchor="w", padx=4, pady=(0, 6))
        nbar = ttk.Frame(notes_page, style="Card.TFrame")
        nbar.pack(side="bottom", fill="x", pady=(8, 0))
        self.notes_btn = button(nbar, text="Save notes", style="Accent.TButton", command=self.flush_notes)
        self.notes_btn.pack(side="left")
        self.notes_state = ttk.Label(nbar, text="", style="Muted.TLabel")
        self.notes_state.pack(side="left", padx=12)
        box = ttk.Frame(notes_page, style="Inset.TFrame", padding=8)
        box.pack(fill="both", expand=True)
        self.notes_text = tk.Text(box, wrap="word", height=8, bg=FIELD, fg=TEXT, insertbackground=GOLD2,
                                  selectbackground=LINE, selectforeground=TEXT, relief="flat", bd=0,
                                  highlightthickness=0, font=(FONT, 11), padx=6, pady=4, undo=True)
        nscroll = ttk.Scrollbar(box, orient="vertical", command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=nscroll.set)
        nscroll.pack(side="right", fill="y")
        self.notes_text.pack(side="left", fill="both", expand=True)
        for ev in ("<KeyRelease>", "<<Paste>>", "<<Cut>>"):
            self.notes_text.bind(ev, self.on_notes_edit, add="+")
        ctl = ttk.Frame(prog_page, style="Card.TFrame")
        ctl.pack(fill="x", padx=4, pady=(0, 6))
        ttk.Label(ctl, text="Show running total of", style="Card.TLabel").pack(side="left")
        self.metric = tk.StringVar(value="My take")
        mc = ttk.Combobox(ctl, textvariable=self.metric, values=list(METRICS), state="readonly", width=12)
        mc.pack(side="left", padx=(8, 16))
        mc.bind("<<ComboboxSelected>>", lambda e: self.draw_chart())
        self.combined = tk.BooleanVar(value=False)
        checkbox(ctl, "Add combined line", self.combined, self.draw_chart).pack(side="left")
        self.chart = tk.Canvas(prog_page, bg=PANEL, highlightthickness=0, height=280)
        self.chart.pack(fill="both", expand=True)
        self.chart_hits = []
        self._chart_job = None
        self._chart_size = None
        self.chart.bind("<Configure>", self.on_chart_resize)
        self.chart.bind("<Motion>", self.on_chart_move)
        self.chart.bind("<Leave>", lambda e: self.chart.delete("tip"))

        self.hist_cols = [("date", "Date", 130, "w"), ("big", "Big", 44, "e"), ("avg", "Avg", 44, "e"),
                          ("small", "Small", 52, "e"), ("cut", "Regular", 100, "e"),
                          ("sale", "Sale price", 100, "e"), ("take", "My take", 100, "e"),
                          ("free", "Free", 70, "e")]
        wrap, self.hist_tree = self.make_tree(hist_page, self.hist_cols, 8)
        bar = ttk.Frame(hist_page, style="Card.TFrame")
        bar.pack(side="bottom", fill="x", pady=(8, 0))
        self.edit_btn = button(bar, text="Edit selected entry", command=self.on_hist_edit)
        self.edit_btn.pack(side="left")
        self.edit_btn.state(["disabled"])
        self.del_entry_btn = button(bar, text="Delete selected entry", style="Danger.TButton",
                                        command=self.on_hist_delete)
        self.del_entry_btn.pack(side="left", padx=(8, 0))
        self.del_entry_btn.state(["disabled"])
        ttk.Label(bar, text="double-click an entry to edit it", style="Muted.TLabel").pack(side="left", padx=10)
        self.hist_tree.bind("<<TreeviewSelect>>", self.on_hist_select)
        self.hist_tree.bind("<Double-1>", self.on_hist_edit)
        self.hist_tree.bind("<Delete>", self.on_hist_delete)
        wrap.pack(fill="both", expand=True)

        self.all_cols = [("client", "Client", 140, "w"), ("type", "Type", 70, "w"),
                         ("entries", "Entries", 60, "e"), ("cut", "Cut total", 100, "e"),
                         ("sale", "Sale total", 100, "e"), ("take", "My take", 100, "e"),
                         ("free", "Free laundry", 90, "e")]
        wrap, self.all_tree = self.make_tree(all_page, self.all_cols, 8)
        wrap.pack(fill="both", expand=True)
        self.all_tree.bind("<Double-1>", self.on_all_open)
        self.all_tree.bind("<Return>", self.on_all_open)

        # --- status bar ---
        self.status = tk.StringVar(value="")
        ttk.Label(root, textvariable=self.status, style="Status.TLabel").grid(
            row=2, column=0, columnspan=2, sticky="w", padx=MARGIN, pady=(0, MARGIN))
        self.where = tk.StringVar(value="")
        ttk.Label(root, textvariable=self.where, style="Status.TLabel").grid(
            row=2, column=1, columnspan=2, sticky="e", padx=MARGIN, pady=(0, MARGIN))
        self.build_scoreboard_page()
        self.show_page("ledger")

    def build_scoreboard_page(self):
        self.page = "ledger"
        self.score_page = ttk.Frame(self.root)
        self.score_page.grid(row=1, column=1, columnspan=2, sticky="nsew", padx=(14, MARGIN), pady=(0, 6))
        self.score_dirty = True
        self.score_page.rowconfigure(0, weight=1)
        self.score_page.columnconfigure(0, weight=1)
        sc = self.card(self.score_page, "Scoreboard")
        sc.grid(row=0, column=0, sticky="nsew")
        ctl = ttk.Frame(sc, style="Card.TFrame")
        ctl.pack(fill="x", pady=(0, 6))
        ttk.Label(ctl, text="Rank clients by", style="Card.TLabel").pack(side="left")
        self.score_metric = tk.StringVar(value=SCORE_METRICS[0])
        mc = ttk.Combobox(ctl, textvariable=self.score_metric, values=SCORE_METRICS, state="readonly", width=16)
        mc.pack(side="left", padx=(8, 16))
        mc.bind("<<ComboboxSelected>>", lambda e: self.render_score())
        ttk.Label(ctl, text="A deposit is an entry; its amount is the sale value.  Double-click a client to open them.",
                  style="Muted.TLabel").pack(side="left")
        self.podium = tk.Canvas(sc, bg=PANEL, highlightthickness=0, height=210)
        self.podium.pack(fill="x", pady=(0, 8))
        self._podium_job = None
        self._podium_size = None
        self.podium.bind("<Configure>", self.on_podium_resize)
        cols = [("rank", "#", 44, "center"), ("client", "Client", 150, "w"), ("tier", "Tier", 84, "w"),
                ("n", "Deposits", 70, "e"), ("total", "Total deposited", 118, "e"), ("avg", "Avg deposit", 100, "e"),
                ("big", "Biggest", 96, "e"), ("freq", "How often", 118, "e"), ("last", "Last deposit", 100, "e"),
                ("score", "Score", 60, "e")]
        wrap, self.score_tree = self.make_tree(sc, cols, 7)
        wrap.pack(fill="both", expand=True)
        for rank, col in MEDALS.items():
            self.score_tree.tag_configure(f"r{rank}", foreground=col)
        self.score_tree.bind("<Double-1>", self.on_score_open)
        self.score_tree.bind("<Return>", self.on_score_open)
        self.score_sum = ttk.Label(sc, text="", style="Muted.TLabel")
        self.score_sum.pack(anchor="w", pady=(8, 0))
        self.score_rows = []

    def debug_time(self, what, t0):
        """With BENEFACTOR_DEBUG=1 set, log how long something took (until it was painted) to timing.log."""
        if not os.environ.get("BENEFACTOR_DEBUG"):
            return
        try:
            self.root.update_idletasks()
            with open(os.path.join(os.path.dirname(os.path.abspath(self.path)), "timing.log"), "a") as fh:
                fh.write(f"{datetime.now():%H:%M:%S}  {what}: {(time.perf_counter() - t0) * 1000:.0f} ms\n")
        except OSError:
            pass

    def show_page(self, page):
        t0 = time.perf_counter()
        self.page = page
        if page == "score":
            if self.score_dirty:
                self.render_score()
            self.score_page.tkraise()
        else:
            self.ledger_page.tkraise()
        for key, tile in self.nav.items():
            tile.set_active(key == page)
        self.debug_time(f"show {page}", t0)

    def render_score(self):
        self.score_dirty = False
        rows = build_scoreboard(self.data, self.score_metric.get(), datetime.now())
        self.score_rows = rows
        self.clear(self.score_tree)
        for r in rows:
            self.score_tree.insert("", "end", iid=f"s{r['name']}", tags=(f"r{r['rank']}",) if r["rank"] <= 3 else (),
                                   values=(r["rank"], r["name"], r["tier"], r["n"],
                                           whole(r["total"]) if r["n"] else "\u2014",
                                           whole(r["avg"]) if r["n"] else "\u2014",
                                           whole(r["big"]) if r["n"] else "\u2014",
                                           gap_text(r["gap"]), ago_text(r["since"]), r["score"]))
        total = sum(r["total"] for r in rows)
        deposits = sum(r["n"] for r in rows)
        self.score_sum.configure(text=(f"{len(rows)} clients  \u00b7  {deposits} deposits  \u00b7  {whole(total)} deposited"
                                       f"  \u00b7  {whole(total / deposits) if deposits else '$0'} average deposit")
                                 if rows else "No clients yet.")
        self._podium_size = None
        self.draw_podium()

    def on_podium_resize(self, event):
        if (event.width, event.height) == self._podium_size:
            return
        if self._podium_job:
            self.root.after_cancel(self._podium_job)
        self._podium_job = self.root.after(80, self.draw_podium)

    def draw_podium(self):
        self._podium_job = None
        cv = self.podium
        w, h = cv.winfo_width(), cv.winfo_height()
        if w < 50 or h < 50:
            return
        self._podium_size = (w, h)
        paint_scene(cv, build_podium(self.score_rows, w, h, self.score_metric.get()))

    def on_score_open(self, _event=None):
        sel = self.score_tree.selection()
        if sel and sel[0].startswith("s") and sel[0][1:] in self.data:
            self.cur = sel[0][1:]
            self.reset_inputs()
            self.refresh()
            self.show_page("ledger")
            self.tabs.select(0)

    def write(self, data):
        """Save, then read the file back to prove it really landed on disk."""
        L.save(self.path, data)
        with open(self.path) as f:
            back = json.load(f)
        if back != json.loads(json.dumps(data)):
            raise OSError("The file was written, but reading it back gave different data.")

    def on_error(self, exc, val, tb):
        """Tk calls this when any button/menu action fails; without it, errors vanish silently."""
        traceback.print_exception(exc, val, tb)
        if isinstance(val, OSError):
            msg = ("Couldn't save your clients.\n\nFile: " + str(self.path) + "\n\n" + str(val) +
                   "\n\nThis usually means the folder is protected or read-only. "
                   "Move The Benefactor into a normal folder such as Documents and try again.")
        else:
            msg = "Something went wrong:\n\n" + "".join(traceback.format_exception(exc, val, tb))[-1000:]
        messagebox.showerror("The Benefactor", msg)

    # ----- helpers -----

    def say(self, msg):
        self.status.set(msg)
        if self._status_job:
            self.root.after_cancel(self._status_job)
        self._status_job = self.root.after(6000, lambda: self.status.set(""))

    def profile(self):
        return self.data.get(self.cur) if self.cur else None

    def counts(self):
        out = {}
        for k, v in self.vars.items():
            t = v.get().strip()
            out[k] = int(t) if t.isdigit() else 0
        return out

    def set_counts(self, counts):
        self.busy = True
        try:
            for k, v in self.vars.items():
                v.set(str(counts.get(k, 0)))
        finally:
            self.busy = False
        self.saved = False

    def label(self):
        p = self.profile()
        return L.label(p["type"]) if p else "Regular"

    # ----- rendering -----

    def on_chart_resize(self, event):
        if (event.width, event.height) == self._chart_size:
            return
        if self._chart_job:
            self.root.after_cancel(self._chart_job)
        self._chart_job = self.root.after(100, self.draw_chart)

    def draw_chart(self):
        self._chart_job = None
        cv = self.chart
        w, h = cv.winfo_width(), cv.winfo_height()
        self._chart_size = (w, h)
        cv.delete("all")
        self.chart_hits = []
        if w < 50 or h < 50:
            return  # not laid out yet; <Configure> will call us again
        series = build_series(self.data, self.metric.get(), self.combined.get())
        prims, self.chart_hits = build_scene(series, w, h, self.cur)
        sprite_dot = False
        for p in prims:
            if p["t"] == "line":
                flat = [c for pt in p["pts"] for c in pt]
                opts = {"fill": p["color"], "width": p["width"], "capstyle": "round", "joinstyle": "round"}
                if p["dash"]:
                    opts["dash"] = p["dash"]
                cv.create_line(*flat, **opts)
            elif p["t"] == "poly":
                flat = [c for pt in p["pts"] for c in pt]
                cv.create_polygon(*flat, fill=p["fill"], outline="")
            elif p["t"] == "rect":
                cv.create_rectangle(p["x0"], p["y0"], p["x1"], p["y1"], fill=p["fill"], outline="")
            elif p["t"] == "oval":
                r = p["r"]
                dot = sprite(f"dot_{p['fill'].lstrip('#')}_{'b' if r > 4 else 's'}")
                sprite_dot = dot is not None
                if sprite_dot:
                    cv.create_image(p["x"], p["y"], image=dot)
                else:
                    cv.create_oval(p["x"] - r, p["y"] - r, p["x"] + r, p["y"] + r, fill=p["fill"], outline=PANEL, width=1)
            elif p["t"] == "shine":
                r = p["r"]
                if sprite_dot:
                    continue                    # the picture already has its shine
                cv.create_oval(p["x"] - r, p["y"] - r, p["x"] + r, p["y"] + r, fill=p["fill"], outline="")
            elif p["t"] == "text":
                cv.create_text(p["x"], p["y"], text=p["text"], anchor=p["anchor"], fill=p["color"],
                               font=(FONT, p["size"]), justify="center")

    def on_chart_move(self, e):
        cv = self.chart
        cv.delete("tip")
        best, best_d = None, 14 ** 2
        for x, y, text in self.chart_hits:
            d = (x - e.x) ** 2 + (y - e.y) ** 2
            if d <= best_d:
                best, best_d = (x, y, text), d
        if not best:
            return
        x, y, text = best
        tid = cv.create_text(x + 12, y - 12, text=text, anchor="sw", fill=TEXT, font=(FONT, 9),
                             justify="left", tags="tip")
        x0, y0, x1, y1 = cv.bbox(tid)
        rid = cv.create_rectangle(x0 - 7, y0 - 5, x1 + 7, y1 + 5, fill=PANEL2, outline=GOLD, tags="tip")
        cv.tag_lower(rid, tid)
        dx = min(0, cv.winfo_width() - 6 - (x1 + 7))   # keep the tooltip inside the chart
        dy = max(0, 6 - (y0 - 5))
        if dx or dy:
            cv.move("tip", dx, dy)

    # ----- start screen -----

    def open_start(self):
        """A welcome screen laid over the app; Enter / click / Space opens the ledger."""
        root = self.root
        cv = tk.Canvas(root, bg=BG, highlightthickness=0, bd=0, takefocus=1)
        cv.place(x=0, y=0, relwidth=1, relheight=1)
        tk.Misc.tkraise(cv)                       # (Canvas.tkraise would raise canvas items, not the widget)
        self.start = cv
        self._start_job = None
        self._start_size = None
        clients, entries, take = start_stats(L.load(self.path))
        plaque = ttk.Frame(cv, style="Bubble.TFrame", padding=(52, 34))
        self.start_plaque = plaque
        if self.logo_header:
            ttk.Label(plaque, image=self.logo_header, style="Card.TLabel").pack(pady=(0, 10))
        ttk.Label(plaque, text="THE BENEFACTOR", style="Card.TLabel", foreground=GOLD2,
                  font=("Georgia", 30, "bold")).pack()
        ttk.Label(plaque, text="Every dollar accounted for", style="Muted.TLabel",
                  font=("Georgia", 12, "italic")).pack(pady=(2, 20))
        stats = ttk.Frame(plaque, style="Card.TFrame")
        stats.pack(pady=(0, 22))
        for i, (big, small) in enumerate(((str(clients), "client" if clients == 1 else "clients"),
                                          (str(entries), "entry" if entries == 1 else "entries"),
                                          (whole(take), "my take, all time"))):
            col = ttk.Frame(stats, style="Card.TFrame")
            col.grid(row=0, column=i, padx=22)
            ttk.Label(col, text=big, style="Card.TLabel", foreground=GOLD,
                      font=("Georgia", 20, "bold")).pack()
            ttk.Label(col, text=small, style="Muted.TLabel").pack()
        if not clients:
            ttk.Label(plaque, text="Create your first client to get started.", style="Muted.TLabel").pack(pady=(0, 14))
        enter = button(plaque, text="      Enter the ledger      ", style="Accent.TButton", command=self.close_start)
        enter.pack()
        self.show_start = tk.BooleanVar(value=True)
        checkbox(plaque, "Show this screen when the app opens", self.show_start, self.on_start_pref).pack(pady=(18, 0))
        ttk.Label(plaque, text=f"v{APP_VERSION}", style="Muted.TLabel").pack(pady=(10, 0))
        cv.bind("<Configure>", self.on_start_resize)
        for ev in ("<Return>", "<space>", "<Escape>"):
            cv.bind(ev, lambda e: self.close_start())
        cv.bind("<Button-1>", lambda e: self.close_start() if e.widget is cv else None)
        cv.focus_set()

    def on_start_resize(self, event):
        if (event.width, event.height) == self._start_size:
            return
        if self._start_job:
            self.root.after_cancel(self._start_job)
        self._start_job = self.root.after(60, self.draw_start)

    def draw_start(self):
        self._start_job = None
        cv = self.start
        if cv is None:
            return
        w, h = cv.winfo_width(), cv.winfo_height()
        if w < 50 or h < 50:
            return
        self._start_size = (w, h)
        paint_scene(cv, build_banknote(w, h))          # clears the canvas, so the plaque is placed again
        cv.create_window(w / 2, h / 2, window=self.start_plaque, anchor="center")

    def on_start_pref(self):
        self.settings["start_screen"] = bool(self.show_start.get())
        save_settings(self.settings_file, self.settings)

    def close_start(self):
        t0 = time.perf_counter()
        if self.start is not None:
            self.start.destroy()
            self.start = None
            self.root.focus_set()
            self.debug_time("close start screen", t0)

    # ----- notes -----

    def on_notes_edit(self, _event=None):
        if self.notes_for is None:
            return
        self.notes_dirty = True
        self.notes_state.configure(text="Unsaved changes...")
        if self._notes_job:
            self.root.after_cancel(self._notes_job)
        self._notes_job = self.root.after(1200, self.flush_notes)      # saves itself after you stop typing

    def notes_value(self):
        return self.notes_text.get("1.0", "end-1c")[:20000]

    def flush_notes(self):
        """Save the notes box to the client it belongs to (no-op when nothing changed)."""
        if self._notes_job:
            self.root.after_cancel(self._notes_job)
            self._notes_job = None
        if not self.notes_dirty or not self.notes_for:
            return
        text = self.notes_value()
        data = L.load(self.path)
        name = L.find(data, self.notes_for)
        self.notes_dirty = False
        if name:
            data[name]["notes"] = text
            self.write(data)
            self.notes_state.configure(text="Saved.")

    def show_notes(self):
        """Put the current client's notes in the box (unless it already holds them)."""
        p = self.profile()
        if (self.cur if p else None) == self.notes_for:
            return
        self.notes_for = self.cur if p else None
        self.notes_dirty = False
        self.notes_text.configure(state="normal")
        self.notes_text.delete("1.0", "end")
        self.notes_text.edit_reset()
        if p:
            self.notes_text.insert("1.0", p.get("notes", ""))
            self.notes_title.configure(text=f"Notes for {self.cur}")
            self.notes_state.configure(text="Saves automatically as you type.")
        else:
            self.notes_title.configure(text="Pick or create a client to keep notes.")
            self.notes_state.configure(text="")
            self.notes_text.configure(state="disabled")
        self.notes_btn.state(["!disabled" if p else "disabled"])

    def on_close(self):
        try:
            self.flush_notes()
        finally:
            self.root.destroy()

    def on_root_resize(self, event):
        if event.widget is not self.root or (event.width, event.height) == self._bg_size:
            return                                   # moving the window is not a resize: do nothing
        if self._bg_job:
            self.root.after_cancel(self._bg_job)
        self._bg_job = self.root.after(120, self.draw_bg)

    def draw_bg(self):
        self._bg_job = None
        size = (self.root.winfo_width(), self.root.winfo_height())
        if size != self._bg_size and size[0] > 50 and size[1] > 50:
            self._bg_size = size
            paint_scene(self.bg_cv, build_banknote(*size))

    def on_tab_changed(self, _event=None):
        try:
            cur = self.tabs.index(self.tabs.select())
        except tk.TclError:
            cur = 0
        for i, tile in enumerate(self.tiles):
            tile.set_active(i == cur)

    def update_tiles(self):
        p = self.profile()
        n = len(p["history"]) if p else 0
        self.tiles[0].set_sub(f"{n} entr{'y' if n == 1 else 'ies'}" if p else "pick a client")
        k = len(self.names)
        self.tiles[1].set_sub(f"{k} client{'' if k == 1 else 's'}")
        self.tiles[3].set_sub(("has notes" if (p.get("notes") or "").strip() or (self.notes_dirty and self.notes_value().strip()) else "empty") if p else "pick a client")
        self.on_tab_changed()

    def refresh(self):
        if self.notes_dirty and self.notes_for != self.cur:
            self.flush_notes()                      # you switched client with unsaved notes
        self.data = L.load(self.path)
        self.names = sorted(self.data, key=str.lower)
        n = len(self.names)
        self.where.set(f"{n} client{'' if n == 1 else 's'} loaded  \u00b7  saved in: {self.path}")
        if self.cur not in self.data:
            self.cur = self.names[0] if self.names else None
        self.combo.configure(values=[f"{n}  ({L.label(self.data[n]['type'])})" for n in self.names])
        if self.cur:
            self.combo.current(self.names.index(self.cur))
        else:
            self.combo.set("No clients yet - click + New")
        p = self.profile()
        self.badge.configure(text=L.label(p["type"]) if p else "",
                             foreground=TYPE_COLOR.get(p["type"], TEXT) if p else TEXT)
        state = "!disabled" if p else "disabled"
        self.del_btn.state([state])
        self.edit_client_btn.state([state])
        for sp in self.spins.values():
            sp.state([state])
        for b in self.step_btns:
            b.state([state])
        for key, lbl in self.price_lbls.items():
            sale = L.money(L.SALE[key])
            if p:
                lbl.configure(text=f"{L.label(p['type'])} {L.money(L.CUT[p['type']][key])}  ·  sale {sale}")
            else:
                lbl.configure(text=f"sale {sale}")
        self.update_edit_ui()
        self.show_notes()
        self.update_tiles()
        for tree, cols in ((self.calc_tree, self.calc_cols), (self.hist_tree, self.hist_cols)):
            tree.heading("cut", text=self.label())
        self.render_all()
        self.draw_chart()

    def render_all(self):
        self.render_calc()
        self.render_history()
        self.render_clients()
        self.score_dirty = True
        if getattr(self, "page", None) == "score":
            self.render_score()

    @staticmethod
    def clear(tree):
        tree.delete(*tree.get_children())

    def render_calc(self):
        self.clear(self.calc_tree)
        p = self.profile()
        lines = L.build_lines(p["type"], self.counts()) if p else []
        free = self.free.get()
        t_qty = t_cut = t_sale = 0
        for name, qty, cut, sale in lines:
            if free:
                cut = sale                      # free laundry: the client gets the whole sale value
            t_qty += qty
            t_cut += cut
            t_sale += sale
            self.calc_tree.insert("", "end", values=(name, qty, L.money(cut), L.money(sale), L.money(sale - cut)))
        if lines:
            self.calc_tree.insert("", "end", tags=("total",), values=(
                "Total", t_qty, L.money(t_cut), L.money(t_sale), L.money(t_sale - t_cut)))
        self.save_btn.state(["!disabled" if (p and lines and not self.saved) else "disabled"])

    def render_history(self):
        self.clear(self.hist_tree)
        self.edit_btn.state(["disabled"])
        self.del_entry_btn.state(["disabled"])
        p = self.profile()
        if not p:
            return
        for idx in range(len(p["history"]) - 1, -1, -1):
            h = p["history"][idx]
            c = h["counts"]
            self.hist_tree.insert("", "end", iid=f"h{idx}", values=(
                h["date"], c.get("big", 0), c.get("avg", 0), c.get("small", 0),
                L.money(h["cut"]), L.money(h["sale"]), L.money(h["sale"] - h["cut"]),
                "FREE" if h.get("free") else ""))
        if p["history"]:
            cut, sale = L.lifetime(p)
            n, k = len(p["history"]), L.free_count(p)
            extra = f", {k} free" if k else ""
            self.hist_tree.insert("", "end", tags=("total",), values=(
                f"Lifetime ({n} {'entry' if n == 1 else 'entries'}{extra})", "", "", "",
                L.money(cut), L.money(sale), L.money(sale - cut), f"{k} free" if k else ""))

    def render_clients(self):
        self.clear(self.all_tree)
        g_entries = g_cut = g_sale = g_free = 0
        for i, n in enumerate(self.names):
            p = self.data[n]
            cut, sale = L.lifetime(p)
            g_entries += len(p["history"])
            g_cut += cut
            g_sale += sale
            g_free += L.free_count(p)
            self.all_tree.insert("", "end", iid=str(i), values=(
                n, L.label(p["type"]), len(p["history"]), L.money(cut), L.money(sale), L.money(sale - cut),
                L.free_count(p)))
        if self.names:
            self.all_tree.insert("", "end", iid="total", tags=("total",), values=(
                "All clients", "", g_entries, L.money(g_cut), L.money(g_sale), L.money(g_sale - g_cut), g_free))

    # ----- actions -----

    def on_change(self, *_):
        if self.busy:
            return
        self.saved = False
        self.render_calc()

    def bump(self, key, delta):
        cur = self.counts()[key]
        self.vars[key].set(str(max(0, min(9999, cur + delta))))

    def on_pick_client(self, _event=None):
        i = self.combo.current()
        if 0 <= i < len(self.names):
            self.cur = self.names[i]
            self.reset_inputs()
            self.refresh()

    def ask_new_client(self):
        return NewClientDialog(self.root).show()

    def on_new(self):
        res = self.ask_new_client()
        if not res:
            return
        err = self.add_client(*res)
        if err:
            messagebox.showerror("The Benefactor", err)
        else:
            self.say(f"Created {res[0]} ({L.label(res[1])}).")

    def add_client(self, name, ctype):
        """Create a client. Returns an error message, or None on success."""
        data = L.load(self.path)
        if L.find(data, name):
            return f"'{name}' already exists."
        L.create_profile(data, name, ctype)
        self.write(data)
        self.cur = name
        self.reset_inputs()
        self.refresh()
        return None

    def ask_edit_client(self, name, ctype):
        return NewClientDialog(self.root, title="Edit client", name=name, ctype=ctype,
                               ok_text="Save", reprice=True).show()

    def on_edit_client(self):
        p = self.profile()
        if not p:
            return
        res = self.ask_edit_client(self.cur, p["type"])
        if not res:
            return
        err = self.edit_client(self.cur, *res)
        if err:
            messagebox.showerror("The Benefactor", err)

    def edit_client(self, old, new_name, ctype, reprice=False):
        """Rename / change type of a client. Returns an error message, or None on success."""
        self.flush_notes()
        data = L.load(self.path)
        err = L.update_client(data, old, new_name, ctype, reprice)
        if err:
            return err
        self.write(data)
        self.cur = new_name.strip()
        self.reset_inputs()
        self.refresh()
        self.say(f"Updated {self.cur} ({L.label(ctype)})" + (" and recalculated their entries." if reprice else "."))
        return None

    def on_delete(self):
        p = self.profile()
        if not p:
            return
        if not messagebox.askyesno("Delete client",
                                   f"Delete {self.cur} and all of their history?\nThis can't be undone."):
            return
        name = self.cur
        self.notes_dirty = False
        data = L.load(self.path)
        data.pop(L.find(data, name) or name, None)
        self.write(data)
        self.cur = None
        self.reset_inputs()
        self.refresh()
        self.say(f"Deleted {name}.")

    def reset_inputs(self):
        """Empty the bag boxes and leave edit mode."""
        self.edit_idx = None
        self.free.set(False)
        self.set_counts({})

    def on_clear(self):
        """Clear the boxes; while editing this is 'Cancel edit'."""
        self.reset_inputs()
        self.update_edit_ui()
        self.render_calc()

    def update_edit_ui(self):
        p = self.profile()
        editing = p is not None and self.edit_idx is not None and 0 <= self.edit_idx < len(p["history"])
        if not editing:
            self.edit_idx = None
        self.save_btn.configure(text="Update entry" if editing else "Save entry")
        self.clear_btn.configure(text="Cancel edit" if editing else "Clear")
        if editing:
            self.edit_note.configure(text="Editing the entry from " + p["history"][self.edit_idx]["date"])
            self.edit_note.pack(fill="x", pady=(14, 0), before=self.btn_row)
        else:
            self.edit_note.pack_forget()
        can_repeat = bool(p and any((p.get("last") or {}).values())) and not editing
        self.repeat_btn.state(["!disabled" if can_repeat else "disabled"])

    def on_hist_select(self, _event=None):
        sel = self.hist_tree.selection()
        flag = "!disabled" if sel and str(sel[0]).startswith("h") else "disabled"
        self.edit_btn.state([flag])
        self.del_entry_btn.state([flag])

    def on_hist_edit(self, event=None):
        iid = ""
        if event is not None:                       # double-click on a row
            iid = self.hist_tree.identify_row(event.y)
        if not iid:                                 # button click, or double-click on empty space
            sel = self.hist_tree.selection()
            iid = sel[0] if sel else ""
        if str(iid).startswith("h") and str(iid)[1:].isdigit():
            self.begin_edit(int(str(iid)[1:]))

    def selected_entry(self):
        sel = self.hist_tree.selection()
        iid = str(sel[0]) if sel else ""
        return int(iid[1:]) if iid.startswith("h") and iid[1:].isdigit() else None

    def on_hist_delete(self, _event=None):
        idx = self.selected_entry()
        p = self.profile()
        if idx is None or not p or not 0 <= idx < len(p["history"]):
            return
        h = p["history"][idx]
        c = h["counts"]
        what = ", ".join(f"{c.get(k, 0)} {w}" for k, w in (("big", "big"), ("avg", "avg"), ("small", "small")) if c.get(k, 0))
        if not messagebox.askyesno(
                "Delete entry",
                f"Delete the entry from {h['date']}?\n\n{what or 'no bags'}  \u00b7  your take {L.money(h['sale'] - h['cut'])}"
                f"\n\nThis can't be undone."):
            return
        err = self.delete_entry(idx)
        if err:
            messagebox.showerror("The Benefactor", err)

    def delete_entry(self, idx):
        """Remove one saved entry from the current client. Returns an error message, or None."""
        data = L.load(self.path)
        name = L.find(data, self.cur or "")
        if not name:
            return "No client selected."
        profile = data[name]
        hist = profile["history"]
        if not 0 <= idx < len(hist):
            return "That entry no longer exists."
        removed = hist.pop(idx)
        # 'Repeat last' should point at the newest entry that is still there
        profile["last"] = dict(hist[-1]["counts"]) if hist else {}
        self.write(data)
        # keep the edit box pointing at the right entry (or leave edit mode if it was the one removed)
        if self.edit_idx is not None:
            if self.edit_idx == idx:
                self.reset_inputs()
            elif self.edit_idx > idx:
                self.edit_idx -= 1
        self.refresh()
        self.say(f"Deleted the entry from {removed['date']} for {name}.")
        return None

    def on_prices(self):
        res = PricesDialog(self.root).show()
        if not res:
            return
        err = self.apply_prices(*res)
        if err:
            messagebox.showerror("The Benefactor", err)
        else:
            self.say("Prices updated. New entries use them; saved entries keep their old prices.")

    def apply_prices(self, sale, cut):
        """Save and use new prices. Returns an error message, or None on success."""
        try:
            L.save_prices(sale, cut)
        except ValueError as e:
            return str(e)
        except OSError as e:
            return f"Couldn't save the prices.\n\n{L.PRICES_FILE}\n\n{e}"
        self.refresh()
        return None

    def on_check_update(self):
        """Look for a newer release without freezing the window."""
        if self.checking:
            return
        self.checking = True
        self.update_result = None
        self.update_btn.configure(text="Checking...")
        self.update_btn.state(["disabled"])
        threading.Thread(target=self._update_worker, daemon=True).start()
        self.root.after(150, self._poll_update)

    def _update_worker(self):
        try:
            self.update_result = check_latest_release()
        except Exception as e:                     # never let the background check crash silently
            self.update_result = ("error", f"Something went wrong: {e}")

    def _poll_update(self):
        if self.update_result is None:
            self.root.after(150, self._poll_update)
            return
        result, self.update_result = self.update_result, None
        self.checking = False
        self.update_btn.configure(text="Check for updates")
        self.update_btn.state(["!disabled"])
        self.show_update_result(result)

    def show_update_result(self, result):
        kind = result[0]
        if kind == "new":
            _, tag, notes, url = result
            msg = f"A new version is available: {tag}\nYou have: v{APP_VERSION}"
            if notes:
                msg += f"\n\nWhat's new:\n{notes}"
            msg += "\n\nOpen the download page?"
            if messagebox.askyesno("Update available", msg):
                webbrowser.open(url)
        elif kind == "current":
            messagebox.showinfo("The Benefactor", f"You're up to date.\n\nYou have v{APP_VERSION} (newest: {result[1]}).")
        elif kind == "none":
            messagebox.showinfo("The Benefactor", f"You have v{APP_VERSION}.\n\nNo newer release has been published yet.")
        else:
            messagebox.showerror("The Benefactor", f"Couldn't check for updates.\n\n{result[1]}")

    def begin_edit(self, idx):
        p = self.profile()
        if not p or not 0 <= idx < len(p["history"]):
            return
        self.edit_idx = idx
        self.free.set(bool(p["history"][idx].get("free")))
        self.set_counts(p["history"][idx]["counts"])
        self.update_edit_ui()
        self.render_calc()
        self.say("Change the numbers, then click Update entry.")

    def on_repeat(self):
        p = self.profile()
        if p:
            self.set_counts(p.get("last") or {})
            self.render_calc()

    def on_save(self):
        err = self.save_entry()
        if err:
            messagebox.showerror("The Benefactor", err)

    def save_entry(self):
        """Save the current entry. Returns an error message, or None on success."""
        counts = self.counts()
        data = L.load(self.path)
        name = L.find(data, self.cur or "")
        if not name:
            return "No client selected."
        profile = data[name]
        lines = L.build_lines(profile["type"], counts)
        if not lines:
            return "Enter at least one bag first."
        free = bool(self.free.get())
        cut, sale = L.entry_totals(profile["type"], counts, free)
        hist = profile["history"]
        if self.edit_idx is not None:
            i = self.edit_idx
            if not 0 <= i < len(hist):
                return "That entry no longer exists."
            hist[i].update(counts=counts, cut=cut, sale=sale, free=free)   # keeps its original date
            if i == len(hist) - 1:
                profile["last"] = counts
            msg = f"Updated the entry from {hist[i]['date']} for {name}"
        else:
            profile["last"] = counts
            hist.append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "counts": counts, "cut": cut, "sale": sale, "free": free,
            })
            msg = f"Saved for {name}"
        self.write(data)
        self.reset_inputs()          # empty and ready for the next entry
        self.refresh()
        self.say(f"{msg} - free laundry, no cut taken." if free else f"{msg} - your take {L.money(sale - cut)}.")
        return None

    def on_all_open(self, _event=None):
        sel = self.all_tree.selection()
        if sel and sel[0].isdigit() and int(sel[0]) < len(self.names):
            self.cur = self.names[int(sel[0])]
            self.reset_inputs()
            self.refresh()
            self.tabs.select(0)


def main():
    ap = argparse.ArgumentParser(description="RDR2 cut calculator window")
    ap.add_argument("--file", default=L.DEFAULT_FILE)
    ap.add_argument("--classic", action="store_true", help="use the plain flat look instead of the bubble look")
    args = ap.parse_args()
    root = tk.Tk()
    try:
        App(root, args.file, bubble=not (args.classic or os.environ.get("BENEFACTOR_CLASSIC")))
        root.mainloop()
    except Exception:
        messagebox.showerror("The Benefactor", "Something went wrong:\n\n" + traceback.format_exc()[-1200:])
        raise


if __name__ == "__main__":
    main()
