-- Create the "users" table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,         -- Auto-incremented user ID
    name VARCHAR(255) NOT NULL,     -- User's name
    api_id VARCHAR(255) NOT NULL,   -- API ID
    api_hash VARCHAR(255) NOT NULL, -- API hash
    phone_number VARCHAR(15),       -- User's phone number
    bot_chat TEXT,                  -- Bot chat info
    test_chat_link TEXT,            -- Test chat link
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Timestamp for when the user was created
);

-- Create the "channels" table
CREATE TABLE IF NOT EXISTS channels (
    id SERIAL PRIMARY KEY,      -- Auto-incremented channel ID
    name VARCHAR(255) NOT NULL,  -- Channel name
    link TEXT NOT NULL           -- Channel link (URL)
);

-- Create the "user_channels" table for the many-to-many relationship between users and channels
CREATE TABLE IF NOT EXISTS user_channels (
    user_id INT REFERENCES users(id) ON DELETE CASCADE,  -- Foreign key to the users table
    channel_id INT REFERENCES channels(id) ON DELETE CASCADE,  -- Foreign key to the channels table
    PRIMARY KEY (user_id, channel_id)  -- Composite primary key to prevent duplicates
);

-- Create the "coins" table
CREATE TABLE IF NOT EXISTS coins (
    id SERIAL PRIMARY KEY,            -- Auto-incremented coin ID
    address VARCHAR(44) NOT NULL,      -- 44-character coin address
    rug_pull BOOLEAN DEFAULT FALSE,    -- Whether the coin is a rug pull (true/false)
    from_channel VARCHAR(255) NOT NULL,  -- Name of the channel this coin came from
    message_id BIGINT,                 -- The message ID from where this coin came
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp for when the coin was created
);

-- Optionally, create some indexes to speed up queries
CREATE INDEX IF NOT EXISTS idx_user_channels_user_id ON user_channels(user_id);
CREATE INDEX IF NOT EXISTS idx_user_channels_channel_id ON user_channels(channel_id);