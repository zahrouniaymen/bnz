import React, { useState } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useNotifications } from '../context/NotificationContext';
import './Layout.css';
import './DropdownNav.css';

function Layout() {
    const { user, logout, isCommerciale } = useAuth();
    const { notifications, markAsRead, clearAll } = useNotifications();
    const navigate = useNavigate();
    const location = useLocation();
    const [showNotifications, setShowNotifications] = useState(false);

    const unreadCount = notifications.filter(n => !n.read).length;

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="app">
            <nav className="navbar">
                <div className="container">
                    <div className="navbar-content">
                        <div className="navbar-brand">
                            <h1 className="gradient-text">M54 Offer Management</h1>
                            <p className="navbar-subtitle">Sistema di Gestione Offerte</p>
                        </div>
                        <div className="navbar-links">
                            <Link to="/" className="nav-link">
                                <span className="nav-icon">📊</span>
                                Dashboard
                            </Link>
                            <Link to="/clients" className="nav-link">
                                <span className="nav-icon">🏢</span>
                                Clienti
                            </Link>

                            {isCommerciale() ? (
                                <>
                                    {/* Analytics with submenu */}
                                    <div className="nav-dropdown">
                                        <Link to="/analytics" className={`nav-link ${location.pathname.startsWith('/analytics') ? 'active' : ''}`}>
                                            <span className="nav-icon">📈</span>
                                            Analisi
                                        </Link>
                                        <div className="dropdown-content">
                                            <Link to="/analytics" className={location.pathname === '/analytics' ? 'active' : ''}>📊 Performance Business</Link>
                                            <Link to="/analytics/team" className={location.pathname === '/analytics/team' ? 'active' : ''}>👥 Performance Team</Link>
                                            <Link to="/analytics/workflow" className={location.pathname === '/analytics/workflow' ? 'active' : ''}>⏱️ Workflow & Timing</Link>
                                            <Link to="/analytics/trends" className={location.pathname === '/analytics/trends' ? 'active' : ''}>📈 Tendances Saisonnières</Link>
                                        </div>
                                    </div>
                                    <Link to="/offers" className="nav-link">
                                        <span className="nav-icon">📋</span>
                                        Tutte le Offerte
                                    </Link>
                                    <Link to="/offers/pending" className="nav-link">
                                        <span className="nav-icon">📥</span>
                                        Da Registrare
                                    </Link>
                                </>
                            ) : (
                                <Link to="/my-offers" className="nav-link">
                                    <span className="nav-icon">📋</span>
                                    Le Mie Offerte
                                </Link>
                            )}

                            <div className="nav-notifications">
                                <button
                                    className="notification-btn"
                                    onClick={() => setShowNotifications(!showNotifications)}
                                >
                                    🔔
                                    {unreadCount > 0 && <span className="notification-badge">{unreadCount}</span>}
                                </button>

                                {showNotifications && (
                                    <div className="notification-dropdown glass-effect">
                                        <div className="notification-header">
                                            <h3>Notifiche</h3>
                                            <button onClick={clearAll} className="btn-text">Pulisci tutto</button>
                                        </div>
                                        <div className="notification-list">
                                            {notifications.length === 0 ? (
                                                <p className="no-notifications">Nessuna notifica</p>
                                            ) : (
                                                notifications.map(n => (
                                                    <div key={n.id} className={`notification-item ${n.read ? 'read' : 'unread'}`} onClick={() => markAsRead(n.id)}>
                                                        <p className="notification-msg">{n.message}</p>
                                                        <span className="notification-time">
                                                            {new Date(n.timestamp).toLocaleTimeString()}
                                                        </span>
                                                    </div>
                                                ))
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>

                            <div className="nav-user">
                                <span className="user-info">
                                    👤 {user?.full_name || user?.username}
                                    <span className="user-role">{user?.role}</span>
                                </span>
                                <button onClick={handleLogout} className="btn btn-secondary btn-sm">
                                    Esci
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </nav>

            <main className="main-content">
                <Outlet />
            </main>

            <footer className="footer">
                <div className="container">
                    <p>© 2024 Benozzi - Sistema Gestione Offerte M54 v2.0</p>
                </div>
            </footer>
        </div>
    );
}

export default Layout;
