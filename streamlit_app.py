import streamlit as st
import pandas as pd
import base64

# Set up clean, wide layout
st.set_page_config(page_title="Visual Task & Timeline Planner", layout="wide")

# Helper function to generate safe, clickable download buttons
def get_svg_download_link(svg_string, filename="template.svg"):
    b64 = base64.b64encode(svg_string.encode('utf-8')).decode()
    return f'<a href="data:image/svg+xml;base64,{b64}" download="{filename}" style="text-decoration:none;"><button style="background-color:#4CAF50; color:white; padding:10px 20px; border:none; border-radius:4px; cursor:pointer; font-weight:bold; margin-top:15px;">📥 Download SVG Vector File</button></a>'

# Helper function to guarantee safe browser rendering of raw SVG strings
def render_svg(svg_code, height=500):
    html_wrapper = f"""
    <div style="width:100%; overflow-x:auto; background-color:transparent; padding:10px; border:1px dashed #E2E8F0; border-radius:8px;">
        {svg_code}
    </div>
    """
    st.components.v1.html(html_wrapper, height=height, scrolling=True)

# --- NAVIGATION SIDEBAR ---
st.sidebar.title("🛠️ Tools Dashboard")
app_mode = st.sidebar.radio("Select Tool Mode", ["Timeline Generator", "Eisenhower Matrix Generator"])

