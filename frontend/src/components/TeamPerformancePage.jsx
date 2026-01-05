import React, { useState, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import './Analytics.css';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const TeamPerformancePage = () => {
    const [period, setPeriod] = useState('2026-01');
    const [teamMetrics, setTeamMetrics] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchTeamPerformance();
    }, [period]);

    const fetchTeamPerformance = async () => {
        try {
            setLoading(true);
            const response = await fetch(`/analytics/team-performance?period=${period}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                // Backend now includes user_name directly
                setTeamMetrics(data);
            }
        } catch (error) {
            console.error('Error fetching team performance:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="analytics-container"><p>Chargement...</p></div>;
    }

    // Calculate team totals
    const totalOffers = teamMetrics.reduce((sum, m) => sum + m.offers_handled, 0);
    const avgSuccessRate = teamMetrics.length > 0
        ? teamMetrics.reduce((sum, m) => sum + m.success_rate, 0) / teamMetrics.length
        : 0;
    const totalWorkload = teamMetrics.reduce((sum, m) => sum + m.current_workload, 0);

    return (
        <div className="analytics-container">
            <div className="analytics-header">
                <h1>👥 Performance Équipe</h1>
                <div className="period-selector">
                    <label>Période: </label>
                    <select value={period} onChange={(e) => setPeriod(e.target.value)}>
                        <option value="2026-01">Janvier 2026</option>
                        <option value="2025-12">Décembre 2025</option>
                        <option value="2025-11">Novembre 2025</option>
                        <option value="2025-10">Octobre 2025</option>
                        <option value="2025-09">Septembre 2025</option>
                        <option value="2024-12">Décembre 2024</option>
                        <option value="2024-11">Novembre 2024</option>
                        <option value="2024-10">Octobre 2024</option>
                    </select>
                </div>
            </div>

            {/* Summary Cards */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon">📊</div>
                    <div className="stat-content">
                        <div className="stat-value">{totalOffers}</div>
                        <div className="stat-label">Offres Totales</div>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon">✅</div>
                    <div className="stat-content">
                        <div className="stat-value">{avgSuccessRate.toFixed(1)}%</div>
                        <div className="stat-label">Taux de Succès Moyen</div>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon">⚡</div>
                    <div className="stat-content">
                        <div className="stat-value">{totalWorkload}</div>
                        <div className="stat-label">Charge Actuelle</div>
                    </div>
                </div>
            </div>

            {/* Performance Comparison */}
            <div className="card">
                <div className="card-header">
                    <h2>Comparaison Performance par Utilisateur</h2>
                </div>
                <div className="card-body">
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={teamMetrics}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="user_name" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="offers_handled" fill="#0088FE" name="Offres Gérées" />
                            <Bar dataKey="accepted_count" fill="#00C49F" name="Acceptées" />
                            <Bar dataKey="declined_count" fill="#FF8042" name="Déclinées" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Success Rate Comparison */}
            <div className="card">
                <div className="card-header">
                    <h2>Taux de Succès par Utilisateur</h2>
                </div>
                <div className="card-body">
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={teamMetrics}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="user_name" />
                            <YAxis domain={[0, 100]} />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="success_rate" fill="#00C49F" name="Taux de Succès (%)" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Workload Distribution */}
            <div className="card">
                <div className="card-header">
                    <h2>Répartition de la Charge de Travail</h2>
                </div>
                <div className="card-body">
                    <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                            <Pie
                                data={teamMetrics}
                                dataKey="current_workload"
                                nameKey="user_name"
                                cx="50%"
                                cy="50%"
                                outerRadius={100}
                                label
                            >
                                {teamMetrics.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};

export default TeamPerformancePage;
