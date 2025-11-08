# Supabase Database Trigger Setup

## Purpose
Automatically create a row in the public `users` table whenever a new user signs up via Supabase Auth.

## Steps to Set Up

### 1. Open Supabase SQL Editor
1. Go to https://app.supabase.com
2. Select your project (rszqticfieqpmdmrixbt)
3. Click on **SQL Editor** in the left sidebar
4. Click **New Query**

### 2. Run This SQL Code

Copy and paste this entire block into the SQL Editor:

```sql
-- Function to handle new user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, name, created_at)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'name', SPLIT_PART(NEW.email, '@', 1)),
    NOW()
  )
  ON CONFLICT (id) DO NOTHING; -- Prevents errors if user already exists
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create the trigger that fires after a new auth user is created
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

### 3. Execute the Query
- Click **Run** (or press Cmd/Ctrl + Enter)
- You should see "Success. No rows returned"

### 4. Verify It Works
1. Go to **Authentication** → **Users** in Supabase
2. Create a test user (or sign up from your frontend)
3. Go to **Table Editor** → **users**
4. You should see the new user automatically created!

## How It Works

- When someone signs up via Supabase Auth, a row is created in `auth.users`
- The trigger automatically fires
- It extracts the user's ID, email, and name (from metadata or email prefix)
- Creates a corresponding row in your public `users` table
- `ON CONFLICT DO NOTHING` prevents errors if the user already exists

## Troubleshooting

If you get an error:
- **"permission denied"**: Make sure you're using the SQL Editor (not the Table Editor)
- **"relation does not exist"**: Make sure your `users` table exists and is in the `public` schema
- **"column does not exist"**: Check that your `users` table has columns: `id`, `email`, `name`, `created_at`

## Testing

After setting up:
1. Sign up a new user from your frontend
2. Check the `users` table - you should see them automatically!
3. The `id` in `users` will match the `id` in `auth.users`