# ==============================================================================
# MODE 1: TIMELINE GENERATOR
# ==============================================================================
if app_mode == "Timeline Generator":
    st.title("⏳ Advanced SVG Timeline Generator")
    st.markdown("Upload data spreadsheets, choose layout templates, and customize your visual timeline graphics.")

    st.subheader("1. Data Input Source")
    
    # Default sample data template
    sample_df = pd.DataFrame({
        "Period": ["2020", "2021", "2023", "2026", "2030"],
        "Milestone": ["Foundation", "First Product", "Market Leader", "Strategic Alliance", "Tenth Anniversary"],
        "Description": [
            "Company founded by a group of visionary entrepreneurs.",
            "Launch of its first project management software application.",
            "Acquisition of a competing firm, cementing market dominance.",
            "Strategic alliance with an AI sector technology giant.",
            "Celebrating a decade of global tech innovation."
        ]
    })
    
    use_sample = st.checkbox("💡 Use Sample Data (Quick Demo)", value=True)
    uploaded_file = st.file_uploader("Or upload your own data spreadsheet (CSV or Excel)", type=["csv", "xlsx"])
    
    df = None
    if use_sample:
        df = sample_df
    elif uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.success("File loaded successfully!")
        except Exception as e:
            st.error(f"Error parsing file columns: {e}")

    if df is not None:
        st.write("### Preview Data Table:", df)
        
        col_setup_1, col_setup_2 = st.columns(2)
        with col_setup_1:
            template_style = st.selectbox(
                "🎨 Select Timeline Layout Style",
                ["Vertical Step List (History style)", "Horizontal Zig-Zag Alternating", "Gantt Flat Block Tracking"]
            )
            accent_color = st.color_picker("Pick Main Brand Accent Color", "#10B981")
            bg_color = st.color_picker("Pick Canvas Background Color", "#FFFFFF")
            
        with col_setup_2:
            st.markdown("**Map Data Columns to Visual Elements**")
            time_col = st.selectbox("Select Time / Period Column", df.columns, index=0)
            title_col = st.selectbox("Select Milestone Title Column", df.columns, index=1)
            desc_col = st.selectbox("Select Detailed Description Column", df.columns, index=2)

        # Build dynamic clean text structures
        timeline_data = []
        for _, row in df.iterrows():
            timeline_data.append({
                "time": str(row[time_col]),
                "title": str(row[title_col]),
                "desc": str(row[desc_col])
            })

        # SVG Generator Engine
        def generate_custom_timeline(data, style, accent, bg):
            num_items = len(data)
            if num_items == 0:
                return '<svg width="100" height="50"><text y="20">Empty Matrix</text></svg>'
            
            # Template A: Vertical Step List
            if style == "Vertical Step List (History style)":
                svg_w, svg_h = 1000, 150 + (num_items * 130)
                svg = f'<svg xmlns="http://w3.org" viewBox="0 0 {svg_w} {svg_h}" width="100%" height="{svg_h}" style="background-color:{bg}; font-family:\'Segoe UI\', sans-serif;">'
                svg += f'<text x="500" y="50" font-size="26" font-weight="bold" fill="#111827" text-anchor="middle">COMPANY TIMELINE HISTORY</text>'
                line_x = 450
                svg += f'<line x1="{line_x}" y1="100" x2="{line_x}" y2="{svg_h - 60}" stroke="{accent}" stroke-width="4" stroke-dasharray="6 4" />'
                
                for i, item in enumerate(data):
                    item_y = 140 + (i * 130)
                    svg += f'<circle cx="{line_x}" cy="{item_y}" r="20" fill="{bg}" stroke="{accent}" stroke-width="4"/>'
                    svg += f'<text x="{line_x}" y="{item_y+6}" font-size="15" font-weight="bold" fill="{accent}" text-anchor="middle">{i+1}</text>'
                    
                    # Left Tags
                    svg += f'<rect x="230" y="{item_y-25}" width="180" height="36" rx="6" fill="{accent}15" />'
                    svg += f'<text x="400" y="{item_y-2}" font-size="15" font-weight="bold" fill="{accent}" text-anchor="end">{item["time"]}</text>'
                    svg += f'<text x="400" y="{item_y+18}" font-size="12" font-weight="600" fill="#4B5563" text-anchor="end">{item["title"]}</text>'
                    
                    # Right Descriptions
                    svg += f'<text x="495" y="{item_y+5}" font-size="14" font-weight="bold" fill="#111827">{item["desc"][:65]}</text>'
                    if len(item["desc"]) > 65:
                        svg += f'<text x="495" y="{item_y+24}" font-size="13" fill="#4B5563">{item["desc"][65:130]}</text>'
                svg += '</svg>'
                return svg

            # Template B: Horizontal Zig-Zag Alternating
            elif style == "Horizontal Zig-Zag Alternating":
                svg_w, svg_h = 1200, 450
                spacing = (svg_w - 180) / max((num_items - 1), 1)
                svg = f'<svg xmlns="http://w3.org" viewBox="0 0 {svg_w} {svg_h}" width="100%" height="{svg_h}" style="background-color:{bg}; font-family:\'Segoe UI\', sans-serif;">'
                svg += f'<line x1="80" y1="225" x2="{svg_w - 80}" y2="225" stroke="{accent}" stroke-width="6" stroke-linecap="round"/>'
                
                for i, item in enumerate(data):
                    cx = 90 + (i * spacing)
                    is_top = (i % 2 == 0)
                    svg += f'<circle cx="{cx}" cy="225" r="14" fill="#FFFFFF" stroke="{accent}" stroke-width="4"/>'
                    svg += f'<circle cx="{cx}" cy="225" r="6" fill="{accent}"/>'
                    
                    y_end = 145 if is_top else 305
                    svg += f'<line x1="{cx}" y1="225" x2="{cx}" y2="{y_end}" stroke="{accent}" stroke-width="2" stroke-dasharray="4 4"/>'
                    
                    box_y = 45 if is_top else 315
                    svg += f'<rect x="{cx-90}" y="{box_y}" width="180" height="90" rx="8" fill="#F9FAFB" stroke="#E5E7EB" stroke-width="1"/>'
                    svg += f'<rect x="{cx-90}" y="{box_y}" width="180" height="26" rx="8" fill="{accent}"/>'
                    svg += f'<text x="{cx}" y="{box_y+18}" font-size="12" font-weight="bold" fill="#FFFFFF" text-anchor="middle">{item["time"]}</text>'
                    svg += f'<text x="{cx}" y="{box_y+46}" font-size="12" font-weight="bold" fill="#111827" text-anchor="middle">{item["title"][:22]}</text>'
                    svg += f'<text x="{cx}" y="{box_y+68}" font-size="10" fill="#6B7280" text-anchor="middle">{item["desc"][:28]}</text>'
                svg += '</svg>'
                return svg

            # Template C: Gantt Flat Block Tracking
            else:
                svg_w, svg_h = 1100, 160 + (num_items * 70)
                svg = f'<svg xmlns="http://w3.org" viewBox="0 0 {svg_w} {svg_h}" width="100%" height="{svg_h}" style="background-color:{bg}; font-family:\'Segoe UI\', sans-serif;">'
                for col_i in range(5):
                    grid_x = 320 + (col_i * 180)
                    svg += f'<line x1="{grid_x}" y1="80" x2="{grid_x}" y2="{svg_h - 40}" stroke="#E5E7EB" stroke-width="1"/>'
                    svg += f'<text x="{grid_x}" y="95" font-size="11" font-weight="600" fill="#9CA3AF" text-anchor="middle">PHASE 0{col_i+1}</text>'
                for i, item in enumerate(data):
                    row_y = 120 + (i * 70)
                    block_x = 320 + (i * 100)
                    svg += f'<text x="40" y="{row_y+20}" font-size="14" font-weight="bold" fill="#111827">{item["time"]} — {item["title"]}</text>'
                    svg += f'<rect x="{block_x}" y="{row_y}" width="300" height="34" rx="17" fill="{accent}" opacity="0.9"/>'
                    svg += f'<text x="{block_x + 20}" y="{row_y+21}" font-size="12" font-weight="bold" fill="#FFFFFF">{item["desc"][:40]}</text>'
                svg += '</svg>'
                return svg

        # Display outputs
        generated_timeline_svg = generate_custom_timeline(timeline_data, template_style, accent_color, bg_color)
        
        st.subheader("🖼️ Live Render Preview")
        render_svg(generated_timeline_svg, height=550)
        st.markdown(get_svg_download_link(generated_timeline_svg, "custom_timeline.svg"), unsafe_allow_html=True)

