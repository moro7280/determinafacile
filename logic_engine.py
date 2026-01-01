"""
================================================================================
LOGIC_ENGINE_ADDITIONS.PY
================================================================================
Queste funzioni devono essere AGGIUNTE al file logic_engine.py esistente.
Contengono la logica per generare le nuove sezioni:
- Riferimenti delibere bilancio (DUP, Bilancio, PEG)
- DURC
- Visto di regolarità contabile
- Modalità di ricorso e conflitto interessi

ISTRUZIONI:
1. Apri il file logic_engine.py
2. Copia le funzioni qui sotto
3. Modifica la funzione `genera_testo_completo` per chiamare queste funzioni
================================================================================
"""

from datetime import datetime


def formatta_data_estesa(data):
    """Formatta data in formato esteso italiano: '29/07/2024'."""
    if data is None:
        return ""
    if isinstance(data, datetime):
        return data.strftime("%d/%m/%Y")
    return str(data)


def genera_richiami_bilancio(dati: dict) -> str:
    """
    Genera la sezione RICHIAMATA con i riferimenti alle delibere di bilancio.
    Da inserire DOPO il preambolo iniziale e PRIMA delle premesse.
    """
    righe = []
    
    # Verifica se ci sono dati di bilancio da includere
    has_bilancio = any([
        dati.get("dup_num"),
        dati.get("bilancio_num"),
        dati.get("peg_num")
    ])
    
    if not has_bilancio:
        return ""
    
    righe.append("RICHIAMATA:")
    righe.append("")
    
    # DUP
    if dati.get("dup_num"):
        dup_data_str = formatta_data_estesa(dati.get("dup_data"))
        dup_periodo = dati.get("dup_periodo", "")
        righe.append(f"- la deliberazione di Consiglio Comunale n. {dati['dup_num']} in data {dup_data_str}, esecutiva, con cui è stato approvato il documento unico di programmazione (DUP) periodo {dup_periodo};")
        righe.append("")
    
    # Nota aggiornamento DUP
    if dati.get("nota_dup_num"):
        nota_data_str = formatta_data_estesa(dati.get("nota_dup_data"))
        dup_periodo = dati.get("dup_periodo", "")
        righe.append(f"- la deliberazione di Consiglio Comunale n. {dati['nota_dup_num']} in data {nota_data_str}, esecutiva, con cui è stata approvata la nota di aggiornamento al documento unico di programmazione (DUP) periodo {dup_periodo};")
        righe.append("")
    
    # Bilancio di previsione
    if dati.get("bilancio_num"):
        bil_data_str = formatta_data_estesa(dati.get("bilancio_data"))
        bil_triennio = dati.get("bilancio_triennio", "")
        righe.append(f"- la deliberazione di Consiglio Comunale n. {dati['bilancio_num']} in data {bil_data_str}, esecutiva, e successive modificazioni ed integrazioni, con cui è stato approvato il bilancio di previsione finanziario per il triennio {bil_triennio};")
        righe.append("")
    
    # PEG
    if dati.get("peg_num"):
        peg_data_str = formatta_data_estesa(dati.get("peg_data"))
        peg_periodo = dati.get("peg_periodo", "")
        righe.append(f"- la deliberazione di Giunta comunale n. {dati['peg_num']} in data {peg_data_str}, esecutiva, con la quale è stato approvato l'atto ad oggetto: \"Esercizio finanziario {peg_periodo} – Assegnazione Fondi di bilancio ai responsabili di settore per la realizzazione del programma di bilancio {peg_periodo} – approvazione PEG {peg_periodo}\";")
        righe.append("")
    
    return "\n".join(righe)


def genera_sezione_durc(dati: dict) -> str:
    """
    Genera la clausola relativa al DURC.
    Da inserire nella sezione DATO ATTO.
    """
    if not dati.get("durc_protocollo"):
        return ""
    
    durc_scadenza_str = formatta_data_estesa(dati.get("durc_scadenza"))
    esito = dati.get("durc_esito", "REGOLARE")
    
    testo = f"""DATO ATTO altresì che per l'operatore economico {dati.get('ragione_sociale', '')} è stato acquisito il Documento Unico di Regolarità Contributiva (DURC) Prot. {dati['durc_protocollo']} e che lo stesso risulta {esito}"""
    
    if durc_scadenza_str:
        testo += f" con scadenza validità il {durc_scadenza_str}"
    
    testo += ";\n"
    
    return testo


