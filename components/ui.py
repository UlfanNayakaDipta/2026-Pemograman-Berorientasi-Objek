"""Global CSS styling and shared UI helpers for CoreDoc."""

import streamlit as st

# ── CSS — single minified block per theme ──
_CSS_DARK = """:root{--cd-bg:#0b1120;--cd-header-bg:rgba(15,23,42,0.95);--cd-card-bg:rgba(30,41,59,0.7);--cd-text:#e2e8f0;--cd-text-soft:#94a3b8;--cd-border:rgba(51,65,85,0.5);--cd-upload-bg:rgba(15,23,42,0.5);--cd-textarea-bg:rgba(15,23,42,0.5)}"""
_CSS_LIGHT = """:root{--cd-bg:#f8fafc;--cd-header-bg:rgba(255,255,255,0.92);--cd-card-bg:rgba(241,245,249,0.9);--cd-text:#0f172a;--cd-text-soft:#334155;--cd-border:rgba(203,213,225,0.7);--cd-upload-bg:rgba(255,255,255,0.7);--cd-textarea-bg:rgba(255,255,255,0.7)}"""
_CSS_COMMON = """.stApp{background:radial-gradient(circle at top left,rgba(56,189,248,0.08),transparent 30%),radial-gradient(circle at bottom right,rgba(148,163,184,0.08),transparent 28%),var(--cd-bg)}.stMainMenu{display:none}header[data-testid="stHeader"]{background:var(--cd-header-bg)!important;backdrop-filter:blur(12px);border-bottom:1px solid var(--cd-border)!important}[data-testid="stAppDeployButton"]{display:none!important}.st-emotion-cache-1gh7gps{font-size:.875rem;font-weight:500}.st-emotion-cache-1gh7gps[aria-current="page"]{color:#06b4d4;font-weight:600}.card{border:1px solid var(--cd-border);background:var(--cd-card-bg);padding:1.5rem;transition:border-color .2s}.card:hover{border-color:rgba(148,163,184,0.5)}.phase-label{font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:.35em;color:var(--cd-text-soft)!important;margin-bottom:.5rem}.badge{display:inline-flex;align-items:center;padding:.125rem .625rem;font-size:.75rem;font-weight:600;border-radius:.375rem;border:1px solid}.badge-cyan, .badge-cyan *{color:#06b4d4!important;border-color:rgba(6,182,212,0.3)}.badge-emerald, .badge-emerald *{color:#10b981!important;border-color:rgba(16,185,129,0.3)}.badge-purple, .badge-purple *{color:#a855f7!important;border-color:rgba(168,85,247,0.3)}.stButton>button{border:1px solid #06b4d4!important;background:#06b4d4!important;color:#0b1120!important;font-weight:600;font-size:.875rem;border-radius:0!important;transition:background .2s}.stButton>button *{color:#0b1120!important}.stButton>button:hover{background:#05a3c0!important;border-color:#05a3c0!important;color:#0b1120!important}.stButton>button:disabled{opacity:.5;cursor:not-allowed}.stDownloadButton>button{border:1px solid #10b981!important;background:#10b981!important;color:#0b1120!important;font-weight:600;border-radius:0!important}.stDownloadButton>button *{color:#0b1120!important}.stDownloadButton>button:hover{background:#059669!important;border-color:#059669!important}[data-testid="stFileUploader"]{border:1px solid var(--cd-border);background:var(--cd-upload-bg);padding:.75rem}[data-testid="stFileUploaderDropzone"] button{border:1px solid #06b4d4!important;background:#06b4d4!important;color:#0b1120!important;font-weight:600!important;border-radius:0!important;transition:background .2s}[data-testid="stFileUploaderDropzone"] button *{color:#0b1120!important}[data-testid="stFileUploaderDropzone"] button:hover{background:#05a3c0!important;border-color:#05a3c0!important}.stTextArea textarea{font-family:"JetBrains Mono","Fira Code",monospace;font-size:.875rem;background:var(--cd-textarea-bg)!important;border:1px solid var(--cd-border)!important;color:var(--cd-text)!important}.stAlert{border-radius:0;border-left:3px solid}[data-testid="stDataFrameContainer"]{border:1px solid var(--cd-border)}.stApp, .stApp [data-testid="stMarkdownContainer"] *, .stApp [data-testid="stText"] *, .stApp label *, .stApp .stRadio *{color:var(--cd-text)!important}"""




def apply_global_style(light: bool = False) -> None:
    """Inject global CSS with theme variables."""
    vars_ = _CSS_LIGHT if light else _CSS_DARK
    st.markdown(f"<style>{vars_}{_CSS_COMMON}.stFileUploaderDropzoneInstructions>div>span{{color:var(--cd-text)!important;font-weight:600}}.stFileUploaderDropzoneInstructions small{{color:var(--cd-text-soft)!important}}</style>", unsafe_allow_html=True)



