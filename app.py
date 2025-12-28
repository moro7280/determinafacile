"""
DETERMINAFACILE - Piattaforma Nazionale
Generatore Universale di Determine di Affidamento Diretto (D.Lgs 36/2023)
Versione: 3.2 (Fix Bordi Input)
"""

import streamlit as st
from datetime import datetime, date
from decimal import Decimal
import io
import time

# Integrazione OpenAI
from openai import OpenAI

# Import moduli locali
from logic_engine import (
    genera_testo_completo, 
    valida_dati, 
    calcola_importi, 
    formatta_importo,
    formatta_data
)
from document_generator import esporta_determina_rtf


# =============================================================================
# CONFIGURAZIONE API KEY (AI)
# =============================================================================

try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except (FileNotFoundError, KeyError):
    OPENAI_API_KEY = None

client = None
if OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print(f"Errore inizializzazione client AI: {e}")


# =============================================================================
# FUNZIONI AI (HELPER)
# =============================================================================

def riscrivi_motivazione_ai(testo_grezzo):
    """Trasforma testo informale in burocratese."""
    if not client: return "Errore: API Key mancante."
    prompt = "Sei un esperto funzionario della P.A. Riscrivi il testo dell'utente in linguaggio amministrativo formale per la premessa di una Determina. Usa termini come 'preso atto', 'verificata', 'ritenuto'. Non aggiungere saluti."
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": f"Testo: '{testo_grezzo}'"}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e: return f"Errore AI: {str(e)}"

def genera_oggetto_ai(testo_motivazione):
    """Sintetizza la motivazione in un Oggetto maiuscolo."""
    if not client: return "Errore: API Key mancante."
    prompt = "Sei un esperto amministrativo. Sintetizza il testo fornito in un OGGETTO DI DETERMINA. Regole: 1. Massimo 15 parole. 2. Tutto MAIUSCOLO. 3. Stile telegrafico. 4. Niente punto finale."
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": f"Testo: '{testo_motivazione}'"}],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e: return f"Errore AI: {str(e)}"

def trova_cpv_ai(descrizione_oggetto):
    """Trova il codice CPV più probabile."""
    if not client: return "Errore: API Key mancante."
    prompt = "Identifica il codice CPV (Common Procurement Vocabulary) più idoneo per l'oggetto fornito. Restituisci SOLO il codice numerico e la descrizione sintetica."
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": f"Oggetto: '{descrizione_oggetto}'"}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e: return f"Errore AI: {str(e)}"


# =============================================================================
# CONFIGURAZIONE PAGINA E CSS AGGRESSIVO (v3.2 - Fix Bordi)
# =============================================================================

st.set_page_config(
    page_title="DeterminaFacile | Generatore Gratuito Atti PA",
    page_icon="🇮🇹",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'mailto:supporto@determinafacile.it',
        'About': "DeterminaFacile: Generatore di atti amministrativi gratuito e open-source."
    }
)

