import React, { createContext, useContext, useEffect, useState } from 'react';

const AuthContext = createContext({
  user: null,
  session: null,
  loading: false,
  login: async (email, password) => {},
  logout: async () => {},
});

// Secure clinic staff access password (stored locally/client-side)
const CLINIC_STAFF_PASSWORD = 'radevdent2026';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load local session from localStorage on startup
  useEffect(() => {
    const savedUser = localStorage.getItem('radev_staff_user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
      setSession({ access_token: 'local_token' });
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    setLoading(true);
    try {
      // Validate against the local clinic administrative staff password
      if (password === CLINIC_STAFF_PASSWORD) {
        const staffUser = { email: email || 'staff@radevclinic.bg', role: 'admin' };
        setUser(staffUser);
        setSession({ access_token: 'local_token' });
        localStorage.setItem('radev_staff_user', JSON.stringify(staffUser));
        return { user: staffUser };
      } else {
        throw new Error('Неправилна административна парола за достъп.');
      }
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    try {
      setUser(null);
      setSession(null);
      localStorage.removeItem('radev_staff_user');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthContext.Provider value={{ user, session, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
