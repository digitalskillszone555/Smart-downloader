import streamlit.components.v1 as components

def show_top_ad():
    """Adsterra 728x90 Banner Ad for the Top of the page."""
    ad_code = """
    <div style="text-align: center;">
        <script type="text/javascript">
            atOptions = {
                'key' : 'b71b21554137cf4d1e4e4d5d9e26fa97',
                'format' : 'iframe',
                'height' : 90,
                'width' : 728,
                'params' : {}
            };
        </script>
        <script type="text/javascript" src="https://www.highperformanceformat.com/b71b21554137cf4d1e4e4d5d9e26fa97/invoke.js"></script>
    </div>
    """
    # height slightly more than 90 to ensure no scrollbar
    components.html(ad_code, height=110)

def show_middle_ad():
    """Placeholder for middle ad - you can add another code here later."""
    pass

def show_bottom_ad():
    """Placeholder for bottom ad - you can add another code here later."""
    pass