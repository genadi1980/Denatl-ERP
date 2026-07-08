import { createClient } from '@supabase/supabase-js';

// Use placeholders to prevent Supabase SDK from throwing an initialization exception and crashing the Vite bundle if environment variables are not yet configured.
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://placeholder-project.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBsYWNlaG9sZGVyIn0.dummy_key';

if (!import.meta.env.VITE_SUPABASE_URL || !import.meta.env.VITE_SUPABASE_ANON_KEY) {
  console.warn(
    'WARNING: Supabase URL or Anon Key is missing from Vite environment variables! Auth services and direct database queries will fail. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in your frontend/.env file.'
  );
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
