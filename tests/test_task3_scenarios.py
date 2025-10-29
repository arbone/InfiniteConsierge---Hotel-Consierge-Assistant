"""
TASK 3: Test Cases - Scenari Completi e Edge Cases
Test che coprono tutti i requisiti del TASK 3
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from concierge_bot import HotelConciergeBot


class TestScenario1_HotelInfo:
    """Scenario 1: Richiesta Informazioni Hotel"""
    
    def test_breakfast_hours_italian(self):
        """Test: Ospite chiede orari colazione in italiano"""
        bot = HotelConciergeBot()
        guest_info = {
            "guest_id": "G001",
            "room_number": "305",
            "language": "it",
            "preferences": {}
        }
        
        response = bot.process_guest_message(
            "A che ora è servita la colazione?",
            [],
            guest_info
        )
        
        assert response is not None
        assert len(response) > 0
        # Should mention breakfast times
        assert any(word in response.lower() for word in ["7:00", "colazione", "breakfast"])
    
    def test_wifi_info_english(self):
        """Test: Guest asks about WiFi in English"""
        bot = HotelConciergeBot()
        guest_info = {
            "guest_id": "G002",
            "room_number": "208",
            "language": "en",
            "preferences": {}
        }
        
        response = bot.process_guest_message(
            "Is there free WiFi?",
            [],
            guest_info
        )
        
        assert response is not None
        # Should mention WiFi or internet
        assert any(word in response.lower() for word in ["wifi", "internet", "wireless"])


class TestScenario2_RoomService:
    """Scenario 2: Richiesta Room Service"""
    
    def test_order_breakfast_room_service(self):
        """Test: Ospite ordina colazione in camera"""
        bot = HotelConciergeBot()
        guest_info = {
            "guest_id": "G003",
            "room_number": "412",
            "language": "it",
            "preferences": {"dietary": ["vegetarian"]}
        }
        
        response = bot.process_guest_message(
            "Vorrei ordinare room service: 2 cappuccini e croissant per le 8:00",
            [],
            guest_info
        )
        
        assert response is not None
        # Should contain request ID
        assert "SR-" in response
        # Should confirm the request
        assert "confermata" in response.lower() or "confirmed" in response.lower()
    
    def test_housekeeping_towels(self):
        """Test: Richiesta asciugamani extra"""
        bot = HotelConciergeBot()
        guest_info = {
            "guest_id": "G004",
            "room_number": "101",
            "language": "it",
            "preferences": {}
        }
        
        response = bot.process_guest_message(
            "Ho bisogno di asciugamani puliti",
            [],
            guest_info
        )
        
        assert response is not None
        assert "SR-" in response or "richiesta" in response.lower()


class TestScenario3_Recommendations:
    """Scenario 3: Raccomandazioni Ristoranti"""
    
    def test_restaurant_recommendation_italian(self):
        """Test: Ospite chiede raccomandazione ristorante italiano"""
        bot = HotelConciergeBot()
        guest_info = {
            "guest_id": "G005",
            "room_number": "305",
            "language": "it",
            "preferences": {"interests": ["food", "wine"]}
        }
        
        response = bot.process_guest_message(
            "Mi può consigliare un buon ristorante veneziano?",
            [],
            guest_info
        )
        
        assert response is not None
        assert len(response) > 50  # Should be detailed
        # Should mention restaurants
        assert any(word in response.lower() for word in ["ristorante", "restaurant", "trattoria"])
    
    def test_attraction_recommendation(self):
        """Test: Raccomandazione attrazioni turistiche"""
        bot = HotelConciergeBot()
        guest_info = {
            "guest_id": "G006",
            "room_number": "208",
            "language": "it",
            "preferences": {"interests": ["art", "history"]}
        }
        
        response = bot.process_guest_message(
            "Cosa mi consiglia di visitare a Venezia?",
            [],
            guest_info
        )
        
        assert response is not None
        # Should mention attractions
        assert any(word in response.lower() for word in ["san marco", "museo", "palazzo", "piazza"])


class TestScenario4_Emergency:
    """Scenario 4: Gestione Emergenze"""
    
    def test_emergency_alert(self):
        """Test: Ospite segnala emergenza"""
        bot = HotelConciergeBot()
        guest_info = {
            "guest_id": "G007",
            "room_number": "512",
            "language": "it",
            "preferences": {}
        }
        
        response = bot.process_guest_message(
            "Aiuto! C'è un'emergenza!",
            [],
            guest_info
        )
        
        assert response is not None
        # Should have emergency indicators
        assert "🚨" in response or "emergenza" in response.lower()
        # Should mention staff/reception
        assert any(word in response.lower() for word in ["staff", "reception", "allertato", "numero"])
    
    def test_maintenance_urgent(self):
        """Test: Problema urgente manutenzione"""
        bot = HotelConciergeBot()
        guest_info = {
            "guest_id": "G008",
            "room_number": "305",
            "language": "it",
            "preferences": {}
        }
        
        response = bot.process_guest_message(
            "C'è una perdita d'acqua urgente in bagno!",
            [],
            guest_info
        )
        
        assert response is not None
        # Should create high priority request
        assert "SR-" in response or "priorit" in response.lower()


class TestScenario5_LanguageSwitch:
    """Scenario 5: Cambio Lingua (Multilingua)"""
    
    def test_conversation_italian_to_english(self):
        """Test: Conversazione che passa da italiano a inglese"""
        bot = HotelConciergeBot()
        
        # Prima in italiano
        guest_info_it = {
            "guest_id": "G009",
            "room_number": "305",
            "language": "it",
            "preferences": {}
        }
        
        response_it = bot.process_guest_message(
            "A che ora è la colazione?",
            [],
            guest_info_it
        )
        
        assert response_it is not None
        
        # Poi in inglese (guest cambia lingua)
        guest_info_en = {
            "guest_id": "G009",
            "room_number": "305",
            "language": "en",
            "preferences": {}
        }
        
        response_en = bot.process_guest_message(
            "Can you recommend a restaurant?",
            [],
            guest_info_en
        )
        
        assert response_en is not None
        # Both responses should be valid
        assert len(response_it) > 0
        assert len(response_en) > 0
    
    def test_english_guest_complete_flow(self):
        """Test: Guest inglese - flusso completo"""
        bot = HotelConciergeBot()
        guest_info = {
            "guest_id": "G010",
            "room_number": "208",
            "language": "en",
            "preferences": {"interests": ["culture"]}
        }
        
        conversation = []
        
        # Info request
        msg1 = "What time is check-out?"
        resp1 = bot.process_guest_message(msg1, conversation, guest_info)
        assert resp1 is not None
        conversation.extend([
            {"role": "guest", "content": msg1},
            {"role": "bot", "content": resp1}
        ])
        
        # Service request
        msg2 = "I'd like to book a massage"
        resp2 = bot.process_guest_message(msg2, conversation, guest_info)
        assert resp2 is not None
        assert "SR-" in resp2 or "request" in resp2.lower()


class TestEdgeCases:
    """Test Edge Cases e Situazioni di Errore"""
    
    def test_empty_message(self):
        """Test: Messaggio vuoto"""
        bot = HotelConciergeBot()
        guest_info = {
            "guest_id": "G011",
            "room_number": "305",
            "language": "it",
            "preferences": {}
        }
        
        response = bot.process_guest_message(
            "",
            [],
            guest_info
        )
        
        # Should handle gracefully
        assert response is not None
    
    def test_very_long_message(self):
        """Test: Messaggio molto lungo"""
        bot = HotelConciergeBot()
        guest_info = {
            "guest_id": "G012",
            "room_number": "305",
            "language": "it",
            "preferences": {}
        }
        
        long_message = "Vorrei sapere " + " e anche " * 50 + "gli orari della colazione"
        response = bot.process_guest_message(
            long_message,
            [],
            guest_info
        )
        
        # Should still process
        assert response is not None
    
    def test_unknown_room_number(self):
        """Test: Numero camera non valido"""
        bot = HotelConciergeBot()
        guest_info = {
            "guest_id": "UNKNOWN",
            "room_number": "9999",
            "language": "it",
            "preferences": {}
        }
        
        response = bot.process_guest_message(
            "Vorrei ordinare room service",
            [],
            guest_info
        )
        
        # Should still create request (system is lenient)
        assert response is not None
    
    def test_mixed_language_query(self):
        """Test: Query con parole miste italiano/inglese"""
        bot = HotelConciergeBot()
        guest_info = {
            "guest_id": "G013",
            "room_number": "305",
            "language": "it",
            "preferences": {}
        }
        
        response = bot.process_guest_message(
            "Vorrei fare il check-out late",
            [],
            guest_info
        )
        
        assert response is not None
    
    def test_escalation_trigger_many_questions(self):
        """Test: Escalation dopo molte domande"""
        bot = HotelConciergeBot()
        guest_info = {
            "guest_id": "G014",
            "room_number": "305",
            "language": "it",
            "preferences": {}
        }
        
        # Simula lunga conversazione
        long_history = []
        for i in range(12):
            long_history.extend([
                {"role": "guest", "content": f"Domanda {i}"},
                {"role": "bot", "content": f"Risposta {i}"}
            ])
        
        response = bot.process_guest_message(
            "Ancora una domanda",
            long_history,
            guest_info
        )
        
        # Should escalate or mention human staff
        assert response is not None
        assert any(word in response.lower() for word in ["staff", "concierge", "reception", "personale"])
    
    def test_repeated_complaints(self):
        """Test: Lamentele ripetute dovrebbero escalare"""
        bot = HotelConciergeBot()
        guest_info = {
            "guest_id": "G015",
            "room_number": "305",
            "language": "it",
            "preferences": {}
        }
        
        history = [
            {"role": "guest", "content": "La camera ha un problema"},
            {"role": "bot", "content": "Mi dispiace"},
            {"role": "guest", "content": "C'è ancora il problema"},
            {"role": "bot", "content": "Risolviamo subito"},
            {"role": "guest", "content": "Sempre problemi qui"}
        ]
        
        response = bot.process_guest_message(
            "Non va bene",
            history,
            guest_info
        )
        
        assert response is not None
        # Should escalate after repeated complaints
        should_escalate = bot.should_escalate_to_staff(history, "complaint")
        assert should_escalate == True


class TestPerformanceMetrics:
    """Test per valutare performance e qualità"""
    
    def test_response_time_acceptable(self):
        """Test: Tempo di risposta accettabile"""
        import time
        
        bot = HotelConciergeBot()
        guest_info = {
            "guest_id": "G016",
            "room_number": "305",
            "language": "it",
            "preferences": {}
        }
        
        start = time.time()
        response = bot.process_guest_message(
            "A che ora è la colazione?",
            [],
            guest_info
        )
        elapsed = time.time() - start
        
        assert response is not None
        # Should respond in less than 2 seconds (without LLM)
        assert elapsed < 2.0
    
    def test_response_completeness(self):
        """Test: Completezza delle risposte"""
        bot = HotelConciergeBot()
        guest_info = {
            "guest_id": "G017",
            "room_number": "305",
            "language": "it",
            "preferences": {}
        }
        
        response = bot.process_guest_message(
            "Quali servizi offre la spa?",
            [],
            guest_info
        )
        
        assert response is not None
        # Response should be substantial (not too short)
        assert len(response) > 50
        # Should contain useful info
        assert any(word in response.lower() for word in ["spa", "massaggio", "sauna", "orari"])


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
