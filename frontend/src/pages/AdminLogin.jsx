import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Shield, Loader2, LogIn } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import logo from '../assets/logo.jpg';

const API_BASE = `http://${window.location.hostname}:5000`;

const AdminLogin = () => {
    const { login } = useAuth();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const response = await axios.post(`${API_BASE}/api/auth/admin-login`, {
                username,
                password
            });

            const { uid, username: adminUsername } = response.data;
            login({ uid, username: adminUsername, role: 'admin' });
            navigate('/admin');
        } catch (err) {
            setError(err.response?.data?.error || 'Invalid credentials');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card glass-card">
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <img src={logo} alt="NP Genie Logo" style={{ width: '120px', height: '120px', borderRadius: '50%', marginBottom: '1rem', objectFit: 'cover', border: '3px solid var(--accent)' }} />
                    <div className="auth-title outfit" style={{ marginBottom: '0.25rem' }}>Admin Login</div>
                    <p style={{ textAlign: 'center', color: 'var(--secondary)', fontSize: '0.9rem', fontStyle: 'italic' }}>
                        NP Genie Administration
                    </p>
                </div>

                <form onSubmit={handleLogin}>
                    <div className="input-group">
                        <label className="input-label">Username</label>
                        <input
                            type="text"
                            className="input-field"
                            placeholder="admin"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </div>
                    <div className="input-group">
                        <label className="input-label">Password</label>
                        <input
                            type="password"
                            className="input-field"
                            placeholder="••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>
                    {error && <p style={{ color: 'var(--danger)', fontSize: '0.8rem', marginBottom: '1rem' }}>{error}</p>}
                    <button type="submit" className="btn btn-primary" disabled={loading} style={{ background: 'var(--accent)' }}>
                        {loading ? <Loader2 className="animate-spin" /> : <LogIn size={18} />}
                        Login
                    </button>
                    <button
                        type="button"
                        onClick={() => navigate('/')}
                        style={{ background: 'none', border: 'none', color: 'var(--primary)', marginTop: '1rem', width: '100%', fontSize: '0.875rem', cursor: 'pointer' }}
                    >
                        ← Back to Role Selection
                    </button>
                </form>
            </div>
        </div>
    );
};

export default AdminLogin;