# CSS INIETTATO CON FORZATURA ESTREMA
st.markdown("""
<style>
    /* ================= TEMA GLOBALE ================= */
    .stApp {
        background-color: #ffffff;
    }

    /* BARRA LATERALE (SIDEBAR) */
    [data-testid="stSidebar"] {
        background-color: #eef4f9 !important;
        border-right: 2px solid #d0e0f0 !important;
    }
    /* Testi nella sidebar più grandi */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] .stTextInput label, 
    [data-testid="stSidebar"] .stSelectbox label {
        font-size: 1rem !important;
        color: #003366 !important;
    }

    /* ================= FIX BORDI INPUT (Il trucco è qui) ================= */
    /* Invece di colorare l'input interno, coloriamo il contenitore (wrapper) */
    
    div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="select"] > div {
        border: 1px solid #003366 !important;
        border-radius: 6px !important;
        background-color: white !important;
    }
    
    /* Rimuoviamo il bordo dall'input interno per evitare doppi bordi o glitch */
    .stTextInput input, .stTextArea textarea {
        border: none !important;
        box-shadow: none !important;
    }

    /* Etichette (Labels) */
    .stTextInput label, .stTextArea label, .stSelectbox label, .stNumberInput label, .stDateInput label, .stCheckbox label {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #003366 !important;
    }

    /* ================= COMPONENTI GRAFICI ================= */

    /* HERO CONTAINER */
    div.hero-container {
        background-color: #003366 !important;
        background-image: linear-gradient(180deg, #004080 0%, #003366 100%) !important;
        color: white !important;
        padding: 2.5rem 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 10px rgba(0, 51, 102, 0.2);
    }
    h1.hero-title {
        color: white !important;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800 !important;
    }
    p.hero-subtitle { color: #dceefb !important; font-size: 1.25rem !important; }

    /* BADGE GRATIS */
    div.free-badge {
        background-color: #FFC107 !important;
        color: #003366 !important;
        padding: 8px 18px;
        border-radius: 20px;
        font-weight: 900;
        font-size: 1rem !important;
        display: inline-block;
        margin-top: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }

    /* CARD VANTAGGI */
    div.feature-card {
        background-color: white !important;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #dae1e7;
        text-align: center;
        height: 100%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        transition: transform 0.2s;
    }
    div.feature-card:hover {
        transform: translateY(-3px);
        border-color: #003366 !important;
    }
    div.feature-title {
        color: #003366 !important;
        font-weight: 700;
        margin-top: 10px;
        font-size: 1.2rem !important;
    }
    div.feature-card p { font-size: 1rem !important; line-height: 1.5; }

    /* PULSANTI STANDARD */
    div.stButton > button:first-child {
        background-color: #003366 !important;
        color: white !important;
        border: 1px solid #002244 !important;
        font-weight: 600;
        font-size: 1.1rem !important;
        padding: 0.7rem 1rem !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #002244 !important;
        color: #FFC107 !important;
        border-color: #FFC107 !important;
    }

    /* BOX AI */
    div.ai-box {
        background-color: #eef6fc !important;
        border-left: 5px solid #0055A4 !important;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 15px;
    }

    /* SEO BOX FOOTER */
    div.seo-box {
        background-color: #f9f9f9 !important;
        padding: 2rem;
        border-top: 3px solid #003366;
        margin-top: 3rem;
    }
    div.seo-box h2 { color: #003366 !important; }
    div.seo-box p, div.seo-box li { font-size: 1rem !important; line-height: 1.6; }

    /* DISCLAIMER */
    div.disclaimer-alert {
        background-color: #fffde7 !important;
        border-left: 6px solid #ffc107 !important;
        padding: 1.2rem !important;
        color: #333 !important;
        font-size: 1rem !important;
    }
    
    .stCaption { font-size: 0.95rem !important; color: #555 !important; }
    div[data-testid="stExpander"] p { font-size: 1rem !important; }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# HEADER & LANDING
# =============================================================================

st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">DeterminaFacile</h1>
    <p class="hero-subtitle">Crea la tua <strong>Determina di Affidamento Diretto</strong> (Art. 50) in 2 minuti.<br>Conforme al D.Lgs 36/2023, con assistenza AI.</p>
    <div class="free-badge">✨ 100% GRATUITO & OPEN SOURCE</div>
</div>
""", unsafe_allow_html=True)

