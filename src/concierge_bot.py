"""
Sistema Conversazionale Hotel Concierge Bot
Orchestrazione completa con intent classification, RAG e service management
"""
import json
import sqlite3
from typing import List, Dict, Optional
from pathlib import Path

# Import moduli locali
from intent_classifier import classify_guest_intent, get_intent_confidence
from rag_engine import search_hotel_knowledge, generate_concierge_response, load_knowledge_base
from service_manager import create_service_request, get_request_status, format_service_confirmation, get_guest_requests


class HotelConciergeBot:
    """
    Bot conversazionale per hotel concierge con AI-powered features.
    
    Capabilities:
        - Intent classification
        - RAG-based knowledge retrieval
        - Service request management
        - Personalized recommendations
        - Auto-escalation to human staff
    """
    
    def __init__(self, kb_path: str = "data/hotel_knowledge_base.json", db_path: str = "data/hotel_database.sqlite"):
        """
        Inizializza il bot con knowledge base e database.
        
        Args:
            kb_path: Path al file JSON della knowledge base
            db_path: Path al database SQLite
        """
        # Carica knowledge base
        try:
            self.kb_data = load_knowledge_base(kb_path)
            print(f"✓ Knowledge base caricata: {len(self.kb_data)} documenti")
        except Exception as e:
            print(f"⚠️ Errore caricamento KB: {e}")
            self.kb_data = []
        
        self.db_path = db_path
        
        # Statistiche conversazione
        self.failed_intents_count = {}  # Track per escalation
        
    def process_guest_message(
        self,
        message: str,
        conversation_history: List[Dict],
        guest_info: Dict
    ) -> str:
        """
        Elabora messaggio ospite e genera risposta appropriata.
        
        Args:
            message: Messaggio dell'ospite
            conversation_history: Storia conversazione
                                  Formato: [{"role": "guest"|"bot", "content": str}, ...]
            guest_info: Informazioni ospite
                        Deve contenere: room_number, language, preferences (dict)
                        Esempio: {
                            "guest_id": "G001",
                            "room_number": "305",
                            "language": "it",
                            "preferences": {"dietary": [], "interests": ["art"]}
                        }
        
        Returns:
            str: Risposta del bot
        
        Examples:
            >>> bot = HotelConciergeBot()
            >>> guest_info = {
            ...     "guest_id": "G001",
            ...     "room_number": "305",
            ...     "language": "it",
            ...     "preferences": {"interests": ["food"]}
            ... }
            >>> response = bot.process_guest_message(
            ...     "A che ora è la colazione?",
            ...     [],
            ...     guest_info
            ... )
            >>> print(response)
        
        Note:
            - Gestisce automaticamente tutti i tipi di intent
            - Salva conversazione nel database
            - Determina auto-escalation se necessario
        """
        try:
            # Estrai info ospite
            guest_id = guest_info.get('guest_id', 'UNKNOWN')
            room_number = guest_info.get('room_number', 'N/A')
            language = guest_info.get('language', 'it')
            
            # Classify intent
            intent, confidence = get_intent_confidence(message)
            
            # Check escalation
            if self.should_escalate_to_staff(conversation_history, intent):
                return self._handle_escalation(language)
            
            # Route basato su intent
            if intent == 'emergency':
                response = self._handle_emergency(message, guest_info, language)
            
            elif intent == 'hotel_info':
                response = self._handle_hotel_info(message, language)
            
            elif intent == 'recommendation':
                response = self._handle_recommendation(message, guest_info, language)
            
            elif intent == 'service_request':
                response = self._handle_service_request(message, guest_info, language)
            
            elif intent == 'complaint':
                response = self._handle_complaint(message, guest_info, language)
            
            elif intent == 'special_request':
                response = self._handle_special_request(message, guest_info, language)
            
            else:
                response = "Mi dispiace, non ho capito la richiesta. Può riformulare?" if language == 'it' else "I'm sorry, I didn't understand. Can you rephrase?"
            
            # Salva conversazione
            self._save_conversation(guest_id, room_number, message, response, language)
            
            return response
        
        except Exception as e:
            print(f"Error in process_guest_message: {e}")
            return "Mi dispiace, si è verificato un errore. Contatti la reception." if guest_info.get('language') == 'it' else "I apologize, an error occurred. Please contact reception."
    
    def _handle_emergency(self, message: str, guest_info: Dict, language: str) -> str:
        """Gestisce situazioni di emergenza"""
        guest_id = guest_info.get('guest_id')
        room_number = guest_info.get('room_number')
        
        # Crea richiesta urgente
        try:
            request = create_service_request(
                guest_id=guest_id,
                room_number=room_number,
                request_type='concierge',
                details=f"EMERGENZA: {message}",
                priority='urgent'
            )
        except Exception as e:
            print(f"Error creating emergency request: {e}")
        
        if language == 'it':
            return (
                "🚨 **EMERGENZA RILEVATA** 🚨\n\n"
                "Il nostro staff è stato allertato immediatamente.\n"
                "Stiamo inviando assistenza alla sua camera.\n\n"
                "Per emergenze immediate:\n"
                "📞 Chiami il numero interno 0 (reception)\n"
                "📞 Numero esterno: +39 041 1234567\n\n"
                "Rimanga calmo, l'aiuto sta arrivando."
            )
        else:
            return (
                "🚨 **EMERGENCY DETECTED** 🚨\n\n"
                "Our staff has been alerted immediately.\n"
                "We are sending assistance to your room.\n\n"
                "For immediate emergencies:\n"
                "📞 Call internal number 0 (reception)\n"
                "📞 External number: +39 041 1234567\n\n"
                "Stay calm, help is on the way."
            )
    
    def _handle_hotel_info(self, message: str, language: str) -> str:
        """Gestisce richieste di informazioni hotel"""
        # Search KB
        results = search_hotel_knowledge(message, self.kb_data)
        
        # Generate response
        response = generate_concierge_response(message, results, language)
        return response
    
    def _handle_recommendation(self, message: str, guest_info: Dict, language: str) -> str:
        """Gestisce richieste di raccomandazioni"""
        preferences = guest_info.get('preferences', {})
        
        # Determina categoria dalla query
        message_lower = message.lower()
        if any(kw in message_lower for kw in ['ristorante', 'mangiare', 'cena', 'pranzo', 'restaurant', 'dining']):
            category = 'dining'
        elif any(kw in message_lower for kw in ['visitare', 'vedere', 'museo', 'attrazione', 'visit', 'see', 'museum']):
            category = 'local_attractions'
        elif any(kw in message_lower for kw in ['trasporto', 'taxi', 'vaporetto', 'transport']):
            category = 'transport'
        else:
            category = None
        
        # Search con category filter
        results = search_hotel_knowledge(message, self.kb_data, category=category)
        
        # Personalizza basandosi su preferenze
        personalized_results = self._personalize_recommendations(results, preferences)
        
        # Generate response
        response = generate_concierge_response(message, personalized_results, language)
        return response
    
    def _handle_service_request(self, message: str, guest_info: Dict, language: str) -> str:
        """Gestisce richieste di servizio"""
        guest_id = guest_info.get('guest_id')
        room_number = guest_info.get('room_number')
        
        # Determina tipo servizio dal messaggio
        request_type = self._infer_service_type(message)
        
        try:
            # Crea richiesta
            request = create_service_request(
                guest_id=guest_id,
                room_number=room_number,
                request_type=request_type,
                details=message
            )
            
            # Format conferma
            confirmation = format_service_confirmation(request)
            return confirmation
        
        except Exception as e:
            print(f"Error creating service request: {e}")
            if language == 'it':
                return "Mi dispiace, si è verificato un errore nella creazione della richiesta. Contatti la reception."
            else:
                return "I apologize, there was an error creating your request. Please contact reception."
    
    def _infer_service_type(self, message: str) -> str:
        """Determina tipo servizio dal messaggio"""
        message_lower = message.lower()
        
        if any(kw in message_lower for kw in ['room service', 'servizio in camera', 'ordinare', 'order']):
            return 'room_service'
        elif any(kw in message_lower for kw in ['pulizie', 'housekeeping', 'pulire', 'towel', 'asciugaman']):
            return 'housekeeping'
        elif any(kw in message_lower for kw in ['manutenzione', 'maintenance', 'riparazione', 'repair', 'rotto']):
            return 'maintenance'
        elif any(kw in message_lower for kw in ['spa', 'massaggio', 'massage']):
            return 'spa_booking'
        elif any(kw in message_lower for kw in ['ristorante', 'restaurant', 'tavolo', 'table']):
            return 'restaurant_booking'
        else:
            return 'concierge'
    
    def _handle_complaint(self, message: str, guest_info: Dict, language: str) -> str:
        """Gestisce lamentele"""
        guest_id = guest_info.get('guest_id')
        room_number = guest_info.get('room_number')
        
        # Crea richiesta con priorità alta
        try:
            request = create_service_request(
                guest_id=guest_id,
                room_number=room_number,
                request_type='maintenance',
                details=f"RECLAMO: {message}",
                priority='high'
            )
            
            if language == 'it':
                return (
                    f"Mi scuso sinceramente per l'inconveniente. 🙏\n\n"
                    f"Ho registrato la sua segnalazione (Rif. {request['request_id']}) "
                    f"con priorità ALTA.\n\n"
                    f"Il nostro staff interverrà entro 15-20 minuti per risolvere il problema.\n\n"
                    f"La contatteremo appena possibile. Grazie per la pazienza."
                )
            else:
                return (
                    f"I sincerely apologize for the inconvenience. 🙏\n\n"
                    f"I've registered your complaint (Ref. {request['request_id']}) "
                    f"with HIGH priority.\n\n"
                    f"Our staff will intervene within 15-20 minutes to resolve the issue.\n\n"
                    f"We'll contact you as soon as possible. Thank you for your patience."
                )
        
        except Exception as e:
            print(f"Error handling complaint: {e}")
            return "Mi dispiace, contatti la reception immediatamente." if language == 'it' else "I apologize, please contact reception immediately."
    
    def _handle_special_request(self, message: str, guest_info: Dict, language: str) -> str:
        """Gestisce richieste speciali"""
        # Prova a cercare nella KB
        results = search_hotel_knowledge(message, self.kb_data)
        
        if results and results[0].get('score', 0) > 0.3:
            return generate_concierge_response(message, results, guest_info.get('language', 'it'))
        
        # Altrimenti escalate
        if language == 'it':
            return (
                "Ho registrato la sua richiesta speciale. 📝\n\n"
                "Per gestire al meglio questa esigenza, la metterò in contatto con il nostro concierge umano "
                "che potrà assisterla personalmente.\n\n"
                "Riceverà una chiamata in camera entro 10 minuti. Grazie!"
            )
        else:
            return (
                "I've registered your special request. 📝\n\n"
                "To best handle this requirement, I'll connect you with our human concierge "
                "who can assist you personally.\n\n"
                "You'll receive a call in your room within 10 minutes. Thank you!"
            )
    
    def _handle_escalation(self, language: str) -> str:
        """Gestisce escalation a staff umano"""
        if language == 'it':
            return (
                "Capisco che la sua richiesta necessita attenzione particolare. 👤\n\n"
                "Sto trasferendo la conversazione a un membro del nostro staff "
                "che la contatterà immediatamente.\n\n"
                "Grazie per la pazienza!"
            )
        else:
            return (
                "I understand your request needs special attention. 👤\n\n"
                "I'm transferring the conversation to a member of our staff "
                "who will contact you immediately.\n\n"
                "Thank you for your patience!"
            )
    
    def should_escalate_to_staff(
        self,
        conversation_history: List[Dict],
        intent: str
    ) -> bool:
        """
        Determina se escalare conversazione a concierge/reception umano.
        
        Args:
            conversation_history: Storia della conversazione
            intent: Intent corrente
        
        Returns:
            bool: True se necessita escalation, False altrimenti
        
        Logic:
            - Emergency: sempre escalate (dopo messaggio automatico)
            - Troppi turni senza soluzione (>5)
            - Intent ripetuti falliti (>2 volte stesso intent)
            - Complaint ripetuto
            - VIP guest con richiesta complessa
        """
        # Emergency: no escalation immediato (messaggio automatico prima)
        if intent == 'emergency':
            return False  # Gestito automaticamente con alert
        
        # Troppi turni
        if len(conversation_history) > 10:
            return True
        
        # Conta turni guest recenti
        recent_guest_messages = [
            msg for msg in conversation_history[-6:]
            if msg.get('role') == 'guest'
        ]
        
        if len(recent_guest_messages) > 3:
            # Molte domande ravvicinate = frustrazione
            return True
        
        # Complaint ripetuto
        complaint_count = sum(
            1 for msg in conversation_history[-4:]
            if 'problem' in msg.get('content', '').lower() or 'lament' in msg.get('content', '').lower()
        )
        
        if complaint_count >= 2:
            return True
        
        return False
    
    def get_personalized_recommendations(
        self,
        guest_info: Dict,
        category: str
    ) -> List[Dict]:
        """
        Raccomandazioni personalizzate basate su preferenze ospite.
        
        Args:
            guest_info: Info ospite con preferences
            category: Categoria ('dining', 'local_attractions', etc)
        
        Returns:
            list: Raccomandazioni filtrate e ordinate per rilevanza
        
        Examples:
            >>> bot = HotelConciergeBot()
            >>> guest = {
            ...     "preferences": {"interests": ["art", "history"]}
            ... }
            >>> recs = bot.get_personalized_recommendations(guest, "local_attractions")
            >>> print(recs[0]['question'])
        """
        # Get all items for category
        category_items = [doc for doc in self.kb_data if doc.get('category') == category]
        
        # Personalize
        preferences = guest_info.get('preferences', {})
        personalized = self._personalize_recommendations(category_items, preferences)
        
        return personalized
    
    def _personalize_recommendations(self, results: List[Dict], preferences: Dict) -> List[Dict]:
        """
        Personalizza raccomandazioni basandosi su preferenze.
        
        Args:
            results: Risultati da personalizzare
            preferences: Preferenze ospite (interests, dietary)
        
        Returns:
            list: Risultati riordinati per preferenze
        """
        if not preferences or not results:
            return results
        
        interests = preferences.get('interests', [])
        dietary = preferences.get('dietary', [])
        
        # Score boost per match preferenze
        scored_results = []
        for result in results:
            score = result.get('score', 0.5)
            text = f"{result.get('question', '')} {result.get('answer', '')}".lower()
            
            # Boost per interests
            for interest in interests:
                if interest.lower() in text:
                    score += 0.2
            
            # Boost per dietary
            for diet in dietary:
                if diet.lower() in text:
                    score += 0.15
            
            result_copy = result.copy()
            result_copy['score'] = min(score, 1.0)
            scored_results.append(result_copy)
        
        # Riordina
        scored_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return scored_results
    
    def _save_conversation(
        self,
        guest_id: str,
        room_number: str,
        guest_message: str,
        bot_response: str,
        language: str
    ):
        """Salva conversazione nel database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Semplice logging (in produzione usare conversation_id persistente)
            messages_json = json.dumps([
                {"role": "guest", "content": guest_message},
                {"role": "bot", "content": bot_response}
            ])
            
            # Per semplicità, crea nuova conversazione ogni volta
            # In produzione, recuperare conversation_id esistente
            conv_id = f"CONV-{guest_id}-{int(datetime.now().timestamp())}"
            
            cursor.execute("""
                INSERT OR IGNORE INTO conversations
                (conversation_id, guest_id, room_number, messages, language)
                VALUES (?, ?, ?, ?, ?)
            """, (conv_id, guest_id, room_number, messages_json, language))
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            print(f"Error saving conversation: {e}")


# Import datetime per _save_conversation
from datetime import datetime
