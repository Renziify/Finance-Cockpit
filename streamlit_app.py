import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

conn = sqlite3.connect("finanzcockpit.db")
c = conn.cursor()

# Vermögen anzeigen
st.title("🧠 Finanzcockpit")

# Lade Vermögensdaten
df = pd.read_sql_query("""
SELECT a.name, a.typ, e.wert, e.datum
FROM asset_entries e
JOIN assets a ON a.id = e.asset_id
WHERE e.datum = (SELECT MAX(datum) FROM asset_entries WHERE asset_id = a.id)
""", conn)

# Pie Chart: Verteilung Vermögen
st.subheader("💰 Vermögensverteilung (heute)")
st.plotly_chart({
    "data": [{"type": "pie", "labels": df['name'], "values": df['wert']}],
    "layout": {"margin": {"t": 0, "b": 0}}
})

# Gruppiert nach Typ
nutzbar = df[df['typ'].isin(['konto', 'bargeld'])]['wert'].sum()
anlagen = df[df['typ'].isin(['depot', 'tresor', 'bausparen'])]['wert'].sum()

st.metric("🟢 Nutzbares Vermögen", f"{nutzbar:,.2f} €")
st.metric("🔵 Anlagevermögen", f"{anlagen:,.2f} €")
st.metric("🟣 Gesamt", f"{(nutzbar + anlagen):,.2f} €")

# Verlauf (Linechart)
hist = pd.read_sql_query("""
SELECT e.datum, a.typ, SUM(e.wert) AS summe
FROM asset_entries e
JOIN assets a ON a.id = e.asset_id
GROUP BY e.datum, a.typ
""", conn)

st.subheader("📈 Vermögensverlauf")
chart_df = hist.pivot(index="datum", columns="typ", values="summe").fillna(0)
st.line_chart(chart_df)
