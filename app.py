import streamlit as st
import validators
from engine import download_video, download_audio, download_image, ensure_latest_engine, check_ffmpeg
from ads import show_top_ad, show_middle_ad, show_bottom_ad

# Initialize Production Ready Settings
st.set_page_config(
    page_title="Ultimate Downloader Pro",
    page_icon="⚡",
    layout="centered",
)

# Silently ensure the engine is up to date (cached for 24h)
ensure_latest_engine()

def inject_premium_dark_theme() -> None:
    """Original Premium Dark / Glassmorphism theme with high-end aesthetics."""
    st.markdown(
        """
        <style>
        .stApp {
            background: radial-gradient(circle at top left, #020617 0, #020617 40%, #020617 100%);
            color: #e5e7eb;
        }
        .block-container {
            max-width: 720px;
            padding-top: 1rem;
            padding-bottom: 2rem;
        }
        .sd-card {
            background: radial-gradient(circle at top left, rgba(15,23,42,0.96), rgba(15,23,42,0.98));
            border-radius: 1.6rem;
            padding: 1.7rem 1.5rem 1.4rem 1.5rem;
            box-shadow:
                0 24px 60px rgba(15,23,42,0.95),
                0 0 0 1px rgba(15,23,42,0.9);
            border: 1px solid rgba(148,163,184,0.45);
            backdrop-filter: blur(18px);
            margin-bottom: 1rem;
        }
        .sd-card h1, .sd-card h2, .sd-card h3, .sd-card label {
            color: #e5e7eb;
        }
        div.stButton > button {
            width: 100%;
            border-radius: 999px;
            background: linear-gradient(135deg, #38bdf8, #0ea5e9);
            color: #020617;
            font-weight: 700;
            border: none;
            padding: 0.85rem 1.4rem;
            box-shadow: 0 15px 30px rgba(14, 165, 233, 0.35);
            transition: all 0.3s ease;
        }
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 20px 40px rgba(14, 165, 233, 0.55);
            filter: brightness(1.1);
        }
        .stTextInput > div > div > input {
            background-color: rgba(15,23,42,0.98) !important;
            border-radius: 0.9rem !important;
            border: 1px solid rgba(55,65,81,0.9) !important;
            color: #e5e7eb !important;
        }
        .stTextInput > div > div > input:focus {
            border-color: #38bdf8 !important;
            box-shadow: 0 0 0 1px rgba(56,189,248,0.6) !important;
        }
        .stSelectbox > div > div {
            border-radius: 0.9rem !important;
            background-color: rgba(15,23,42,0.98) !important;
            border: 1px solid rgba(55,65,81,0.9) !important;
            color: #e5e7eb !important;
        }
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #38bdf8, #22c55e) !important;
        }
        .success-box {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid #10b981;
            border-radius: 0.8rem;
            padding: 1rem;
            margin-top: 1rem;
        }
        .warning-box {
            background: rgba(245, 158, 11, 0.1);
            border: 1px solid #f59e0b;
            border-radius: 0.8rem;
            padding: 0.8rem;
            margin-bottom: 1rem;
            font-size: 0.85rem;
        }
        .error-box {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid #ef4444;
            border-radius: 0.8rem;
            padding: 1rem;
            margin-top: 1rem;
            color: #fca5a5;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def main() -> None:
    inject_premium_dark_theme()
    
    # Monetization: Top Placement
    show_top_ad()

    st.title("⚡ Ultimate Downloader Pro")
    st.caption("Auto-Updating Engine • 4K Video • MP3 Audio • HQ Photos")

    # Global Environmental Audit
    has_ffmpeg = check_ffmpeg()
    if not has_ffmpeg:
        st.markdown("""
            <div class="warning-box">
                ⚠️ <b>Environmental Alert:</b> ffmpeg is missing on the server. 4K Video Merging and MP3 extraction might be limited.
            </div>
        """, unsafe_allow_html=True)

    if "selected_url" not in st.session_state:
        st.session_state.selected_url = ""
    if "options_ready" not in st.session_state:
        st.session_state.options_ready = False

    with st.container():
        st.markdown('<div class="sd-card">', unsafe_allow_html=True)

        url_input = st.text_input(
            "Paste Media URL Here",
            value=st.session_state.selected_url,
            placeholder="YouTube, Instagram, TikTok, Facebook, etc.",
        )

        if st.button("🔍 Analyze Media", type="primary"):
            if url_input and validators.url(url_input):
                st.session_state.selected_url = url_input.strip()
                st.session_state.options_ready = True
            elif url_input:
                st.warning("Please enter a valid URL.")

        # Monetization: Middle Placement (Native)
        show_middle_ad()

        if st.session_state.options_ready and st.session_state.selected_url:
            st.write("Ready to Download:")
            st.code(st.session_state.selected_url, language="text")

            col1, col2 = st.columns(2)
            with col1:
                kind = st.radio("Media Type", ["Video", "Audio", "Photo"], horizontal=True)
            with col2:
                if kind == "Video":
                    quality = st.selectbox(
                        "Resolution",
                        ["4K (2160p)", "2K (1440p)", "1080p", "720p", "480p", "360p"],
                        index=2,
                    )
                elif kind == "Audio":
                    quality = st.selectbox(
                        "Bitrate",
                        ["320kbps (Best)", "256kbps", "128kbps"],
                        index=0,
                    )
                else:
                    quality = "Original"

            if st.button("🚀 Execute Powerful Download"):
                progress_bar = st.progress(0.0)
                status_text = st.empty()

                def yt_dlp_hook(d):
                    if d.get("status") == "downloading":
                        p = d.get("_percent_str", "0%").replace("%", "")
                        try:
                            val = float(p) / 100.0
                            progress_bar.progress(val)
                            status_text.text(f"Processing... {d.get('_percent_str')} • {d.get('_speed_str')}")
                        except: pass
                    elif d.get("status") == "finished":
                        progress_bar.progress(1.0)
                        status_text.text("Merging streams and finalizing container...")

                try:
                    with st.spinner("Bypassing security and powering up the engine..."):
                        if kind == "Photo":
                            file_path = download_image(st.session_state.selected_url, progress_callback=progress_bar.progress)
                        elif kind == "Video":
                            if not has_ffmpeg and "p" in quality and int(quality.split('p')[0].split('(')[-1]) > 720:
                                st.warning("Notice: Downloading without ffmpeg may result in lower resolution.")
                            file_path = download_video(st.session_state.selected_url, quality, progress_hook=yt_dlp_hook)
                        else:
                            file_path = download_audio(st.session_state.selected_url, quality, progress_hook=yt_dlp_hook)
                    
                    st.balloons()
                    st.markdown(f"""
                        <div class="success-box">
                            <span style="color: #10b981; font-weight: bold;">✅ DOWNLOAD COMPLETE</span><br/>
                            <span style="font-size: 0.9rem;">File saved successfully! Ready to play.</span><br/>
                            <code style="color: #e5e7eb; font-size: 0.8rem;">Path: {file_path}</code>
                        </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    error_msg = str(e).lower()
                    
                    # Smart Error Handling Logic
                    if "ffmpeg" in error_msg:
                        st.markdown('<div class="error-box">⚙️ <b>Engine Error:</b> FFmpeg is required for this specific high-quality format. Try a lower resolution.</div>', unsafe_allow_html=True)
                    elif "403" in error_msg or "forbidden" in error_msg:
                        st.markdown('<div class="error-box">🛡️ <b>Security Block:</b> YouTube temporarily blocked the request. Our rotating engine is refreshing. Please try again in a few seconds!</div>', unsafe_allow_html=True)
                    elif "sign in" in error_msg or "private" in error_msg:
                        st.markdown('<div class="error-box">🔒 <b>Private Video:</b> This media requires a login or is age-restricted and cannot be downloaded publicly.</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="error-box">❌ <b>Execution Error:</b> Something went wrong.<br><small>{str(e)}</small></div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Monetization: Bottom Placement
    show_bottom_ad()
    
    st.markdown("<br/>", unsafe_allow_html=True)
    st.caption("Public Content Only • Family Friendly • Powered by Smart Downloader Engine")

if __name__ == "__main__":
    main()
