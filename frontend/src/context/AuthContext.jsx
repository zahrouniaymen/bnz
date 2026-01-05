import { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Auto-create admin session
        const adminUser = {
            id: 1,
            username: 'admin',
            email: 'admin@m54.com',
            role: 'admin',
            full_name: 'Administrator',
            department: 'Direction',
            active: true
        };

        localStorage.setItem('token', 'auto-admin-session');
        localStorage.setItem('user', JSON.stringify(adminUser));
        setUser(adminUser);
        setLoading(false);
    }, []);

    const logout = () => {
        // Logout does nothing, just reload to reset
        window.location.reload();
    };

    const isCommerciale = () => {
        return true; // Always admin
    };

    const isAdmin = () => {
        return true; // Always admin
    };

    const isDepartment = (department) => {
        return true; // Always has all permissions
    };

    const value = {
        user,
        loading,
        logout,
        isCommerciale,
        isAdmin,
        isDepartment,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};
