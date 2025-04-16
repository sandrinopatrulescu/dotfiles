#!/usr/bin/env python3
# TODO: test if this could have been a spreadsheet instead - the only problem is updated exchange rate
import os
from decimal import Decimal, getcontext

from texttable import Texttable

# Set high precision for financial math
getcontext().prec = 10

# Inputs (can be provided via env vars or hardcoded)
GLR_E = Decimal(os.getenv("GLR_E"))
GLR_SPLIT_FACTOR = Decimal(os.getenv("GLR_SPLIT_FACTOR"))
diffSource = Decimal("5")
rate = Decimal(os.getenv("RATE", "4.9775"))  # result of e2r() # TODO: replace with call to API

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
