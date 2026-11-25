#!/usr/bin/env python3
"""RDR2 cut calculator with client profiles.

Each client gets a saved profile (name + VIP/regular), so repeat clients
don't need re-entering. Profiles remember their last entry and keep a
history with running totals.

Data is saved in profiles.json in your user data folder (on Windows:
%APPDATA%\\The Benefactor). An older profiles.json next to this script is
copied there automatically the first time.

    Item                Regular    VIP     Sale price
    Big bag of cash       $750    $1,000     $1,500
    Avg bag of cash       $400      $500       $750
    Small bag of cash     $150      $200       $300

Usage:
    python launder.py                          # pick or create a client
    python launder.py --profile Bob            # jump straight to Bob
    python launder.py --profile Bob --big 2 --avg 1
    python launder.py --new Bob --type vip     # create a profile
    python launder.py --list                   # all clients + lifetime totals
    python launder.py --history Bob            # Bob's past entries
    python launder.py --delete Bob             # remove a profile
    python launder.py --no-save ...            # calculate without saving
"""
import argparse
import json
import math
import os
import shutil
import sys
from datetime import datetime

if getattr(sys, "frozen", False):
    # Packaged as an .exe: HERE is the folder the .exe is in (not its temp folder).
    HERE = os.path.dirname(sys.executable)
else:
    HERE = os.path.dirname(os.path.abspath(__file__))


def default_profiles_file():
    """Where clients are saved: a fixed per-user folder that doesn't depend on where the
    app or .exe sits (so moving it, or running from a temp/zip folder, can't lose data).
    On Windows this is %APPDATA%\\The Benefactor. An older profiles.json next to the app is
    copied there the first time. If that folder can't be used, fall back to next to the app."""
    legacy = os.path.join(HERE, "profiles.json")
    base = os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), ".local", "share")
    folder = os.path.join(base, "The Benefactor")
    target = os.path.join(folder, "profiles.json")
    try:
        os.makedirs(folder, exist_ok=True)
        probe = os.path.join(folder, ".write-test")
        with open(probe, "w") as f:
            f.write("ok")
        os.remove(probe)
        if not os.path.exists(target) and os.path.exists(legacy):
            shutil.copy2(legacy, target)
        return target
    except OSError:
        return legacy


DEFAULT_FILE = default_profiles_file()

# Built-in prices. They can be changed (Edit prices in the app); changes are kept in prices.json
# in the same folder as profiles.json and loaded on start-up.
DEFAULT_SALE = {"big": 1500, "avg": 750, "small": 300}
DEFAULT_CUT = {
    "regular": {"big": 750, "avg": 400, "small": 150},
    "vip": {"big": 1000, "avg": 500, "small": 200},
}
SALE = dict(DEFAULT_SALE)                                   # live prices (updated in place)
CUT = {t: dict(v) for t, v in DEFAULT_CUT.items()}
NAMES = {"big": "Big bag of cash", "avg": "Avg bag of cash", "small": "Small bag of cash"}
PRICES_FILE = os.path.join(os.path.dirname(DEFAULT_FILE), "prices.json")


def money(x):
    return "$" + format(x, ",.2f")


def label(client_type):
    return "VIP" if client_type == "vip" else "Regular"


# ---------- storage ----------

def load(path):
    if not os.path.exists(path):
        return {}
    try:
        if os.path.getsize(path) == 0:
            return {}
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Damaged file: keep a copy so a later save can't wipe the only record.
        backup = path + ".damaged-" + datetime.now().strftime("%Y%m%d-%H%M%S")
        try:
            os.replace(path, backup)
            print(f"{path} was damaged; kept a copy at {backup} and started fresh.")
        except OSError:
            print(f"Couldn't read {path}; starting with no profiles.")
        return {}
    except OSError:
        print(f"Couldn't read {path}; starting with no profiles.")
        return {}


def save(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def find(data, name):
    """Case-insensitive profile lookup; returns the stored name or None."""
    for n in data:
        if n.lower() == name.strip().lower():
            return n
    return None


# ---------- calculation ----------

def _valid_price(v):
    return (isinstance(v, (int, float)) and not isinstance(v, bool)
            and math.isfinite(v) and 0 < v <= 10_000_000)


def _tidy(v):
    v = round(float(v), 2)
    return int(v) if v == int(v) else v


def validate_prices(sale, cut):
    """Return a plain-English error, or None if these prices are usable."""
    for k in NAMES:
        s = sale.get(k)
        if not _valid_price(s):
            return f"{NAMES[k]}: enter a sale value above 0."
        for t in ("regular", "vip"):
            c = (cut.get(t) or {}).get(k)
            if not _valid_price(c):
                return f"{NAMES[k]} ({label(t)}): enter a price above 0."
            if c > s:
                return f"{NAMES[k]} ({label(t)}): can't be higher than the sale value ({money(s)})."
    return None


def apply_prices(sale, cut):
    """Make these the live prices (the tables are updated in place, so everything sees them)."""
    for k in NAMES:
        SALE[k] = _tidy(sale[k])
        for t in ("regular", "vip"):
            CUT[t][k] = _tidy(cut[t][k])


def load_prices(path=None):
    """Load saved price changes. A missing or damaged file just leaves the built-in prices."""
    try:
        with open(path or PRICES_FILE) as f:
            raw = json.load(f)
        sale = {k: raw["sale"][k] for k in NAMES}
        cut = {t: {k: raw["cut"][t][k] for k in NAMES} for t in ("regular", "vip")}
    except (OSError, ValueError, KeyError, TypeError):
        return False
    if validate_prices(sale, cut):
        return False
    apply_prices(sale, cut)
    return True


def save_prices(sale, cut, path=None):
    """Validate, save to prices.json, and make the prices live. Raises ValueError / OSError."""
    err = validate_prices(sale, cut)
    if err:
        raise ValueError(err)
    path = path or PRICES_FILE
    data = {"sale": {k: _tidy(sale[k]) for k in NAMES},
            "cut": {t: {k: _tidy(cut[t][k]) for k in NAMES} for t in ("regular", "vip")}}
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)
    apply_prices(sale, cut)


