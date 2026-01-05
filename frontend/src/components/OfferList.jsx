import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { offersAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import './OfferList.css';

function OfferList({ filterStatus = null, filterYear = null, myOffers = false }) {
    const [offers, setOffers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({
        status: filterStatus || '',
        priority: '',
        year: filterYear || '', // Initialize with filterYear
        search: ''
    });
    const navigate = useNavigate();
    const { user, isCommerciale } = useAuth();

    useEffect(() => {
        fetchOffers();
    }, [filterStatus, myOffers]);

    const fetchOffers = async () => {
        try {
            setLoading(true);

            const params = {};
            if (filterStatus) params.status = filterStatus;

            let response;
            if (myOffers) {
                response = await offersAPI.getMyOffers();
            } else {
                response = await offersAPI.getAll(params);
            }

            // Handle both list response (real API) and object wrapper (if any)
            const offersData = Array.isArray(response.data) ? response.data : (response.data.offers || []);
            setOffers(offersData);
        } catch (error) {
            console.error('[OfferList] Error:', error);
            setOffers([]);
        } finally {
            setLoading(false);
        }
    };

    const getStatusBadge = (status) => {
        const statusMap = {
            'PENDING_REGISTRATION': { class: 'badge-warning', label: 'Da Registrare' },
            'IN_LAVORO': { class: 'badge-info', label: 'In Lavoro' },
            'CHECKS_IN_PROGRESS': { class: 'badge-info', label: 'In Verifica' },
            'READY_TO_SEND': { class: 'badge-success', label: 'Pronta' },
            'SENT': { class: 'badge-primary', label: 'Inviata' },
            'ACCETTATA': { class: 'badge-success', label: 'Accettata' },
            'DECLINATA': { class: 'badge-danger', label: 'Declinata' },
            'NON_ACCETTATA': { class: 'badge-warning', label: 'Non Accettata' },
        };
        return statusMap[status] || { class: 'badge-default', label: status };
    };

    const getPriorityBadge = (priority) => {
        const priorityMap = {
            'URGENTE': { class: 'priority-urgent', icon: '🔴', label: 'Urgente' },
            'ALTA': { class: 'priority-high', icon: '🟠', label: 'Alta' },
            'MEDIA': { class: 'priority-medium', icon: '🟡', label: 'Media' },
            'BASSA': { class: 'priority-low', icon: '🟢', label: 'Bassa' },
        };
        return priorityMap[priority] || { class: '', icon: '', label: priority };
    };

    const filteredOffers = offers.filter(offer => {
        if (filters.status && offer.status !== filters.status) return false;
        if (filters.priority && offer.priority !== filters.priority) return false;
        if (filters.year && offer.year_stats !== parseInt(filters.year)) return false; // Added year filter
        if (filters.search) {
            const search = filters.search.toLowerCase();
            return (
                offer.offer_number?.toString().toLowerCase().includes(search) || // Changed to toString()
                offer.client?.name?.toLowerCase().includes(search) ||
                offer.item_name?.toLowerCase().includes(search) // Added item_name
            );
        }
        return true;
    });

    if (loading) {
        return (
            <div className="container">
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Caricamento offerte...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="container fade-in">
            <div className="list-header">
                <div>
                    <h2>
                        {filterStatus === 'PENDING_REGISTRATION' ? '📥 Offerte da Registrare' :
                            filterStatus === 'IN_LAVORO' ? '⚙️ Offerte in Lavorazione' :
                                filterStatus === 'ACCETTATA' ? '✅ Offerte Accettate' :
                                    filters.year === '2024' ? '📅 Offerte 2024' :
                                        filters.year === '2025' ? '📅 Offerte 2025' :
                                            myOffers ? '📋 Le Mie Offerte' : '📋 Tutte le Offerte'}
                    </h2>
                    <p className="list-subtitle">{filteredOffers.length} offerte trovate</p>
                </div>
            </div>

            {!filterStatus && (
                <div className="filters-bar glass-card">
                    <input
                        type="text"
                        className="form-input"
                        placeholder="🔍 Cerca per numero, cliente, oggetto..."
                        value={filters.search}
                        onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                    />

                    <select
                        className="form-select"
                        value={filters.status}
                        onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                    >
                        <option value="">Tutti gli stati</option>
                        <option value="PENDING_REGISTRATION">Da Registrare</option>
                        <option value="IN_LAVORO">In Lavoro</option>
                        <option value="CHECKS_IN_PROGRESS">In Verifica</option>
                        <option value="READY_TO_SEND">Pronta</option>
                        <option value="SENT">Inviata</option>
                        <option value="ACCETTATA">Accettata</option>
                        <option value="DECLINATA">Declinata</option>
                    </select>

                    <select
                        className="form-select"
                        value={filters.priority}
                        onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
                    >
                        <option value="">Tutte le priorità</option>
                        <option value="URGENTE">🔴 Urgente</option>
                        <option value="ALTA">🟠 Alta</option>
                        <option value="MEDIA">🟡 Media</option>
                        <option value="BASSA">🟢 Bassa</option>
                    </select>

                    <select
                        className="form-select"
                        value={filters.year}
                        onChange={(e) => setFilters({ ...filters, year: e.target.value })}
                    >
                        <option value="">Tutti gli anni</option>
                        <option value="2024">2024</option>
                        <option value="2025">2025</option>
                    </select>
                </div>
            )}

            {filteredOffers.length === 0 ? (
                <div className="empty-state glass-card">
                    <h3>📭 Nessuna offerta trovata</h3>
                    <p>Non ci sono offerte che corrispondono ai criteri selezionati.</p>
                </div>
            ) : (
                <div className="offers-grid">
                    {filteredOffers.map(offer => {
                        const statusInfo = getStatusBadge(offer.status);
                        const priorityInfo = getPriorityBadge(offer.priority);

                        return (
                            <div
                                key={offer.id}
                                className="offer-card glass-card"
                                onClick={() => navigate(`/offers/${offer.id}`)}
                            >
                                <div className="offer-card-header">
                                    <div className="offer-number">
                                        <strong>{offer.offer_number}</strong>
                                        {offer.priority && (
                                            <span className={`priority-badge ${priorityInfo.class}`}>
                                                {priorityInfo.icon} {priorityInfo.label}
                                            </span>
                                        )}
                                    </div>
                                    <span className={`badge ${statusInfo.class}`}>
                                        {statusInfo.label}
                                    </span>
                                </div>

                                <div className="offer-card-body">
                                    <div className="offer-info">
                                        <span className="offer-label">Cliente</span>
                                        <span className="offer-value">
                                            {offer.client?.name || 'N/A'}
                                        </span>
                                    </div>

                                    {offer.email_subject && (
                                        <div className="offer-info">
                                            <span className="offer-label">Oggetto</span>
                                            <span className="offer-value offer-subject">
                                                {offer.email_subject}
                                            </span>
                                        </div>
                                    )}

                                    {offer.offer_amount > 0 && (
                                        <div className="offer-info">
                                            <span className="offer-label">Importo</span>
                                            <span className="offer-value offer-amount">
                                                €{offer.offer_amount.toLocaleString('it-IT', {
                                                    minimumFractionDigits: 2
                                                })}
                                            </span>
                                        </div>
                                    )}

                                    {offer.mail_date && (
                                        <div className="offer-info">
                                            <span className="offer-label">Data Mail</span>
                                            <span className="offer-value">
                                                {new Date(offer.mail_date).toLocaleString('it-IT')}
                                            </span>
                                        </div>
                                    )}
                                </div>

                                <div className="offer-card-footer">
                                    <button className="btn btn-sm btn-primary">
                                        Visualizza Dettagli →
                                    </button>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}

export default OfferList;
