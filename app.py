import streamlit as st
from typing import Union

ARMOR_FACTOR = {
    "None": 0,
    "Light": 1,
    "Heavy": 3
}

BODY_AREA_BASE_COST = {
    "Torso": 6,
    "Limb": 3,
    "Head": 2
}

def compute_cost_for_body_area(body_area: str, armor_type: Union[str, None]) -> int:
    if armor_type is None:
        return 0
    return BODY_AREA_BASE_COST[body_area] * ARMOR_FACTOR[armor_type]

def convert_currency(sc: int) -> tuple[int, int]:
    return divmod(sc, 20)

st.title("Olde World Armor Upkeep Calculator")

st.write("This is a simple calculator to help you determine the cost of maintaining your armor in the Olde World game.")
st.write("For each body area, select the armor type.")

armor_cost = 0

x = st.selectbox("Torso", ["None", "Light", "Heavy"])
armor_cost += compute_cost_for_body_area("Torso", x)

x = st.selectbox("Left Arm", ["None", "Light", "Heavy"])  
armor_cost += compute_cost_for_body_area("Limb", x)

x = st.selectbox("Right Arm", ["None", "Light", "Heavy"])
armor_cost += compute_cost_for_body_area("Limb", x)

x = st.selectbox("Left Leg", ["None", "Light", "Heavy"])
armor_cost += compute_cost_for_body_area("Limb", x)

x = st.selectbox("Right Leg", ["None", "Light", "Heavy"])
armor_cost += compute_cost_for_body_area("Limb", x)

x = st.selectbox("Head", ["None", "Light", "Heavy"])
armor_cost += compute_cost_for_body_area("Head", x)

gc, sc = convert_currency(armor_cost)

st.header(f"The total cost of maintaining your armor is {gc} gc and {sc} sc.")
