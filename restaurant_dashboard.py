import streamlit as st
import pandas as pd

# ======================================================
# CONFIG
# ======================================================
st.set_page_config(
    page_title="Restaurant Performance Dashboard",
    page_icon="🍽️",
    layout="wide"
)

st.title("🍽️ Restaurant Performance Dashboard")
st.markdown("### Turkish vs Sushi Market Comparison & Insights")


# ======================================================
# CACHE (makes app feel fast + professional)
# ======================================================
@st.cache_data
def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)


# ======================================================
# HELPERS
# ======================================================
def clean_rating(col):
    return (
        col.astype(str)
        .str.replace("Sterne", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip()
        .astype(float)
    )


def classify_cuisine(row):
    text = (str(row["Name"]) + " " + str(row["Address"])).lower()

    turkish = ["türk", "turk", "döner", "doner", "kebab", "istanbul", "ankara", "izmir"]
    sushi = ["sushi", "japan", "ramen", "tokyo", "bento", "asiatisch", "asia"]

    if any(w in text for w in turkish):
        return "Turkish"
    elif any(w in text for w in sushi):
        return "Sushi"
    return "Other"


# ======================================================
# SIDEBAR
# ======================================================
st.sidebar.header("📂 Data")

file = st.sidebar.file_uploader("Upload CSV / Excel", ["csv", "xlsx"])

if not file:
    st.info("Upload a dataset to begin")
    st.stop()


# ======================================================
# LOAD + PROCESS
# ======================================================
df = load_data(file)
df["Rating"] = clean_rating(df["Rating"])
df["Cuisine"] = df.apply(classify_cuisine, axis=1)


# ======================================================
# FILTERS
# ======================================================
st.sidebar.header("🔎 Filters")

cuisine = st.sidebar.multiselect(
    "Cuisine",
    sorted(df["Cuisine"].unique()),
    default=sorted(df["Cuisine"].unique())
)

min_rating = st.sidebar.slider("Minimum rating", 0.0, 5.0, 0.0, 0.1)

search = st.sidebar.text_input("Search restaurant")

df_filtered = df.copy()
df_filtered = df_filtered[df_filtered["Cuisine"].isin(cuisine)]
df_filtered = df_filtered[df_filtered["Rating"] >= min_rating]

if search:
    df_filtered = df_filtered[
        df_filtered["Name"].str.contains(search, case=False)
    ]


# ======================================================
# TABS
# ======================================================
tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Insights", "📋 Data"])


# ======================================================
# OVERVIEW
# ======================================================
with tab1:

    total = len(df_filtered)
    avg = round(df_filtered["Rating"].mean(), 2)
    best = round(df_filtered["Rating"].max(), 2)
    top_cuisine = df_filtered["Cuisine"].value_counts().idxmax()

    st.subheader("Key Metrics")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Restaurants", total)
    m2.metric("Average Rating", avg)
    m3.metric("Best Rating", best)
    m4.metric("Top Cuisine", top_cuisine)

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Cuisine Distribution")
        st.bar_chart(df_filtered["Cuisine"].value_counts())

    with c2:
        st.subheader("Average Rating by Cuisine")
        avg_rating = df_filtered.groupby("Cuisine")["Rating"].mean()
        st.bar_chart(avg_rating)

    best_cuisine = avg_rating.idxmax()
    score = round(avg_rating.max(), 2)

    st.success(
        f"📌 Business Insight: **{best_cuisine} restaurants outperform others with {score}⭐ average rating.**"
    )


# ======================================================
# INSIGHTS TAB
# ======================================================
with tab2:

    st.subheader("Top 10 Restaurants")

    top10 = (
        df_filtered
        .sort_values("Rating", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )

    top10.index += 1
    st.dataframe(
        top10[["Name", "Cuisine", "Rating", "Address"]],
        use_container_width=True
    )

    st.divider()

    st.subheader("Cuisine Summary")

    summary = (
        df_filtered.groupby("Cuisine")
        .agg(
            Count=("Name", "count"),
            Avg_Rating=("Rating", "mean")
        )
        .round(2)
    )

    st.dataframe(summary, use_container_width=True)


# ======================================================
# DATA TAB
# ======================================================
with tab3:

    st.subheader("Full Dataset")

    st.dataframe(df_filtered, use_container_width=True)

    csv = df_filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download filtered data",
        csv,
        "restaurants_filtered.csv",
        "text/csv"
    )
