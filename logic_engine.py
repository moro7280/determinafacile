"""
================================================================================
DETERMINAFACILE - Logic Engine v4.0
================================================================================
Modulo per la gestione della logica normativa e l'assemblaggio dei testi legali.
Aggiornato con:
- GDPR, Congruità, Rotazione rafforzata e Durata
- Riferimenti delibere bilancio (DUP, Bilancio, PEG)
- DURC con estremi
- Visto di regolarità contabile (art. 183 c.7 TUEL)
- Modalità di ricorso e conflitto interessi
- Attestato di pubblicazione
================================================================================
"""

from datetime import datetime
from typing import Dict, Tuple
from decimal import Decimal, ROUND_HALF_UP

# =============================================================================
# KNOWLEDGE BASE - CHUNK NORMATIVI
# =============================================================================

CHUNKS = {
    # Chunk Base
    "art_50_affidamento": """l'art. 50, comma 1, lett. b) del D. Lgs. n. 36/2023 dispone che le stazioni appaltanti procedono all'affidamento dei contratti di servizi e forniture di importo inferiore a 140.000 euro, anche senza consultazione di più operatori economici, assicurando che siano scelti soggetti in possesso di documentate esperienze pregresse idonee all'esecuzione delle prestazioni contrattuali""",
    
    "art_15_rup": """ai sensi dell'art. 15 del D. Lgs. n. 36/2023, il Responsabile Unico del Progetto (RUP) è individuato nel Responsabile del Settore competente per materia o in altro dipendente appositamente delegato""",
    
    "art_18_forma_contratto": """il contratto verrà stipulato mediante corrispondenza secondo l'uso del commercio ai sensi dell'art. 18, comma 1, ultimo periodo del D. Lgs. n. 36/2023, consistente in un apposito scambio di lettere (o PEC)""",
    
    "art_52_requisiti": """il suddetto operatore economico ha presentato dichiarazione sostitutiva, ai sensi degli artt. 46 e 47 del D.P.R. n. 445/2000, circa il possesso dei requisiti di ordine generale di cui all'art. 94 e 95 del D. Lgs. n. 36/2023 e dei requisiti di idoneità professionale di cui all'art. 100 del medesimo decreto""",
    
    "tracciabilita_l136": """l'affidatario assume tutti gli obblighi di tracciabilità dei flussi finanziari di cui all'art. 3 della Legge 13 agosto 2010, n. 136 e successive modificazioni, pena la nullità assoluta del contratto""",
    
    "art_16_conflitto_interessi": """in relazione alla presente procedura sono assenti situazioni di conflitto d'interesse ai sensi dell'art. 16 del D. Lgs. n. 36/2023 e che non sussistono le condizioni di cui all'art. 53, comma 16-ter, del D. Lgs. n. 165/2001""",
    
    "dichiarazioni_responsabile": """di non trovarsi in alcuna situazione di conflitto di interessi ai sensi dell'art. 6-bis della Legge n. 241/1990, dell'art. 7 del D.P.R. n. 62/2013 e dell'art. 16 del D. Lgs. n. 36/2023, e di non incorrere nelle cause di incompatibilità previste dal D. Lgs. n. 39/2013""",

    # CHUNK - GDPR & CONGRUITÀ
    "gdpr_clause": """il servizio in oggetto comporta il trattamento di dati personali e pertanto l'operatore economico assumerà la qualifica di Responsabile del Trattamento ai sensi dell'art. 28 del Regolamento UE 2016/679 (GDPR), impegnandosi ad adottare tutte le misure tecniche e organizzative adeguate alla tutela dei dati""",
    
    "congruita_economica": """il corrispettivo offerto è stato valutato congruo in relazione ai prezzi di mercato e alla tipologia del servizio richiesto, garantendo l'economicità dell'azione amministrativa""",

    # Chunk Condizionali
    "obbligo_mepa_5000": """ai sensi dell'art. 1, comma 450, della Legge 27 dicembre 2006, n. 296 e ss.mm.ii., per gli acquisti di importo pari o superiore a 5.000 euro, l'Ente è tenuto a fare ricorso al Mercato Elettronico della Pubblica Amministrazione (MEPA) ovvero ad altri mercati elettronici""",
    
    "deroga_rotazione_5000": """ai sensi dell'art. 49, comma 6, del D. Lgs. n. 36/2023, per affidamenti diretti di importo inferiore a 5.000 euro, è consentito derogare al principio di rotazione degli affidamenti""",
    
    "esenzione_garanzia_ccnl": """considerata la natura della prestazione e l'importo ridotto, ai sensi dell'art. 53, comma 4, del D. Lgs. n. 36/2023 non si richiede la costituzione della garanzia definitiva; altresì, trattandosi di prestazione standardizzata o di piccola entità, non si rende necessaria la specifica indicazione del CCNL, fermo restando l'obbligo per l'operatore di garantire trattamenti salariali conformi alla normativa vigente""",
    
    "regolamento_comunale": """ai sensi dell'art. 4, comma 4, del Regolamento comunale per l'affidamento di lavori, servizi e forniture approvato con deliberazione {delibera_riferimento}""",
    
    "principi_art_1": """nel rispetto dei principi di cui all'art. 1 del D. Lgs. n. 36/2023, in particolare dei principi del risultato, della fiducia e dell'accesso al mercato""",
    
    "pubblicita_trasparenza": """ai sensi dell'art. 28 del D. Lgs. n. 36/2023 e del D. Lgs. n. 33/2013, il presente provvedimento sarà pubblicato nella sezione "Amministrazione Trasparente" del sito istituzionale dell'Ente e i dati saranno trasmessi alla Banca Dati Nazionale dei Contratti Pubblici (BDNCP) tramite Piattaforma Certificata (PCP) secondo le modalità stabilite dall'ANAC""",
    
    "esecutivita": """la presente determinazione è immediatamente eseguibile ai sensi dell'art. 183 del D. Lgs. n. 267/2000"""
}


