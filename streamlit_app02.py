# Save this code as app.py and run it using 'pip install streamlit pandas openpyxl'
import streamlit as st
import pandas as pd
import random

# App Title & Layout
st.set_page_config(page_title="Dynamic Visual Timeline Generator", layout="wide")
st.title("📊 Dynamic Visual Timeline Generator")
st.write("Upload your project Excel sheet, map your custom columns, choose a template, and generate an instant timeline image!")

# 1. Sidebar - Template & Design Selection
st.sidebar.header("🎨 Theme & Template Configuration")
template_style = st.sidebar.selectbox(
    "Choose Timeline Template Style",
    ["Minimalist Corporate (Blues)", "Agile Sprint (Vibrant Multi)", "Warm Executive (Earth Tones)", "Dark Mode Neon"]
)

# Template Color Palettes
PALETTES = {
    "Minimalist Corporate (Blues)": ["#1E3A8A", "#3B82F6", "#60A5FA", "#93C5FD", "#1D4ED8"],
    "Agile Sprint (Vibrant Multi)": ["#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"],
    "Warm Executive (Earth Tones)": ["#78350F", "#B45309", "#D97706", "#F59E0B", "#FBBF24"],
    "Dark Mode Neon": ["#06B6D4", "#10B981", "#3B82F6", "#F43F5E", "#A855F7"]
}
colors = PALETTES[template_style]

# 2. File Upload & Sample Data Generation
uploaded_file = st.file_uploader("Upload your Project Tracking Excel file (.xlsx, .xls)", type=["xlsx", "xls"])

