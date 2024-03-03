import sys
import os

import pandas as pd
import pdfplumber

from utils import log

COLUMNS = ["Emission Source", "Air Contaminant Name", "Emission Rate lbs/hr", "Emission Rate tons/year"]

def extract_from_text(text):
    """Table formatted without vertical lines - extract from text.
    """
    lines = text.split("\n")
    start = [i for i, line in enumerate(lines) if line.strip().lower() == "air contaminants data"][0]

    # Find first row ending in a number
    while True:
        if lines[start].strip()[-1].isdigit():
            break
        start += 1

    end = [i for i, line in enumerate(lines) if i > start and "emission point identification" in line.lower()][0]

    rows = [line.strip().split() for line in lines[start:end]]
    print(rows)
    def tonum(x):
        try:
            return float(x)
        except:
            return float("nan")
        
    new_rows = []
    for rr in rows:
        if len(rr) < 3:
            log.debug(f"Ignoring short row {rr} of length {len(rr)}")
        else:
            new_rows.append((" ".join(rr[:-3]), rr[-3], tonum(rr[-2]), tonum(rr[-1])))
    last_non_none = None
    rows = []
    for row in new_rows:
        if row[0] is not None:
            last_non_none = row[0]
        elif row[0] is None:
            row[0] = last_non_none
        rows.append(row)
    df = pd.DataFrame(rows, columns=COLUMNS)
    df["Emission Source"].replace('', pd.NA, inplace=True)
    df["Emission Source"].fillna(method="ffill", inplace=True)
    return df


def extract_from_file(fname: str) -> pd.DataFrame:
    log.info(f"Extracting from {fname}")
    pdf = pdfplumber.open(fname)
    try:
        rows = pdf.pages[0].extract_table()[2:]
        log.debug("Encountered table with vertical lines")
        rows = [[f"{row[0]}: {row[1]}"]  + row[2:] if row[0] is not None else [""] + row[2:] for row in rows]
        df = pd.DataFrame(rows, columns=COLUMNS)
        df["Emission Source"].replace('', pd.NA, inplace=True)
        df["Emission Source"].fillna(method="ffill", inplace=True)
    except TypeError:
        log.debug("Encountered table without vertical lines, extracting from text")
        text = "\n".join([p.extract_text() for p in pdf.pages])
        df = extract_from_text(text)
    log.debug(f"Extracted table has shape {df.shape}")
    return(df)


if __name__ == "__main__":
    print(extract_from_file(sys.argv[1]))