# =============================================================================
# FUNZIONI DI CALCOLO E FORMATTAZIONE
# =============================================================================

def calcola_importi(imponibile: float, aliquota_iva: float) -> Dict[str, Decimal]:
    imp = Decimal(str(imponibile))
    aliq = Decimal(str(aliquota_iva)) / Decimal("100")
    iva = (imp * aliq).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    totale = (imp + iva).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {"imponibile": imp, "iva": iva, "totale": totale}

def formatta_importo(valore: Decimal) -> str:
    return f"€ {valore:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatta_data(data: datetime) -> str:
    mesi = ["", "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
            "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
    return f"{data.day} {mesi[data.month]} {data.year}"

def formatta_data_breve(data) -> str:
    """Formatta data in formato breve: '29/07/2024'."""
    if data is None:
        return ""
    if isinstance(data, datetime):
        return data.strftime("%d/%m/%Y")
    return str(data)


# =============================================================================
# NUOVE FUNZIONI v4.0 - SEZIONI AGGIUNTIVE
# =============================================================================

def genera_richiami_bilancio(dati: Dict) -> str:
    """
    Genera la sezione RICHIAMATA con i riferimenti alle delibere di bilancio.
    Include: DUP, Nota aggiornamento DUP, Bilancio di previsione, PEG.
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
    
    # DUP - Documento Unico di Programmazione
    if dati.get("dup_num"):
        dup_data_str = formatta_data_breve(dati.get("dup_data"))
        dup_periodo = dati.get("dup_periodo", "")
        righe.append(
            f"- la deliberazione di Consiglio Comunale n. {dati['dup_num']} "
            f"in data {dup_data_str}, esecutiva, con cui è stato approvato "
            f"il documento unico di programmazione (DUP) periodo {dup_periodo};"
        )
    
    # Nota aggiornamento DUP (opzionale)
    if dati.get("nota_dup_num"):
        nota_data_str = formatta_data_breve(dati.get("nota_dup_data"))
        dup_periodo = dati.get("dup_periodo", "")
        righe.append(
            f"- la deliberazione di Consiglio Comunale n. {dati['nota_dup_num']} "
            f"in data {nota_data_str}, esecutiva, con cui è stata approvata "
            f"la nota di aggiornamento al documento unico di programmazione (DUP) "
            f"periodo {dup_periodo};"
        )
    
    # Bilancio di previsione
    if dati.get("bilancio_num"):
        bil_data_str = formatta_data_breve(dati.get("bilancio_data"))
        bil_triennio = dati.get("bilancio_triennio", "")
        righe.append(
            f"- la deliberazione di Consiglio Comunale n. {dati['bilancio_num']} "
            f"in data {bil_data_str}, esecutiva, e successive modificazioni ed "
            f"integrazioni, con cui è stato approvato il bilancio di previsione "
            f"finanziario per il triennio {bil_triennio};"
        )
    
    # PEG - Piano Esecutivo di Gestione
    if dati.get("peg_num"):
        peg_data_str = formatta_data_breve(dati.get("peg_data"))
        peg_periodo = dati.get("peg_periodo", "")
        righe.append(
            f"- la deliberazione di Giunta comunale n. {dati['peg_num']} "
            f"in data {peg_data_str}, esecutiva, con la quale è stato approvato "
            f"l'atto ad oggetto: \"Esercizio finanziario {peg_periodo} - "
            f"Assegnazione Fondi di bilancio ai responsabili di settore per la "
            f"realizzazione del programma di bilancio {peg_periodo} - "
            f"approvazione PEG {peg_periodo}\";"
        )
    
    return "\n\n".join(righe) + "\n"


def genera_sezione_durc(dati: Dict) -> str:
    """
    Genera la clausola DATO ATTO relativa al DURC.
    Include: protocollo, esito e scadenza validità.
    """
    if not dati.get("durc_protocollo"):
        return ""
    
    durc_scadenza_str = formatta_data_breve(dati.get("durc_scadenza"))
    esito = dati.get("durc_esito", "REGOLARE")
    ragione_sociale = dati.get('ragione_sociale', '')
    
    testo = (
        f"DATO ATTO altresì che per l'operatore economico {ragione_sociale} "
        f"è stato acquisito il Documento Unico di Regolarità Contributiva (DURC) "
        f"Prot. {dati['durc_protocollo']} e che lo stesso risulta {esito}"
    )
    
    if durc_scadenza_str:
        testo += f" con scadenza validità il {durc_scadenza_str}"
    
    testo += ";"
    
    return testo


def genera_sezione_altre_informazioni(dati: Dict) -> str:
    """
    Genera la sezione ALTRE INFORMAZIONI con:
    - Responsabile del procedimento
    - Modalità di ricorso (TAR e ricorso straordinario)
    - Dichiarazione conflitto interessi
    - Nota pubblicazione trasparenza
    """
    righe = []
    
    # Verifica se includere la sezione
    includi_ricorsi = dati.get("includi_ricorsi", False)
    includi_conflitto = dati.get("includi_conflitto", False)
    
    if not (includi_ricorsi or includi_conflitto):
        return ""
    
    righe.append("")
    righe.append("_" * 70)
    righe.append("")
    righe.append("ALTRE INFORMAZIONI:")
    righe.append("")
    
    # Responsabile del procedimento
    nome_resp = dati.get('nome_responsabile', 'il sottoscritto')
    righe.append(
        f"Responsabile del procedimento (artt. 4-6 legge 241/1990): {nome_resp}."
    )
    
    # Ricorsi
    if includi_ricorsi:
        tar = dati.get("tar_competente", "TAR competente per territorio")
        righe.append("")
        righe.append(
            f"Ricorsi: ai sensi dell'art. 3, comma 4, della legge 241/1990, "
            f"contro il presente atto è ammesso il ricorso al {tar} nel termine "
            f"di 60 giorni dalla pubblicazione (d.lgs. 2 luglio 2010, n. 104) o, "
            f"in alternativa, il ricorso straordinario al Presidente della Repubblica "
            f"nel termine di 120 giorni dalla pubblicazione, nei modi previsti "
            f"dall'art. 8 e seguenti del d.P.R. 24 novembre 1971, n. 1199."
        )
    
    # Conflitto di interessi
    if includi_conflitto:
        righe.append("")
        righe.append(
            "Conflitto d'interessi: in relazione all'adozione del presente atto, "
            "per il sottoscritto:"
        )
        righe.append(
            "[X] non ricorre conflitto, anche potenziale, di interessi a norma "
            "dell'art. 6-bis della legge 241/1990, dell'art. 6 del DPR 62/2013 "
            "e del Codice di comportamento dell'Ente;"
        )
        righe.append(
            "[X] non ricorre l'obbligo di astensione, previsto dall'art. 7 del "
            "DPR 62/2013 e del Codice di comportamento dell'Ente."
        )
    
    # Pubblicazione trasparenza
    righe.append("")
    righe.append("Pubblicazione nella sezione \"Trasparenza\" (D.lgs. n. 33/2013)")
    righe.append(
        "I dati della presente determinazione saranno pubblicati nella sezione "
        "Amministrazione Trasparente/Provvedimenti."
    )
    
    return "\n".join(righe)


def genera_visto_regolarita_contabile(dati: Dict) -> str:
    """
    Genera la sezione del VISTO DI REGOLARITÀ CONTABILE.
    Ex art. 183 comma 7 del D.Lgs. 267/2000 (TUEL).
    """
    if not dati.get("includi_visto", False):
        return ""
    
    visto_nome = dati.get("visto_nome", "[Nome Responsabile Finanziario]")
    visto_qualifica = dati.get(
        "visto_qualifica", 
        "Responsabile dell'Area Economico-Finanziaria"
    )
    data_atto = dati.get("data_atto")
    data_str = formatta_data_breve(data_atto) if data_atto else "[Data]"
    comune = dati.get("comune", "[Comune]")
    
    # Estrai solo il nome del comune senza "Comune di"
    if comune.lower().startswith("comune di "):
        nome_comune = comune[10:]
    else:
        nome_comune = comune
    
    testo = f"""

{'_' * 70}

VISTO DI REGOLARITÀ CONTABILE

Si appone il visto di regolarità contabile attestante la copertura finanziaria della presente determinazione, ai sensi dell'art. 183 comma VII del D.lgs. 267/2000 e s.m.i., che pertanto in data odierna, diviene esecutiva.

{nome_comune} lì {data_str}

{visto_qualifica}

f.to {visto_nome}
"""
    
    return testo


def genera_attestato_pubblicazione(dati: Dict) -> str:
    """
    Genera l'ATTESTATO DI PUBBLICAZIONE all'Albo Pretorio.
    """
    # Includi solo se è richiesto il visto (per coerenza)
    if not dati.get("includi_visto", False):
        return ""
    
    testo = f"""
{'_' * 70}

ATTESTATO DI PUBBLICAZIONE

Della su estesa determinazione viene iniziata la pubblicazione all'Albo Pretorio per 15 giorni consecutivi dal _____________ al _____________

Il Responsabile del Servizio

f.to _______________________
"""
    return testo


# =============================================================================
# MOTORE LOGICO PRINCIPALE
# =============================================================================

def assembla_visti(dati: Dict) -> list:
    visti = []
    
    visti.append(f"VISTO {CHUNKS['art_50_affidamento']};")
    visti.append(f"VISTO {CHUNKS['principi_art_1']};")
    visti.append(f"VISTO {CHUNKS['art_15_rup']};")
    
    imponibile = float(dati.get("imponibile", 0))
    
    # MEPA
    if imponibile >= 5000:
        visti.append(f"VISTO {CHUNKS['obbligo_mepa_5000']};")
    
    # ROTAZIONE E MOTIVAZIONE SCELTA
    if imponibile < 5000:
        visti.append(f"VISTO {CHUNKS['deroga_rotazione_5000']};")
    
    # Gestione Regolamento
    if dati.get("regolamento_comunale"):
        regolamento_testo = CHUNKS['regolamento_comunale'].format(
            delibera_riferimento=dati.get("regolamento_comunale", "")
        )
        visti.append(f"VISTO {regolamento_testo};")
    
    # Garanzia / CCNL
    if dati.get("piccola_fornitura", False):
        visti.append(f"RITENUTO che {CHUNKS['esenzione_garanzia_ccnl']};")
    
    visti.append(f"DATO ATTO che {CHUNKS['art_52_requisiti']};")
    visti.append(f"DATO ATTO che {CHUNKS['art_16_conflitto_interessi']};")
    visti.append(f"DATO ATTO che {CHUNKS['tracciabilita_l136']};")
    
    # GDPR
    visti.append(f"DATO ATTO che {CHUNKS['gdpr_clause']};")
    
    visti.append(f"CONSIDERATO che {CHUNKS['art_18_forma_contratto']};")
    
    return visti


def genera_premesse(dati: Dict) -> str:
    importi = calcola_importi(dati.get("imponibile", 0), dati.get("aliquota_iva", 22))
    
    data_prev = dati.get("data_preventivo")
    data_prev_str = formatta_data(data_prev) if isinstance(data_prev, datetime) else str(data_prev)
    
    premesse = []
    
    # 0. RICHIAMI BILANCIO (NUOVO v4.0)
    richiami_bilancio = genera_richiami_bilancio(dati)
    if richiami_bilancio:
        premesse.append(richiami_bilancio)
    
    # 1. Narrativa
    premesse.append(f"VERIFICATA la necessità di procedere all'acquisizione di quanto in oggetto, in considerazione di quanto segue: {dati.get('motivazione', '')};")
    premesse.append(f"CONSIDERATO che la finalità che si intende perseguire con il presente affidamento è: {dati.get('finalita', '')};")
    
    # 2. Fornitore e Offerta
    tipo_doc = dati.get("tipo_documento", "preventivo")
    premesse.append(
        f"DATO ATTO che l'operatore economico {dati.get('ragione_sociale', '')} "
        f"con sede in {dati.get('indirizzo', '')}, {dati.get('cap', '')} {dati.get('citta', '')} ({dati.get('provincia_fornitore', '')}), "
        f"P.IVA/C.F. {dati.get('piva_cf', '')}, ha presentato {tipo_doc} "
        f"n. {dati.get('numero_preventivo', '')} del {data_prev_str} "
        f"per un importo di {formatta_importo(importi['imponibile'])} oltre IVA al {dati.get('aliquota_iva', 22)}% "
        f"pari a {formatta_importo(importi['iva'])}, per un totale complessivo di {formatta_importo(importi['totale'])};"
    )
    
    # 3. Normativa Base
    premesse.append("CONSIDERATO che l'importo dell'affidamento è inferiore a € 140.000,00 e pertanto rientra nella fattispecie prevista dall'art. 50, comma 1, lett. b) del D. Lgs. n. 36/2023;")
    
    # 4. Motivazione Scelta e Rotazione
    criterio = dati.get("criterio_scelta", "esperienza specifica nel settore")
    uscente = dati.get("operatore_uscente", False)
    
    if uscente:
        premesse.append(
            f"RITENUTO che, pur trattandosi di gestore uscente, la deroga al principio di rotazione è ampiamente giustificata "
            f"dalla necessità di garantire {criterio}, nonché dall'assenza di alternative altrettanto vantaggiose in termini "
            f"di costi/benefici e tempi di avviamento, in conformità a quanto previsto dall'art. 49 c. 6 del D.Lgs. 36/2023;"
        )
    else:
        premesse.append(
            f"RITENUTO che la scelta del suddetto operatore economico è motivata da {criterio}, "
            f"elementi che garantiscono l'affidabilità nell'esecuzione della prestazione richiesta;"
        )

    # 5. Congruità
    premesse.append(f"RITENUTO altresì che {CHUNKS['congruita_economica']};")

    # 6. Visti Normativi
    premesse.extend(assembla_visti(dati))
    
    # 7. DURC (NUOVO v4.0)
    sezione_durc = genera_sezione_durc(dati)
    if sezione_durc:
        premesse.append(sezione_durc)
    
    # 8. Dati Amministrativi
    premesse.append(f"DATO ATTO che è stato acquisito il Codice Identificativo di Gara (CIG): {dati.get('cig', '')};")
    
    rup_nome = f"{dati.get('rup_nome', '')} {dati.get('rup_cognome', '')}"
    premesse.append(f"DATO ATTO che il Responsabile Unico del Progetto (RUP) è individuato in {rup_nome}, {dati.get('rup_qualifica', '')};")
    
    premesse.append(f"VERIFICATA la disponibilità finanziaria sul Capitolo {dati.get('capitolo_bilancio', '')} del Bilancio {dati.get('esercizio_finanziario', '')};")
    premesse.append(f"ATTESTATO {CHUNKS['dichiarazioni_responsabile']};")
    
    premesse.append(f"RITENUTO pertanto di procedere all'affidamento diretto ai sensi dell'art. 50, comma 1, lett. b) del D. Lgs. n. 36/2023 del servizio/fornitura in oggetto all'operatore economico {dati.get('ragione_sociale', '')};")
    
    return "\n\n".join(premesse)


def genera_dispositivo(dati: Dict) -> str:
    importi = calcola_importi(dati.get("imponibile", 0), dati.get("aliquota_iva", 22))
    
    dispositivo = []
    dispositivo.append("D E T E R M I N A")
    
    # Punto 1: Affidamento e Durata
    durata = dati.get("durata_servizio", "tempi strettamente necessari all'esecuzione")
    
    dispositivo.append(
        f"1. DI AFFIDARE, ai sensi dell'art. 50, comma 1, lett. b) del D. Lgs. n. 36/2023, "
        f"all'operatore economico {dati.get('ragione_sociale', '')} "
        f"(P.IVA/C.F. {dati.get('piva_cf', '')}), con sede in {dati.get('indirizzo', '')}, "
        f"{dati.get('cap', '')} {dati.get('citta', '')} ({dati.get('provincia_fornitore', '')}), "
        f"il servizio/fornitura indicato in oggetto, per la durata di {durata} e per l'importo complessivo di "
        f"{formatta_importo(importi['totale'])} (di cui imponibile {formatta_importo(importi['imponibile'])} "
        f"e IVA {formatta_importo(importi['iva'])});"
    )
    
    dispositivo.append(
        f"2. DI IMPEGNARE la somma complessiva di {formatta_importo(importi['totale'])} "
        f"al Capitolo {dati.get('capitolo_bilancio', '')} del Bilancio "
        f"{dati.get('esercizio_finanziario', '')}, dando atto che il pagamento "
        f"avverrà a seguito di presentazione di regolare fattura elettronica e previa verifica "
        f"della regolarità contributiva (DURC) e fiscale;"
    )
    
    dispositivo.append(f"3. DI STIPULARE il contratto mediante corrispondenza secondo l'uso del commercio ai sensi dell'art. 18, comma 1, ultimo periodo del D. Lgs. n. 36/2023;")
    
    dispositivo.append(f"4. DI DARE ATTO che il Codice Identificativo di Gara (CIG) assegnato alla presente procedura è: {dati.get('cig', '')};")
    
    rup_nome = f"{dati.get('rup_nome', '')} {dati.get('rup_cognome', '')}"
    dispositivo.append(f"5. DI DARE ATTO che il Responsabile Unico del Progetto (RUP) è {rup_nome}, {dati.get('rup_qualifica', '')};")
    
    dispositivo.append(f"6. DI DARE ATTO che l'affidatario assume tutti gli obblighi di tracciabilità dei flussi finanziari di cui all'art. 3 della Legge n. 136/2010 e ss.mm.ii.;")
    
    # Pubblicità e Trasparenza
    dispositivo.append(f"7. DI DISPORRE la pubblicazione del presente provvedimento nella sezione \"Amministrazione Trasparente\" e la trasmissione dei dati alla BDNCP tramite Piattaforma Certificata (PCP) secondo le specifiche tecniche ANAC vigenti;")
    
    dispositivo.append(f"8. DI DARE ATTO che la presente determinazione è immediatamente eseguibile ai sensi dell'art. 183 del D. Lgs. n. 267/2000 (TUEL).")
    
    # SEZIONI FINALI (NUOVO v4.0)
    altre_info = genera_sezione_altre_informazioni(dati)
    if altre_info:
        dispositivo.append(altre_info)
    
    return "\n\n".join(dispositivo)


def genera_chiusura(dati: Dict) -> str:
    """
    Genera la parte di chiusura del documento con visto contabile e attestato.
    (NUOVO v4.0)
    """
    chiusura = []
    
    # Visto di regolarità contabile
    visto = genera_visto_regolarita_contabile(dati)
    if visto:
        chiusura.append(visto)
    
    # Attestato di pubblicazione
    attestato = genera_attestato_pubblicazione(dati)
    if attestato:
        chiusura.append(attestato)
    
    return "\n".join(chiusura)


def genera_testo_completo(dati: Dict) -> Tuple[str, str]:
    """
    Funzione principale che genera il testo completo della determina.
    Restituisce una tupla (premesse, dispositivo).
    
    v4.0: Include sezioni bilancio, DURC, visto contabile, ricorsi.
    """
    premesse = genera_premesse(dati)
    dispositivo = genera_dispositivo(dati)
    
    # Aggiungi chiusura (visto contabile + attestato) al dispositivo
    chiusura = genera_chiusura(dati)
    if chiusura:
        dispositivo += chiusura
    
    return premesse, dispositivo


def valida_dati(dati: Dict) -> Tuple[bool, list]:
    """
    Valida i dati obbligatori per la generazione della determina.
    """
    errori = []
    campi_obbligatori = [
        ("ragione_sociale", "Ragione Sociale"),
        ("piva_cf", "P.IVA / Codice Fiscale"),
        ("imponibile", "Importo imponibile"),
        ("cig", "CIG"),
        ("capitolo_bilancio", "Capitolo"),
        ("motivazione", "Motivazione"),
        ("oggetto", "Oggetto"),
        ("durata_servizio", "Durata del Servizio")
    ]
    
    for campo, nome in campi_obbligatori:
        valore = dati.get(campo)
        if valore is None or (isinstance(valore, str) and not valore.strip()):
            errori.append(f"Il campo '{nome}' è obbligatorio")
    
    return len(errori) == 0, errori
