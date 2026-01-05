import React, { useState, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './Analytics.css';

const WorkflowTimingPage = () => {
    const [year, setYear] = useState(2024);
    const [timingStats, setTimingStats] = useState([]);
    const [bottlenecks, setBottlenecks] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, [year]);

    const fetchData = async () => {
        try {
            setLoading(true);

            // Fetch timing stats
            const timingResponse = await fetch(`/analytics/workflow-timing/${year}`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (timingResponse.ok) {
                setTimingStats(await timingResponse.json());
            }

            // Fetch bottlenecks
            const bottleneckResponse = await fetch('/analytics/bottlenecks?threshold_hours=48', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (bottleneckResponse.ok) {
                setBottlenecks(await bottleneckResponse.json());
            }
        } catch (error) {
            console.error('Error fetching workflow timing:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="analytics-container"><p>Chargement...</p></div>;
    }

    return (
        <div className="analytics-container">
            <div className="analytics-header">
                <h1>⏱️ Analyse Temps de Traitement</h1>
                <div className="period-selector">
                    <label>Année: </label>
                    <select value={year} onChange={(e) => setYear(parseInt(e.target.value))}>
                        <option value={2025}>2025</option>
                        <option value={2024}>2024</option>
                    </select>
                </div>
            </div>

            {/* Bottleneck Alerts */}
            {bottlenecks.length > 0 && (
                <div className="card alert-card">
                    <div className="card-header">
                        <h2>⚠️ Alertes Goulots d'Étranglement ({bottlenecks.length})</h2>
                    </div>
                    <div className="card-body">
                        <div className="table-container">
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>Offre</th>
                                        <th>Client</th>
                                        <th>Phase</th>
                                        <th>Durée (h)</th>
                                        <th>Assigné à</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {bottlenecks.slice(0, 10).map((alert, idx) => (
                                        <tr key={idx}>
                                            <td>{alert.offer_number}</td>
                                            <td>{alert.client_name}</td>
                                            <td><span className="badge badge-warning">{alert.phase}</span></td>
                                            <td className="text-danger">{alert.duration_hours.toFixed(1)}h</td>
                                            <td>{alert.assigned_user || 'Non assigné'}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}

            {/* Timing by Phase */}
            <div className="card">
                <div className="card-header">
                    <h2>Temps Moyen par Phase</h2>
                </div>
                <div className="card-body">
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={timingStats}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="phase" />
                            <YAxis label={{ value: 'Heures', angle: -90, position: 'insideLeft' }} />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="avg_duration_hours" fill="#0088FE" name="Temps Moyen (h)" />
                            <Bar dataKey="max_duration_hours" fill="#FF8042" name="Temps Max (h)" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Bottleneck Count by Phase */}
            <div className="card">
                <div className="card-header">
                    <h2>Goulots d'Étranglement par Phase</h2>
                </div>
                <div className="card-body">
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={timingStats}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="phase" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="bottleneck_count" fill="#FF8042" name="Nombre de Goulots" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};

export default WorkflowTimingPage;
