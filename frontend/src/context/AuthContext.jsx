import React, { createContext, useContext, useEffect, useState } from 'react';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [role, setRole] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check for manual session in localStorage
        const savedSession = localStorage.getItem('bt_session');
        if (savedSession) {
            try {
                const session = JSON.parse(savedSession);
                setUser({ uid: session.uid, phone: session.phone });
                setRole(session.role);
            } catch (e) {
                console.error("Failed to parse session", e);
                localStorage.removeItem('bt_session');
            }
        }
        setLoading(false);
    }, []);

    const login = (userData) => {
        const { uid, phone, role } = userData;
        setUser({ uid, phone });
        setRole(role);
        localStorage.setItem('bt_session', JSON.stringify({ uid, phone, role }));
    };

    const logout = () => {
        setUser(null);
        setRole(null);
        localStorage.removeItem('bt_session');
    };

    const value = {
        user,
        role,
        loading,
        login,
        logout
    };

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    );
};