# VANTAGGI
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div class="feature-card">
        <div style="font-size: 2.5rem;">⚡</div>
        <div class="feature-title">Più veloce di un Fac-simile</div>
        <p>Non perdere tempo a cancellare dati vecchi da modelli Word obsoleti. Genera una determina pulita e pronta in pochi click.</p>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown("""
    <div class="feature-card">
        <div style="font-size: 2.5rem;">⚖️</div>
        <div class="feature-title">Conforme Art. 50 D.Lgs 36/2023</div>
        <p>Include automaticamente le clausole per l'affidamento diretto sottosoglia e la deroga alla rotazione (Art. 49) per importi < 5.000€.</p>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown("""
    <div class="feature-card">
        <div style="font-size: 2.5rem;">✨</div>
        <div class="feature-title">AI Magic Writer</div>
        <p>Non sai come scrivere la motivazione? L'Intelligenza Artificiale trasforma la tua idea in linguaggio amministrativo formale.</p>
    </div>
    """, unsafe_allow_html=True)

if not OPENAI_API_KEY:
    st.warning("⚠️ API Key non rilevata. Le funzioni 'Magic Writer' sono disabilitate.")


# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.header("🏛️ Dati Ente")
    comune = st.text_input("Ente", placeholder="es. Comune di Milano")
    provincia = st.text_input("Provincia", placeholder="MI")
    st.markdown("---")
    st.subheader("👤 RUP / Firmatario")
    titolo_responsabile = st.selectbox("Titolo", ["Dott.", "Dott.ssa", "Ing.", "Arch.", "Avv.", "Geom.", "Rag.", ""], index=0)
    nome_responsabile = st.text_input("Nome Cognome", placeholder="es. Mario Rossi")
    qualifica_responsabile = st.text_input("Qualifica", value="Responsabile del Settore")
    decreto_funzioni = st.text_input("Decreto Nomina", placeholder="Decr. n. X del...")
    st.markdown("---")
    usa_regolamento = st.checkbox("Cita Regolamento")
    regolamento_riferimento = st.text_input("Estremi Regolamento") if usa_regolamento else ""
    st.markdown("---")
    st.caption("ℹ️ Licenza: **Open Source (Gratis)**")


# =============================================================================
# FORM PRINCIPALE
# =============================================================================

st.markdown("---")
st.markdown("### 🛠️ Compila la tua Determina")

col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("#### 1. Oggetto e Motivazione")
    
    # --- BOX AI 1: MOTIVAZIONE ---
    st.markdown('<div class="ai-box">', unsafe_allow_html=True)
    st.caption("✨ AI MAGIC WRITER: Scrivi l'idea grezza, l'AI la rende formale.")
    col_in_ai, col_btn_ai = st.columns([3,1])
    with col_in_ai:
        input_motivazione_grezza = st.text_input("Cosa devi acquistare?", placeholder="es. servono pc nuovi...", label_visibility="collapsed")
    with col_btn_ai:
        if st.button("🪄 Riscrivi", use_container_width=True):
            with st.spinner("AI al lavoro..."):
                testo_formale = riscrivi_motivazione_ai(input_motivazione_grezza)
                st.session_state['motivazione_ai'] = testo_formale
    st.markdown('</div>', unsafe_allow_html=True)

    motivazione = st.text_area("Motivazione (Narrativa)", value=st.session_state.get('motivazione_ai', ""), height=120)

    # --- BOX AI 2: OGGETTO ---
    col_ogg_lbl, col_ogg_btn = st.columns([2, 1])
    with col_ogg_lbl: st.markdown("**Oggetto della Determina**")
    with col_ogg_btn:
        if st.button("⚡ Genera da Motivazione", help="Crea oggetto sintetico"):
            if motivazione and len(motivazione) > 10:
                with st.spinner("Sintesi..."):
                    ogg_ai = genera_oggetto_ai(motivazione)
                    st.session_state['oggetto_ai'] = ogg_ai
            else: st.warning("Scrivi prima la motivazione!")
    
    oggetto = st.text_area("Testo Oggetto (Maiuscolo)", value=st.session_state.get('oggetto_ai', ""), height=70, label_visibility="collapsed")
    
    # --- BOX AI 3: CPV ---
    col_cpv_in, col_cpv_btn = st.columns([2, 1])
    with col_cpv_in:
        codice_cpv = st.text_input("Codice CPV (Opzionale)", value=st.session_state.get('cpv_ai', ""))
    with col_cpv_btn:
        st.write("")
        st.write("")
        if st.button("🔍 Trova CPV"):
            txt = oggetto if oggetto else motivazione
            if txt:
                with st.spinner("Ricerca..."):
                    st.session_state['cpv_ai'] = trova_cpv_ai(txt)
            else: st.warning("Serve Oggetto o Motivazione")

    st.markdown("#### 2. Dati Amministrativi")
    c1, c2, c3 = st.columns(3)
    with c1: num_determina_settore = st.text_input("N. Det. Settore")
    with c2: num_determina_generale = st.text_input("N. Reg. Gen.")
    with c3: data_atto = st.date_input("Data", value=date.today())
    area_settore = st.text_input("Area / Settore", placeholder="es. AREA TECNICA")
    finalita = st.text_area("Finalità Pubblica", height=70)
    durata_servizio = st.text_input("Durata / Consegna")

    st.markdown("#### 3. Fornitore")
    ragione_sociale = st.text_input("Ragione Sociale")
    sel1, sel2 = st.columns(2)
    with sel1:
        criterio_scelta = st.selectbox("Criterio Scelta", [
            "preventivo più conveniente (indagine informale)",
            "esperienza specifica nel settore pubblico",
            "conoscenza pregressa dell'ente",
            "continuità operativa",
            "affidabilità pregressa"
        ])
    with sel2: operatore_uscente = st.checkbox("È gestore uscente?")
    
    indirizzo = st.text_input("Indirizzo")
    cc1, cc2, cc3 = st.columns([1,2,1])
    with cc1: cap = st.text_input("CAP", max_chars=5)
    with cc2: citta = st.text_input("Città")
    with cc3: provincia_forn = st.text_input("PR", max_chars=2)
    piva_cf = st.text_input("P.IVA / CF")
    
    st.markdown("**Dati Preventivo**")
    p1, p2, p3 = st.columns(3)
    with p1: tipo_doc = st.selectbox("Tipo", ["preventivo", "offerta"])
    with p2: num_prev = st.text_input("N. Doc")
    with p3: data_prev = st.date_input("Data Doc")

    st.markdown("#### 4. Economico")
    e1, e2 = st.columns(2)
    with e1: imponibile = st.number_input("Imponibile €", step=100.00)
    with e2: iva = st.selectbox("IVA %", [22, 10, 5, 4, 0])
    
    if imponibile > 0:
        tot = calcola_importi(imponibile, iva)
        st.info(f"Totale: **{formatta_importo(tot['totale'])}**")
        
    cig = st.text_input("CIG (SmartCIG)")
    capitolo = st.text_input("Capitolo Bilancio")
    esercizio = st.number_input("Anno", value=2025)
    rup = st.text_input("RUP (Se diverso)", value=nome_responsabile)
    
    st.markdown("#### 5. Opzioni")
    o1, o2 = st.columns(2)
    with o1: mepa = st.checkbox("Acquisto su MEPA", value=(imponibile>=5000))
    with o2: no_garanzia = st.checkbox("Esenzione Garanzia (Art. 53)", value=True)


# =============================================================================
# COLONNA DESTRA (AZIONI)
# =============================================================================

with col_right:
    st.markdown("### 🚀 Genera")
    
    dati_form = {
        "comune": comune, "provincia": provincia, "area_settore": area_settore,
        "nome_responsabile": nome_responsabile, "titolo_responsabile": titolo_responsabile,
        "qualifica_responsabile": qualifica_responsabile, "decreto_funzioni": decreto_funzioni,
        "regolamento_comunale": regolamento_riferimento if usa_regolamento else None,
        "num_determina_generale": num_determina_generale, "num_determina_settore": num_determina_settore,
        "data_atto": datetime.combine(data_atto, datetime.min.time()),
        "oggetto": oggetto, "motivazione": motivazione, "finalita": finalita, "durata_servizio": durata_servizio,
        "ragione_sociale": ragione_sociale, "indirizzo": indirizzo, "cap": cap, "citta": citta,
        "provincia_fornitore": provincia_forn, "piva_cf": piva_cf, "tipo_documento": tipo_doc,
        "numero_preventivo": num_prev, 
        "data_preventivo": datetime.combine(data_prev, datetime.min.time()),
        "criterio_scelta": criterio_scelta, "operatore_uscente": operatore_uscente,
        "imponibile": imponibile, "aliquota_iva": iva, "cig": cig,
        "capitolo_bilancio": capitolo, "esercizio_finanziario": esercizio,
        "rup_nome": rup, "rup_cognome": "", "rup_qualifica": qualifica_responsabile,
        "importo_sotto_5000": imponibile < 5000,
        "usa_mepa": mepa, "piccola_fornitura": no_garanzia
    }
    
    valido, errori = valida_dati(dati_form)
    
    if valido:
        if st.button("SCARICA DETERMINA (.RTF)", type="primary"):
            try:
                p, d = genera_testo_completo(dati_form)
                if codice_cpv: p += f"\nVISTO il codice CPV individuato: {codice_cpv};\n"
                rtf_data, nome_file = esporta_determina_rtf(dati_form, p, d)
                st.download_button("📥 DOWNLOAD", data=rtf_data.encode('cp1252', errors='replace'), file_name=nome_file, mime="application/rtf")
                st.balloons()
            except Exception as e: st.error(str(e))
    else:
        st.warning("Compila i campi obbligatori.")
        if errori: st.caption(f"Mancano: {', '.join(errori)}")

    st.markdown("---")
    st.markdown("""
    <div class="disclaimer-alert">
    <strong>⚠️ DISCLAIMER LEGALE</strong><br>
    Questo strumento genera bozze di atti amministrativi. L'utente (RUP/Istruttore) è l'unico responsabile della verifica di correttezza formale, sostanziale e contabile prima della sottoscrizione.
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# SEZIONE SEO & FOOTER
# =============================================================================

st.markdown("""
<div class="seo-box">
<h2>Domande Frequenti su DeterminaFacile</h2>

<h3>Cerchi un Fac-simile di Determina Aggiornato al 2025?</h3>
<p>Molti RUP cercano <em>modelli Word statici</em> che rischiano di avere riferimenti normativi vecchi. DeterminaFacile non è un semplice fac-simile, ma un <strong>generatore intelligente gratuito</strong> che compila per te l'atto citando correttamente il <strong>Nuovo Codice Appalti (D.Lgs 36/2023)</strong>.</p>

<h3>È davvero gratuito?</h3>
<p>Sì. DeterminaFacile è un progetto <strong>Open Source</strong> senza fini di lucro, nato per semplificare la burocrazia. Non ci sono costi nascosti né abbonamenti.</p>

<h3>Come gestire l'Affidamento Diretto Sottosoglia (Art. 50)?</h3>
<p>Il software crea automaticamente la struttura per gli affidamenti diretti di servizi e forniture sotto i 140.000€, inserendo le clausole corrette per l'<strong>Art. 50 comma 1 lett. b)</strong>.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

with st.expander("⚖️ Note Legali, Privacy Policy e Cookie"):
    st.markdown("""
    ### 1. Termini e Condizioni
    L'applicazione "DeterminaFacile" è fornita "così com'è" (as-is). L'autore non si assume responsabilità per errori o omissioni negli atti generati.
    ### 2. Privacy Policy AI
    I dati inseriti nei campi assistiti dall'Intelligenza Artificiale vengono elaborati da OpenAI. **NON inserire dati personali** (nomi di persone fisiche, dati sanitari) nei prompt dell'AI.
    Tutti i dati inseriti nel modulo vengono cancellati al termine della sessione (chiusura pagina).
    ### 3. Cookie Policy
    Questo sito utilizza esclusivamente **Cookie Tecnici** necessari al funzionamento. Non viene effettuata profilazione pubblicitaria.
    """)

st.markdown("""
<div style="text-align: center; margin-top: 2rem; color: #888; font-size: 0.8rem;">
    <p><strong>DeterminaFacile.it</strong> © 2025 - Piattaforma Open Source per la P.A.</p>
</div>
""", unsafe_allow_html=True)