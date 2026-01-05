import React, { useState, useEffect } from 'react';
import { clientsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import './ClientList.css';

const ClientList = () => {
    const [clients, setClients] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingClient, setEditingClient] = useState(null);
    const [formData, setFormData] = useState({
        name: '',
        email_domain: '',
        sector: '',
        management_time: '',
        notes: '',
        strategic: false,
        voto: ''
    });
    const { isAdmin, user, isCommerciale } = useAuth();

    useEffect(() => {
        fetchClients();
    }, []);

    const fetchClients = async () => {
        try {
            setLoading(true);
            const response = await clientsAPI.getAll(0, 500); // Get many for list
            setClients(response.data);
        } catch (error) {
            console.error('Error fetching clients:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = (e) => {
        setSearchTerm(e.target.value);
    };

    const filteredClients = clients.filter(client =>
        client.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (client.email_domain && client.email_domain.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    const openModal = (client = null) => {
        if (client) {
            setEditingClient(client);
            setFormData({
                name: client.name,
                email_domain: client.email_domain || '',
                sector: client.sector || '',
                management_time: client.management_time || '',
                notes: client.notes || '',
                strategic: client.strategic || false,
                voto: client.voto || ''
            });
        } else {
            setEditingClient(null);
            setFormData({
                name: '',
                email_domain: '',
                sector: '',
                management_time: '',
                notes: '',
                strategic: false,
                voto: ''
            });
        }
        setIsModalOpen(true);
    };

    const closeModal = () => {
        setIsModalOpen(false);
        setEditingClient(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (editingClient) {
                await clientsAPI.update(editingClient.id, formData);
            } else {
                await clientsAPI.create(formData);
            }
            fetchClients();
            closeModal();
        } catch (error) {
            console.error('Error saving client:', error);
            alert('Errore dans la sauvegarde du client');
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm('Sei sicuro di voler eliminare questo cliente?')) {
            try {
                await clientsAPI.delete(id);
                fetchClients();
            } catch (error) {
                console.error('Error deleting client:', error);
                alert('Errore nella cancellazione del client');
            }
        }
    };

    return (
        <div className="client-container">
            <div className="client-header">
                <h1>Gestione Clienti</h1>
                <div className="client-actions">
                    <input
                        type="text"
                        placeholder="Cerca cliente..."
                        value={searchTerm}
                        onChange={handleSearch}
                        className="search-input"
                    />
                    <button className="btn-primary" onClick={() => openModal()}>
                        + Nuovo Cliente
                    </button>
                </div>
            </div>

            <div className="client-list-card">
                {loading ? (
                    <div className="loading">Caricamento...</div>
                ) : (
                    <table className="client-table">
                        <thead>
                            <tr>
                                <th>Nome Cliente</th>
                                <th>Settore</th>
                                <th>Tempo Gestione (gg)</th>
                                <th>Dominio Email</th>
                                <th>Strategico</th>
                                <th>Voto</th>
                                <th>Note</th>
                                <th>Azioni</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredClients.map(client => (
                                <tr key={client.id}>
                                    <td><strong>{client.name}</strong></td>
                                    <td>{client.sector || '-'}</td>
                                    <td style={{ textAlign: 'center' }}>{client.management_time || '-'}</td>
                                    <td className="email-cell"><code>{client.email_domain}</code></td>
                                    <td>
                                        {client.strategic ?
                                            <span className="badge strategic">SI</span> :
                                            <span className="badge">NO</span>
                                        }
                                    </td>
                                    <td style={{ textAlign: 'center' }}>
                                        {client.voto ? <span className="voto-badge">{client.voto}/10</span> : '-'}
                                    </td>
                                    <td className="note-cell">{client.notes}</td>
                                    <td>
                                        <div className="action-buttons">
                                            <button className="btn-icon edit" onClick={() => openModal(client)} title="Modifica">
                                                ✏️
                                            </button>
                                            {isCommerciale() && (
                                                <button className="btn-icon delete" onClick={() => handleDelete(client.id)} title="Elimina">
                                                    🗑️
                                                </button>
                                            )}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                            {(!filteredClients || filteredClients.length === 0) && (
                                <tr>
                                    <td colSpan="8" style={{ textAlign: 'center', padding: '3rem', opacity: 0.5 }}>
                                        {searchTerm ? 'Nessun cliente trovato per la ricerca' : 'Nessun cliente in archivio'}
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                )}
            </div>

            {isModalOpen && (
                <div className="modal-overlay">
                    <div className="modal-content">
                        <h2>{editingClient ? 'Modifica Cliente' : 'Aggiungi Nuovo Cliente'}</h2>
                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label>Nome Cliente *</label>
                                <input
                                    type="text"
                                    required
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                />
                            </div>
                            <div className="form-group">
                                <label>Dominio Email (es: @benozzi.com)</label>
                                <input
                                    type="text"
                                    value={formData.email_domain}
                                    onChange={(e) => setFormData({ ...formData, email_domain: e.target.value })}
                                />
                            </div>
                            <div className="form-row" style={{ display: 'flex', gap: '1rem' }}>
                                <div className="form-group" style={{ flex: 1 }}>
                                    <label>Settore</label>
                                    <input
                                        type="text"
                                        value={formData.sector}
                                        onChange={(e) => setFormData({ ...formData, sector: e.target.value })}
                                    />
                                </div>
                                <div className="form-group" style={{ flex: 1 }}>
                                    <label>Tempo Gestione (gg)</label>
                                    <input
                                        type="number"
                                        value={formData.management_time}
                                        onChange={(e) => setFormData({ ...formData, management_time: e.target.value })}
                                    />
                                </div>
                                <div className="form-group" style={{ flex: 1 }}>
                                    <label>Voto Cliente (1-10)</label>
                                    <input
                                        type="number"
                                        min="1"
                                        max="10"
                                        value={formData.voto}
                                        onChange={(e) => setFormData({ ...formData, voto: e.target.value })}
                                    />
                                </div>
                            </div>
                            <div className="form-group checkbox">
                                <label>
                                    <input
                                        type="checkbox"
                                        checked={formData.strategic}
                                        onChange={(e) => setFormData({ ...formData, strategic: e.target.checked })}
                                    />
                                    Cliente Strategico
                                </label>
                            </div>
                            <div className="form-group">
                                <label>Note</label>
                                <textarea
                                    value={formData.notes}
                                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                                />
                            </div>
                            <div className="modal-actions">
                                <button type="button" className="btn-secondary" onClick={closeModal}>Annulla</button>
                                <button type="submit" className="btn-primary">Salva</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ClientList;
