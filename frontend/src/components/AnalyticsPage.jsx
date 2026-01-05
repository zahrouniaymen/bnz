import React, { useState, useEffect } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    LineChart, Line, PieChart, Pie, Cell
} from 'recharts';
import { analyticsAPI } from '../services/api';
import './Analytics.css';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658'];

const AnalyticsPage = () => {
    const [year, setYear] = useState(2024);
    const [monthlyData, setMonthlyData] = useState([]);
    const [reasonsData, setReasonsData] = useState({ declined_reasons: [], not_accepted_reasons: [] });
    const [clientRanking, setClientRanking] = useState([]);
    const [sectorData, setSectorData] = useState([]);
    const [itemMixData, setItemMixData] = useState({ new: { count: 0, value: 0 }, reorder: { count: 0, value: 0 } });
    const [searchTerm, setSearchTerm] = useState('');
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('performance');

    const availableYears = [2024, 2025];

    const [comparisonData, setComparisonData] = useState({
        requests: [], declined: [], proposed: [], accepted: [], order_value: []
    });

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const [monthlyRes, reasonsRes, comparisonRes, clientsRes, sectorRes, itemMixRes] = await Promise.allSettled([
                    analyticsAPI.getMonthlyEvolution(year),
                    analyticsAPI.getReasons(year),
                    analyticsAPI.getComparison("2024,2025"),
                    analyticsAPI.getClientRanking(year),
                    analyticsAPI.getSectorDistribution(year),
                    analyticsAPI.getItemMix(year)
                ]);

                if (monthlyRes.status === 'fulfilled') setMonthlyData(monthlyRes.value.data || []);
                if (reasonsRes.status === 'fulfilled') setReasonsData(reasonsRes.value.data || { declined_reasons: [], not_accepted_reasons: [] });
                if (comparisonRes.status === 'fulfilled') setComparisonData(comparisonRes.value.data || { requests: [], declined: [], proposed: [], accepted: [], order_value: [] });
                if (clientsRes.status === 'fulfilled') setClientRanking(clientsRes.value.data || []);
                if (sectorRes.status === 'fulfilled') setSectorData(sectorRes.value.data || []);
                if (itemMixRes.status === 'fulfilled') setItemMixData(itemMixRes.value.data || { new: { count: 0, value: 0 }, reorder: { count: 0, value: 0 } });

            } catch (error) {
                console.error("Error fetching analytics:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [year]);

    const handleExportExcel = () => {
        const baseUrl = window.location.origin.replace('5175', '8002');
        window.open(`${baseUrl}/analytics/export/excel/${year}`, '_blank');
    };

    const handleExportPDF = () => {
        const baseUrl = window.location.origin.replace('5175', '8002');
        window.open(`${baseUrl}/analytics/export/pdf/${year}`, '_blank');
    };

    const renderComparisonLines = () => (
        <>
            <Line type="monotone" dataKey="2024" name="2024" stroke="#82ca9d" strokeWidth={3} dot={{ r: 4 }} />
            <Line type="monotone" dataKey="2025" name="2025" stroke="#ffc658" strokeWidth={2} dot={{ r: 4 }} />
        </>
    );

    const formatCurrency = (val) => {
        return new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(val);
    };

    const formatPercent = (val) => {
        if (!val || isNaN(val)) return '0.0%';
        return `${val.toFixed(1)}%`;
    };

    const formatYAxis = (tickItem) => {
        if (tickItem >= 1000000) return `${(tickItem / 1000000).toFixed(1)}M`;
        if (tickItem >= 1000) return `${(tickItem / 1000).toFixed(0)}k`;
        return tickItem;
    };

    const totals = monthlyData.reduce((acc, curr) => ({
        requests: acc.requests + curr.requests,
        declined: acc.declined + curr.declined,
        proposed: acc.proposed + curr.proposed,
        accepted: acc.accepted + curr.accepted,
        order_value: acc.order_value + curr.order_value
    }), { requests: 0, declined: 0, proposed: 0, accepted: 0, order_value: 0 });

    const totalAcceptedRate = totals.requests > 0 ? (totals.accepted / totals.requests * 100) : 0;

    if (loading) return <div className="loading">Caricamento analisi...</div>;

    return (
        <div className="analytics-container">
            <div className="analytics-header glass-effect">
                <div className="header-title">
                    <h2>📈 Analisi Dettagliata Offerte - {year}</h2>
                    <p className="subtitle">Visualizzazione e monitoraggio dei KPI aziendali</p>
                </div>

                <div className="header-actions">
                    <div className="year-selector">
                        {availableYears.map(y => (
                            <button key={y} className={year === y ? 'active' : ''} onClick={() => setYear(y)}>
                                {y}
                            </button>
                        ))}
                    </div>
                    <div className="export-actions">
                        <button onClick={handleExportExcel} className="btn btn-secondary">
                            📥 Excel
                        </button>
                        <button onClick={handleExportPDF} className="btn btn-primary">
                            📄 PDF
                        </button>
                    </div>
                </div>
            </div>

            <div className="analytics-tabs">
                <button className={`tab-btn ${activeTab === 'performance' ? 'active' : ''}`} onClick={() => setActiveTab('performance')}>📈 Performance</button>
                <button className={`tab-btn ${activeTab === 'business' ? 'active' : ''}`} onClick={() => setActiveTab('business')}>🏢 Analisi Business</button>
                <button className={`tab-btn ${activeTab === 'confronto' ? 'active' : ''}`} onClick={() => setActiveTab('confronto')}>📊 Confronto Anni</button>
                <button className={`tab-btn ${activeTab === 'clienti' ? 'active' : ''}`} onClick={() => setActiveTab('clienti')}>👥 Ranking Clienti</button>
            </div>

            {activeTab === 'performance' && (
                <div className="tab-content fade-in">
                    <div className="card table-card full-width">
                        <h3>📋 Riepilogo Mensile {year}</h3>
                        <div className="table-responsive">
                            <table className="analysis-table">
                                <thead>
                                    <tr>
                                        <th>MESE</th><th>RICHIESTE</th><th>DECLINATE</th><th>PROPOSTE</th><th>ACCETTATE</th><th>%</th><th>VALORE (€)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {monthlyData.map((data, index) => {
                                        const acceptedRate = data.requests > 0 ? (data.accepted / data.requests * 100) : 0;
                                        return (
                                            <tr key={index}>
                                                <td>{data.month}</td>
                                                <td>{data.requests}</td><td>{data.declined}</td><td>{data.proposed}</td><td>{data.accepted}</td>
                                                <td>{formatPercent(acceptedRate)}</td>
                                                <td className="currency-cell">{formatCurrency(data.order_value)}</td>
                                            </tr>
                                        );
                                    })}
                                    <tr className="totals-row" style={{ fontWeight: 'bold' }}>
                                        <td>TOT.</td><td>{totals.requests}</td><td>{totals.declined}</td><td>{totals.proposed}</td><td>{totals.accepted}</td>
                                        <td>{formatPercent(totalAcceptedRate)}</td><td>{formatCurrency(totals.order_value)}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}

            {activeTab === 'business' && (
                <div className="tab-content fade-in">
                    <div className="grid-2">
                        <div className="card chart-card">
                            <h3>🔍 Distribuzione per Settore</h3>
                            <div style={{ height: 300 }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie
                                            data={sectorData}
                                            cx="50%"
                                            cy="50%"
                                            labelLine={true}
                                            label={({ percent }) => `${(percent * 100).toFixed(0)}%`}
                                            outerRadius={80}
                                            fill="#8884d8"
                                            dataKey="value"
                                            nameKey="sector"
                                        >
                                            {sectorData.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <Tooltip formatter={(value) => formatCurrency(value)} />
                                        <Legend />
                                    </PieChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        <div className="card chart-card">
                            <h3>📦 Mix Articoli (Nuovi vs Riordini)</h3>
                            <div style={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                <div className="item-mix-stats">
                                    <div className="stat-item">
                                        <span className="label">Nuovi Articoli:</span>
                                        <span className="value">{itemMixData.new.count} ({formatCurrency(itemMixData.new.value)})</span>
                                    </div>
                                    <div className="stat-item">
                                        <span className="label">Riordini:</span>
                                        <span className="value">{itemMixData.reorder.count} ({formatCurrency(itemMixData.reorder.value)})</span>
                                    </div>
                                    <div className="progress-bar-container">
                                        <div className="progress-bar">
                                            <div
                                                className="progress-fill new"
                                                style={{ width: `${(itemMixData.new.count / (itemMixData.new.count + itemMixData.reorder.count + 0.1) * 100)}%` }}
                                            ></div>
                                        </div>
                                        <div className="progress-labels">
                                            <span>Nuovi</span>
                                            <span>Riordini</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="card chart-card full-width">
                            <h3>📉 Analisi Motivi Rifiuto {year}</h3>
                            <div className="grid-2">
                                <div>
                                    <h4>Offerte DECLINATE (Motivi Interni)</h4>
                                    <ResponsiveContainer width="100%" height={250}>
                                        <BarChart data={reasonsData.declined_reasons} layout="vertical">
                                            <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                            <XAxis type="number" hide />
                                            <YAxis dataKey="reason" type="category" width={150} tick={{ fontSize: 12 }} />
                                            <Tooltip />
                                            <Bar dataKey="count" fill="#FF8042" radius={[0, 4, 4, 0]} />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                                <div>
                                    <h4>NON ACCETTATE (Motivi Cliente)</h4>
                                    <ResponsiveContainer width="100%" height={250}>
                                        <BarChart data={reasonsData.not_accepted_reasons} layout="vertical">
                                            <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                            <XAxis type="number" hide />
                                            <YAxis dataKey="reason" type="category" width={150} tick={{ fontSize: 12 }} />
                                            <Tooltip />
                                            <Bar dataKey="count" fill="#8884d8" radius={[0, 4, 4, 0]} />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {activeTab === 'confronto' && (
                <div className="tab-content fade-in">
                    <div className="grid-2">
                        <div className="card chart-card">
                            <h3>📊 Richieste Ricevute (2024 vs 2025)</h3>
                            <div style={{ height: 300 }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={comparisonData.requests} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                                        <XAxis dataKey="month" tick={{ fill: '#aaa', fontSize: 12 }} />
                                        <YAxis tick={{ fill: '#aaa', fontSize: 12 }} tickFormatter={formatYAxis} />
                                        <Tooltip contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #444' }} />
                                        <Legend />
                                        {renderComparisonLines()}
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        <div className="card chart-card">
                            <h3>💰 Valore Ordini (2024 vs 2025)</h3>
                            <div style={{ height: 300 }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={comparisonData.order_value} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                                        <XAxis dataKey="month" tick={{ fill: '#aaa', fontSize: 12 }} />
                                        <YAxis tick={{ fill: '#aaa', fontSize: 12 }} tickFormatter={formatYAxis} />
                                        <Tooltip formatter={(val) => formatCurrency(val)} />
                                        <Legend />
                                        <Bar dataKey="2024" name="2024" fill="#8884d8" />
                                        <Bar dataKey="2025" name="2025" fill="#82ca9d" />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {activeTab === 'clienti' && (
                <div className="tab-content fade-in">
                    <div className="card table-card full-width">
                        <div className="card-header">
                            <h3>👥 Top 50 Clienti - {year}</h3>
                            <input
                                type="text"
                                placeholder="Cerca cliente..."
                                className="search-input"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>
                        <div className="table-responsive">
                            <table className="analysis-table">
                                <thead>
                                    <tr>
                                        <th>CLIENTE</th><th>RICHIESTE</th><th>ACCETTATE</th><th>RIFIUTATE</th><th>% SUCCESSO</th><th>VALORE TOTALE</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {clientRanking
                                        .filter(c => c.client_name.toLowerCase().includes(searchTerm.toLowerCase()))
                                        .map((client, index) => (
                                            <tr key={index}>
                                                <td style={{ fontWeight: 500 }}>{client.client_name}</td>
                                                <td>{client.requests}</td>
                                                <td className="success-cell">{client.accepted}</td>
                                                <td className="danger-cell">{client.declined + client.not_accepted}</td>
                                                <td>
                                                    <div className="rank-progress">
                                                        <div className="progress-bar">
                                                            <div className="progress-fill" style={{ width: `${client.success_rate}%` }}></div>
                                                        </div>
                                                        <span>{formatPercent(client.success_rate)}</span>
                                                    </div>
                                                </td>
                                                <td className="currency-cell">{formatCurrency(client.total_value)}</td>
                                            </tr>
                                        ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AnalyticsPage;