def build_lines(client_type, counts):
    lines = []
    for k in NAMES:
        qty = counts.get(k, 0)
        if qty:
            lines.append((NAMES[k], qty, qty * CUT[client_type][k], qty * SALE[k]))
    return lines


def print_report(name, client_type, lines):
    print(f"\nClient: {name} ({label(client_type)})\n")
    print(f"{'Item':<20}{'Qty':>5}{label(client_type):>14}{'Sale price':>14}{'My take':>14}")
    print("-" * 67)
    t_cut = t_sale = t_qty = 0
    for item, qty, cut, sale in lines:
        t_cut += cut
        t_sale += sale
        t_qty += qty
        print(f"{item:<20}{qty:>5}{money(cut):>14}{money(sale):>14}{money(sale - cut):>14}")
    print("-" * 67)
    print(f"{'Total':<20}{t_qty:>5}{money(t_cut):>14}{money(t_sale):>14}{money(t_sale - t_cut):>14}\n")
    return t_cut, t_sale


# ---------- prompts ----------

def ask_type():
    while True:
        raw = input("VIP or regular client? [v/r]: ").strip().lower()
        if raw in ("v", "vip"):
            return "vip"
        if raw in ("r", "reg", "regular"):
            return "regular"
        print("  Type v for VIP or r for regular.")


def ask_int(prompt):
    while True:
        raw = input(prompt).strip()
        if not raw:
            return 0
        try:
            return max(0, int(raw))
        except ValueError:
            print("  Enter a whole number.")


def ask_counts():
    print("How many of each? (blank = 0)")
    return {k: ask_int(f"  {n}: ") for k, n in NAMES.items()}


def ask_yes(prompt):
    return input(prompt).strip().lower() in ("y", "yes")


def entry_totals(client_type, counts, free=False):
    """(cut, sale) for one entry. A free laundry is a 100% return: the client keeps the whole
    sale value, so the cut equals the sale and my take is zero."""
    lines = build_lines(client_type, counts)
    sale = sum(x[3] for x in lines)
    return (sale if free else sum(x[2] for x in lines)), sale


def free_count(profile):
    """How many free-laundry entries a client has received."""
    return sum(1 for h in profile.get("history", []) if h.get("free"))


def lifetime(profile):
    return (sum(h["cut"] for h in profile["history"]),
            sum(h["sale"] for h in profile["history"]))


def create_profile(data, name, client_type):
    data[name] = {"type": client_type, "last": {}, "history": []}
    return data[name]


def update_client(data, old, new_name, client_type, reprice=False):
    """Rename a client and/or switch VIP/Regular, in place. Returns an error message or None.
    Past entries keep the amounts they were saved with unless reprice=True, which recalculates
    each one from its bag counts at the new type's prices."""
    key = find(data, old)
    if key is None:
        return "That client no longer exists."
    new_name = new_name.strip()
    if not new_name:
        return "Enter a client name."
    if client_type not in CUT:
        return "Pick VIP or Regular."
    clash = find(data, new_name)
    if clash is not None and clash != key:
        return f"'{new_name}' already exists."
    profile = data[key]
    profile["type"] = client_type
    if reprice:
        for h in profile.get("history", []):
            lines = build_lines(client_type, h.get("counts") or {})
            if lines:
                h["cut"], h["sale"] = entry_totals(client_type, h.get("counts") or {}, bool(h.get("free")))
    if new_name != key:
        del data[key]
        data[new_name] = profile
    return None


def pick_profile(data):
    """Interactive: choose an existing client or create a new one. Returns (name, profile)."""
    names = sorted(data, key=str.lower)
    if names:
        print("Clients:")
        for i, n in enumerate(names, 1):
            print(f"  {i}. {n} ({label(data[n]['type'])})")
        print("  n. New client")
    else:
        print("No saved clients yet.")
    while True:
        raw = input("Pick a number, type a name, or n for new: " if names else "Client name: ").strip()
        if not raw:
            continue
        if names and raw.isdigit() and 1 <= int(raw) <= len(names):
            n = names[int(raw) - 1]
            return n, data[n]
        if raw.lower() in ("n", "new") and names:
            raw = input("New client name: ").strip()
            if not raw:
                continue
        existing = find(data, raw)
        if existing:
            return existing, data[existing]
        if ask_yes(f"No client named '{raw}'. Create it? [y/N]: "):
            return raw, create_profile(data, raw, ask_type())


