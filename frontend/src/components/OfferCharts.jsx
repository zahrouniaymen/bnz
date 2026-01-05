import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function OfferCharts({ stats }) {
    // Data for status pie chart
    const statusData = [
        { name: 'Da Registrare', value: stats?.pending_registration || 0, color: '#f59e0b' },
        { name: 'In Lavorazione', value: stats?.in_progress || 0, color: '#3b82f6' },
        { name: 'Accettate', value: stats?.accepted || 0, color: '#10b981' },
        { name: 'Declinate', value: stats?.declined || 0, color: '#ef4444' }
    ].filter(item => item.value > 0);

    // Data for value chart
    const valueData = [
        { name: 'Valore Totale', value: stats?.total_value || 0 }
    ];

    const formatYAxis = (tickItem) => {
        if (tickItem >= 1000000) return `${(tickItem / 1000000).toFixed(1)}M`;
        if (tickItem >= 1000) return `${(tickItem / 1000).toFixed(0)}k`;
        return tickItem;
    };

    return (
        <div className="charts-container" style={{ marginTop: '2rem' }}>
            <h3 style={{ marginBottom: '1.5rem', color: '#e2e8f0' }}>📊 Statistiche Visuali</h3>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
                {/* Status Distribution Pie Chart */}
                <div className="glass-card" style={{ padding: '1.5rem' }}>
                    <h4 style={{ marginBottom: '1rem', color: '#cbd5e1' }}>Distribuzione per Stato</h4>
                    <ResponsiveContainer width="100%" height={280}>
                        <PieChart>
                            <Pie
                                data={statusData}
                                cx="50%"
                                cy="45%"
                                labelLine={true}
                                label={({ percent }) => `${(percent * 100).toFixed(0)}%`}
                                outerRadius={80}
                                fill="#8884d8"
                                dataKey="value"
                            >
                                {statusData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                            <Tooltip formatter={(value, name, props) => [`${value} offerte`, name]} />
                            <Legend verticalAlign="bottom" height={36} />
                        </PieChart>
                    </ResponsiveContainer>
                </div>

                {/* Total Value Bar Chart */}
                <div className="glass-card" style={{ padding: '1.5rem' }}>
                    <h4 style={{ marginBottom: '1rem', color: '#cbd5e1' }}>Valore Totale Offerte</h4>
                    <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={valueData} margin={{ top: 10, right: 30, left: 10, bottom: 20 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                            <XAxis
                                dataKey="name"
                                stroke="#9ca3af"
                                tick={{ fontSize: 12 }}
                            />
                            <YAxis
                                stroke="#9ca3af"
                                tickFormatter={formatYAxis}
                                tick={{ fontSize: 12 }}
                            />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
                                formatter={(value) => `€${value.toLocaleString('it-IT', { minimumFractionDigits: 0 })}`}
                            />
                            <Bar dataKey="value" fill="#10b981" barSize={60} radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                {/* Summary Stats */}
                <div className="glass-card" style={{ padding: '1.5rem' }}>
                    <h4 style={{ marginBottom: '1rem', color: '#cbd5e1' }}>Riepilogo Rapido</h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem', backgroundColor: 'rgba(59, 130, 246, 0.1)', borderRadius: '6px' }}>
                            <span>Totale Offerte:</span>
                            <strong>{stats?.total_offers || 0}</strong>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem', backgroundColor: 'rgba(245, 158, 11, 0.1)', borderRadius: '6px' }}>
                            <span>Da Processare:</span>
                            <strong>{stats?.pending_registration || 0}</strong>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem', backgroundColor: 'rgba(16, 185, 129, 0.1)', borderRadius: '6px' }}>
                            <span>Tasso Successo:</span>
                            <strong>
                                {stats?.total_offers > 0
                                    ? ((stats.accepted / stats.total_offers) * 100).toFixed(1)
                                    : 0}%
                            </strong>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem', backgroundColor: 'rgba(16, 185, 129, 0.1)', borderRadius: '6px' }}>
                            <span>Valore Medio:</span>
                            <strong>
                                €{stats?.total_offers > 0
                                    ? ((stats.total_value || 0) / stats.total_offers).toLocaleString('it-IT', { minimumFractionDigits: 2 })
                                    : '0.00'}
                            </strong>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default OfferCharts;
