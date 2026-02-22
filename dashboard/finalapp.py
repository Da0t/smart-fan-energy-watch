import streamlit as st
import pandas as pd
from supabase import create_client, Client
import datetime
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Smart Fan Energy Watch", layout="wide")
st.title("Smart Fan Energy Watch")

# Connect to Supabase
SUPABASE_URL = st.secrets["https://fmhxjiqadxdlmalscvoc.supabase.co"]
SUPABASE_KEY = st.secrets["sb_publishable_QIs5RteU49_YkZ35JoEfRQ_T2UHVhV_"]

d