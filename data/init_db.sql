-- Hotel Concierge Database Schema

-- Tabella Ospiti/Prenotazioni
CREATE TABLE IF NOT EXISTS guests (
    guest_id TEXT PRIMARY KEY,
    name TEXT,
    room_number TEXT,
    check_in DATE,
    check_out DATE,
    language TEXT,
    preferences TEXT, -- JSON: dietary, interests, etc.
    vip_status BOOLEAN DEFAULT 0
);

-- Tabella Richieste Servizio
CREATE TABLE IF NOT EXISTS service_requests (
    request_id TEXT PRIMARY KEY,
    guest_id TEXT,
    room_number TEXT,
    request_type TEXT, -- 'room_service', 'housekeeping', 'maintenance', 'concierge', 'spa_booking', 'restaurant_booking'
    details TEXT,
    status TEXT DEFAULT 'pending', -- 'pending', 'in_progress', 'completed'
    priority TEXT DEFAULT 'normal', -- 'low', 'normal', 'high', 'urgent'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (guest_id) REFERENCES guests(guest_id)
);

-- Tabella Conversazioni
CREATE TABLE IF NOT EXISTS conversations (
    conversation_id TEXT PRIMARY KEY,
    guest_id TEXT,
    room_number TEXT,
    messages TEXT, -- JSON array
    language TEXT DEFAULT 'it',
    escalated BOOLEAN DEFAULT 0,
    satisfaction_rating INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (guest_id) REFERENCES guests(guest_id)
);

-- Sample data
INSERT OR IGNORE INTO guests (guest_id, name, room_number, check_in, check_out, language, preferences, vip_status) VALUES
('G001', 'Mario Rossi', '305', '2025-10-28', '2025-10-31', 'it', '{"dietary": ["vegetarian"], "interests": ["art", "history", "wine"]}', 0),
('G002', 'Laura Bianchi', '412', '2025-10-27', '2025-10-30', 'it', '{"dietary": [], "interests": ["shopping", "spa", "food"]}', 1),
('G003', 'John Smith', '208', '2025-10-29', '2025-11-02', 'en', '{"dietary": ["gluten-free"], "interests": ["photography", "culture"]}', 0);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_service_requests_guest ON service_requests(guest_id);
CREATE INDEX IF NOT EXISTS idx_service_requests_status ON service_requests(status);
CREATE INDEX IF NOT EXISTS idx_conversations_guest ON conversations(guest_id);
