import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { auth, db } from '../firebase';
import { collection, query, onSnapshot, doc, updateDoc, orderBy } from 'firebase/firestore';
import { LayoutDashboard, Ticket, PieChart, Settings, LogOut, CheckCircle, Clock, AlertCircle } from 'lucide-react';

const AdminDashboard = () => {
    const { user, logout } = useAuth();
    const [tickets, setTickets] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const q = query(collection(db, "tickets"), orderBy("timestamp", "desc"));
        const unsubscribe = onSnapshot(q, (snapshot) => {
            const ticketData = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
            setTickets(ticketData);
            setLoading(false);
        });
        return unsubscribe;
    }, []);

    const updateStatus = async (ticketId, newStatus) => {
        try {
            await updateDoc(doc(db, "tickets", ticketId), { status: newStatus });
        } catch (err) {
            console.error("Error updating status:", err);
        }
    };

    const stats = {
        total: tickets.length,
        high: tickets.filter(t => t.priority === 'High' || t.priority === 'Critical').length,
        resolved: tickets.filter(t => t.status === 'Resolved').length,
        open: tickets.filter(t => t.status === 'Ticket Created' || t.status === 'Open').length
    };

    return (
        <div className="admin-layout">
            <aside className="sidebar">
                <div className="outfit" style={{ fontSize: '1.25rem', fontWeight: '800', marginBottom: '2rem', color: 'var(--primary)', letterSpacing: '-0.5px' }}>NP GENIE ADMIN</div>

                <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    <div className="btn" style={{ justifyContent: 'flex-start', background: 'rgba(255,255,255,0.1)' }}>
                        <LayoutDashboard size={20} /> Dashboard
                    </div>
                    <div className="btn" style={{ justifyContent: 'flex-start' }}>
                        <Ticket size={20} /> Manage Tickets
                    </div>
                    <div className="btn" style={{ justifyContent: 'flex-start' }}>
                        <PieChart size={20} /> Analytics
                    </div>
                </nav>

                <button onClick={logout} className="btn" style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#f87171' }}>
                    <LogOut size={20} /> Logout
                </button>
            </aside>

            <main className="content">
                <div className="dashboard-header">
                    <h1 className="outfit">Dashboard Overview</h1>
                    <div style={{ color: 'var(--secondary)', fontSize: '0.875rem' }}>
                        Logged in as <strong>{user?.phone || 'Admin'}</strong>
                    </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
                    <div className="glass-card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div style={{ background: 'rgba(99, 102, 241, 0.1)', color: 'var(--primary)', padding: '0.75rem', borderRadius: '12px' }}>
                            <Ticket size={24} />
                        </div>
                        <div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--secondary)', fontWeight: '600' }}>TOTAL TICKETS</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: '700' }}>{stats.total}</div>
                        </div>
                    </div>
                    <div className="glass-card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)', padding: '0.75rem', borderRadius: '12px' }}>
                            <AlertCircle size={24} />
                        </div>
                        <div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--secondary)', fontWeight: '600' }}>CRITICAL / HIGH</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: '700' }}>{stats.high}</div>
                        </div>
                    </div>
                    <div className="glass-card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div style={{ background: 'rgba(16, 185, 129, 0.1)', color: 'var(--accent)', padding: '0.75rem', borderRadius: '12px' }}>
                            <CheckCircle size={24} />
                        </div>
                        <div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--secondary)', fontWeight: '600' }}>RESOLVED</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: '700' }}>{stats.resolved}</div>
                        </div>
                    </div>
                    <div className="glass-card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div style={{ background: 'rgba(245, 158, 11, 0.1)', color: '#f59e0b', padding: '0.75rem', borderRadius: '12px' }}>
                            <Clock size={24} />
                        </div>
                        <div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--secondary)', fontWeight: '600' }}>OPEN / NEW</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: '700' }}>{stats.open}</div>
                        </div>
                    </div>
                </div>

                <div className="table-container">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Ticket ID</th>
                                <th>Student</th>
                                <th>Complaint</th>
                                <th>Affected</th>
                                <th>Category</th>
                                <th>Priority</th>
                                <th>Sentiment</th>
                                <th>Insight</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {tickets.map(ticket => (
                                <tr key={ticket.id}>
                                    <td style={{ fontWeight: '600', fontSize: '0.8125rem' }}>#{ticket.ticket_id}</td>
                                    <td style={{ fontSize: '0.8125rem', color: 'var(--secondary)' }}>{ticket.user_uid?.replace('phone_', '+91 ')}</td>
                                    <td style={{ maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                        {ticket.complaint}
                                    </td>
                                    <td>
                                        <span style={{ fontSize: '0.8rem', fontWeight: '500' }}>{ticket.affected_student_count || 1}</span>
                                    </td>
                                    <td><span className="badge" style={{ background: '#f1f5f9' }}>{ticket.category}</span></td>
                                    <td>
                                        <span className={`badge badge-${ticket.priority?.toLowerCase()}`}>
                                            {ticket.priority}
                                        </span>
                                    </td>
                                    <td>
                                        <span style={{ fontSize: '0.75rem', fontWeight: '600', color: ticket.sentiment === 'Angry' || ticket.sentiment === 'Frustrated' ? 'var(--danger)' : 'var(--accent)' }}>
                                            {ticket.sentiment || 'Calm'}
                                        </span>
                                    </td>
                                    <td style={{ fontSize: '0.75rem', color: 'var(--secondary)', maxWidth: '150px' }}>
                                        {ticket.escalation_reason || 'N/A'}
                                    </td>
                                    <td>
                                        <span style={{ fontSize: '0.875rem', color: 'var(--secondary)' }}>{ticket.status}</span>
                                    </td>
                                    <td>
                                        <select
                                            className="input-field"
                                            style={{ padding: '0.25rem', width: 'auto', fontSize: '0.8rem' }}
                                            value={ticket.status}
                                            onChange={(e) => updateStatus(ticket.id, e.target.value)}
                                        >
                                            <option value="Ticket Created">Open</option>
                                            <option value="In Progress">In Progress</option>
                                            <option value="Resolved">Resolved</option>
                                        </select>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {loading && <div style={{ padding: '2rem', textAlign: 'center' }}>Loading tickets...</div>}
                </div>
            </main >
        </div >
    );
};

export default AdminDashboard;
