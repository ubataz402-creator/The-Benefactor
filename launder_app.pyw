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
# Generated artwork; corners are baked in the colour they sit on. See setup_bubble().
BUBBLE_ASSETS = {
    "card": (22, 64, 64,
        "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAIAAAAlC+aJAAAFIUlEQVR42u1a224URxCtqr7N7s7ewDhgYRFZuZBEkfL//xFFIi8g"
        "FIPBrNezOzPd091VeRhMHGwTkIzYQam3eZjROV23rqmDs4M7cLMhIjNLYjLKzopiORntlWS1KR0iwu2ZiMRt4C61p1t/VneV55hR"
        "ExGJyIcQ3kgAEUQ4ZlWY6eGyPFiYiROWHFL2sdsG+OB3P9kQbelUYZTTSBjrsD1eb56fZR/JqB7MpxBA5JjJqNmjO7Nv98iqcNa0"
        "rzZd5bnLzAwCALdKABAQiIissrNitD91yzF3uXp6Wj1b9WCu5XA9AY55tDe988sDOy3q4/P6eJ2aKCKoEBEBAQDh9k1AQEQkCyLq"
        "sZkcLCYH827jV7+/aE83ZNTVd5Sbjt7/DPPi6N693x7mkFd/vKyPzyUzKkT1FvtnNUTsj4lj9m/qsG6L5Xh+tAcs/qy+mnjvE5DE"
        "d356sPzxfv3Xev3kpA9B/Oywb2JCue3a11tSNP9unxS1JxskvIEAgmRe/vxg9uju+smr7fMVIqBSt5ysn0pDEYj4VZ19mh3tkVXt"
        "qw0qvEIAkbs8P7q3/OGb8z9f1cfnZBQAwi4YIirs1i3HvPh+nxP70y1qdYkAgiQe3S33fn1YH6+3z8/IKBDYKUNNsfKoaPboblg3"
        "qQ69H6jvIqTV8vH9buM3z1ZIuGvo+xKFhJtnq27jl4/vk34b2wSInLg8XJrSVU/fSGYghN00QslcPX1jSlceLjkxIBIwK2emh8vm"
        "ZdVVHjXt4vG/c4KmrvLNy2p6uFTOADNx4vJgQUY3Lyrc2bO/nAyEzYuKjC4PFpyYyKjx/jSsm+Tjjkb/lUxIPoZ1M96fklFkSqfH"
        "1p/WIAIDcAAAAoj401qPrSkduflIWOLWI9GuH/8/TqC49cLi5iNyi0kOiWMexvFfOIFjziG5xYSUVTkkYYFBWT+ZKKtIFSY2HQAM"
        "ywMAEJtOFYb6nIAhmgggEAjAMPH3yAkGbv3MP1QXiMjwPTD8HBhoCboIIhq4A76KMjpsBgRDTgEQoCG3AZCLEBqwC4YfQoP3gAjI"
        "MHuZiMjXcBsd/FVi8J144EUICFgABBAHhh0RQIDlK8gBGHIO9DOxXHoeEHQB+H8m3pWZGIfJAAVEKIWkrB4ifmV1Cok4ZVSEQ+sD"
        "/R6fU6a4DagJ1cCyGRWhprgNlJoOBZTTA1oRCItyGgVS01HyMYWkJ3ZY+wE9sSmk5CNJ5q5qldM7KC+4cYw0SjndVa1kJiQK60YS"
        "m4kbxGgmImbiJHFYN0hEQMAx+1VtS6ec3nEOIqKctqXzq5pjBgLqt5Z+XUcf7bzY8XqKiHZeRB/9uu73wnQhdZL2pCKj7azY3Qu2"
        "iJ0VZHR7Ukl+u5ani7KKsQnt640pCz22O1hShUWPrSmL9vUmNuGdaEtfXn/7s5o0FYsxCKS226ExTcSMrZuP/Grrz+rLooJ/if4Q"
        "MW4DErnlBBC5SyBfetoUAUQzHdnZKJw1zesPiP7ecWhCH23KakksiXtV6pe4LQtZZecjVWj/ZtuutlcFQdfoRhExNSH7ZMbWlAUS"
        "Coswv1XX4uf/5wwCAKSVKZ2djSRzc1J1VYtEHy89BsmCitxs5OYjVJRDyiFyzMLy+XoFIiIhGaWcUU5L5nDehqrtlbfXXhTww+p1"
        "YUat3LQwE0dWgYBkYWaJ+fbRG0VEqBAQuMuxDmHjJeVrD/5jCQACMIgIEiqrVaH1yCIhGX27uS0CHJOwpLbLPuUuCQsi/ufv878B"
        "L40LWojhmF4AAAAASUVORK5CYII="
    ),
    "inset": (12, 40, 40,
        "iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAIAAAADnC86AAACt0lEQVR42uWYX2/bRhDEd/bu+E+WathFjLTv/f5fqgkaoIAsRRR5"
        "d7uTBzmu3aZI7VjiQ+eZ5A+ztzvYI37+7Rd5FERc6NQmNJsuDU1oE6IKRSD/VRSBsLrNpYw57ybPBoWoCP96Kj57xahR+3frZtMB"
        "sLmWz5MVA/D0ne8IQjKkENrU3151N6u8m6Y/P3t1KL4BpjMOzfD+J42at8d5O9pcRfgC5HO8CEIb2+uhue7jVTt+vK9jfmTjVGo6"
        "m02/er+pxzL+sbOpiALA10+8XBQRISnO0KXhbhP7dPi4y7vjiR2G2/XJ6+rX6zrmw+9br46oeCXwuW0AAV687KfQp/ZmqMfi2QCo"
        "UDTqcLe2MR8+bEki4JXl/RfrCCB5+LC1MQ93a40qFKV7e7NCDOOnPY3QN6U+shU0jp/2iKG9WdFdtYnpqs33R5vLG3v9h2+bS74/"
        "pqtWm6hp1UIkb8dT2c8oCqB5O0IkrVqNQ7JcLdtbNNP3Z8yyWa5xSKop1LnKBVXnqikoFCx+STCLQ6Gvj4gfKLiIqFDO21PfDDWK"
        "cgkyhXpp6FfTKgtJhVzijKkL9ZYsecbLeF5yjhep9KmrFyBzyTleLqsvnCD8v2Y1zaHABZcAKGiuVgwxyAXJiMGKqWfToIjhIs1N"
        "xKBBPZv6XEmGPvL8Gx9dQh9J+lzVzW0qsUuawnlTjNQUYpdsKm6uAOpY3BjXreCMVxgB4rp1Yx0LcFpvnWU/adC06QRyjkubQNKm"
        "06BlP4lTRB72ahYv+0mTpk2HiDdLM4qQiEibTpOW/cTipwkKw+36gV3JYqGJoU9QpVP8B3McCBqHJl61oNT97Nkf5zY+nTAvnndT"
        "6KM2MbaB1Wl+qszLkwkIevpjZFOxYxXn07SIf88V0g7FjlWboEk1BXnFVR0iTprbWDzbA/J5Rn0BPQKgFlAS4WkAAAAASUVORK5C"
        "YII="
    ),
    "fld_n": (12, 60, 32,
        "iVBORw0KGgoAAAANSUhEUgAAADwAAAAgCAIAAADBiozFAAACyUlEQVR42tWYS28bRxCEu3peHFJLSTalQ3LwIUb+/59KDMXya/lY"
        "zux0dw6UFMo2AuQQclnY4yzwoTDTXd1Y/f4LfScjYnB0HBmOwUxmdDIBpmqiWlWrkBrh+yP+B1zy88jJE5lWkTJq0x9/+x9lxJ45"
        "OD8PNI9aWhsqKR0z+OPTCBy6REDblHFddGyntPi13cTBhy75qxSTG9fFxn+8e4Y24xTCMklp5dNWSgOIAIDOJR3b/lNzm5LeLuJN"
        "HvuiZSSAiPiJOLh4nbS04aGX0sCgM/I+uw2GlDY89FpavE4c3OF1MRERc7jOUmT30JMa+Ny4x+QMUts99FIkXGdiJiI2M78IYOwf"
        "NyZGUyJ+EsPE9o8bMPwimBnDsc9xXBcpDQ5kk2MmIzhIaeO6+BzhmP0sAKj9AEyS+IX7GdLPArvktTapjUCTFkhq09pc8szRSW0/"
        "bTxTgyY1qY2jYzino9KFSEeFcwwQGJcCDQZwqNOXJj5/5/vvnZIBogvCBh2ux6VRExi4NGQc7vSlUV9m9QBPOHL8NIQw2EQ5+Qt5"
        "i+DkTZSlSsiBmKbutxExhRykCsuu+hx98mQTzkwgMvPJ+xxlV7luC4HyXWc6aatNLd91BKrbwlql9iWvOj9PJpM0G2Rifp7yqqt9"
        "0SoMxv7zxkSX797AsU0tWINMDY6X796Y6P7zBgwmkDbdfvgWFrPb9/dgthOvlP6duCmYb9/fh8Vs++HbYd3l5m87AFJFa8urLi1n"
        "465KGZ9WNYe+eerv6RKbaljMbn+7i1ez7Z9f6qYcoj9eFpCmFubx6tcbeDd8XO/+6tswmtkZSiEIgM9hfr/Md5012fzxddzVl2EF"
        "x1tTU2PPedWlmwyicRjbwfVTZm4zl4Kfx5CDEZWvw/C41qbH49Ur6MPwaGocfVrmeJXcLLB3pyvhRgRoE9mPdVNKP2htYNDrrPE3"
        "hql4oAftPvgAAAAASUVORK5CYII="
    ),
    "fld_f": (12, 60, 32,
        "iVBORw0KGgoAAAANSUhEUgAAADwAAAAgCAIAAADBiozFAAAEW0lEQVR42tXYX2yTVRQA8HPP/f70a7+2g/XPgO6PY7AKkUlk409M"
        "fGHJFkLGg9HoA8EYIb7Ii4nRkPikiYkm6oO8AgkxS4wxUTNMTEAgQwUy54h04jbYuo62G2u/tf3a7889PgzqkBdf7NqT+3gffjk5"
        "995zDwtt3wyPgiOr2MK03LawNrg7dCDeFN/iizQpjkuMMfj/g4gkzjI5KzFfHE3kRsYWZ7OmpnBVRldQdRurojkyw3SiQeXNgdbD"
        "vRGFs0SycHu2MLdoypwR1CIYgO1Sa0h7uk2Px3TLpW+vZ05fmEvnrYAmVd0P0YiwUnL3dwc/OtodDSpf/jR/7sfkX6mi5Qii2oDX"
        "0BlTJOza7Dt6MPbKC1vSeeudc5PXJvN+LxfiEZojM0rOkb7Ix8e2/zZtvHcmMT5teBT0KIg1qYonQxCVLVG2RE9n4MNj8Wc7A2+f"
        "+fObXzMBr+QK4v5wwDCd/d3BL07suJZYfv3T8blseYNflhCJYL0WACgS+jx8LlseuZHp6Qy+djB2Yyo/lTY1hXM5qDf75dMndkwt"
        "FN/4bNysCF3jjlvzmnjyUAIIAq/KzYr44WZmb3zD4b7IyNhiseyiabnH+2Nhv3Lq7KRRcjQVHXfdwf+E45KmolFyTp2dDPuV4/0x"
        "03KxNeQZ2N08fDk1MWMEvFJdiavugFeamDGGL6cGdje3hjzY39MsIzt/KamqKKjuxNVzqap4/lJSRtbf04y9XYHJZHF6oeSRH14o"
        "9YgW4JH59EJpMlns7QpgV4s3kSxYjkAG9RzIwHJEIlnoavFiSJfnl8x6rYt/PfIwv2SGdBktl6Q6T/KakJBZLiEACWoUMwgCAEIh"
        "gBoHTQRCAAoggoZRE5AAQhKNQwYgABKA1EiJBiAgIhTUaDVNq5lmjaNmRETIGHOchkE7DjHGMGtY0Sa1IZ4XZBBtUrOGhdP3za2b"
        "vLJUvy1etdGTJdy6yTt938SxGaMjorVHtIot1utH+B9yzCq2aI9oHRFtbMbAK7dzlktD+6KWXb+NHjKwbDG0L2q5dOV2DlM56+Kt"
        "5cE94e6YvlJ2eP3BObKVstMd0wf3hC/eWk7lLFRlHB5NLxr2yaEO3SNVbFFX7tWhl+6RTg51LBr28GhalZEHw4G86c5kzJcPROOt"
        "+tU/lgtlxyPz9b+RGXBkhbLjVfn7r27b2aZ/8PXdmWzFKyPXmv2qxOaWrIXlypG+yK6nAndSpdRSBYBJnCEyZLVeq3PDik2lsrtt"
        "i+/dl7p2tumffDf7850Vn4qCqmMxBsWK2NXme2swtlGXL9zMfn89O5c1bZfWZSwmc9Ya1g71hgeeCz8o2J+PJH+fLa6KHxtArro3"
        "6tKLeyPPx4MSsnsZ827aTOcrHBnUagLpCooG1Y6o1h7RHEFXE/mvfsk8KDhV8WNoAEBktiPKtmhpUvZvCz7T5msPeTbokiuIAatN"
        "D8eRLRece4vlidnitTv5+znLI6MsoVjzv/obbVx3sbwcHlsAAAAASUVORK5CYII="
    ),
    "fld_d": (12, 60, 32,
        "iVBORw0KGgoAAAANSUhEUgAAADwAAAAgCAIAAADBiozFAAACDklEQVR42u2Yu3LbQAxF7wWwJG1N1CRVPiD//22aOKK4eKSQLMtO"
        "JpNKpGeEghWLw0NgH5fffnzHhypAKCY0oZBCFO5XRGVVVnmmJ7LAj6/YH7iQ0aQJgPLMJTKKvB9zFURJFRlVRs2euTgSt+h2S0yj"
        "Tg1knHrMXp5A3dPyq2sApIlOpmMTk5h7+ZtyeyNuYk8te/SXJT0IggDuafm9cs/+8xSzt91gz4Mfe/U8c8vVsU0teyyHuTxIYi3Y"
        "G+Eky2M5zNnDpka7TJecHzq19FwOM9aU+1d0AlgOc3rq1F55CzIYyf5yWqOB/3c8+8uJpAyGgkAgTfzU02Nbjt/7Tg8/dWkCgYgp"
        "wDj6ZoGvbRJHByimQmN5VgSwbWqwIsqTRhGRjMAnqYwQEQGJ3OwAftyvkQVS8AnrAf2AfkA/oB/QW4eugmz8sHRzDROiSjJTVD+N"
        "Y9XMlPKiCVWBjR9Aiqo0KS9JD6D0yTZ+aKqCPhlQ6SFIZE8bm5hu+bolpja27ImEgMjFq6rtxi1ft9purKpcHDwveYmYu5gM++ny"
        "JzbVFsCwn86RDfK6ThPl5XOXpsN+omlVrT+Whaqi6bCfpKnfhEz6/PXLZQ2MqkgZTKdGZWUha91YzJ6HthtJxvGvsdjV969FBtPR"
        "dLTyrMi1AkiaAMge/wwgz99YyNlzuUS9MpiuFPXmKd6i3vfWfgOBDzneOBmmXwAAAABJRU5ErkJggg=="
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

APP_VERSION = "1.20"  # shown in the title bar so you can tell which build you are running
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
            cv.create_rectangle(p["x0"], p["y0"], p["x1"], p["y1"], fill=p["fill"], outline="")
        elif p["t"] == "line":
            flat = [c for pt in p["pts"] for c in pt]
            if len(flat) >= 4:
                cv.create_line(*flat, fill=p["color"], width=p["width"])
        elif p["t"] == "text":
            cv.create_text(p["x"], p["y"], text=p["text"], fill=p["color"], font=("Georgia", p["size"], "bold"))


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
        for sh in shapes:
            self.create_polygon(*rrect_points(*sh["box"], sh["r"]), smooth=True, fill=sh["fill"], outline="")
        self.create_text(tx, ty, text=self.text, fill=fg, font=self.font)


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
            ttk.Checkbutton(body, text="Recalculate their past entries at the new prices", variable=self.again,
                            style="Card.TCheckbutton").grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))
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
        root.columnconfigure(1, weight=1)
        root.rowconfigure(1, weight=1)
        self.bg_cv = tk.Canvas(root, bg=BG, highlightthickness=0, bd=0)    # engraved banknote border
        self.bg_cv.place(x=0, y=0, relwidth=1, relheight=1)
        self._bg_job = None
        self._bg_size = None
        root.bind("<Configure>", self.on_root_resize, add="+")

        head = ttk.Frame(root, style="Bubble.TFrame", padding=(16, 10))
        head.grid(row=0, column=0, columnspan=2, sticky="ew", padx=MARGIN, pady=(MARGIN, 8))
        if self.logo_header:
            ttk.Label(head, image=self.logo_header, style="Card.TLabel").pack(side="left", padx=(0, 12))
        ttk.Label(head, text="THE BENEFACTOR", style="CardTitle.TLabel").pack(side="left")
        self.update_btn = button(head, text="Check for updates", command=self.on_check_update)
        self.update_btn.pack(side="right")
        button(head, text="Edit prices", command=self.on_prices).pack(side="right", padx=(0, 8))
        ttk.Label(head, text=f"v{APP_VERSION}", style="Muted.TLabel").pack(side="right", padx=(0, 12))

        left = ttk.Frame(root)
        left.grid(row=1, column=0, sticky="ns", padx=(MARGIN, 10), pady=(0, 6))
        right = ttk.Frame(root)
        right.grid(row=1, column=1, sticky="nsew", padx=(10, MARGIN), pady=(0, 6))
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
        ttk.Checkbutton(ctl, text="Add combined line", variable=self.combined, style="Card.TCheckbutton",
                        command=self.draw_chart).pack(side="left")
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
                          ("sale", "Sale price", 100, "e"), ("take", "My take", 100, "e")]
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
                         ("sale", "Sale total", 100, "e"), ("take", "My take", 100, "e")]
        wrap, self.all_tree = self.make_tree(all_page, self.all_cols, 8)
        wrap.pack(fill="both", expand=True)
        self.all_tree.bind("<Double-1>", self.on_all_open)
        self.all_tree.bind("<Return>", self.on_all_open)

        # --- status bar ---
        self.status = tk.StringVar(value="")
        ttk.Label(root, textvariable=self.status, style="Status.TLabel").grid(
            row=2, column=0, sticky="w", padx=MARGIN, pady=(0, MARGIN))
        self.where = tk.StringVar(value="")
        ttk.Label(root, textvariable=self.where, style="Status.TLabel").grid(
            row=2, column=1, sticky="e", padx=MARGIN, pady=(0, MARGIN))

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
                cv.create_oval(p["x"] - r, p["y"] - r, p["x"] + r, p["y"] + r, fill=p["fill"], outline=PANEL, width=1)
            elif p["t"] == "shine":
                r = p["r"]
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
        ttk.Checkbutton(plaque, text="Show this screen when the app opens", variable=self.show_start,
                        style="Card.TCheckbutton", command=self.on_start_pref).pack(pady=(18, 0))
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
        if self.start is not None:
            self.start.destroy()
            self.start = None
            self.root.focus_set()

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

    @staticmethod
    def clear(tree):
        tree.delete(*tree.get_children())

    def render_calc(self):
        self.clear(self.calc_tree)
        p = self.profile()
        lines = L.build_lines(p["type"], self.counts()) if p else []
        t_qty = t_cut = t_sale = 0
        for name, qty, cut, sale in lines:
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
                L.money(h["cut"]), L.money(h["sale"]), L.money(h["sale"] - h["cut"])))
        if p["history"]:
            cut, sale = L.lifetime(p)
            n = len(p["history"])
            self.hist_tree.insert("", "end", tags=("total",), values=(
                f"Lifetime ({n} {'entry' if n == 1 else 'entries'})", "", "", "",
                L.money(cut), L.money(sale), L.money(sale - cut)))

    def render_clients(self):
        self.clear(self.all_tree)
        g_entries = g_cut = g_sale = 0
        for i, n in enumerate(self.names):
            p = self.data[n]
            cut, sale = L.lifetime(p)
            g_entries += len(p["history"])
            g_cut += cut
            g_sale += sale
            self.all_tree.insert("", "end", iid=str(i), values=(
                n, L.label(p["type"]), len(p["history"]), L.money(cut), L.money(sale), L.money(sale - cut)))
        if self.names:
            self.all_tree.insert("", "end", iid="total", tags=("total",), values=(
                "All clients", "", g_entries, L.money(g_cut), L.money(g_sale), L.money(g_sale - g_cut)))

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
        cut = sum(x[2] for x in lines)
        sale = sum(x[3] for x in lines)
        hist = profile["history"]
        if self.edit_idx is not None:
            i = self.edit_idx
            if not 0 <= i < len(hist):
                return "That entry no longer exists."
            hist[i].update(counts=counts, cut=cut, sale=sale)   # keeps its original date
            if i == len(hist) - 1:
                profile["last"] = counts
            msg = f"Updated the entry from {hist[i]['date']} for {name}"
        else:
            profile["last"] = counts
            hist.append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "counts": counts, "cut": cut, "sale": sale,
            })
            msg = f"Saved for {name}"
        self.write(data)
        self.reset_inputs()          # empty and ready for the next entry
        self.refresh()
        self.say(f"{msg} - your take {L.money(sale - cut)}.")
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
