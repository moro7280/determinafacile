"""
REGOLA Standalone v1.0 - Document Generator
Modulo per la generazione di documenti RTF formattati.
Gestisce correttamente i caratteri speciali italiani.
"""

from datetime import datetime
from typing import Dict
from decimal import Decimal
import re


# =============================================================================
# GESTIONE CARATTERI SPECIALI RTF
# =============================================================================

def escape_rtf(text: str) -> str:
    """
    Converte i caratteri speciali italiani e altri caratteri in escape RTF.
    
    Args:
        text: Testo da convertire
    
    Returns:
        Testo con escape RTF
    """
    if not text:
        return ""
    
    # Prima escape dei caratteri RTF speciali
    text = text.replace("\\", "\\\\")
    text = text.replace("{", "\\{")
    text = text.replace("}", "\\}")
    
    # Mappa caratteri italiani -> codici RTF
    char_map = {
        # Vocali accentate minuscole
        'à': "\\'e0",
        'è': "\\'e8",
        'é': "\\'e9",
        'ì': "\\'ec",
        'ò': "\\'f2",
        'ù': "\\'f9",
        # Vocali accentate maiuscole
        'À': "\\'c0",
        'È': "\\'c8",
        'É': "\\'c9",
        'Ì': "\\'cc",
        'Ò': "\\'d2",
        'Ù': "\\'d9",
        # Altri caratteri comuni
        '€': "\\'80",
        '°': "\\'b0",
        '§': "\\'a7",
        '©': "\\'a9",
        '®': "\\'ae",
        '–': "\\'96",  # En dash
        '—': "\\'97",  # Em dash
        '"': "\\'93",  # Left double quote
        '"': "\\'94",  # Right double quote
        ''': "\\'91",  # Left single quote
        ''': "\\'92",  # Right single quote
        '…': "\\'85",  # Ellipsis
    }
    
    for char, escape in char_map.items():
        text = text.replace(char, escape)
    
    # Gestione newline
    text = text.replace("\n\n", "\\par\\par ")
    text = text.replace("\n", "\\par ")
    
    return text


# =============================================================================
# TEMPLATE RTF
# =============================================================================

def genera_rtf(dati: Dict, testo_premesse: str, testo_dispositivo: str) -> str:
    """
    Genera il documento RTF completo della determina.
    
    Args:
        dati: Dizionario con tutti i dati del form
        testo_premesse: Testo delle premesse generato da logic_engine
        testo_dispositivo: Testo del dispositivo generato da logic_engine
    
    Returns:
        Stringa con il documento RTF completo
    """
    # Dati formattati
    comune = escape_rtf(dati.get("comune", ""))
    provincia = escape_rtf(dati.get("provincia", ""))
    area_settore = escape_rtf(dati.get("area_settore", ""))
    oggetto = escape_rtf(dati.get("oggetto", "").upper())
    
    num_det_generale = dati.get("num_determina_generale", "______")
    num_det_settore = dati.get("num_determina_settore", "______")
    
    data_atto = dati.get("data_atto")
    if isinstance(data_atto, datetime):
        data_str = data_atto.strftime("%d/%m/%Y")
    else:
        data_str = str(data_atto) if data_atto else "___/___/_____"
    
    responsabile = escape_rtf(dati.get("nome_responsabile", ""))
    titolo_resp = escape_rtf(dati.get("titolo_responsabile", ""))
    qualifica_resp = escape_rtf(dati.get("qualifica_responsabile", ""))
    
    # Escape dei testi lunghi
    premesse_rtf = escape_rtf(testo_premesse)
    dispositivo_rtf = escape_rtf(testo_dispositivo)
    
    # Header RTF con font e impostazioni pagina
    rtf_header = r"""{\rtf1\ansi\ansicpg1252\deff0\deflang1040
{\fonttbl
{\f0\froman\fcharset0 Times New Roman;}
{\f1\fswiss\fcharset0 Arial;}
}
{\colortbl;\red0\green0\blue0;\red128\green128\blue128;}
\paperw11906\paperh16838\margl1417\margr1417\margt1417\margb1134
\viewkind4\uc1"""

    # Intestazione documento
    intestazione = rf"""
\pard\qc\f1\fs28\b COMUNE DI {comune}\b0\par
\fs22 Provincia di {provincia}\par
\par
\pard\ql\f0\fs24\b {area_settore}\b0\par
\par
\pard\qc\b DETERMINAZIONE N. {num_det_settore} del {data_str}\b0\par
\fs20 (Registro Generale n. {num_det_generale})\par
\par"""

    # Oggetto
    oggetto_section = rf"""
\pard\ql\f0\fs24\par
\b OGGETTO: \b0 {oggetto}\par
\par
\pard\qj\fs22"""

    # Premesse (con "IL RESPONSABILE DEL SETTORE")
    premesse_section = rf"""
\pard\qc\b IL RESPONSABILE DEL SETTORE\b0\par
\par
\pard\qj\fs22
{premesse_rtf}
\par\par"""

    # Dispositivo
    dispositivo_section = rf"""
\pard\qc\b\fs24 {dispositivo_rtf.split(chr(92)+'par')[0]}\b0\par
\par
\pard\qj\fs22
{escape_rtf(chr(10).join(testo_dispositivo.split(chr(10))[1:]))}
\par\par"""

    # Firma
    firma_section = rf"""
\pard\qr\fs22\par
\par
Il Responsabile del Settore\par
\b {titolo_resp} {responsabile}\b0\par
{qualifica_resp}\par
\par
\fs18\i (Documento informatico firmato digitalmente ai sensi del D.Lgs. 82/2005 e ss.mm.ii.)\i0\par
"""

    # Footer RTF
    rtf_footer = r"""
}"""

    # Assemblaggio documento completo
    documento = (
        rtf_header +
        intestazione +
        oggetto_section +
        premesse_section +
        dispositivo_section +
        firma_section +
        rtf_footer
    )
    
    return documento