def genera_sezione_altre_informazioni(dati: dict) -> str:
    """
    Genera la sezione ALTRE INFORMAZIONI con:
    - Responsabile del procedimento
    - Modalità di ricorso
    - Dichiarazione conflitto interessi
    
    Da inserire DOPO il dispositivo (DETERMINA) e PRIMA della firma.
    """
    righe = []
    
    if not (dati.get("includi_ricorsi") or dati.get("includi_conflitto")):
        return ""
    
    righe.append("")
    righe.append("=" * 70)
    righe.append("ALTRE INFORMAZIONI:")
    righe.append("")
    
    # Responsabile del procedimento
    righe.append(f"Responsabile del procedimento (artt. 4-6 legge 241/1990): {dati.get('nome_responsabile', 'il sottoscritto')}.")
    righe.append("")
    
    # Ricorsi
    if dati.get("includi_ricorsi"):
        tar = dati.get("tar_competente", "TAR competente")
        righe.append(f"Ricorsi: ai sensi dell'art. 3, comma 4, della legge 241/1990, contro il presente atto è ammesso il ricorso al {tar} nel termine di 60 giorni dalla pubblicazione (d.lgs. 2 luglio 2010, n. 104) o, in alternativa, il ricorso straordinario al Presidente della Repubblica nel termine di 120 giorni dalla pubblicazione, nei modi previsti dall'art. 8 e seguenti del d.P.R. 24 novembre 1971, n. 1199.")
        righe.append("")
    
    # Conflitto di interessi
    if dati.get("includi_conflitto"):
        righe.append("Conflitto d'interessi: in relazione all'adozione del presente atto, per il sottoscritto:")
        righe.append("[X] non ricorre conflitto, anche potenziale, di interessi a norma dell'art. 6-bis della legge 241/1990, dell'art. 6 del DPR 62/2013 e del Codice di comportamento dell'Ente;")
        righe.append("[X] non ricorre l'obbligo di astensione, previsto dall'art. 7 del DPR 62/2013 e del Codice di comportamento dell'Ente.")
        righe.append("")
    
    # Pubblicazione trasparenza
    righe.append("Pubblicazione nella sezione \"Trasparenza\" (D.lgs. n. 33/2013)")
    righe.append("I dati della presente determinazione saranno pubblicati nella sezione Amministrazione Trasparente/Provvedimenti.")
    righe.append("")
    
    return "\n".join(righe)


def genera_visto_regolarita_contabile(dati: dict) -> str:
    """
    Genera la sezione del VISTO DI REGOLARITÀ CONTABILE.
    Da inserire DOPO la firma del responsabile del settore.
    """
    if not dati.get("includi_visto"):
        return ""
    
    visto_nome = dati.get("visto_nome", "[Nome Responsabile Finanziario]")
    visto_qualifica = dati.get("visto_qualifica", "Responsabile dell'Area Economico-Finanziaria")
    data_atto = dati.get("data_atto")
    data_str = formatta_data_estesa(data_atto) if data_atto else "[Data]"
    comune = dati.get("comune", "[Comune]")
    
    # Estrai solo il nome del comune senza "Comune di"
    if comune.lower().startswith("comune di "):
        nome_comune = comune[10:]
    else:
        nome_comune = comune
    
    testo = f"""
{'=' * 70}

VISTO DI REGOLARITÀ CONTABILE

Si appone il visto di regolarità contabile attestante la copertura finanziaria della presente determinazione, ai sensi dell'art. 183 comma VII del D.lgs. 267/2000 e s.m.i., che pertanto in data odierna, diviene esecutiva.

{nome_comune} lì {data_str}

{visto_qualifica}

f.to {visto_nome}

{'=' * 70}
"""
    
    return testo


def genera_attestato_pubblicazione(dati: dict) -> str:
    """
    Genera l'ATTESTATO DI PUBBLICAZIONE all'Albo Pretorio.
    Da inserire alla fine del documento.
    """
    testo = """
ATTESTATO DI PUBBLICAZIONE

Della su estesa determinazione viene iniziata la pubblicazione all'Albo Pretorio per 15 giorni consecutivi dal _____________ al _____________

Il Responsabile del Servizio

f.to _______________________
"""
    return testo


# ================================================================================
# ESEMPIO DI INTEGRAZIONE NELLA FUNZIONE genera_testo_completo
# ================================================================================

"""
Nella funzione `genera_testo_completo` del file logic_engine.py, 
devi modificare la struttura per includere le nuove sezioni.

Ecco lo schema di come dovrebbe essere organizzato il documento finale:

1. INTESTAZIONE (Comune, Provincia, Area, ecc.)
2. OGGETTO
3. IL RESPONSABILE DEL SETTORE
4. >>> RICHIAMATA (delibere bilancio) <<< NUOVO - genera_richiami_bilancio()
5. VERIFICATA / PREMESSO / CONSIDERATO (motivazioni)
6. >>> DATO ATTO DURC <<< NUOVO - genera_sezione_durc()
7. Altri DATO ATTO esistenti
8. VISTO (riferimenti normativi)
9. D E T E R M I N A (dispositivo)
10. >>> ALTRE INFORMAZIONI <<< NUOVO - genera_sezione_altre_informazioni()
11. FIRMA del Responsabile del Settore
12. >>> VISTO REGOLARITÀ CONTABILE <<< NUOVO - genera_visto_regolarita_contabile()
13. >>> ATTESTATO PUBBLICAZIONE <<< NUOVO - genera_attestato_pubblicazione()


ESEMPIO DI MODIFICA:

def genera_testo_completo(dati: dict) -> tuple[str, str]:
    # ... codice esistente per premesse ...
    
    # Aggiungi richiami bilancio dopo il preambolo
    richiami_bilancio = genera_richiami_bilancio(dati)
    if richiami_bilancio:
        premesse = richiami_bilancio + "\n" + premesse
    
    # ... codice esistente per DATO ATTO ...
    
    # Aggiungi DURC nella sezione DATO ATTO
    sezione_durc = genera_sezione_durc(dati)
    if sezione_durc:
        premesse += sezione_durc
    
    # ... codice esistente per dispositivo ...
    
    # Aggiungi sezioni finali dopo il dispositivo
    altre_info = genera_sezione_altre_informazioni(dati)
    visto_contabile = genera_visto_regolarita_contabile(dati)
    attestato = genera_attestato_pubblicazione(dati)
    
    dispositivo += altre_info + visto_contabile + attestato
    
    return premesse, dispositivo
"""