_JS_INJECT = """
<script>
const parentDoc = window.parent.document;

// 1) Inject font import
if (!parentDoc.getElementById('coredoc-fonts')) {
    const fontLink = parentDoc.createElement('link');
    fontLink.id = 'coredoc-fonts';
    fontLink.rel = 'stylesheet';
    fontLink.href = 'https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap';
    parentDoc.head.appendChild(fontLink);
}

// 2) Move Theme button
setTimeout(() => {
    parentDoc.querySelectorAll('button').forEach(b => {
        if(b.innerText.includes('☀️') || b.innerText.includes('🌙') || b.innerText.includes('\u2600') || b.innerText.includes('\U0001f319')) {
            let el = b.closest('.element-container');
            if(el) {
                const header = parentDoc.querySelector('[data-testid="stHeader"]');
                if (header && !parentDoc.getElementById('cd-theme-container')) {
                    const container = parentDoc.createElement('div');
                    container.id = 'cd-theme-container';
                    container.style.marginLeft = 'auto';
                    container.style.marginRight = '1rem';
                    container.style.display = 'flex';
                    container.style.alignItems = 'center';
                    header.appendChild(container);
                    container.appendChild(el);
                    
                    b.style.width = '38px';
                    b.style.minWidth = '38px';
                    b.style.height = '38px';
                    b.style.padding = '0';
                    b.style.borderRadius = '8px';
                    b.style.border = '1px solid var(--cd-border)';
                    b.style.background = 'var(--cd-header-bg)';
                    b.style.display = 'flex';
                    b.style.alignItems = 'center';
                    b.style.justifyContent = 'center';
                    
                    const p = b.querySelector('p');
                    if(p) {
                        p.style.margin = '0';
                        p.style.fontSize = '1.2rem';
                    }
                }
            }
        }
    });
}, 100);

// 3) Anti-Spam (Debounce) for all buttons
if (!parentDoc.getElementById('cd-anti-spam')) {
    const scriptTag = parentDoc.createElement('script');
    scriptTag.id = 'cd-anti-spam';
    scriptTag.type = 'text/javascript';
    scriptTag.text = `
        document.addEventListener('click', function(e) {
            let btn = e.target.closest('button');
            if (btn && !btn.innerText.includes('☀️') && !btn.innerText.includes('🌙') && !btn.getAttribute('aria-expanded')) {
                let origEvents = btn.style.pointerEvents || '';
                let origOpacity = btn.style.opacity || '';
                btn.style.pointerEvents = 'none';
                btn.style.opacity = '0.5';
                setTimeout(() => {
                    btn.style.pointerEvents = origEvents;
                    btn.style.opacity = origOpacity;
                }, 1500);
            }
        });
    `;
    parentDoc.head.appendChild(scriptTag);
}
</script>
"""

def theme_toggle_widget() -> None:
    """Brand label + theme toggle button, both fixed-overlay on the header.

    Must be called from every page **before other visible elements**.
    """
    if "cd_theme" not in st.session_state:
        from config import STORAGE_DIR
        theme_file = STORAGE_DIR / ".theme"
        theme = "light"
        if theme_file.exists():
            try:
                theme = theme_file.read_text().strip()
            except Exception:
                pass
        if theme not in ["light", "dark"]:
            theme = "light"
        st.session_state.cd_theme = theme

    theme = st.session_state.cd_theme
    label = "\u2600\ufe0f" if theme == "dark" else "\U0001f319"  # ☀️ / 🌙

    def _toggle():
        cur = st.session_state.cd_theme
        new_theme = "light" if cur == "dark" else "dark"
        st.session_state.cd_theme = new_theme
        
        from config import STORAGE_DIR
        try:
            (STORAGE_DIR / ".theme").write_text(new_theme)
        except Exception:
            pass

    
    # Theme toggle button
    st.button(label, key="theme_toggle_header", on_click=_toggle)
    
    import streamlit.components.v1 as components
    components.html(_JS_INJECT, height=0, width=0)

    


def inject_theme_control() -> None:
    """No-op — use ``theme_toggle_widget()``."""
    pass


def section_header(title: str, subtitle: str | None = None) -> None:
    st.markdown(f'<p class="phase-label">{title}</p>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(
            f'<p style="font-size: 0.875rem; color: var(--cd-text-soft, #94a3b8); line-height: 1.5;">{subtitle}</p>',
            unsafe_allow_html=True,
        )


def spacer(height: str = "1.5rem") -> None:
    st.markdown(f'<div style="height: {height}"></div>', unsafe_allow_html=True)
