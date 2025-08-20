import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Circular Construction Simulation Model (Ireland)")
st.markdown("Adjust parameters below to simulate material reuse, CO₂ impact, and policy scenarios.")

# --- INPUTS ---
st.header("Input Parameters")

concrete_recycle_percent = st.slider("Concrete Recycle Percent", 0.0, 1.0, 0.3, 0.05)
soil_reuse_percent = st.slider("Soil Reuse Percent", 0.0, 1.0, 0.2, 0.05)
max_rca_permitted = st.slider("Max RCA Permitted", 0.0, 1.0, 0.3, 0.05)

houses_built_per_year = st.number_input("Houses Built Per Year", value=25000)
houses_demolished_per_year = st.number_input("Houses Demolished Per Year", value=1500)

# --- CONSTANTS ---
concrete_per_house = 50
concrete_per_deconstructed_house = 45
soil_per_deconstructed_house = 15
cement_content_per_tonne = 0.3
emission_cement = 698
emission_aggregate = 9
emission_transport_virgin = 100
emission_transport_recycled = 50
emission_waste_processing = 30
emission_soil = 10

# --- SIMULATION FUNCTION ---
def run_simulation(concrete_recycle, soil_reuse, rca_limit):
    concrete_demand = houses_built_per_year * concrete_per_house
    concrete_deconstruction = houses_demolished_per_year * concrete_per_deconstructed_house
    soil_from_demo = houses_demolished_per_year * soil_per_deconstructed_house

    recycled = concrete_deconstruction * concrete_recycle
    reused_soil = soil_from_demo * soil_reuse

    used_rca = min(recycled, concrete_demand * rca_limit)
    virgin = concrete_demand - used_rca
    virgin_soil = soil_from_demo - reused_soil

    co2_cement = concrete_demand * cement_content_per_tonne * emission_cement
    co2_aggregate = virgin * emission_aggregate
    co2_transport_virgin = virgin * emission_transport_virgin
    co2_transport_recycled = used_rca * emission_transport_recycled
    co2_waste = concrete_deconstruction * emission_waste_processing
    co2_soil = virgin_soil * emission_soil

    co2_total = co2_cement + co2_aggregate + co2_transport_virgin + co2_transport_recycled + co2_waste + co2_soil

    co2_breakdown = {
        "Cement Production": co2_cement,
        "Virgin Aggregate": co2_aggregate,
        "Transport (Virgin)": co2_transport_virgin,
        "Transport (Recycled)": co2_transport_recycled,
        "Waste Processing": co2_waste,
        "Virgin Soil": co2_soil
    }

    return {
        "Total CO2": co2_total,
        "Recycled Concrete": recycled,
        "Virgin Aggregate": virgin,
        "Reused Soil": reused_soil,
        "Virgin Soil": virgin_soil,
        "Sand & Gravel Saved": used_rca,
        "CO2 Breakdown": co2_breakdown
    }

# --- RUN SIMULATION ---
if st.button("Run Simulation"):
    result = run_simulation(concrete_recycle_percent, soil_reuse_percent, max_rca_permitted)

    st.success("Simulation Completed")
    st.metric("Total CO₂ Emissions (kg)", round(result["Total CO2"], 2))
    st.metric("Recycled Concrete (t)", round(result["Recycled Concrete"], 2))
    st.metric("Virgin Aggregate Used (t)", round(result["Virgin Aggregate"], 2))
    st.metric("Reused Soil (t)", round(result["Reused Soil"], 2))
    st.metric("Virgin Soil Used (t)", round(result["Virgin Soil"], 2))
    st.metric("Sand & Gravel Saved (t)", round(result["Sand & Gravel Saved"], 2))

    # CO2 Breakdown Chart
    st.subheader("📊 CO₂ Emissions Breakdown")
    co2_df = pd.DataFrame({
        "Source": list(result["CO2 Breakdown"].keys()),
        "CO2 (kg)": list(result["CO2 Breakdown"].values())
    })
    fig, ax = plt.subplots()
    ax.bar(co2_df["Source"], co2_df["CO2 (kg)"], color='skyblue')
    plt.xticks(rotation=45)
    st.pyplot(fig)

# --- SCENARIO COMPARISON ---
st.header("Scenario Comparison")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Scenario A")
    a_concrete = st.slider("A: Concrete Recycle %", 0.0, 1.0, 0.3, 0.05, key="a1")
    a_soil = st.slider("A: Soil Reuse %", 0.0, 1.0, 0.2, 0.05, key="a2")
    a_rca = st.slider("A: Max RCA Permitted", 0.0, 1.0, 0.3, 0.05, key="a3")

with col2:
    st.subheader("Scenario B")
    b_concrete = st.slider("B: Concrete Recycle %", 0.0, 1.0, 0.6, 0.05, key="b1")
    b_soil = st.slider("B: Soil Reuse %", 0.0, 1.0, 0.3, 0.05, key="b2")
    b_rca = st.slider("B: Max RCA Permitted", 0.0, 1.0, 0.5, 0.05, key="b3")

if st.button("Compare Scenarios"):
    result_a = run_simulation(a_concrete, a_soil, a_rca)
    result_b = run_simulation(b_concrete, b_soil, b_rca)

    df_compare = pd.DataFrame({
        "Metric": ["Total CO2", "Recycled Concrete", "Virgin Aggregate", "Reused Soil", "Virgin Soil", "Sand & Gravel Saved"],
        "Scenario A": [result_a["Total CO2"], result_a["Recycled Concrete"], result_a["Virgin Aggregate"], result_a["Reused Soil"], result_a["Virgin Soil"], result_a["Sand & Gravel Saved"]],
        "Scenario B": [result_b["Total CO2"], result_b["Recycled Concrete"], result_b["Virgin Aggregate"], result_b["Reused Soil"], result_b["Virgin Soil"], result_b["Sand & Gravel Saved"]]
    })

    st.subheader("Comparison Table")
    st.dataframe(df_compare)
    st.bar_chart(df_compare.set_index("Metric"))
