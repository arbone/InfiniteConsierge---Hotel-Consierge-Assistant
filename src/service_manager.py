"""
Gestione Richieste di Servizio
Gestisce creazione, tracking e formattazione delle richieste di servizio
"""
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path


def _get_db_connection(db_path: str = "data/hotel_database.sqlite") -> sqlite3.Connection:
    """
    Ottiene connessione al database SQLite.
    
    Args:
        db_path: Path al database SQLite
    
    Returns:
        sqlite3.Connection: Connessione al database
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Abilita accesso dict-like
    return conn


def _initialize_database(db_path: str = "data/hotel_database.sqlite"):
    """
    Inizializza il database se non esiste.
    
    Args:
        db_path: Path al database
    """
    db_file = Path(db_path)
    
    # Crea directory se non esiste
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Leggi e esegui schema SQL
    schema_file = db_file.parent / "init_db.sql"
    if schema_file.exists():
        conn = _get_db_connection(db_path)
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            conn.executescript(schema_sql)
            conn.commit()
        except Exception as e:
            print(f"Error initializing database: {e}")
        finally:
            conn.close()


def create_service_request(
    guest_id: str,
    room_number: str,
    request_type: str,
    details: str,
    priority: Optional[str] = None
) -> dict:
    """
    Crea richiesta di servizio nel sistema.
    
    Args:
        guest_id: ID univoco dell'ospite
        room_number: Numero camera
        request_type: Tipo richiesta - Valori validi:
                      'room_service', 'housekeeping', 'maintenance',
                      'concierge', 'spa_booking', 'restaurant_booking'
        details: Descrizione dettagliata della richiesta
        priority: Priorità ('low', 'normal', 'high', 'urgent')
                  Se None, viene auto-determinata
    
    Returns:
        dict: Dati della richiesta creata con tutti i campi incluso request_id
    
    Raises:
        ValueError: Se request_type non è valido
        RuntimeError: Se si verifica un errore database
    
    Examples:
        >>> request = create_service_request(
        ...     guest_id="G001",
        ...     room_number="305",
        ...     request_type="room_service",
        ...     details="2 cappuccini e croissant alle 8:00"
        ... )
        >>> print(request['request_id'])
        'SR-...'
    
    Note:
        - request_id viene generato automaticamente (formato: SR-uuid)
        - status iniziale è sempre 'pending'
        - created_at viene impostato automaticamente
    """
    # Validazione request_type
    valid_types = ['room_service', 'housekeeping', 'maintenance', 
                   'concierge', 'spa_booking', 'restaurant_booking']
    
    if request_type not in valid_types:
        raise ValueError(
            f"Invalid request_type '{request_type}'. "
            f"Must be one of: {', '.join(valid_types)}"
        )
    
    # Auto-determina priority se non specificata
    if priority is None:
        priority = _determine_priority(request_type, details)
    
    # Genera request_id univoco
    request_id = f"SR-{uuid.uuid4().hex[:8].upper()}"
    
    # Inizializza database se necessario
    _initialize_database()
    
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO service_requests 
            (request_id, guest_id, room_number, request_type, details, status, priority, created_at)
            VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)
        """, (request_id, guest_id, room_number, request_type, details, priority, datetime.now()))
        
        conn.commit()
        
        # Recupera e restituisci la richiesta creata
        return get_request_status(request_id)
    
    except sqlite3.Error as e:
        conn.rollback()
        raise RuntimeError(f"Database error creating service request: {e}")
    finally:
        conn.close()


def _determine_priority(request_type: str, details: str) -> str:
    """
    Determina automaticamente la priorità della richiesta.
    
    Args:
        request_type: Tipo di richiesta
        details: Dettagli della richiesta
    
    Returns:
        str: Priorità ('low', 'normal', 'high', 'urgent')
    """
    details_lower = details.lower()
    
    # Keywords urgenti
    urgent_keywords = ['urgente', 'urgent', 'subito', 'immediately', 'asap', 'emergenza']
    if any(kw in details_lower for kw in urgent_keywords):
        return 'urgent'
    
    # Manutenzione critica
    if request_type == 'maintenance':
        critical_keywords = ['acqua', 'water', 'leak', 'perdita', 'allagamento',
                           'elettric', 'luce', 'riscaldamento', 'aria condizionata']
        if any(kw in details_lower for kw in critical_keywords):
            return 'high'
        return 'normal'
    
    # Room service e housekeeping sono generalmente normali
    if request_type in ['room_service', 'housekeeping']:
        return 'normal'
    
    # Spa e restaurant booking sono low priority
    if request_type in ['spa_booking', 'restaurant_booking']:
        return 'low'
    
    return 'normal'


