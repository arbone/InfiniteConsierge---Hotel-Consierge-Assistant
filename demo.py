"""
Script Demo per Hotel Concierge Bot
Testa tutte le funzionalità principali del sistema
"""
import sys
sys.path.append('src')

from concierge_bot import HotelConciergeBot

def print_section(title):
    """Helper per output formattato"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_bot():
    """Test completo del bot"""
    print("🏨 Hotel Concierge Bot - Demo\n")
    
    # Inizializza bot
    print("📦 Inizializzazione bot...")
    bot = HotelConciergeBot()
    
    # Guest info di test
    guest_info = {
        "guest_id": "G001",
        "room_number": "305",
        "language": "it",
        "preferences": {
            "dietary": ["vegetarian"],
            "interests": ["art", "history", "wine"]
        }
    }
    
    conversation_history = []
    
    # Test 1: Hotel Info
    print_section("TEST 1: Richiesta Informazioni Hotel")
    message1 = "A che ora è la colazione?"
    print(f"👤 Ospite: {message1}")
    response1 = bot.process_guest_message(message1, conversation_history, guest_info)
    print(f"🤖 Bot: {response1}")
    conversation_history.append({"role": "guest", "content": message1})
    conversation_history.append({"role": "bot", "content": response1})
    
    # Test 2: Recommendation
    print_section("TEST 2: Richiesta Raccomandazioni")
    message2 = "Consigli un ristorante per una cena romantica?"
    print(f"👤 Ospite: {message2}")
    response2 = bot.process_guest_message(message2, conversation_history, guest_info)
    print(f"🤖 Bot: {response2}")
    conversation_history.append({"role": "guest", "content": message2})
    conversation_history.append({"role": "bot", "content": response2})
    
    # Test 3: Service Request
    print_section("TEST 3: Richiesta Servizio")
    message3 = "Vorrei ordinare room service: 2 cappuccini e croissant"
    print(f"👤 Ospite: {message3}")
    response3 = bot.process_guest_message(message3, conversation_history, guest_info)
    print(f"🤖 Bot: {response3}")
    conversation_history.append({"role": "guest", "content": message3})
    conversation_history.append({"role": "bot", "content": response3})
    
    # Test 4: Complaint
    print_section("TEST 4: Lamentela")
    message4 = "C'è troppo rumore dalla camera accanto"
    print(f"👤 Ospite: {message4}")
    response4 = bot.process_guest_message(message4, conversation_history, guest_info)
    print(f"🤖 Bot: {response4}")
    conversation_history.append({"role": "guest", "content": message4})
    conversation_history.append({"role": "bot", "content": response4})
    
    # Test 5: Attractions
    print_section("TEST 5: Informazioni Attrazioni")
    message5 = "Cosa posso visitare a Venezia oggi?"
    print(f"👤 Ospite: {message5}")
    response5 = bot.process_guest_message(message5, conversation_history, guest_info)
    print(f"🤖 Bot: {response5}")
    
    # Test 6: Special Request
    print_section("TEST 6: Richiesta Speciale")
    message6 = "Vorrei organizzare una proposta di matrimonio romantica"
    print(f"👤 Ospite: {message6}")
    response6 = bot.process_guest_message(message6, conversation_history, guest_info)
    print(f"🤖 Bot: {response6}")
    
    print("\n" + "="*60)
    print("✅ Demo completata con successo!")
    print("="*60 + "\n")


def test_intent_classification():
    """Test classificazione intent"""
    from intent_classifier import classify_guest_intent, get_intent_confidence
    
    print_section("TEST: Intent Classification")
    
    test_messages = [
        "A che ora è la colazione?",
        "Vorrei prenotare un massaggio",
        "Consigli un ristorante?",
        "La doccia non funziona",
        "C'è un'emergenza!",
        "Posso avere un late check-out?"
    ]
    
    for msg in test_messages:
        intent, confidence = get_intent_confidence(msg)
        print(f"📝 \"{msg}\"")
        print(f"   → Intent: {intent} (confidence: {confidence:.2f})\n")


def test_rag():
    """Test RAG engine"""
    from rag_engine import search_hotel_knowledge, generate_concierge_response, load_knowledge_base
    
    print_section("TEST: RAG Knowledge Search")
    
    kb = load_knowledge_base()
    print(f"KB caricata: {len(kb)} documenti\n")
    
    queries = [
        "orari colazione",
        "ristoranti veneziani",
        "come arrivare aeroporto"
    ]
    
    for query in queries:
        print(f"🔍 Query: \"{query}\"")
        results = search_hotel_knowledge(query, kb)
        print(f"   Trovati {len(results)} risultati")
        if results:
            print(f"   Top result: {results[0]['question']} (score: {results[0]['score']:.3f})")
        print()


def test_service_requests():
    """Test service request management"""
    from service_manager import create_service_request, get_request_status, format_service_confirmation
    
    print_section("TEST: Service Request Management")
    
    # Crea richiesta
    print("📋 Creazione richiesta...")
    request = create_service_request(
        guest_id="G001",
        room_number="305",
        request_type="room_service",
        details="2 cappuccini e croissant per le 8:00"
    )
    
    print(f"✓ Richiesta creata: {request['request_id']}\n")
    
    # Formatta conferma
    confirmation = format_service_confirmation(request)
    print("Conferma per ospite:")
    print(confirmation)


def interactive_mode():
    """Modalità interattiva"""
    print("\n🏨 Hotel Concierge Bot - Modalità Interattiva")
    print("="*60)
    print("Digita 'exit' per uscire\n")
    
    bot = HotelConciergeBot()
    
    guest_info = {
        "guest_id": "G999",
        "room_number": "TEST",
        "language": "it",
        "preferences": {"dietary": [], "interests": []}
    }
    
    conversation_history = []
    
    while True:
        try:
            user_input = input("\n👤 Tu: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'esci']:
                print("\n👋 Grazie per aver usato Hotel Concierge Bot!")
                break
            
            if not user_input:
                continue
            
            response = bot.process_guest_message(user_input, conversation_history, guest_info)
            print(f"\n🤖 Bot: {response}")
            
            conversation_history.append({"role": "guest", "content": user_input})
            conversation_history.append({"role": "bot", "content": response})
        
        except KeyboardInterrupt:
            print("\n\n👋 Arrivederci!")
            break
        except Exception as e:
            print(f"\n❌ Errore: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        print("\n🧪 Esecuzione test suite completa...\n")
        
        # Test individuali
        test_intent_classification()
        input("\nPremi INVIO per continuare...")
        
        test_rag()
        input("\nPremi INVIO per continuare...")
        
        test_service_requests()
        input("\nPremi INVIO per continuare...")
        
        # Test completo bot
        test_bot()
        
        print("\n💡 Suggerimento: Esegui con --interactive per modalità interattiva")
        print("   python demo.py --interactive\n")
