import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './components/Dashboard';
import OfferList from './components/OfferList';
import OfferDetail from './components/OfferDetail';
import ClientList from './components/ClientList';
import Layout from './components/Layout';
import AnalyticsPage from './components/AnalyticsPage';
import TeamPerformancePage from './components/TeamPerformancePage';
import WorkflowTimingPage from './components/WorkflowTimingPage';
import SeasonalTrendsPage from './components/SeasonalTrendsPage';
import { NotificationProvider } from './context/NotificationContext';
import './App.css';

function App() {
    return (
        <AuthProvider>
            <NotificationProvider>
                <Router>
                    <Routes>
                        <Route path="/" element={
                            <ProtectedRoute>
                                <Layout />
                            </ProtectedRoute>
                        }>
                            <Route index element={<Dashboard />} />
                            <Route path="analytics" element={<AnalyticsPage />} />
                            <Route path="analytics/team" element={<TeamPerformancePage />} />
                            <Route path="analytics/workflow" element={<WorkflowTimingPage />} />
                            <Route path="analytics/trends" element={<SeasonalTrendsPage />} />
                            <Route path="clients" element={<ClientList />} />

                            <Route path="offers" element={<OfferList />} />
                            <Route path="offers/pending" element={
                                <OfferList filterStatus="PENDING_REGISTRATION" />
                            } />
                            <Route path="offers/in-progress" element={
                                <OfferList filterStatus="IN_LAVORO" />
                            } />
                            <Route path="offers/accepted" element={
                                <OfferList filterStatus="ACCETTATA" />
                            } />
                            <Route path="offers/2024" element={
                                <OfferList filterYear="2024" />
                            } />
                            <Route path="offers/2025" element={
                                <OfferList filterYear="2025" />
                            } />
                            <Route path="offers/:id" element={<OfferDetail />} />

                            <Route path="my-offers" element={<OfferList myOffers={true} />} />
                        </Route>

                        <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                </Router>
            </NotificationProvider>
        </AuthProvider>
    );
}

export default App;