def genera_nome_file(dati: Dict) -> str:
    """
    Genera un nome file significativo per la determina.
    
    Args:
        dati: Dizionario con i dati del form
    
    Returns:
        Nome file (senza estensione)
    """
    comune = dati.get("comune", "Comune").replace(" ", "_")
    num_det = dati.get("num_determina_settore", "X")
    
    data_atto = dati.get("data_atto")
    if isinstance(data_atto, datetime):
        data_str = data_atto.strftime("%Y%m%d")
    else:
        data_str = datetime.now().strftime("%Y%m%d")
    
    # Pulisci oggetto per nome file
    oggetto = dati.get("oggetto", "Determina")[:50]
    oggetto_clean = re.sub(r'[^\w\s-]', '', oggetto).strip().replace(" ", "_")
    
    return f"Determina_{num_det}_{data_str}_{oggetto_clean}"


# =============================================================================
# FUNZIONE PRINCIPALE DI EXPORT
# =============================================================================

def esporta_determina_rtf(dati: Dict, testo_premesse: str, testo_dispositivo: str) -> tuple:
    """
    Funzione principale per esportare la determina in formato RTF.
    
    Args:
        dati: Dizionario con tutti i dati del form
        testo_premesse: Testo delle premesse
        testo_dispositivo: Testo del dispositivo
    
    Returns:
        Tupla (contenuto_rtf, nome_file)
    """
    contenuto = genera_rtf(dati, testo_premesse, testo_dispositivo)
    nome_file = genera_nome_file(dati)
    
    return contenuto, f"{nome_file}.rtf"


# =============================================================================
# FUNZIONI DI UTILITÀ
# =============================================================================

def formatta_importo_testo(valore: float) -> str:
    """Formatta un importo per la visualizzazione testuale."""
    return f"€ {valore:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def numero_in_lettere(n: int) -> str:
    """
    Converte un numero intero in lettere (italiano).
    Utile per importi in lettere su atti ufficiali.
    """
    if n == 0:
        return "zero"
    
    unita = ["", "uno", "due", "tre", "quattro", "cinque", "sei", "sette", "otto", "nove"]
    decine = ["", "dieci", "venti", "trenta", "quaranta", "cinquanta", 
              "sessanta", "settanta", "ottanta", "novanta"]
    teens = ["dieci", "undici", "dodici", "tredici", "quattordici", "quindici",
             "sedici", "diciassette", "diciotto", "diciannove"]
    
    def sotto_cento(n):
        if n < 10:
            return unita[n]
        elif n < 20:
            return teens[n - 10]
        else:
            d, u = divmod(n, 10)
            if u == 1 or u == 8:
                return decine[d][:-1] + unita[u]
            return decine[d] + unita[u]
    
    def sotto_mille(n):
        if n < 100:
            return sotto_cento(n)
        c, resto = divmod(n, 100)
        if c == 1:
            prefix = "cento"
        else:
            prefix = unita[c] + "cento"
        if resto == 0:
            return prefix
        return prefix + sotto_cento(resto)
    
    if n < 1000:
        return sotto_mille(n)
    elif n < 1000000:
        migliaia, resto = divmod(n, 1000)
        if migliaia == 1:
            prefix = "mille"
        else:
            prefix = sotto_mille(migliaia) + "mila"
        if resto == 0:
            return prefix
        return prefix + sotto_mille(resto)
    else:
        milioni, resto = divmod(n, 1000000)
        if milioni == 1:
            prefix = "unmilione"
        else:
            prefix = sotto_mille(milioni) + "milioni"
        if resto == 0:
            return prefix
        if resto < 1000:
            return prefix + sotto_mille(resto)
        return prefix + "e" + sotto_mille(resto // 1000) + "mila" + sotto_mille(resto % 1000)
