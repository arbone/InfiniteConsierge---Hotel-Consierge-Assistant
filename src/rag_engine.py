"""
RAG Engine per Knowledge Base Hotel
Gestisce ricerca semantica e generazione risposte per il concierge bot
"""
import json
from typing import List, Dict, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def search_hotel_knowledge(
    query: str, 
    kb_data: list,
    category: Optional[str] = None
) -> list:
    """
    Cerca nella knowledge base hotel/città usando TF-IDF e cosine similarity.
    
    Args:
        query: Query di ricerca dell'ospite
        kb_data: Lista di dizionari con knowledge base
                 Formato: [{"id": str, "category": str, "question": str, "answer": str}, ...]
        category: Filtra per categoria specifica (opzionale)
                  Valori: 'hotel_services', 'local_attractions', 'dining', 
                         'transport', 'policies', 'spa_wellness'
    
    Returns:
        list: Lista di documenti rilevanti ordinati per relevance score.
              Ogni elemento contiene: {id, category, question, answer, score}
    
    Examples:
        >>> kb = load_knowledge_base()
        >>> results = search_hotel_knowledge("orari colazione", kb, category="hotel_services")
        >>> print(results[0]['answer'])
        'La colazione è servita dalle 7:00 alle 10:30...'
    
    Note:
        - Usa TF-IDF vectorization per similarity search
        - Restituisce top 5 risultati
        - Score normalizzato tra 0 e 1
    """
    if not kb_data or not query:
        return []
    
    try:
        # Filtra per categoria se specificata
        filtered_kb = kb_data
        if category:
            filtered_kb = [doc for doc in kb_data if doc.get('category') == category]
        
        if not filtered_kb:
            return []
        
        # Prepara i testi per TF-IDF
        # Combina question + answer per search migliore
        documents = [
            f"{doc.get('question', '')} {doc.get('answer', '')}" 
            for doc in filtered_kb
        ]
        
        # TF-IDF Vectorization
        vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),  # unigrams e bigrams
            max_features=500,
            stop_words=None  # Manteniamo stop words per italiano
        )
        
        # Fit sui documenti
        tfidf_matrix = vectorizer.fit_transform(documents)
        
        # Transform query
        query_vector = vectorizer.transform([query.lower()])
        
        # Calcola cosine similarity
        similarities = cosine_similarity(query_vector, tfidf_matrix)[0]
        
        # Ottieni top k risultati
        top_k = 5
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Build results
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Solo risultati con score > 0
                doc = filtered_kb[idx].copy()
                doc['score'] = float(similarities[idx])
                results.append(doc)
        
        return results
    
    except Exception as e:
        print(f"Error in search_hotel_knowledge: {e}")
        # Fallback: simple keyword match
        return _fallback_keyword_search(query, kb_data, category)


def _fallback_keyword_search(
    query: str,
    kb_data: list,
    category: Optional[str] = None
) -> list:
    """Fallback search usando simple keyword matching"""
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    results = []
    for doc in kb_data:
        if category and doc.get('category') != category:
            continue
        
        doc_text = f"{doc.get('question', '')} {doc.get('answer', '')}".lower()
        doc_words = set(doc_text.split())
        
        # Calcola intersection
        common_words = query_words.intersection(doc_words)
        if common_words:
            score = len(common_words) / len(query_words)
            doc_copy = doc.copy()
            doc_copy['score'] = score
            results.append(doc_copy)
    
    # Ordina per score
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:5]


def generate_concierge_response(
    query: str,
    context: List[Dict],
    guest_language: str = 'it'
) -> str:
    """
    Genera risposta in stile concierge professionale basata sul contesto.
    
    Args:
        query: Domanda originale dell'ospite
        context: Lista di documenti rilevanti dalla KB (output di search_hotel_knowledge)
        guest_language: Lingua dell'ospite ('it' o 'en')
    
    Returns:
        str: Risposta formattata in stile concierge professionale
    
    Examples:
        >>> results = search_hotel_knowledge("orari colazione", kb)
        >>> response = generate_concierge_response(
        ...     "A che ora è la colazione?",
        ...     results,
        ...     guest_language='it'
        ... )
        >>> print(response)
    
    Note:
        - Se context è vuoto, restituisce messaggio di fallback
        - Usa il documento con score più alto
        - Aggiunge informazioni correlate se disponibili
        - Stile: formale, cortese, chiaro
    """
    if not context:
        # No relevant information found
        if guest_language == 'it':
            return (
                "Mi dispiace, non ho trovato informazioni specifiche per la sua richiesta. "
                "Posso metterla in contatto con il nostro concierge umano che sarà lieto di assisterla. "
                "Può anche contattare la reception al numero interno 0."
            )
        else:
            return (
                "I apologize, I couldn't find specific information for your request. "
                "I can connect you with our human concierge who will be happy to assist you. "
                "You can also contact the reception at internal number 0."
            )
    
    # Usa il documento con score più alto
    main_doc = context[0]
    answer = main_doc.get('answer', '')
    
    if guest_language == 'it':
        # Risposta in italiano
        response = f"{answer}\n\n"
        
        # Aggiungi informazioni correlate se ci sono altri risultati rilevanti
        if len(context) > 1 and context[1].get('score', 0) > 0.3:
            response += "📌 Informazioni correlate:\n"
            for i, doc in enumerate(context[1:3], 1):
                if doc.get('score', 0) > 0.25:
                    response += f"• {doc.get('question', 'Info')}\n"
        
        # Chiusura cortese
        response += "\nSono a disposizione per ulteriori informazioni. Come posso esserle ancora utile?"
        
    else:
        # Risposta in inglese (translation would require API)
        response = f"{answer}\n\n"
        
        if len(context) > 1 and context[1].get('score', 0) > 0.3:
            response += "📌 Related information:\n"
            for i, doc in enumerate(context[1:3], 1):
                if doc.get('score', 0) > 0.25:
                    response += f"• {doc.get('question', 'Info')}\n"
        
        response += "\nI'm at your disposal for further information. How else may I assist you?"
    
    return response


def load_knowledge_base(kb_path: str = "data/hotel_knowledge_base.json") -> list:
    """
    Carica la knowledge base da file JSON.
    
    Args:
        kb_path: Path al file JSON della knowledge base
    
    Returns:
        list: Knowledge base caricata
    
    Raises:
        FileNotFoundError: Se il file non esiste
        json.JSONDecodeError: Se il file non è un JSON valido
    """
    try:
        with open(kb_path, 'r', encoding='utf-8') as f:
            kb_data = json.load(f)
        return kb_data
    except FileNotFoundError:
        raise FileNotFoundError(f"Knowledge base file not found: {kb_path}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in knowledge base: {e}", e.doc, e.pos)


def get_categories_summary(kb_data: list) -> Dict[str, int]:
    """
    Restituisce statistiche sulle categorie nella KB.
    
    Args:
        kb_data: Knowledge base data
    
    Returns:
        dict: {category: count}
    """
    categories = {}
    for doc in kb_data:
        cat = doc.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
    return categories
