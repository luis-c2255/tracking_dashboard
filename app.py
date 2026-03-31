import streamlit as st # type: ignore
import pandas as pd # type: ignore
from datetime import datetime, timedelta
import plotly.express as px # type: ignore
from storage import load_state, save_state

# Configuration & constants
STEPS = {
    0: "Not Started", 
    1: "Cleaning", 
    2: "Processing", 
    3: "Visualizations", 
    4: "Findings", 
    5: "Complete"
}
STEP_COLORS = {
    0: "#B4B2A9",
    1: "#378ADD",
    2: "#1D9E75",
    3: "#BA7517", 
    4: "#D4537E",
    5: "#940C0C"
}

DATASETS = [
        "Supply Chain Data", "Global Suicide Rates 2000-2021", "Amazon Sales Dataset",
        "Global Volcano Eruption", "Global Movie Trends", "Online Shoppers Purchasing",
        "Netflix Content Analysis", "Pypi Ai Packages Download", "Global Population 1950-2024",
        "Amazon Sales Analysis", "Hospital Patient Readmission", "Mental Health Burnout",
        "Spotify Wrapped 2025", "Spam Email Detection"
        ]
loaded_df, loaded_start = load_state()

# Initialize Session State
if 'df' not in st.session_state:
    st.session_state.df = loaded_df if loaded_df is not None else pd.DataFrame({
        "Dataset": DATASETS,
        "Days": [3] * len(DATASETS),
        "Progress": [0] * len(DATASETS),
        "Order": list(range(len(DATASETS)))
        })
if 'start_date' not in st.session_state:
    st.session_state.start_date = loaded_start if loaded_start else datetime.now().date()

# Functions
def cycle_step(idx):
    st.session_state.df.at[idx, "Progress"] = (st.session_state.df.at[idx, "Progress"] + 1) % 5

# UI Layout
st.set_page_config(page_title="Dataset Analysis Schedule", layout="wide")

st.title("📆 :rainbow[ Dataset Analysis Schedule]", text_alignment="center")
st.caption("14 datasets - 1 analyst - Adjust days and progress below")

# Metric Row
total_days = st.session_state.df["Days"].sum()
project_end = st.session_state.start_date + timedelta(days=int(total_days))
completed = len(st.session_state.df[st.session_state.df["Progress"] == 4])
in_progress = len(st.session_state.df[(st.session_state.df["Progress"] > 0) & (st.session_state.df["Progress"] < 4)])

m1, m2, m3, m4 = st.columns(4)
m1.metric(":blue[Total Days]", total_days, border=True)
m2.metric(":red[End Date]", project_end.strftime("%d %b"), border=True)
m3.metric(":green[Completed]", f"{completed} / 14", border=True)
m4.metric(":yellow[In Progress]", in_progress, border=True)

# Sidebar / Controls
with st.expander("Schedule Settings", expanded=True):
    col_date, col_legend = st.columns([1, 2])
    st.session_state.start_date = col_date.date_input("Start Date", st.session_state.start_date)
    save_state(st.session_state.df, st.session_state.start_date)

    # Legend
    legend_html = "".join([f'<span style="color:{STEP_COLORS[k]}; margin-right:15px;"> {v}</span>' for k, v in STEPS.items()])
    col_legend.markdown(f"<div style='margin-top:35px; font-size:18px; text-align:center;'>{legend_html}</div>", unsafe_allow_html=True)

# Data Editor (Replaces the Drag-and-Drop)
st.subheader(":rainbow[Dataset Queue]", divider="rainbow")
edited_df = st.data_editor(
        st.session_state.df.sort_values("Order"),
        column_config={
            "Order": st.column_config.NumberColumn("Sort Order", help="Change numbers to reorder tasks"),
            "Days": st.column_config.NumberColumn("Duration", min_value=2, max_value=5),
            "Progress": st.column_config.ProgressColumn("Step Progress", min_value=0, max_value=4),
            "Dataset": st.column_config.TextColumn(disabled=True)
            },
        hide_index=True,
        width="stretch"
        )
st.session_state.df = edited_df
save_state(st.session_state.df, st.session_state.start_date)

# Calculate Timeline
schedule_data = []
cursor = st.session_state.start_date
for _, row in edited_df.sort_values("Order").iterrows():
    start = cursor
    end = start + timedelta(days=row['Days'] - 1)
    schedule_data.append({
        "Task": row['Dataset'],
        "Start": start,
        "End": end,
        "Steps Completed": STEPS[row['Progress']],
        "Color": STEP_COLORS[row['Progress']]
        })
    cursor = end + timedelta(days=1)

st.subheader(":rainbow[Datasets]", divider="rainbow")
# Gantt Chart Visualization
df_plot = pd.DataFrame(schedule_data)
fig = px.timeline(
        df_plot,
        x_start="Start",
        x_end="End",
        y="Task",
        color="Steps Completed",
        color_discrete_map={v: STEP_COLORS[k] for k, v in STEPS.items()},
        hover_data=["Start", "End"]
        )
fig.update_yaxes(autorange="reversed", tickfont=dict(size=14))
fig.update_layout(height=700, margin=dict(t=0, b=0, l=0, r=0), legend=dict(font=dict(size=15)))
st.plotly_chart(fig, width="stretch")

# Detail Panel
st.divider()
st.subheader(":rainbow[Manage Selected Dataset]", divider="rainbow")
selected_name = st.selectbox("Select a dataset to update steps:", DATASETS)
selected_idx = st.session_state.df[st.session_state.df["Dataset"] == selected_name].index[0]
current_prog = st.session_state.df.at[selected_idx, "Progress"]

current_step_name = STEPS[current_prog]
c1, c2 = st.columns([1, 3])
with c1:
    st.button(f"Cycle Step  (Currently: {current_step_name})",
              on_click=cycle_step, args=(selected_idx,))
with c2:
    if current_prog == 4:
        st.success("This dataset is fully complete!")
    elif current_prog > 0:
        st.info(f"Working on: **{current_step_name}**")
    else:
        st.warning("Not started yet. Click the button to begin!")
