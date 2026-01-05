import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useAuth } from './AuthContext';

const NotificationContext = createContext();

export const NotificationProvider = ({ children }) => {
    const { user } = useAuth();
    const [notifications, setNotifications] = useState([]);
    const [socket, setSocket] = useState(null);

    const connect = useCallback(() => {
        if (!user) return;

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        const wsUrl = `${protocol}//${host}/ws/notifications`;

        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('Connected to notifications');
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setNotifications(prev => [
                {
                    id: Date.now(),
                    ...data,
                    read: false,
                    timestamp: new Date()
                },
                ...prev
            ]);
        };

        ws.onclose = () => {
            console.log('Disconnected from notifications. Retrying in 5s...');
            setTimeout(connect, 5000);
        };

        setSocket(ws);

        return () => {
            ws.close();
        };
    }, [user]);

    useEffect(() => {
        let cleanup;
        if (user) {
            cleanup = connect();
        } else {
            setNotifications([]);
            if (socket) socket.close();
        }
        return cleanup;
    }, [user, connect]);

    const markAsRead = (id) => {
        setNotifications(prev =>
            prev.map(n => n.id === id ? { ...n, read: true } : n)
        );
    };

    const clearAll = () => {
        setNotifications([]);
    };

    return (
        <NotificationContext.Provider value={{ notifications, markAsRead, clearAll }}>
            {children}
        </NotificationContext.Provider>
    );
};

export const useNotifications = () => {
    const context = useContext(NotificationContext);
    if (!context) {
        throw new Error('useNotifications must be used within a NotificationProvider');
    }
    return context;
};
