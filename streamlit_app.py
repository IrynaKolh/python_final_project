import streamlit as st
import sqlite3
import pandas as pd
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt

# === Main config ===
st.set_page_config(page_title="MLB Dashboard", layout="wide")
st.title("MLB Baseball Stats Dashboard")

# === Cashing data from DB ===
@st.cache_data
def get_table_names():
    with sqlite3.connect("baseball.db") as conn:
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
    return tables["name"].tolist()

@st.cache_data
def load_data(table_name):
    with sqlite3.connect("baseball.db") as conn:
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    return df

# === Dropdown with all tables ===
table_names = get_table_names()
table = st.sidebar.selectbox("Select Statistic Table", table_names)

# === Loading data from DB ===
df = load_data(table)

# === Column handling ===
if df.shape[1] == 6:
    df.columns = ["ID", "Year", "League", "Player", "Team", "Value"]
elif df.shape[1] == 5:
    df.columns = ["ID", "Year", "League", "Player", "Value"]
    df["Team"] = "Unknown"
else:
    st.error("Unexpected number of columns in the table.")
    st.stop()

# === Fix year type ===
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df.dropna(subset=["Year"], inplace=True)
df["Year"] = df["Year"].astype(int)
df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

# === Filtering ===
min_year, max_year = int(df["Year"].min()), int(df["Year"].max())

year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

league_filter = st.sidebar.multiselect("Select League(s)", options=["AL", "NL"], default=["AL", "NL"])

# === Filtering  ===
filtered_df = df[
    (df["Year"] >= year_range[0]) &
    (df["Year"] <= year_range[1]) &
    (df["League"].isin(league_filter))
]

# === Showing tables ===
st.subheader("Filtered Data")
st.dataframe(filtered_df, use_container_width=True)

# === Diagramm: Top 10 Players by Value ===
st.subheader("Top 10 Players by Value")

top_players = (
    filtered_df.groupby("Player", as_index=False)["Value"]
    .max()
    .sort_values("Value", ascending=False)
    .head(10)
)

if not top_players.empty:
    chart = alt.Chart(top_players).mark_bar().encode(
        x=alt.X("Player", type="nominal", sort="-y", title="Player"),
        y=alt.Y("Value", type="quantitative", title="Statistic"),
        color=alt.Color("Player", type="nominal", legend=None)
    ).properties(
        width=700,
        height=400
    )
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("No players match the selected filters.")

# === Line Chart: Yearly Statistics: Max, Min, and Average ===
st.subheader("Yearly Statistics: Max, Min, and Average")

yearly_stats = filtered_df.groupby("Year", as_index=False)["Value"].agg(
    Max="max",
    Min="min",
    Average="mean"
)

melted = yearly_stats.melt(id_vars="Year", var_name="Metric", value_name="Value")

chart = alt.Chart(melted).mark_line(point=True).encode(
    x=alt.X("Year:O", title="Year"),
    y=alt.Y("Value:Q", title="Value"),
    color=alt.Color("Metric:N", title="Metric"),
    tooltip=["Year", "Metric", "Value"]
).properties(
    width=800,
    height=400
)

st.altair_chart(chart, use_container_width=True)


# === Histogramm: Distribution of Values ===
st.subheader("Distribution of Values")

if not filtered_df["Value"].dropna().empty:
    st.bar_chart(filtered_df["Value"].value_counts().sort_index())
else:
    st.info("No data to show histogram.")

# === Top 10 Teams by Total Value ===
st.subheader("Top 10 Teams by Total Value")

top_teams = (
    filtered_df.groupby("Team", as_index=False)["Value"]
    .sum()
    .sort_values("Value", ascending=False)
    .head(10)
)

if not top_teams.empty:
    team_chart = alt.Chart(top_teams).mark_bar().encode(
        x=alt.X("Team", sort="-y"),
        y=alt.Y("Value"),
        color=alt.Color("Team", legend=None)
    ).properties(width=700, height=400)
    st.altair_chart(team_chart, use_container_width=True)
else:
    st.info("No team data to display.")

# Footer
st.markdown("**Data Source:** Baseball Almanac - Top League Batting Averages")