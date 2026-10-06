import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Recupera dados da sessao armazenados no localStorage
    const savedToken = localStorage.getItem('cardioia_token');
    const savedUser = localStorage.getItem('cardioia_user');

    if (savedToken && savedUser) {
      try {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
      } catch (e) {
        console.error('Erro ao recuperar sessao:', e);
        localStorage.removeItem('cardioia_token');
        localStorage.removeItem('cardioia_user');
      }
    }
    setLoading(false);
  }, []);

  const login = (email, password) => {
    // Simulacao de autenticacao com geracao de JWT fake
    if (!email || !password) {
      return { success: false, message: 'Preencha o e-mail e a senha' };
    }

    const fakeJwt = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.cardioia_auth_token_secret_simulation_2026';
    const fakeUserData = {
      email,
      nome: email.includes('@') ? email.split('@')[0].toUpperCase() : 'Dr. Giovani Saavedra',
      crm: '123456-SP',
      cargo: 'Cardiologista'
    };

    localStorage.setItem('cardioia_token', fakeJwt);
    localStorage.setItem('cardioia_user', JSON.stringify(fakeUserData));

    setToken(fakeJwt);
    setUser(fakeUserData);

    return { success: true };
  };

  const logout = () => {
    localStorage.removeItem('cardioia_token');
    localStorage.removeItem('cardioia_user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: !!token, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth deve ser utilizado dentro de um AuthProvider');
  }
  return context;
};
