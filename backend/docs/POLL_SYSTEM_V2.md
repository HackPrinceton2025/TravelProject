# Poll System v2 - Database Schema

## Supabase SQL Migration

Run this in your Supabase SQL Editor to create the new poll tables:

```sql
-- ============================================
-- Poll System v2 Tables
-- ============================================

-- Main polls table
CREATE TABLE IF NOT EXISTS polls (
    id TEXT PRIMARY KEY,
    group_id UUID NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES users(id),
    question TEXT NOT NULL,
    poll_type TEXT NOT NULL CHECK (poll_type IN ('destination', 'hotel', 'flight', 'restaurant', 'activity', 'date', 'time', 'custom')),
    voting_type TEXT NOT NULL CHECK (voting_type IN ('single_choice', 'multiple_choice')),
    status TEXT NOT NULL CHECK (status IN ('active', 'confirmed', 'cancelled')),
    winning_option_id TEXT,
    confirmed_by UUID REFERENCES users(id),
    confirmed_at TIMESTAMPTZ,
    cancelled_by UUID REFERENCES users(id),
    cancelled_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Poll options table
CREATE TABLE IF NOT EXISTS poll_options (
    id TEXT PRIMARY KEY,
    poll_id TEXT NOT NULL REFERENCES polls(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    metadata JSONB,  -- Extra data like price, rating, image_url, etc.
    vote_count INTEGER DEFAULT 0,
    is_winner BOOLEAN DEFAULT FALSE,
    order_index INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Poll votes table (tracks who voted for what)
CREATE TABLE IF NOT EXISTS poll_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    poll_id TEXT NOT NULL REFERENCES polls(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    option_id TEXT NOT NULL REFERENCES poll_options(id) ON DELETE CASCADE,
    voted_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(poll_id, user_id, option_id)  -- One vote per user per option
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_polls_group_id ON polls(group_id);
CREATE INDEX IF NOT EXISTS idx_polls_status ON polls(status);
CREATE INDEX IF NOT EXISTS idx_poll_options_poll_id ON poll_options(poll_id);
CREATE INDEX IF NOT EXISTS idx_poll_votes_poll_id ON poll_votes(poll_id);
CREATE INDEX IF NOT EXISTS idx_poll_votes_user_id ON poll_votes(user_id);
CREATE INDEX IF NOT EXISTS idx_poll_votes_option_id ON poll_votes(option_id);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_polls_updated_at BEFORE UPDATE ON polls
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS)
ALTER TABLE polls ENABLE ROW LEVEL SECURITY;
ALTER TABLE poll_options ENABLE ROW LEVEL SECURITY;
ALTER TABLE poll_votes ENABLE ROW LEVEL SECURITY;

-- Policies: Group members can read polls in their groups
CREATE POLICY "Group members can view polls" ON polls
    FOR SELECT USING (
        group_id IN (
            SELECT group_id FROM group_members WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Group members can view poll options" ON poll_options
    FOR SELECT USING (
        poll_id IN (
            SELECT id FROM polls WHERE group_id IN (
                SELECT group_id FROM group_members WHERE user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Group members can vote" ON poll_votes
    FOR INSERT WITH CHECK (
        user_id = auth.uid() AND
        poll_id IN (
            SELECT id FROM polls WHERE group_id IN (
                SELECT group_id FROM group_members WHERE user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Group members can view votes" ON poll_votes
    FOR SELECT USING (
        poll_id IN (
            SELECT id FROM polls WHERE group_id IN (
                SELECT group_id FROM group_members WHERE user_id = auth.uid()
            )
        )
    );

-- Agent can create polls (service key bypasses RLS)
-- Agent can update poll status (service key)
```

## Example Data

```sql
-- Example poll
INSERT INTO polls (id, group_id, created_by, question, poll_type, voting_type, status)
VALUES (
    'poll_abc123',
    'group-uuid-here',
    'user-uuid-here',
    'Which hotel should we book for Paris?',
    'hotel',
    'single_choice',
    'active'
);

-- Example options
INSERT INTO poll_options (id, poll_id, text, metadata, order_index) VALUES
    ('opt_1', 'poll_abc123', 'Hotel Le Marais ($120/night)', '{"price": 120, "rating": 4.5, "image_url": "..."}', 0),
    ('opt_2', 'poll_abc123', 'Hotel Montmartre ($95/night)', '{"price": 95, "rating": 4.2, "image_url": "..."}', 1),
    ('opt_3', 'poll_abc123', 'Hotel Latin Quarter ($150/night)', '{"price": 150, "rating": 4.8, "image_url": "..."}', 2);

-- Example votes
INSERT INTO poll_votes (poll_id, user_id, option_id) VALUES
    ('poll_abc123', 'user-1-uuid', 'opt_1'),
    ('poll_abc123', 'user-2-uuid', 'opt_1'),
    ('poll_abc123', 'user-3-uuid', 'opt_2');
```

## Verification Queries

```sql
-- Check poll with votes
SELECT 
    p.id,
    p.question,
    p.status,
    o.text as option_text,
    COUNT(v.id) as vote_count
FROM polls p
LEFT JOIN poll_options o ON o.poll_id = p.id
LEFT JOIN poll_votes v ON v.option_id = o.id
WHERE p.id = 'poll_abc123'
GROUP BY p.id, p.question, p.status, o.text;

-- Get current leader
SELECT 
    o.text,
    COUNT(v.id) as votes
FROM poll_options o
LEFT JOIN poll_votes v ON v.option_id = o.id
WHERE o.poll_id = 'poll_abc123'
GROUP BY o.id, o.text
ORDER BY votes DESC
LIMIT 1;
```
