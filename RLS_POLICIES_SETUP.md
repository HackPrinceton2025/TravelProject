# Row Level Security (RLS) Policies Setup

## ⚠️ CRITICAL: Security Issue

**Currently, your tables likely have NO RLS enabled**, which means:
- ❌ Anyone can read ALL messages from ALL groups
- ❌ Anyone can write messages to any group
- ❌ Anyone can see all users and groups
- ❌ **This is a major security vulnerability!**

## What You Need

For a group chat app, you need RLS policies so that:
1. ✅ Users can only read messages from groups they're members of
2. ✅ Users can only write messages to groups they're members of
3. ✅ Users can only see groups they belong to
4. ✅ Users can only see group members of their groups
5. ✅ Users can read their own profile, but limited info about others

---

## Step-by-Step Setup

### 1. Enable RLS on All Tables

Run this in Supabase SQL Editor:

```sql
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE group_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE expense_splits ENABLE ROW LEVEL SECURITY;
ALTER TABLE polls ENABLE ROW LEVEL SECURITY;
ALTER TABLE poll_votes ENABLE ROW LEVEL SECURITY;
```

### 2. Create Helper Function to Check Group Membership

This function checks if a user is a member of a group:

```sql
-- Helper function to check if user is member of a group
CREATE OR REPLACE FUNCTION public.is_group_member(group_id_param UUID, user_id_param UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1
    FROM group_members
    WHERE group_members.group_id = group_id_param
      AND group_members.user_id = user_id_param
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### 3. Users Table Policies

Users can read their own profile and basic info about other users:

```sql
-- Users can read their own profile
CREATE POLICY "Users can read own profile"
  ON users FOR SELECT
  USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile"
  ON users FOR UPDATE
  USING (auth.uid() = id);

-- Users can read basic info about other users (name, id only)
-- This allows showing who sent messages, etc.
CREATE POLICY "Users can read other users basic info"
  ON users FOR SELECT
  USING (true);  -- Allow reading name and id for display purposes
  -- Note: You might want to restrict this to only users in same groups
```

### 4. Groups Table Policies

Users can only see groups they're members of:

```sql
-- Users can read groups they're members of
CREATE POLICY "Users can read their groups"
  ON groups FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM group_members
      WHERE group_members.group_id = groups.id
        AND group_members.user_id = auth.uid()
    )
  );

-- Users can create groups (they'll be added as owner/member separately)
CREATE POLICY "Users can create groups"
  ON groups FOR INSERT
  WITH CHECK (auth.uid() IS NOT NULL);

-- Group owners can update their groups
CREATE POLICY "Group owners can update groups"
  ON groups FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM group_members
      WHERE group_members.group_id = groups.id
        AND group_members.user_id = auth.uid()
        AND group_members.role = 'owner'
    )
  );
```

### 5. Group Members Table Policies

Users can see members of groups they belong to:

```sql
-- Users can read members of their groups
CREATE POLICY "Users can read group members"
  ON group_members FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM group_members gm
      WHERE gm.group_id = group_members.group_id
        AND gm.user_id = auth.uid()
    )
  );

-- Users can join groups (insert themselves)
CREATE POLICY "Users can join groups"
  ON group_members FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Group owners can add/remove members
CREATE POLICY "Group owners can manage members"
  ON group_members FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM group_members gm
      WHERE gm.group_id = group_members.group_id
        AND gm.user_id = auth.uid()
        AND gm.role = 'owner'
    )
  );
```

### 6. Messages Table Policies

**Most Important**: Users can only read/write messages in groups they're members of:

```sql
-- Users can read messages from groups they're members of
CREATE POLICY "Users can read messages in their groups"
  ON messages FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM group_members
      WHERE group_members.group_id = messages.group_id
        AND group_members.user_id = auth.uid()
    )
  );

-- Users can send messages to groups they're members of
-- NOTE: Your messages table should have a sender_id (UUID) column, not sender (string)
-- If you only have 'sender' (string), this policy won't work properly!
CREATE POLICY "Users can send messages in their groups"
  ON messages FOR INSERT
  WITH CHECK (
    auth.uid()::text = sender_id::text  -- Convert UUIDs to text for comparison
    AND EXISTS (
      SELECT 1 FROM group_members
      WHERE group_members.group_id = messages.group_id
        AND group_members.user_id = auth.uid()
    )
  );

-- Users can update/delete their own messages
CREATE POLICY "Users can update own messages"
  ON messages FOR UPDATE
  USING (auth.uid()::text = sender_id::text);

CREATE POLICY "Users can delete own messages"
  ON messages FOR DELETE
  USING (auth.uid()::text = sender_id::text);
```

### 7. Expenses Table Policies

```sql
-- Users can read expenses from their groups
CREATE POLICY "Users can read expenses in their groups"
  ON expenses FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM group_members
      WHERE group_members.group_id = expenses.group_id
        AND group_members.user_id = auth.uid()
    )
  );

-- Users can create expenses in their groups
CREATE POLICY "Users can create expenses in their groups"
  ON expenses FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM group_members
      WHERE group_members.group_id = expenses.group_id
        AND group_members.user_id = auth.uid()
    )
  );
```

### 8. Polls Table Policies

```sql
-- Users can read polls from their groups
CREATE POLICY "Users can read polls in their groups"
  ON polls FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM group_members
      WHERE group_members.group_id = polls.group_id
        AND group_members.user_id = auth.uid()
    )
  );

