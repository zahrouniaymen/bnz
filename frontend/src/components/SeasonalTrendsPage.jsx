import React, { useState, useEffect } from 'react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './Analytics.css';

const SeasonalTrendsPage = () => {
    const [year, setYear] = useState(2024);
    const [trends, setTrends] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchTrends();
    }, [year]);

    const fetchTrends = async () => {
        try {
            setLoading(true);
            const response = await fetch(`/analytics/seasonal-trends/${year}`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (response.ok) {
                setTrends(await response.json());
            }
        } catch (error) {
            console.error('Error fetching seasonal trends:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="analytics-container"><p>Chargement...</p></div>;
    }

    const totalOffers = trends.reduce((sum, t) => sum + t.total_offers, 0);
    const avgMonthly = trends.length > 0 ? totalOffers / trends.length : 0;

    return (
        <div className="analytics-container">
            <div className="analytics-header">
                <h1>📈 Tendances Saisonnières</h1>
                <div className="period-selector">
                    <label>Année: </label>
                    <select value={year} onChange={(e) => setYear(parseInt(e.target.value))}>
                        <option value={2025}>2025</option>
                        <option value={2024}>2024</option>
                    </select>
                </div>
            </div>

            {/* Summary */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon">📊</div>
                    <div className="stat-content">
                        <div className="stat-value">{totalOffers}</div>
                        <div className="stat-label">Total Offres {year}</div>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon">📅</div>
                    <div className="stat-content">
                        <div className="stat-value">{avgMonthly.toFixed(0)}</div>
                        <div className="stat-label">Moyenne Mensuelle</div>
                    </div>
                </div>
            </div>

            {/* Monthly Volume Trend */}
            <div className="card">
                <div className="card-header">
                    <h2>Évolution Mensuelle des Volumes</h2>
                </div>
                <div className="card-body">
                    <ResponsiveContainer width="100%" height={300}>
                        <AreaChart data={trends}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="month" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Area type="monotone" dataKey="total_offers" fill="#0088FE" stroke="#0088FE" name="Total Offres" />
                            <Area type="monotone" dataKey="accepted" fill="#00C49F" stroke="#00C49F" name="Acceptées" />
                            <Area type="monotone" dataKey="declined" fill="#FF8042" stroke="#FF8042" name="Déclinées" />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Average Value Trend */}
            <div className="card">
                <div className="card-header">
                    <h2>Valeur Moyenne des Offres</h2>
                </div>
                <div className="card-body">
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={trends}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="month" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="avg_value" stroke="#8884D8" name="Valeur Moyenne (€)" strokeWidth={2} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};

export default SeasonalTrendsPage;
