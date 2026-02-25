"""
data_audit.py  –  Loads, cleans and enriches restaurant + review CSV data.
Handles both 'Page_URL' (original) and 'page_url' (lowercased) automatically.
"""
import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta


def load_and_clean_data(restaurants_path="restaurants.csv", reviews_path="reviews.csv"):
    df_rest = _load_restaurants(restaurants_path)
    df_rev  = _load_reviews(reviews_path)
    df_rest = _enrich_restaurants(df_rest, df_rev)
    benchmarks = _compute_benchmarks(df_rest)
    return df_rest, df_rev, benchmarks


# ──────────────────────────────────────────────────────────────────────────────────
def _load_restaurants(path):
    df = pd.read_csv(path)

    rating_col = find_col(df, ['rating'])
    if rating_col:
        df['rating_n'] = (
            df[rating_col].astype(str)
            .str.replace(',', '.', regex=False)
            .str.extract(r'(\d+\.?\d*)', expand=False)
            .astype(float).fillna(0)
        )
    else:
        df['rating_n'] = 0.0

    rev_col = find_col(df, ['review_count','review_co','reviews','rev_count'])
    df['rev_count_n'] = df[rev_col].apply(_parse_int) if rev_col else 0

    if not find_col(df, ['district']):
        df['district'] = 'Frankfurt City'
    if not find_col(df, ['price']):
        df['price'] = '20-30'

    return df


def _load_reviews(path):
    df = pd.read_csv(path)

    date_col = find_col(df, ['review_date','reviewer_data','date','review_time'])
    df['normalized_date'] = df[date_col].apply(_parse_german_date) if date_col else datetime.now()

    rating_col = find_col(df, ['review_rating','review_c','rating','stars'])
    if rating_col:
        df['review_rating'] = pd.to_numeric(df[rating_col], errors='coerce').fillna(5)
    else:
        df['review_rating'] = 5

    return df


def _enrich_restaurants(df_rest, df_rev):
    r_url = find_col(df_rest, ['page_url','url','link'])
    v_url = find_col(df_rev,  ['page_url','url','link'])
    resp_col = find_col(df_rev, ['owner_response','owner_response_content'])

    # Response rate
    if r_url and v_url:
        rates = {}
        for url in df_rest[r_url].dropna():
            sub = df_rev[df_rev[v_url].astype(str) == str(url)]
            if len(sub) > 0:
                rates[url] = (sub[resp_col].notna().sum() / len(sub)) if resp_col else 0.0
        df_rest['res_rate'] = df_rest[r_url].map(rates).fillna(0.0)
    else:
        np.random.seed(42)
        df_rest['res_rate'] = np.random.beta(2, 3, size=len(df_rest))

    # Sentiment
    if r_url and v_url and 'review_rating' in df_rev.columns:
        sm = {}
        for url in df_rest[r_url].dropna():
            sub = df_rev[df_rev[v_url].astype(str) == str(url)]
            if len(sub) > 0:
                sm[url] = ((sub['review_rating'].mean() - 1) / 4.0) * 100
        df_rest['sentiment'] = df_rest[r_url].map(sm).fillna(((df_rest['rating_n'] - 1) / 4.0) * 100)
    else:
        df_rest['sentiment'] = ((df_rest['rating_n'] - 1) / 4.0) * 100

    # Recency score
    if r_url and v_url and 'normalized_date' in df_rev.columns:
        c90 = datetime.now() - timedelta(days=90)
        c180 = datetime.now() - timedelta(days=180)
        rm = {}
        for url in df_rest[r_url].dropna():
            sub = df_rev[df_rev[v_url].astype(str) == str(url)]
            if len(sub) > 0:
                d = pd.to_datetime(sub['normalized_date'])
                rm[url] = min(((d > c90).sum() * 0.7 + (d > c180).sum() * 0.3) / len(sub), 1.0)
        df_rest['recency_score'] = df_rest[r_url].map(rm).fillna(0.5)
    else:
        df_rest['recency_score'] = 0.5

    return df_rest


def _compute_benchmarks(df_rest):
    return {
        'rating':         float(df_rest['rating_n'].quantile(0.75)),
        'response_rate':  0.90,
        'recency':        0.70,
        'review_volume':  float(df_rest['rev_count_n'].quantile(0.75)),
        'top_rating':     float(df_rest['rating_n'].max()),
        'avg_rating':     float(df_rest['rating_n'].mean()),
        'median_reviews': float(df_rest['rev_count_n'].median()),
    }


# ──────────────────────────────────────────────────────────────────────────────────
# PUBLIC helpers (used by other modules too)
# ──────────────────────────────────────────────────────────────────────────────────
def find_col(df, candidates):
    """Case-insensitive column lookup. Returns actual column name or None."""
    col_map = {c.lower(): c for c in df.columns}
    for c in candidates:
        if c.lower() in col_map:
            return col_map[c.lower()]
    return None


def _parse_int(x):
    found = re.findall(r'\d+', str(x))
    return int(''.join(found[:2])) if found else 0


def _parse_german_date(date_str):
    today = datetime.now()
    s = str(date_str).lower()
    n = int(re.search(r'\d+', s).group()) if re.search(r'\d+', s) else 1
    if 'einem monat' in s:  return today - timedelta(days=30)
    if 'monat' in s:        return today - timedelta(days=n * 30)
    if 'einem jahr' in s:   return today - timedelta(days=365)
    if 'jahr' in s:         return today - timedelta(days=n * 365)
    if 'einer woche' in s:  return today - timedelta(days=7)
    if 'woche' in s:        return today - timedelta(days=n * 7)
    if 'tag' in s:          return today - timedelta(days=n)
    if 'stunde' in s:       return today - timedelta(hours=n)
    if 'gestern' in s:      return today - timedelta(days=1)
    if 'heute' in s:        return today
    for fmt in ['%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y']:
        try:
            return datetime.strptime(str(date_str), fmt)
        except Exception:
            pass
    return today - timedelta(days=90)