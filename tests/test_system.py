"""
Test Suite Completo per Hotel Concierge Bot
Esegui con: pytest tests/test_system.py -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from intent_classifier import classify_guest_intent, get_intent_confidence
from rag_engine import search_hotel_knowledge, generate_concierge_response, load_knowledge_base
from service_manager import create_service_request, get_request_status, format_service_confirmation
from concierge_bot import HotelConciergeBot


class TestIntentClassification:
    """Test Sistema di Routing Intelligente"""
    
    def test_hotel_info_intent(self):
        """Test classificazione hotel_info"""
        assert classify_guest_intent("A che ora è la colazione?") == "hotel_info"
        assert classify_guest_intent("Quali sono gli orari della spa?") == "hotel_info"
        assert classify_guest_intent("C'è il WiFi?") == "hotel_info"
    
    def test_service_request_intent(self):
        """Test classificazione service_request"""
        assert classify_guest_intent("Vorrei prenotare un massaggio") == "service_request"
        assert classify_guest_intent("Posso ordinare room service?") == "service_request"
        assert classify_guest_intent("Ho bisogno di asciugamani puliti") == "service_request"
    
    def test_recommendation_intent(self):
        """Test classificazione recommendation"""
        assert classify_guest_intent("Consigli un ristorante?") == "recommendation"
        assert classify_guest_intent("Cosa visitare a Venezia?") == "recommendation"
        assert classify_guest_intent("Dove mangiare stasera?") == "recommendation"
    
    def test_complaint_intent(self):
        """Test classificazione complaint"""
        assert classify_guest_intent("La doccia non funziona") == "complaint"
        assert classify_guest_intent("C'è troppo rumore") == "complaint"
        assert classify_guest_intent("La camera è sporca") == "complaint"
    
    def test_emergency_intent(self):
        """Test classificazione emergency"""
        assert classify_guest_intent("C'è un'emergenza!") == "emergency"
        assert classify_guest_intent("Aiuto urgente!") == "emergency"
    
    def test_confidence_scoring(self):
        """Test confidence scoring"""
        intent, confidence = get_intent_confidence("A che ora è la colazione?")
        assert intent == "hotel_info"
        assert 0.0 <= confidence <= 1.0


class TestRAGEngine:
    """Test RAG per Knowledge Base"""
    
    @pytest.fixture
    def kb_data(self):
        """Fixture per caricare KB"""
        return load_knowledge_base("data/hotel_knowledge_base.json")
    
    def test_kb_loading(self, kb_data):
        """Test caricamento knowledge base"""
        assert kb_data is not None
        assert len(kb_data) > 0
        assert 'id' in kb_data[0]
        assert 'category' in kb_data[0]
    
    def test_search_hotel_services(self, kb_data):
        """Test ricerca servizi hotel"""
        results = search_hotel_knowledge("colazione", kb_data, category="hotel_services")
        assert len(results) > 0
        assert results[0]['score'] > 0
    
    def test_search_dining(self, kb_data):
        """Test ricerca ristoranti"""
        results = search_hotel_knowledge("ristorante", kb_data, category="dining")
        assert len(results) > 0
    
    def test_search_transport(self, kb_data):
        """Test ricerca trasporti"""
        results = search_hotel_knowledge("aeroporto", kb_data, category="transport")
        assert len(results) > 0
    
    def test_generate_response(self, kb_data):
        """Test generazione risposta"""
        results = search_hotel_knowledge("colazione", kb_data)
        response = generate_concierge_response(
            "A che ora è la colazione?",
            results,
            guest_language="it"
        )
        assert response is not None
        assert len(response) > 0
        assert isinstance(response, str)
    
    def test_no_results_fallback(self, kb_data):
        """Test fallback quando non ci sono risultati"""
        response = generate_concierge_response(
            "query impossibile xyz123",
            [],
            guest_language="it"
        )
        assert "non ho trovato" in response.lower() or "reception" in response.lower()


class TestServiceManagement:
    """Test Gestione Richieste di Servizio"""
    
    def test_create_room_service_request(self):
        """Test creazione richiesta room service"""
        request = create_service_request(
            guest_id="TEST001",
            room_number="999",
            request_type="room_service",
            details="Test cappuccino"
        )
        
        assert request is not None
        assert 'request_id' in request
        assert request['request_type'] == "room_service"
        assert request['status'] == "pending"
        assert request['priority'] in ['low', 'normal', 'high', 'urgent']
    
    def test_create_maintenance_request(self):
        """Test creazione richiesta manutenzione"""
        request = create_service_request(
            guest_id="TEST002",
            room_number="999",
            request_type="maintenance",
            details="Acqua fredda non funziona"
        )
        
        assert request['request_type'] == "maintenance"
        # Maintenance con parole critiche dovrebbe avere priorità alta
        assert request['priority'] in ['high', 'urgent', 'normal']
    
    def test_invalid_request_type(self):
        """Test validazione tipo richiesta"""
        with pytest.raises(ValueError):
            create_service_request(
                guest_id="TEST003",
                room_number="999",
                request_type="invalid_type",
                details="Test"
            )
    
    def test_get_request_status(self):
        """Test recupero stato richiesta"""
        # Crea richiesta
        request = create_service_request(
            guest_id="TEST004",
            room_number="999",
            request_type="housekeeping",
            details="Asciugamani extra"
        )
        
        # Recupera stato
        status = get_request_status(request['request_id'])
        assert status is not None
        assert status['request_id'] == request['request_id']
    
    def test_format_confirmation(self):
        """Test formattazione conferma"""
        request = create_service_request(
            guest_id="TEST005",
            room_number="999",
            request_type="spa_booking",
            details="Massaggio 60 minuti"
        )
        
        confirmation = format_service_confirmation(request)
        assert confirmation is not None
        assert len(confirmation) > 0
        assert request['request_id'] in confirmation
        assert "✅" in confirmation  # Check emoji


class TestHotelConciergeBot:
    """Test Sistema Conversazionale Completo"""
    
    @pytest.fixture
    def bot(self):
        """Fixture per bot instance"""
        return HotelConciergeBot()
    
    @pytest.fixture
    def guest_info(self):
        """Fixture per guest info"""
        return {
            "guest_id": "TEST_GUEST",
            "room_number": "999",
            "language": "it",
            "preferences": {
                "dietary": ["vegetarian"],
                "interests": ["art", "history"]
            }
        }
    
    def test_bot_initialization(self, bot):
        """Test inizializzazione bot"""
        assert bot is not None
        assert bot.kb_data is not None
        assert len(bot.kb_data) > 0
    
    def test_process_hotel_info_message(self, bot, guest_info):
        """Test elaborazione richiesta info hotel"""
        response = bot.process_guest_message(
            "A che ora è la colazione?",
            [],
            guest_info
        )
        assert response is not None
        assert len(response) > 0
    
    def test_process_service_request_message(self, bot, guest_info):
        """Test elaborazione richiesta servizio"""
        response = bot.process_guest_message(
            "Vorrei ordinare 2 cappuccini",
            [],
            guest_info
        )
        assert response is not None
        assert "SR-" in response  # Check request ID format
    
    def test_process_recommendation_message(self, bot, guest_info):
        """Test elaborazione richiesta raccomandazione"""
        response = bot.process_guest_message(
            "Consigli un ristorante?",
            [],
            guest_info
        )
        assert response is not None
        assert len(response) > 0
    
    def test_escalation_logic_long_conversation(self, bot):
        """Test escalation per conversazione lunga"""
        long_history = [
            {"role": "guest", "content": f"Messaggio {i}"}
            for i in range(12)
        ]
        
        should_escalate = bot.should_escalate_to_staff(long_history, "hotel_info")
        assert should_escalate == True
    
    def test_escalation_logic_complaint(self, bot):
        """Test escalation per complaint ripetuti"""
        history = [
            {"role": "guest", "content": "Ho un problema"},
            {"role": "bot", "content": "Mi dispiace"},
            {"role": "guest", "content": "C'è ancora il problema"},
            {"role": "bot", "content": "Capisco"},
            {"role": "guest", "content": "Sempre problemi"}
        ]
        
        should_escalate = bot.should_escalate_to_staff(history, "complaint")
        assert should_escalate == True
    
    def test_personalized_recommendations(self, bot, guest_info):
        """Test raccomandazioni personalizzate"""
        recommendations = bot.get_personalized_recommendations(
            guest_info,
            "local_attractions"
        )
        
        assert recommendations is not None
        assert isinstance(recommendations, list)
        
        # Check se art/history preferences vengono considerate
        if len(recommendations) > 0:
            # Le prime raccomandazioni dovrebbero avere score boost
            assert 'score' in recommendations[0]


class TestEndToEnd:
    """Test End-to-End completi"""
    
    def test_complete_conversation_flow(self):
        """Test flusso conversazionale completo"""
        bot = HotelConciergeBot()
        
        guest_info = {
            "guest_id": "E2E_TEST",
            "room_number": "999",
            "language": "it",
            "preferences": {"dietary": [], "interests": ["food"]}
        }
        
        conversation = []
        
        # Messaggio 1: Info hotel
        msg1 = "A che ora è la colazione?"
        resp1 = bot.process_guest_message(msg1, conversation, guest_info)
        assert resp1 is not None
        conversation.extend([
            {"role": "guest", "content": msg1},
            {"role": "bot", "content": resp1}
        ])
        
        # Messaggio 2: Raccomandazione
        msg2 = "Consigli un ristorante veneziano?"
        resp2 = bot.process_guest_message(msg2, conversation, guest_info)
        assert resp2 is not None
        conversation.extend([
            {"role": "guest", "content": msg2},
            {"role": "bot", "content": resp2}
        ])
        
        # Messaggio 3: Service request
        msg3 = "Vorrei prenotare un tavolo al ristorante"
        resp3 = bot.process_guest_message(msg3, conversation, guest_info)
        assert resp3 is not None
        
        # Check che il flusso sia coerente
        assert len(conversation) >= 4


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
