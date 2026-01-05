import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { offersAPI } from '../services/api'; // Added import
import './OfferDetail.css';

function OfferDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { user } = useAuth();
    const [offer, setOffer] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchOfferDetails();
    }, [id]);

    const fetchOfferDetails = async () => {
        try {
            setLoading(true);
            const response = await offersAPI.getById(id);
            setOffer(response.data);
        } catch (error) {
            console.error('Error fetching offer:', error);
            setError(error.response?.data?.detail || 'Offerta non trouvata');
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

    const getCheckIcon = (status) => {
        if (status === 'OK') return '✅';
        if (status === 'KO') return '❌';
        return '⏳';
    };

    if (loading) {
        return (
            <div className="container">
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Caricamento dettagli offerta...</p>
                </div>
            </div>
        );
    }

    if (error || !offer) {
        return (
            <div className="container">
                <div className="error-container glass-card">
                    <h3>❌ Errore</h3>
                    <p>{error || 'Offerta non trovata'}</p>
                    <button onClick={() => navigate('/offers')} className="btn btn-primary">
                        Torna alla Lista
                    </button>
                </div>
            </div>
        );
    }

    const statusInfo = getStatusBadge(offer.status);

    return (
        <div className="container fade-in">
            <div className="detail-header">
                <button onClick={() => navigate(-1)} className="btn btn-secondary">
                    ← Indietro
                </button>
                <h2>Dettagli Offerta {offer.offer_number}</h2>
                <span className={`badge ${statusInfo.class}`}>{statusInfo.label}</span>
            </div>

            <div className="detail-grid">
                {/* Client Information */}
                <div className="detail-section glass-card">
                    <h3>👤 Informazioni Cliente</h3>
                    <div className="detail-row">
                        <span className="detail-label">Nome Cliente:</span>
                        <span className="detail-value">{offer.client?.name || 'N/A'}</span>
                    </div>
                    <div className="detail-row">
                        <span className="detail-label">Dominio Email:</span>
                        <span className="detail-value">{offer.client?.email_domain || 'N/A'}</span>
                    </div>
                </div>

                {/* Offer Information */}
                <div className="detail-section glass-card">
                    <h3>📋 Informazioni Offerta</h3>
                    <div className="detail-row">
                        <span className="detail-label">Numero Offerta:</span>
                        <span className="detail-value">{offer.offer_number}</span>
                    </div>
                    <div className="detail-row">
                        <span className="detail-label">Tipo Offerta:</span>
                        <span className="detail-value">{offer.offer_type || 'N/A'}</span>
                    </div>
                    <div className="detail-row">
                        <span className="detail-label">Articolo:</span>
                        <span className="detail-value">{offer.item_name || 'N/A'}</span>
                    </div>
                    <div className="detail-row">
                        <span className="detail-label">Oggetto Email:</span>
                        <span className="detail-value">{offer.email_subject || 'N/A'}</span>
                    </div>
                </div>

                {/* Dates */}
                <div className="detail-section glass-card">
                    <h3>📅 Date</h3>
                    <div className="detail-row">
                        <span className="detail-label">Data Mail:</span>
                        <span className="detail-value">
                            {offer.mail_date ? new Date(offer.mail_date).toLocaleString('it-IT') : 'N/A'}
                        </span>
                    </div>
                    <div className="detail-row">
                        <span className="detail-label">Data Invio Offerta:</span>
                        <span className="detail-value">
                            {offer.offer_sent_date ? new Date(offer.offer_sent_date).toLocaleDateString('it-IT') : 'N/A'}
                        </span>
                    </div>
                    <div className="detail-row">
                        <span className="detail-label">Scadenza Risposta:</span>
                        <span className="detail-value">
                            {offer.reply_deadline ? new Date(offer.reply_deadline).toLocaleDateString('it-IT') : 'N/A'}
                        </span>
                    </div>
                    {offer.order_date && (
                        <div className="detail-row">
                            <span className="detail-label">Data Ordine:</span>
                            <span className="detail-value">
                                {new Date(offer.order_date).toLocaleDateString('it-IT')}
                            </span>
                        </div>
                    )}
                </div>

                {/* Amounts */}
                <div className="detail-section glass-card">
                    <h3>💰 Importi</h3>
                    <div className="detail-row">
                        <span className="detail-label">Importo Offerta:</span>
                        <span className="detail-value offer-amount">
                            €{(offer.offer_amount || 0).toLocaleString('it-IT', { minimumFractionDigits: 2 })}
                        </span>
                    </div>
                    {offer.order_amount > 0 && (
                        <div className="detail-row">
                            <span className="detail-label">Importo Ordine:</span>
                            <span className="detail-value offer-amount">
                                €{offer.order_amount.toLocaleString('it-IT', { minimumFractionDigits: 2 })}
                            </span>
                        </div>
                    )}
                </div>

                {/* Management Section */}
                <div className="detail-section glass-card">
                    <h3>👤 Responsabili</h3>
                    <div className="detail-row">
                        <span className="detail-label">Gestita da:</span>
                        <span className="detail-value">{offer.managed_by_name || 'N/A'}</span>
                    </div>
                    <div className="detail-row">
                        <span className="detail-label">Gestore Uff. Acq.:</span>
                        <span className="detail-value">{offer.purchasing_manager_name || 'N/A'}</span>
                    </div>
                </div>

                {/* Lead Times */}
                <div className="detail-section glass-card">
                    <h3>⏱️ Lead Time</h3>
                    <div className="detail-row">
                        <span className="detail-label">Lead Time Commerciale:</span>
                        <span className="detail-value">
                            {offer.commercial_lead_time ? `${offer.commercial_lead_time} giorni` : 'N/A'}
                        </span>
                    </div>
                    <div className="detail-row">
                        <span className="detail-label">Lead Time Pianificazione:</span>
                        <span className="detail-value">
                            {offer.planning_lead_time ? `${offer.planning_lead_time} giorni` : 'N/A'}
                        </span>
                    </div>
                    <div className="detail-row">
                        <span className="detail-label">Lead Time Confermato:</span>
                        <span className="detail-value">
                            {offer.confirmed_lead_time ? `${offer.confirmed_lead_time} giorni` : 'N/A'}
                        </span>
                    </div>
                </div>

                {/* Checks */}
                <div className="detail-section glass-card">
                    <h3>✓ Verifiche</h3>
                    <div className="detail-row">
                        <span className="detail-label">Check Fattibilità:</span>
                        <span className="detail-value">
                            {getCheckIcon(offer.check_feasibility)} {offer.check_feasibility || 'Da Esaminare'}
                        </span>
                    </div>
                    <div className="detail-row">
                        <span className="detail-label">Check Tecnico:</span>
                        <span className="detail-value">
                            {getCheckIcon(offer.check_technical)} {offer.check_technical || 'Da Esaminare'}
                        </span>
                    </div>
                    <div className="detail-row">
                        <span className="detail-label">Check Acquisti:</span>
                        <span className="detail-value">
                            {getCheckIcon(offer.check_purchasing)} {offer.check_purchasing || 'Da Esaminare'}
                        </span>
                    </div>
                    <div className="detail-row">
                        <span className="detail-label">Check Pianificazione:</span>
                        <span className="detail-value">
                            {getCheckIcon(offer.check_planning)} {offer.check_planning || 'Da Esaminare'}
                        </span>
                    </div>
                </div>

                {/* Declined Info */}
                {offer.status === 'DECLINATA' && (offer.declined_reason || offer.declined_notes) && (
                    <div className="detail-section glass-card" style={{ gridColumn: '1 / -1' }}>
                        <h3>❌ Informazioni Declinata</h3>
                        {offer.declined_reason && (
                            <div className="detail-row">
                                <span className="detail-label">Motivo:</span>
                                <span className="detail-value">{offer.declined_reason}</span>
                            </div>
                        )}
                        {offer.declined_notes && (
                            <div className="detail-row">
                                <span className="detail-label">Note:</span>
                                <span className="detail-value">{offer.declined_notes}</span>
                            </div>
                        )}
                    </div>
                )}

            </div>

            <div className="detail-actions">
                <button onClick={() => navigate('/offers')} className="btn btn-secondary">
                    Torna alla Lista
                </button>
            </div>
        </div >
    );
}

export default OfferDetail;
