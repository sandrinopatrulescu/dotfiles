#!/usr/bin/env python3
# TODO: test if this could have been a spreadsheet instead - the only problem is updated exchange rate
import os
import re
import sys
from decimal import Decimal, getcontext

import requests
from texttable import Texttable

# Set high precision for financial math
getcontext().prec = 10

# Inputs (can be provided via env vars or hardcoded)
GLR_E = Decimal(os.getenv("GLR_E"))
GLR_SPLIT_FACTOR = Decimal(os.getenv("GLR_SPLIT_FACTOR"))
diffSource = Decimal("5")


def get_bnr_rate():
    bnr_response = requests.request("GET", "https://www.cursbnr.ro/insert/cursvalutar.php?diff=0&cb=0")
    bnr_response_match = re.search(r"1 EUR = ([0-9.]+)", bnr_response.text)
    if not bnr_response_match:
        sys.stderr.write("Could not parse BNR response from cursvalutar.php\n")
        exit(1)
    return bnr_response_match.group(1)


rate = Decimal(get_bnr_rate())  # result of e2r()

# Calculations
glr_e_split = GLR_E / GLR_SPLIT_FACTOR
# TODO: extract common logic for these calculation ex: for type in ["split", "total"]

glr_r = GLR_E * rate
glr_r_split = glr_e_split * rate

xSource = GLR_E * diffSource
xSourceSplit = glr_e_split * diffSource

glr_r_diff = xSource - glr_r
glr_r_split_diff = xSourceSplit - glr_r_split

# Build table with texttable
table = Texttable()
table.set_precision(4)
table.set_deco(Texttable.HEADER | Texttable.VLINES)
table.set_cols_align(["c", "r", "r", "r", "r"])

table.header(["Type", "glr e", "glr r", "xSource", "diff"])
table.add_rows([
    ["split", glr_e_split, glr_r_split, xSourceSplit, glr_r_split_diff],
    ["total", GLR_E, glr_r, xSource, glr_r_diff],
], header=False)

# Print table
print(table.draw())
