import React from 'react';
import { useNavigate } from 'react-router-dom';
import { GraduationCap, Shield } from 'lucide-react';
import logo from '../assets/logo.jpg';

const RoleSelection = () => {
    const navigate = useNavigate();

    return (
        <div className="auth-container">
            <div className="auth-card glass-card" style={{ maxWidth: '600px' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '2rem' }}>
                    <img src={logo} alt="NP Genie Logo" style={{ width: '100px', height: '100px', borderRadius: '50%', marginBottom: '1rem', objectFit: 'cover', border: '3px solid var(--primary)' }} />
                    <div className="auth-title outfit" style={{ marginBottom: '0.25rem' }}>NP Genie</div>
                    <p style={{ textAlign: 'center', color: 'var(--secondary)', fontSize: '0.9rem', fontStyle: 'italic' }}>
                        Your campus genie
                    </p>
                </div>

                <h2 style={{ textAlign: 'center', marginBottom: '2rem', color: 'var(--text)', fontSize: '1.25rem' }}>
                    Select Your Role
                </h2>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                    {/* Student Card */}
                    <div
                        onClick={() => navigate('/student-login')}
                        className="glass-card"
                        style={{
                            padding: '2rem 1.5rem',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            border: '2px solid transparent',
                            textAlign: 'center'
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.borderColor = 'var(--primary)';
                            e.currentTarget.style.transform = 'translateY(-5px)';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.borderColor = 'transparent';
                            e.currentTarget.style.transform = 'translateY(0)';
                        }}
                    >
                        <div style={{
                            background: 'rgba(99, 102, 241, 0.1)',
                            color: 'var(--primary)',
                            width: '80px',
                            height: '80px',
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            margin: '0 auto 1rem'
                        }}>
                            <GraduationCap size={40} />
                        </div>
                        <h3 className="outfit" style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>Student</h3>
                        <p style={{ fontSize: '0.875rem', color: 'var(--secondary)' }}>
                            Report grievances and get help
                        </p>
                    </div>

                    {/* Admin Card */}
                    <div
                        onClick={() => navigate('/admin-login')}
                        className="glass-card"
                        style={{
                            padding: '2rem 1.5rem',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            border: '2px solid transparent',
                            textAlign: 'center'
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.borderColor = 'var(--accent)';
                            e.currentTarget.style.transform = 'translateY(-5px)';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.borderColor = 'transparent';
                            e.currentTarget.style.transform = 'translateY(0)';
                        }}
                    >
                        <div style={{
                            background: 'rgba(16, 185, 129, 0.1)',
                            color: 'var(--accent)',
                            width: '80px',
                            height: '80px',
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            margin: '0 auto 1rem'
                        }}>
                            <Shield size={40} />
                        </div>
                        <h3 className="outfit" style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>Admin</h3>
                        <p style={{ fontSize: '0.875rem', color: 'var(--secondary)' }}>
                            Manage tickets and resolve issues
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RoleSelection;
