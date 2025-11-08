# Authentication Setup - Frontend Complete ✅

## What's Been Implemented

### 1. **Auth Guard Hook** (`app/lib/useAuth.ts`)
   - Protects routes by checking for valid Supabase session
   - Automatically redirects to `/` if user is not authenticated
   - Returns `{ user, loading }` for use in components

### 2. **Protected Routes**
   - `/groups` - Requires auth (uses `useAuth()` hook)
   - `/g/[groupId]` - Requires auth (uses `useAuth()` hook)
   - `/` - Public (redirects logged-in users to `/groups`)

### 3. **Auth Token Passing**
   - All API calls now include `Authorization: Bearer <token>` header
   - Token is retrieved from Supabase session via `getAccessToken()`
   - Helper function `getAuthHeaders()` in `app/lib/api.ts` handles this automatically

### 4. **User Flow**
   - Unauthenticated users → See homepage → Sign up/in → Redirected to `/groups`
   - Authenticated users visiting `/` → Automatically redirected to `/groups`
   - Authenticated users can access `/groups` and `/g/[groupId]`

---

## For Backend Team: What You Need to Know

### 1. **Supabase JWT Validation**
   Your FastAPI backend needs to validate the Supabase JWT token from the `Authorization` header.

   **Token Format:**
   ```
   Authorization: Bearer <supabase-access-token>
   ```

   **How to Validate:**
   - Use Supabase's public JWT key (available in Supabase dashboard)
   - Or use Supabase Python client to verify tokens
   - Extract user ID from the token payload: `token['sub']` or `token['user_id']`

   **Example FastAPI middleware:**
   ```python
   from supabase import create_client
   import os
   
   supabase = create_client(
       os.getenv("SUPABASE_URL"),
       os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for server-side
   )
   
   async def verify_token(token: str):
       # Verify and decode the JWT
       user = supabase.auth.get_user(token)
       return user
   ```

### 2. **User ID in API Calls**
   After validating the token, you'll have:
   - `user.id` - Supabase user UUID
   - `user.email` - User's email
   - `user.user_metadata` - Any custom metadata (like name)

   Use `user.id` to:
   - Associate groups with users
   - Check group membership
   - Track message senders

### 3. **Environment Variables Needed**
   Share these with frontend team:
   - `NEXT_PUBLIC_SUPABASE_URL` - Your Supabase project URL
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Your Supabase anon key
   - `NEXT_PUBLIC_BACKEND_API_URL` - Your FastAPI backend URL (default: `http://localhost:8000`)

### 4. **API Endpoints That Need Auth**
   All these endpoints should validate the `Authorization` header:
   - `POST /api/groups` - Create group (associate with user)
   - `GET /api/groups` - List user's groups
   - `GET /api/groups/{group_id}` - Get group details (check membership)
   - `POST /api/messages/` - Send message (check group membership)
   - `GET /api/messages/{group_id}` - Get messages (check group membership)
   - `POST /api/groups/{group_id}/join` - Join group (validate invite code)

### 5. **Group Membership**
   When a user creates or joins a group, store the relationship:
   - `group_members` table: `user_id`, `group_id`, `role` (owner/member), `joined_at`
   - Check membership before allowing access to group data

---

## Next Steps

1. **Frontend:** Add real Supabase credentials to `.env.local`
2. **Backend:** Implement JWT validation middleware
3. **Backend:** Create group membership tables/relationships
4. **Both:** Test auth flow end-to-end
5. **Frontend:** Connect group creation/joining to backend APIs

---

## Files Changed

- `app/lib/useAuth.ts` - New auth guard hook
- `app/lib/auth.ts` - Added `getAccessToken()` function
- `app/lib/api.ts` - Updated to include auth headers
- `app/page.tsx` - Added redirect for logged-in users
- `app/groups/page.tsx` - Added auth guard
- `app/g/[groupId]/page.tsx` - Added auth guard
- `.env.local.example` - Template for environment variables