-- Users can create polls in their groups
CREATE POLICY "Users can create polls in their groups"
  ON polls FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM group_members
      WHERE group_members.group_id = polls.group_id
        AND group_members.user_id = auth.uid()
    )
  );
```

---

## Complete Setup Script

Copy and run this entire script in Supabase SQL Editor:

```sql
-- ============================================
-- ROW LEVEL SECURITY SETUP
-- ============================================

-- 1. Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE group_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE expense_splits ENABLE ROW LEVEL SECURITY;
ALTER TABLE polls ENABLE ROW LEVEL SECURITY;
ALTER TABLE poll_votes ENABLE ROW LEVEL SECURITY;

-- 2. Helper function
CREATE OR REPLACE FUNCTION public.is_group_member(group_id_param UUID, user_id_param UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM group_members
    WHERE group_members.group_id = group_id_param
      AND group_members.user_id = user_id_param
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. Users policies
DROP POLICY IF EXISTS "Users can read own profile" ON users;
CREATE POLICY "Users can read own profile"
  ON users FOR SELECT
  USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON users;
CREATE POLICY "Users can update own profile"
  ON users FOR UPDATE
  USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can read other users basic info" ON users;
CREATE POLICY "Users can read other users basic info"
  ON users FOR SELECT
  USING (true);

-- 4. Groups policies
DROP POLICY IF EXISTS "Users can read their groups" ON groups;
CREATE POLICY "Users can read their groups"
  ON groups FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM group_members
      WHERE group_members.group_id = groups.id
        AND group_members.user_id = auth.uid()
    )
  );

DROP POLICY IF EXISTS "Users can create groups" ON groups;
CREATE POLICY "Users can create groups"
  ON groups FOR INSERT
  WITH CHECK (auth.uid() IS NOT NULL);

-- 5. Group members policies
DROP POLICY IF EXISTS "Users can read group members" ON group_members;
CREATE POLICY "Users can read group members"
  ON group_members FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM group_members gm
      WHERE gm.group_id = group_members.group_id
        AND gm.user_id = auth.uid()
    )
  );

DROP POLICY IF EXISTS "Users can join groups" ON group_members;
CREATE POLICY "Users can join groups"
  ON group_members FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- 6. Messages policies (MOST IMPORTANT)
DROP POLICY IF EXISTS "Users can read messages in their groups" ON messages;
CREATE POLICY "Users can read messages in their groups"
  ON messages FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM group_members
      WHERE group_members.group_id = messages.group_id
        AND group_members.user_id = auth.uid()
    )
  );

DROP POLICY IF EXISTS "Users can send messages in their groups" ON messages;
CREATE POLICY "Users can send messages in their groups"
  ON messages FOR INSERT
  WITH CHECK (
    auth.uid()::text = sender_id::text
    AND EXISTS (
      SELECT 1 FROM group_members
      WHERE group_members.group_id = messages.group_id
        AND group_members.user_id = auth.uid()
    )
  );

DROP POLICY IF EXISTS "Users can update own messages" ON messages;
CREATE POLICY "Users can update own messages"
  ON messages FOR UPDATE
  USING (auth.uid()::text = sender_id::text);

DROP POLICY IF EXISTS "Users can delete own messages" ON messages;
CREATE POLICY "Users can delete own messages"
  ON messages FOR DELETE
  USING (auth.uid()::text = sender_id::text);

-- 7. Expenses policies
DROP POLICY IF EXISTS "Users can read expenses in their groups" ON expenses;
CREATE POLICY "Users can read expenses in their groups"
  ON expenses FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM group_members
      WHERE group_members.group_id = expenses.group_id
        AND group_members.user_id = auth.uid()
    )
  );

DROP POLICY IF EXISTS "Users can create expenses in their groups" ON expenses;
CREATE POLICY "Users can create expenses in their groups"
  ON expenses FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM group_members
      WHERE group_members.group_id = expenses.group_id
        AND group_members.user_id = auth.uid()
    )
  );

-- 8. Polls policies
DROP POLICY IF EXISTS "Users can read polls in their groups" ON polls;
CREATE POLICY "Users can read polls in their groups"
  ON polls FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM group_members
      WHERE group_members.group_id = polls.group_id
        AND group_members.user_id = auth.uid()
    )
  );

DROP POLICY IF EXISTS "Users can create polls in their groups" ON polls;
CREATE POLICY "Users can create polls in their groups"
  ON polls FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM group_members
      WHERE group_members.group_id = polls.group_id
        AND group_members.user_id = auth.uid()
    )
  );
```

---

## How to Test

1. **Test Message Access:**
   - Create two users (User A and User B)
   - Create a group with User A
   - User A should be able to read/write messages
   - User B should NOT be able to see messages (until they join)

2. **Test Group Membership:**
   - User A creates a group
   - User B tries to access `/g/{group_id}` → Should fail
   - User B joins the group
   - User B should now be able to see messages

3. **Check RLS Status:**
   ```sql
   -- Check if RLS is enabled
   SELECT tablename, rowsecurity 
   FROM pg_tables 
   WHERE schemaname = 'public';
   ```

---

## Important Notes

1. **Backend API**: Your backend uses the service key, which bypasses RLS. That's fine - your backend should validate permissions in application code.

2. **Frontend**: The frontend uses the anon key, which is subject to RLS. This is correct!

3. **When creating groups**: After creating a group via backend, make sure to also insert the creator into `group_members` with role='owner'.

4. **Testing**: Always test with multiple users to ensure isolation works correctly.

---

## Current Status

❌ **RLS is likely NOT enabled** - You need to run the setup script above ASAP to secure your data!

