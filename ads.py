import streamlit.components.v1 as components

def _ad_template(label: str, height: int = 90):
    """Responsive dark-themed ad placeholder."""
    return f"""
    <div style="
        text-align: center;
        padding: 15px;
        margin: 10px 0;
        background: rgba(15, 23, 42, 0.6);
        border: 1px dashed #334155;
        border-radius: 12px;
        color: #64748b;
        font-family: sans-serif;
        font-size: 13px;
        transition: border 0.3s ease;
    " onmouseover="this.style.borderColor='#38bdf8'" onmouseout="this.style.borderColor='#334155'">
        <div style="font-weight: 600; margin-bottom: 4px;">{label}</div>
        <div style="font-size: 11px; opacity: 0.8;">Adsterra / AdSense / PropellerAds Placeholder</div>
        <!-- Paste your script tags below this line -->
    </div>
    """

def show_top_ad():
    components.html(_ad_template("TOP BANNER AD"), height=110)

def show_middle_ad():
    components.html(_ad_template("NATIVE MIDDLE AD", height=100), height=120)

def show_bottom_ad():
    components.html(_ad_template("BOTTOM STICKY AD"), height=110)
