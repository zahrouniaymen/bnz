import { useAuth } from '../context/AuthContext';

function ProtectedRoute({ children, requireRole = null }) {
    const { user, loading } = useAuth();

    // TEMPORARY: Bypass authentication
    // Just render the children directly
    return children;

    /* Original code - commented out
    if (loading) {
        return (
            <div className="container">
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Caricamento...</p>
                </div>
            </div>
        );
    }

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    if (requireRole && !requireRole.includes(user.role)) {
        return (
            <div className="container">
                <div className="error-container">
                    <h2>❌ Accesso Negato</h2>
                    <p>Non hai i permessi per accedere a questa pagina.</p>
                </div>
            </div>
        );
    }

    return children;
    */
}

export default ProtectedRoute;
