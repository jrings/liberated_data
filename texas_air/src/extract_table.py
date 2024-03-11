import itertools
import sys

import pandas as pd
import pdfplumber

from utils import log, tonum

COLUMNS = ["Emission Source", "Air Contaminant Name", "Emission Rate lbs/hr", "Emission Rate tons/year"]

def extract_from_text(text: str):
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
        
    new_rows = []
    for rr in rows:
        if len(rr) < 3:
            log.debug(f"Ignoring short row {rr} of length {len(rr)}")
        else:
            new_rows.append((" ".join(rr[:-3]), rr[-3], tonum(rr[-2]), tonum(rr[-1])))

    df = pd.DataFrame(new_rows, columns=COLUMNS)
    df["Emission Source"].replace('', pd.NA, inplace=True)
    df["Emission Source"].fillna(method="ffill", inplace=True)
    return df


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        
    df["Emission Source"].replace('', pd.NA, inplace=True)
    df["Emission Source"].fillna(method="ffill", inplace=True)
    df["Air Contaminant Name"] = df["Air Contaminant Name"].str.replace("\n", "_")
    if not df["Emission Rate tons/year"].dtype == "float64":
        df = df[~df["Emission Rate tons/year"].str.contains('[a-zA-Z]', na=False)]
    df = df[~df["Emission Source"].isin([": None"])]
    return df


def fix_and_merge_rows(rows: list) -> list: 
    """Merging and fixing rows to the one dataframe format,
    TODO: lots of edge cases being hit with a big hammer here, refine more
    """
    rows = [[f"{row[0]}: {row[1]}"]  + row[2:] 
        if row[0] is not None 
        else [""] + row[2:] for row in rows]
    rows = [row + [""] if len(row) == 3 else row for row in rows]
    return rows


def extract_from_file(fname: str, out_fname: str = "") -> pd.DataFrame:
    log.info(f"Extracting from {fname}")
    pdf = pdfplumber.open(fname)
    table_segments = []
    for p in pdf.pages:
        try:
            tab = p.extract_table()
            if tab is not None:
                if not len(table_segments) or len(tab[0]) == len(table_segments[0][0]):  # Sometimes there is an extra table
                    table_segments.append(tab)
        except TypeError:
            pass

    if not len(table_segments):
        log.info("Encountered table without vertical lines, extracting from text")
        text = "\n".join([p.extract_text() for p in pdf.pages])
        df = extract_from_text(text)
    else:
        table_segments = [
            t[2:] if "emission" in str(t[0]).lower() else t for t in table_segments
        ]
        rows = list(itertools.chain(*table_segments))
        log.debug("Encountered table with vertical lines")
        rows = fix_and_merge_rows(rows)
        
        df = pd.DataFrame(rows, columns=COLUMNS)
    df = clean_dataframe(df)
    log.debug(f"Extracted table has shape {df.shape}")
    if not out_fname:
        out_fname = fname.replace(".pdf", ".csv")
    df.to_csv(out_fname, index=False)
    return(df)


if __name__ == "__main__":
    extract_from_file(sys.argv[1])