if uploaded_file is None:
    st.info("💡 Pro-Tip: Download our pre-configured sample dataset below to see how it works instantly!")
    
    # Generate a sample DataFrame
    sample_data = {
        "Project Task": ["Kickoff Meeting", "Market Research", "UI/UX Wireframing", "Backend API Setup", "Frontend Integration", "Beta Testing", "Global Launch"],
        "Start Date": ["2026-01-05", "2026-01-12", "2026-02-02", "2026-02-16", "2026-03-09", "2026-04-06", "2026-05-01"],
        "End Date": ["2026-01-08", "2026-01-30", "2026-02-13", "2026-03-06", "2026-04-03", "2026-04-24", "2026-05-05"],
        "Assigned Owner": ["Alice Smith", "Bob Jones", "Charlie Brown", "Dave Miller", "Alice Smith", "Charlie Brown", "Everyone"],
        "Progress Status": ["Completed", "Completed", "In Progress", "In Progress", "Not Started", "Not Started", "Not Started"]
    }
    df = pd.DataFrame(sample_data)
    
    # Create Excel download button for the sample data
    @st.cache_data
    def convert_df(df_to_convert):
        import io
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_to_convert.to_excel(writer, index=False, sheet_name='Sheet1')
        return output.getvalue()
        
    excel_data = convert_df(df)
    st.download_button(
        label="📥 Download Sample Project Excel File",
        data=excel_data,
        file_name="sample_project_tracking.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    df = pd.read_excel(uploaded_file)

# Display Current Data Matrix
st.subheader("📋 Step 1: Review Data Source Matrix")
st.dataframe(df, use_container_width=True)

# 3. Dynamic Column Mapping Interface
st.subheader("⚙️ Step 2: Map Your Custom Excel Columns Dynamically")
st.write("No matter what your columns are named, link them to the system attributes below:")

col1, col2, col3 = st.columns(3)
with col1:
    task_col = st.selectbox("Task Name / Event Description Column", options=df.columns, index=0 if "Project Task" in df.columns else 0)
with col2:
    start_col = st.selectbox("Start Date / Timeline Anchor Column", options=df.columns, index=1 if "Start Date" in df.columns else 0)
with col3:
    status_col = st.selectbox("Status / Label Category Column (Optional)", options=df.columns, index=4 if "Progress Status" in df.columns else 0)

# Process Data Safely
try:
    df_clean = df[[task_col, start_col, status_col]].dropna().copy()
    df_clean[start_col] = df_clean[start_col].astype(str)
except Exception as e:
    st.error(f"Error parsing columns: {e}. Please ensure your selections are correct.")
    st.stop()

# 4. Native SVG Vector Layout Generation
st.subheader("🖼️ Step 3: Generated Visual Vector Timeline (Scalable SVG)")

# SVG Size configurations
canvas_width = 1000
row_height = 110
padding_top = 80
padding_bottom = 50
canvas_height = padding_top + (len(df_clean) * row_height) + padding_bottom

# Dynamic Style Variables Based on Selection
is_dark = "Dark Mode" in template_style
bg_color = "#0F172A" if is_dark else "#FFFFFF"
text_primary = "#F8FAFC" if is_dark else "#1E293B"
text_secondary = "#94A3B8" if is_dark else "#64748B"
axis_line_color = "#334155" if is_dark else "#CBD5E1"

# Assemble SVG String natively without external heavy graphics dependencies
svg_data = f'<svg xmlns="http://w3.org" viewBox="0 0 {canvas_width} {canvas_height}" width="100%" height="100%" style="background-color: {bg_color}; font-family: \'Segoe UI\', system-ui, sans-serif;">'

# Main Visual Canvas Title Card
svg_data += f'<text x="40" y="45" font-size="24" font-weight="bold" fill="{text_primary}">Project Milestone Map &amp; Action Plan Timeline</text>'
svg_data += f'<text x="40" y="65" font-size="12" fill="{text_secondary}">Style Template Active: {template_style}</text>'

# Central Axis Core Backbone Line
axis_x = 220
svg_data += f'<line x1="{axis_x}" y1="{padding_top}" x2="{axis_x}" y2="{canvas_height - padding_bottom}" stroke="{axis_line_color}" stroke-width="4" stroke-linecap="round" />'

# Dynamic Layout Builder Loop
for idx, row in df_clean.reset_index(drop=True).iterrows():
    current_y = padding_top + (idx * row_height) + (row_height / 2)
    node_color = colors[idx % len(colors)]
    
    # Extract row parameters dynamically from user column configurations
    task_label = str(row[task_col]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    date_label = str(row[start_col]).split(" ")[0] # Grab date format neatly
    status_label = str(row[status_col]).replace("&", "&amp;")
    
    # Draw Visual Nodes along the Time Backbone Axis
    svg_data += f'<circle cx="{axis_x}" cy="{current_y}" r="9" fill="{bg_color}" stroke="{node_color}" stroke-width="4" />'
    svg_data += f'<circle cx="{axis_x}" cy="{current_y}" r="4" fill="{node_color}" />'
    
    # Left Column Component: Temporal Milestones Anchor
    svg_data += f'<text x="{axis_x - 30}" y="{current_y + 5}" font-size="14" font-weight="600" fill="{node_color}" text-anchor="end">{date_label}</text>'
    
    # Right Column Component: Visual Descriptive Task Cards
    card_x = axis_x + 30
    card_width = 680
    card_height = 80
    card_bg = "#1E293B" if is_dark else "#F8FAFC"
    card_border = "#475569" if is_dark else "#E2E8F0"
    
    # Render Task Card Enclosure Box
    svg_data += f'<rect x="{card_x}" y="{current_y - card_height/2}" width="{card_width}" height="{card_height}" rx="10" fill="{card_bg}" stroke="{card_border}" stroke-width="1.5" />'
    # Visual accent color ribbon on left border of card
    svg_data += f'<path d="M {card_x} {current_y - card_height/2 + 10} L {card_x} {current_y + card_height/2 - 10}" stroke="{node_color}" stroke-width="5" stroke-linecap="round"/>'
    
    # Inject Text Payload Inside Card
    svg_data += f'<text x="{card_x + 25}" y="{current_y - 8}" font-size="15" font-weight="bold" fill="{text_primary}">{task_label}</text>'
    svg_data += f'<text x="{card_x + 25}" y="{current_y + 18}" font-size="12" fill="{text_secondary}">Stage Metric: </text>'
    
    # Badge Pill Enclosure for Status Metadata 
    badge_x = card_x + 105
    svg_data += f'<rect x="{badge_x}" y="{current_y + 6}" width="95" height="18" rx="9" fill="{node_color}22" />'
    svg_data += f'<text x="{badge_x + 47.5}" y="{current_y + 19}" font-size="11" font-weight="bold" fill="{node_color}" text-anchor="middle">{status_label}</text>'

svg_data += '</svg>'

# 5. Live Responsive Interface Display & High-Fidelity Vector Download Engine
st.write("Your production timeline has been compiled engine-side. See your interactive rendering asset below:")
st.components.v1.html(svg_data, height=canvas_height, scrolling=True)

st.subheader("💾 Step 4: Export Visual Layout Asset")
st.download_button(
    label="📥 Download High-Resolution Vector Timeline (SVG)",
    data=svg_data,
    file_name="production_timeline_layout.svg",
    mime="image/svg+xml"
)

st.success("🎉 Asset Build Complete! Adjust configuration inputs or switch theme palettes on the fly inside the sidebar workspace menu.")