def get_request_status(request_id: str) -> dict:
    """
    Recupera stato e dettagli di una richiesta dal database.
    
    Args:
        request_id: ID della richiesta (formato: SR-XXXXXXXX)
    
    Returns:
        dict: Dizionario con tutti i campi della richiesta:
              {request_id, guest_id, room_number, request_type, details,
               status, priority, created_at, completed_at}
              Restituisce dizionario vuoto se richiesta non trovata
    
    Examples:
        >>> status = get_request_status("SR-A1B2C3D4")
        >>> print(status['status'])
        'pending'
        >>> print(status['priority'])
        'normal'
    
    Note:
        - completed_at è None se richiesta non ancora completata
    """
    _initialize_database()
    
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT request_id, guest_id, room_number, request_type, details,
                   status, priority, created_at, completed_at
            FROM service_requests
            WHERE request_id = ?
        """, (request_id,))
        
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        else:
            return {}
    
    except sqlite3.Error as e:
        raise RuntimeError(f"Database error retrieving request: {e}")
    finally:
        conn.close()


def update_request_status(request_id: str, new_status: str) -> bool:
    """
    Aggiorna lo stato di una richiesta.
    
    Args:
        request_id: ID della richiesta
        new_status: Nuovo stato ('pending', 'in_progress', 'completed')
    
    Returns:
        bool: True se aggiornamento riuscito, False se richiesta non trovata
    """
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Se status è completed, imposta completed_at
        if new_status == 'completed':
            cursor.execute("""
                UPDATE service_requests
                SET status = ?, completed_at = ?
                WHERE request_id = ?
            """, (new_status, datetime.now(), request_id))
        else:
            cursor.execute("""
                UPDATE service_requests
                SET status = ?
                WHERE request_id = ?
            """, (new_status, request_id))
        
        conn.commit()
        return cursor.rowcount > 0
    
    except sqlite3.Error as e:
        conn.rollback()
        raise RuntimeError(f"Database error updating request: {e}")
    finally:
        conn.close()


def format_service_confirmation(request_data: dict) -> str:
    """
    Formatta conferma richiesta per l'ospite in stile professionale.
    
    Args:
        request_data: Dizionario con dati richiesta (output di create_service_request)
    
    Returns:
        str: Messaggio di conferma formattato e user-friendly
    
    Examples:
        >>> request = create_service_request("G001", "305", "room_service", "Caffè")
        >>> confirmation = format_service_confirmation(request)
        >>> print(confirmation)
        ✅ Richiesta confermata!
        ...
    
    Note:
        - Include emoji per migliore UX
        - Mostra ETA stimato basato su priorità
        - Traduce campi tecnici in linguaggio user-friendly
    """
    if not request_data:
        return "❌ Errore: richiesta non trovata nel sistema."
    
    request_id = request_data.get('request_id', 'N/A')
    request_type = request_data.get('request_type', '')
    details = request_data.get('details', '')
    priority = request_data.get('priority', 'normal')
    status = request_data.get('status', 'pending')
    room_number = request_data.get('room_number', 'N/A')
    
    # Traduzioni user-friendly
    type_translations = {
        'room_service': 'Servizio in Camera',
        'housekeeping': 'Pulizie',
        'maintenance': 'Manutenzione',
        'concierge': 'Assistenza Concierge',
        'spa_booking': 'Prenotazione Spa',
        'restaurant_booking': 'Prenotazione Ristorante'
    }
    
    status_translations = {
        'pending': 'In attesa',
        'in_progress': 'In elaborazione',
        'completed': 'Completata'
    }
    
    priority_translations = {
        'low': 'Bassa',
        'normal': 'Normale',
        'high': 'Alta',
        'urgent': 'Urgente'
    }
    
    # ETA basato su priorità
    eta_map = {
        'urgent': '5-10 minuti',
        'high': '15-20 minuti',
        'normal': '30-45 minuti',
        'low': '1-2 ore'
    }
    
    type_display = type_translations.get(request_type, request_type)
    status_display = status_translations.get(status, status)
    priority_display = priority_translations.get(priority, priority)
    eta = eta_map.get(priority, '30-45 minuti')
    
    # Build messaggio
    confirmation = f"""✅ **Richiesta confermata con successo!**

📋 **Numero richiesta**: {request_id}
🏨 **Camera**: {room_number}
🔖 **Tipo**: {type_display}
📝 **Dettagli**: {details}
📊 **Stato**: {status_display}
⚡ **Priorità**: {priority_display}
⏱️ **Tempo stimato**: {eta}

💡 Riceverà una notifica quando la richiesta sarà presa in carico dal nostro staff.

Per urgenze immediate, può contattare la reception al numero interno 0.

Grazie per aver scelto i nostri servizi! 🌟"""
    
    return confirmation


def get_guest_requests(guest_id: str, status_filter: Optional[str] = None) -> list:
    """
    Recupera tutte le richieste di un ospite.
    
    Args:
        guest_id: ID ospite
        status_filter: Filtra per status (opzionale)
    
    Returns:
        list: Lista di richieste (dizionari)
    """
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        if status_filter:
            cursor.execute("""
                SELECT * FROM service_requests
                WHERE guest_id = ? AND status = ?
                ORDER BY created_at DESC
            """, (guest_id, status_filter))
        else:
            cursor.execute("""
                SELECT * FROM service_requests
                WHERE guest_id = ?
                ORDER BY created_at DESC
            """, (guest_id,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    finally:
        conn.close()
