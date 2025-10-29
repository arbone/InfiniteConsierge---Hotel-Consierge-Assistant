"""
Sistema di Routing Intelligente per Hotel Concierge Bot
Classifica gli intent degli ospiti usando pattern matching e keywords
"""
import re
from typing import Literal

Intent = Literal['hotel_info', 'service_request', 'recommendation', 'special_request', 'complaint', 'emergency']


def classify_guest_intent(guest_message: str) -> Intent:
    """
    Classifica l'intent dell'ospite analizzando il messaggio.
    
    Args:
        guest_message: Messaggio dell'ospite da classificare
    
    Returns:
        str: Intent classificato tra:
            - 'hotel_info': domande su servizi, orari, facility dell'hotel
            - 'service_request': richieste di servizio (room service, pulizie, etc)
            - 'recommendation': richiesta di consigli su ristoranti, attrazioni
            - 'special_request': richieste speciali non standard
            - 'complaint': lamentele o problemi
            - 'emergency': situazioni di emergenza
    
    Examples:
        >>> classify_guest_intent("A che ora è la colazione?")
        'hotel_info'
        >>> classify_guest_intent("Vorrei ordinare del room service")
        'service_request'
        >>> classify_guest_intent("Consigli un ristorante?")
        'recommendation'
    
    Note:
        La funzione usa pattern matching con priorità:
        1. Emergency (massima priorità)
        2. Complaint
        3. Service Request
        4. Recommendation
        5. Hotel Info
        6. Special Request (fallback)
    """
    if not guest_message or not isinstance(guest_message, str):
        return 'special_request'
    
    message_lower = guest_message.lower()
    
    # Priority 1: EMERGENCY - Situazioni urgenti
    emergency_patterns = [
        r'\b(emergenza|emergency|aiuto|help|urgente|urgent)\b',
        r'\b(incendio|fire|fuoco)\b',
        r'\b(furto|rub|stolen|theft)\b',
        r'\b(malato|sick|infortunio|injured|ambulanza|ambulance)\b',
        r'\b(pericolo|danger|attacco|attack)\b'
    ]
    
    for pattern in emergency_patterns:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return 'emergency'
    
    # Priority 2: COMPLAINT - Lamentele e problemi
    complaint_patterns = [
        r'\b(lament|complaint|reclamo|problem)\b',
        r'\b(non funziona|not working|rotto|broken|guasto)\b',
        r'\b(sporco|dirty|pulito male|not clean)\b',
        r'\b(rumore|noise|rumoros)\b',
        r'\b(freddo|caldo|troppo|too hot|too cold)\b',
        r'\b(insoddisfatt|unsatisfied|delus|disappointed)\b',
        r'\b(pessim|terribil|awful|terrible)\b'
    ]
    
    complaint_score = sum(1 for p in complaint_patterns if re.search(p, message_lower, re.IGNORECASE))
    
    # Priority 3: SERVICE REQUEST - Richieste di servizio
    service_patterns = [
        r'\b(vorrei|would like|desidero|wish|voglio|want)\b',
        r'\b(room service|servizio in camera|order|ordinare)\b',
        r'\b(pulizie|housekeeping|pulire|clean|towel|asciugaman)\b',
        r'\b(manutenzione|maintenance|riparazione|repair|fix)\b',
        r'\b(prenotare|prenota|book|reservation|reserve)\b',
        r'\b(spa|massaggio|massage)\b',
        r'\b(transfer|taxi|trasporto)\b',
        r'\b(chiamare|call|contattare|contact)\b'
    ]
    
    service_score = sum(1 for p in service_patterns if re.search(p, message_lower, re.IGNORECASE))
    
    # Priority 4: RECOMMENDATION - Consigli e raccomandazioni
    recommendation_patterns = [
        r'\b(consiglio|consiglia|recommend|suggest|sugger)\b',
        r'\b(ristorante|restaurant|mangiare|eat|cena|dinner|pranzo|lunch)\b',
        r'\b(visitare|visit|vedere|see|cosa fare|what to do)\b',
        r'\b(attrazione|attraction|museo|museum|monumento)\b',
        r'\b(dove|where|come arriv|how to get)\b',
        r'\b(shopping|negozi|shop)\b',
        r'\b(migliore|best|top)\b'
    ]
    
    recommendation_score = sum(1 for p in recommendation_patterns if re.search(p, message_lower, re.IGNORECASE))
    
    # Priority 5: HOTEL INFO - Informazioni sull'hotel
    info_patterns = [
        r'\b(orario|orari|hour|quando|when|tempo)\b',
        r'\b(c\'è|ci sono|is there|are there|have you|avete)\b',
        r'\b(informazione|information|info)\b',
        r'\b(check.?in|check.?out)\b',
        r'\b(wifi|internet|password)\b',
        r'\b(colazione|breakfast|cena|dinner)\b',
        r'\b(parcheggio|parking)\b',
        r'\b(servizio|service|facility)\b',
        r'\b(quanto cost|how much|prezzo|price)\b'
    ]
    
    info_score = sum(1 for p in info_patterns if re.search(p, message_lower, re.IGNORECASE))
    
    # Decision logic basata su score
    scores = {
        'complaint': complaint_score,
        'service_request': service_score,
        'recommendation': recommendation_score,
        'hotel_info': info_score
    }
    
    max_score = max(scores.values())
    
    # Se nessun match, è special_request
    if max_score == 0:
        return 'special_request'
    
    # In caso di parità, usa priorità predefinita
    if scores['complaint'] == max_score and max_score > 0:
        return 'complaint'
    elif scores['service_request'] == max_score:
        return 'service_request'
    elif scores['recommendation'] == max_score:
        return 'recommendation'
    elif scores['hotel_info'] == max_score:
        return 'hotel_info'
    else:
        return 'special_request'


def get_intent_confidence(guest_message: str) -> tuple[Intent, float]:
    """
    Restituisce l'intent con livello di confidenza.
    
    Args:
        guest_message: Messaggio dell'ospite
    
    Returns:
        tuple: (intent, confidence_score) dove confidence è tra 0.0 e 1.0
    """
    intent = classify_guest_intent(guest_message)
    
    # Calcolo confidenza semplificato basato su match count
    message_lower = guest_message.lower()
    
    # Pattern per l'intent rilevato
    pattern_map = {
        'emergency': [r'\b(emergenza|emergency|aiuto|urgente)\b'],
        'complaint': [r'\b(lament|problem|non funziona|sporco|rumore)\b'],
        'service_request': [r'\b(vorrei|room service|prenotare|spa|transfer)\b'],
        'recommendation': [r'\b(consiglio|ristorante|visitare|dove)\b'],
        'hotel_info': [r'\b(orario|c\'è|check.?in|wifi|colazione)\b']
    }
    
    if intent in pattern_map:
        matches = sum(1 for p in pattern_map[intent] if re.search(p, message_lower, re.IGNORECASE))
        confidence = min(0.5 + (matches * 0.2), 1.0)
    else:
        confidence = 0.3  # special_request ha confidenza bassa
    
    return intent, confidence
