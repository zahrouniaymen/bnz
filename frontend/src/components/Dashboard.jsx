import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { offersAPI, dashboardAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import OfferCharts from './OfferCharts';
import './Dashboard.css';

function Dashboard() {
    const [stats, setStats] = useState({
        total_offers: 0,
        pending_registration: 0,
        in_progress: 0,
        accepted: 0,
        declined: 0,
        total_value: 0,
        by_year: {}
    });
    const [loading, setLoading] = useState(true);
    const [importing, setImporting] = useState(false);
    const [importStatus, setImportStatus] = useState(null);
    const [selectedYear, setSelectedYear] = useState('');
    const navigate = useNavigate();
    const { user, isCommerciale } = useAuth();

    useEffect(() => {
        fetchStats(selectedYear);
        checkImportStatus();
    }, [selectedYear]);

    const fetchStats = async (year = null) => {
        try {
            setLoading(true);
            const response = await dashboardAPI.getStats(year);
            setStats(response.data);
        } catch (error) {
            console.error('Error fetching stats:', error);
        } finally {
            setLoading(false);
        }
    };



    const handleImportEmails = async () => {
        try {
            setImporting(true);
            setImportStatus({ type: 'info', message: '📧 Avvio import email...' });

            const token = localStorage.getItem('token');
            const response = await fetch('/offers/import-from-email', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            setImportStatus({ type: 'info', message: '⏳ Import in corso...' });

            const pollInterval = setInterval(async () => {
                const statusResponse = await fetch('/offers/import-status', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const status = await statusResponse.json();

                if (!status.running) {
                    clearInterval(pollInterval);
                    setImporting(false);
                    setImportStatus({ type: 'success', message: '✅ Import email completato!' });
                    fetchStats();
                    setTimeout(() => setImportStatus(null), 5000);
                }
            }, 3000);

        } catch (error) {
            setImporting(false);
            setImportStatus({ type: 'error', message: `❌ Errore: ${error.message}` });
            setTimeout(() => setImportStatus(null), 5000);
        }
    };

    const checkImportStatus = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('/offers/import-status', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const status = await response.json();

            if (status.running) {
                setImporting(true);
                setImportStatus({ type: 'info', message: '⏳ Import in corso...' });
            }
        } catch (error) {
            console.error('Error checking import status:', error);
        }
    };

    if (loading) {
        return (
            <div className="container">
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Caricamento dashboard...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="container fade-in">
            <div className="dashboard-header">
                <div>
                    <h2>Dashboard {user?.full_name || user?.username}</h2>
                    <p className="dashboard-subtitle">
                        {isCommerciale() ? 'Gestione Completa Offerte' : `Dashboard ${user?.department}`}
                    </p>
                </div>
                {isCommerciale() && (
                    <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
                        <button
                            onClick={() => navigate('/offers/pending')}
                            className="btn btn-primary"
                        >
                            📥 Offerte da Registrare ({stats?.pending_registration || 0})
                        </button>
                        <button
                            onClick={handleImportEmails}
                            className="btn btn-secondary"
                            disabled={importing}
                        >
                            {importing ? '⏳ ...' : '📧 Importa Email'}
                        </button>
                    </div>
                )}
            </div>

            {importStatus && (
                <div className={`alert alert-${importStatus.type}`} style={{
                    padding: '0.75rem 1rem',
                    borderRadius: '8px',
                    marginBottom: '1rem',
                    backgroundColor: importStatus.type === 'success' ? '#d4edda' :
                        importStatus.type === 'error' ? '#f8d7da' : '#d1ecf1',
                    color: importStatus.type === 'success' ? '#155724' :
                        importStatus.type === 'error' ? '#721c24' : '#0c5460',
                    border: '1px solid currentColor'
                }}>
                    {importStatus.message}
                </div>
            )}

            <div className="dashboard-filters glass-card" style={{
                padding: '1rem',
                marginBottom: '2rem',
                display: 'flex',
                alignItems: 'center',
                gap: '1rem'
            }}>
                <span style={{ fontWeight: '500' }}>📅 Filtra Statistiche per Anno:</span>
                <select
                    className="form-select"
                    style={{ maxWidth: '200px' }}
                    value={selectedYear}
                    onChange={(e) => setSelectedYear(e.target.value)}
                >
                    <option value="">Tutti gli anni</option>
                    <option value="2024">2024</option>
                    <option value="2025">2025</option>
                </select>
                {selectedYear && (
                    <button
                        className="btn btn-sm btn-secondary"
                        onClick={() => setSelectedYear('')}
                    >
                        Ripristina
                    </button>
                )}
            </div>

            <div className="stats-grid">
                <div className="stat-card glass-card" onClick={() => navigate(selectedYear ? `/offers/${selectedYear}` : '/offers')}>
                    <div className="stat-icon stat-icon-primary">📊</div>
                    <div className="stat-content">
                        <h3 className="stat-value">{stats?.total_offers || 0}</h3>
                        <p className="stat-label">Offerte {selectedYear || 'Totali'}</p>
                    </div>
                </div>

                {isCommerciale() && (
                    <div className="stat-card glass-card" onClick={() => navigate('/offers/pending')}>
                        <div className="stat-icon stat-icon-warning">📥</div>
                        <div className="stat-content">
                            <h3 className="stat-value">{stats?.pending_registration || 0}</h3>
                            <p className="stat-label">Da Registrare {selectedYear ? `(${selectedYear})` : ''}</p>
                        </div>
                    </div>
                )}

                <div className="stat-card glass-card" onClick={() => navigate('/offers/in-progress')}>
                    <div className="stat-icon stat-icon-info">⚙️</div>
                    <div className="stat-content">
                        <h3 className="stat-value">{stats?.in_progress || 0}</h3>
                        <p className="stat-label">In Lavorazione {selectedYear ? `(${selectedYear})` : ''}</p>
                    </div>
                </div>

                <div className="stat-card glass-card" onClick={() => navigate('/offers/accepted')}>
                    <div className="stat-icon stat-icon-success">✅</div>
                    <div className="stat-content">
                        <h3 className="stat-value">{stats?.accepted || 0}</h3>
                        <p className="stat-label">Accettate {selectedYear ? `(${selectedYear})` : ''}</p>
                    </div>
                </div>

                {!selectedYear && (
                    <>
                        <div className="stat-card glass-card" onClick={() => navigate('/offers/2024')}>
                            <div className="stat-icon stat-icon-primary">📅</div>
                            <div className="stat-content">
                                <h3 className="stat-value">{stats?.by_year?.['2024'] || 0}</h3>
                                <p className="stat-label">Offerte 2024</p>
                            </div>
                        </div>

                        <div className="stat-card glass-card" onClick={() => navigate('/offers/2025')}>
                            <div className="stat-icon stat-icon-info">📅</div>
                            <div className="stat-content">
                                <h3 className="stat-value">{stats?.by_year?.['2025'] || 0}</h3>
                                <p className="stat-label">Offerte 2025</p>
                            </div>
                        </div>
                    </>
                )}
            </div>

            <OfferCharts stats={stats} />
        </div>
    );
}

export default Dashboard;