# ---------- commands ----------

def cmd_list(data):
    if not data:
        print("No saved clients.")
        return
    print(f"\n{'Client':<18}{'Type':<9}{'Entries':>8}{'Cut total':>15}{'Sale total':>15}{'My take':>15}")
    print("-" * 80)
    g_entries = g_cut = g_sale = 0
    for n in sorted(data, key=str.lower):
        p = data[n]
        cut, sale = lifetime(p)
        g_entries += len(p["history"])
        g_cut += cut
        g_sale += sale
        print(f"{n:<18}{label(p['type']):<9}{len(p['history']):>8}{money(cut):>15}{money(sale):>15}{money(sale - cut):>15}")
    print("-" * 80)
    print(f"{'All clients':<27}{g_entries:>8}{money(g_cut):>15}{money(g_sale):>15}{money(g_sale - g_cut):>15}\n")


def cmd_history(data, name):
    n = find(data, name)
    if not n:
        print(f"No client named '{name}'.")
        return
    p = data[n]
    k = len(p["history"])
    print(f"\n{n} ({label(p['type'])}) - {k} {'entry' if k == 1 else 'entries'}\n")
    if not p["history"]:
        print("No entries yet.\n")
        return
    print(f"{'Date':<18}{'Big':>5}{'Avg':>5}{'Small':>6}{'Cut':>14}{'Sale':>14}{'My take':>14}")
    print("-" * 76)
    for h in p["history"]:
        c = h["counts"]
        print(f"{h['date']:<18}{c.get('big', 0):>5}{c.get('avg', 0):>5}{c.get('small', 0):>6}"
              f"{money(h['cut']):>14}{money(h['sale']):>14}{money(h['sale'] - h['cut']):>14}")
    cut, sale = lifetime(p)
    print("-" * 76)
    print(f"{'Lifetime':<34}{money(cut):>14}{money(sale):>14}{money(sale - cut):>14}\n")


def main():
    ap = argparse.ArgumentParser(description="RDR2 cut calculator with client profiles")
    ap.add_argument("--profile", help="use this client's profile")
    ap.add_argument("--new", metavar="NAME", help="create a new client profile")
    ap.add_argument("--type", choices=["vip", "regular"], help="client type (with --new)")
    ap.add_argument("--list", action="store_true", help="list all clients")
    ap.add_argument("--history", metavar="NAME", help="show a client's history")
    ap.add_argument("--delete", metavar="NAME", help="delete a client profile")
    ap.add_argument("--no-save", action="store_true", help="don't save this entry")
    ap.add_argument("--file", default=DEFAULT_FILE, help="profiles file location")
    for key, name in NAMES.items():
        ap.add_argument(f"--{key}", type=int, default=0, help=f"{name} count")
    args = ap.parse_args()

    data = load(args.file)

    if args.list:
        return cmd_list(data)
    if args.history:
        return cmd_history(data, args.history)
    if args.delete:
        n = find(data, args.delete)
        if not n:
            return print(f"No client named '{args.delete}'.")
        if ask_yes(f"Delete '{n}' and all their history? [y/N]: "):
            del data[n]
            save(args.file, data)
            print(f"Deleted {n}.")
        return

    # choose the profile
    if args.new:
        if find(data, args.new):
            sys.exit(f"'{args.new}' already exists.")
        name, profile = args.new, create_profile(data, args.new, args.type or ask_type())
    elif args.profile:
        name = find(data, args.profile)
        if name:
            profile = data[name]
        elif ask_yes(f"No client named '{args.profile}'. Create it? [y/N]: "):
            name, profile = args.profile, create_profile(data, args.profile, args.type or ask_type())
        else:
            return
    else:
        name, profile = pick_profile(data)

    # get the amounts
    counts = {k: getattr(args, k) for k in NAMES}
    if not any(counts.values()):
        last = profile.get("last") or {}
        if any(last.values()):
            summary = ", ".join(f"{v} {NAMES[k].split()[0].lower()}" for k, v in last.items() if v)
            if ask_yes(f"Repeat last entry ({summary})? [y/N]: "):
                counts = dict(last)
        if not any(counts.values()):
            counts = ask_counts()

    lines = build_lines(profile["type"], counts)
    if not lines:
        print("Nothing entered.")
        return
    cut, sale = print_report(name, profile["type"], lines)

    if args.no_save:
        return
    profile["last"] = counts
    profile["history"].append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "counts": counts, "cut": cut, "sale": sale,
    })
    save(args.file, data)
    t_cut, _ = lifetime(profile)
    n = len(profile["history"])
    print(f"Saved. {name}'s lifetime cut: {money(t_cut)} over {n} {'entry' if n == 1 else 'entries'}.\n")


load_prices()

if __name__ == "__main__":
    main()
