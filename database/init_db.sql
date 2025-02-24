-- Create Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    session_name VARCHAR(255) UNIQUE NOT NULL, -- Unique identifier for each client container
    telegram_api_id INTEGER NOT NULL,
    telegram_api_hash VARCHAR(255) NOT NULL,
    telegram_session VARCHAR(255) NOT NULL,
    telegram_channel VARCHAR(255) NOT NULL, -- Telegram channel invite link or ID
    bot_chat VARCHAR(255) NOT NULL, -- Bot chat handle where CAs are sent
    is_active BOOLEAN DEFAULT TRUE, -- Allow enabling/disabling users
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Coin Addresses Table
CREATE TABLE coin_addresses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL, -- Links CA to a user
    ca VARCHAR(44) UNIQUE NOT NULL, -- Solana addresses are always 44 characters
    status VARCHAR(20) CHECK (status IN ('Buy', 'Rug Pull')), -- Only valid statuses
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for faster lookups
CREATE INDEX idx_users_session ON users(session_name);
CREATE INDEX idx_coin_addresses_ca ON coin_addresses(ca);
