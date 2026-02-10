import React, { useState } from 'react';
import { db } from '../firebase';
import { doc, setDoc, getDoc } from 'firebase/firestore';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Phone, CheckCircle, Loader2, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import logo from '../assets/logo.jpg';

const API_BASE = `http://${window.location.hostname}:5000`;

const Login = () => {
    const { login } = useAuth();
    const [phoneNumber, setPhoneNumber] = useState('');
    const [otp, setOtp] = useState('');
    const [verificationId, setVerificationId] = useState(null);
    const [role, setRole] = useState('student');
    const [showRoleSelection, setShowRoleSelection] = useState(false);
    const [tempUid, setTempUid] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const onSendOTP = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const response = await axios.post(`${API_BASE}/api/auth/send-otp`, {
                phone: phoneNumber
            });
            setVerificationId(response.data.verificationId);
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to send OTP.');
        } finally {
            setLoading(false);
        }
    };

    const onVerifyOTP = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const response = await axios.post(`${API_BASE}/api/auth/verify-otp`, {
                phone: phoneNumber,
                otp: otp,
                verificationId: verificationId
            });

            const { uid, role: userRole } = response.data;

            if (userRole) {
                // Existing user, log in and go to dashboard
                login({ uid, phone: phoneNumber, role: userRole });
                navigate(userRole === 'admin' ? '/admin' : '/student');
            } else {
                // New user, show role selection
                setTempUid(uid);
                setShowRoleSelection(true);
            }
        } catch (err) {
            setError(err.response?.data?.error || 'Verification failed.');
        } finally {
            setLoading(false);
        }
    };

    const handleRoleFinalize = async () => {
        setLoading(true);
        try {
            // Save new user profile to Firestore via Backend (to avoid auth issues)
            await axios.post(`${API_BASE}/api/auth/complete-profile`, {
                uid: tempUid,
                phone: phoneNumber,
                role: role
            });

            // Log in with the new role
            login({ uid: tempUid, phone: phoneNumber, role });
            navigate(role === 'admin' ? '/admin' : '/student');
        } catch (err) {
            setError(err.response?.data?.error || 'Error saving profile.');
        } finally {
            setLoading(false);
        }
    };

    if (showRoleSelection) {
        return (
            <div className="auth-container">
                <div className="auth-card glass-card">
                    <div className="auth-title outfit">Complete Profile</div>
                    <p style={{ textAlign: 'center', marginBottom: '1.5rem', color: 'var(--secondary)' }}>
                        Welcome! Please select your role to continue.
                    </p>
                    <div className="input-group">
                        <label className="input-label">I am a...</label>
                        <select className="input-field" value={role} onChange={(e) => setRole(e.target.value)}>
                            <option value="student">Student</option>
                            <option value="admin">College Staff (Admin)</option>
                        </select>
                    </div>
                    <button onClick={handleRoleFinalize} className="btn btn-primary" disabled={loading}>
                        {loading ? <Loader2 className="animate-spin" /> : <ArrowRight size={18} />}
                        Get Started
                    </button>
                    {error && <p style={{ color: 'var(--danger)', fontSize: '0.8rem', marginTop: '1rem', textAlign: 'center' }}>{error}</p>}
                </div>
            </div>
        );
    }

    return (
        <div className="auth-container">
            <div className="auth-card glass-card">
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <img src={logo} alt="NP Genie Logo" style={{ width: '120px', height: '120px', borderRadius: '50%', marginBottom: '1rem', objectFit: 'cover', border: '3px solid var(--primary)' }} />
                    <div className="auth-title outfit" style={{ marginBottom: '0.25rem' }}>Student Login</div>
                    <p style={{ textAlign: 'center', color: 'var(--secondary)', fontSize: '0.9rem', fontStyle: 'italic' }}>
                        NP Genie - Your campus genie
                    </p>
                </div>

                {!verificationId ? (
                    <form onSubmit={onSendOTP}>
                        <div className="input-group">
                            <label className="input-label">Phone Number (India)</label>
                            <div style={{ position: 'relative' }}>
                                <span style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', fontWeight: '600', color: 'var(--secondary)' }}>+91</span>
                                <input
                                    type="tel"
                                    className="input-field"
                                    style={{ paddingLeft: '3.5rem' }}
                                    placeholder="9876543210"
                                    value={phoneNumber}
                                    onChange={(e) => setPhoneNumber(e.target.value.replace(/\D/g, '').slice(0, 10))}
                                    required
                                />
                            </div>
                        </div>
                        {error && <p style={{ color: 'var(--danger)', fontSize: '0.8rem', marginBottom: '1rem' }}>{error}</p>}
                        <button type="submit" className="btn btn-primary" disabled={loading || phoneNumber.length < 10}>
                            {loading ? <Loader2 className="animate-spin" /> : <Phone size={18} />}
                            Send Verification Code
                        </button>
                    </form>
                ) : (
                    <form onSubmit={onVerifyOTP}>
                        <div className="input-group">
                            <label className="input-label">Enter 6-digit OTP sent to +91 {phoneNumber}</label>
                            <input
                                type="text"
                                className="input-field"
                                placeholder="123456"
                                maxLength="6"
                                value={otp}
                                onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                                required
                            />
                        </div>
                        {error && <p style={{ color: 'var(--danger)', fontSize: '0.8rem', marginBottom: '1rem' }}>{error}</p>}
                        <button type="submit" className="btn btn-primary" disabled={loading || otp.length < 6}>
                            {loading ? <Loader2 className="animate-spin" /> : <CheckCircle size={18} />}
                            Verify & Login
                        </button>
                        <button
                            type="button"
                            onClick={() => setVerificationId(null)}
                            style={{ background: 'none', border: 'none', color: 'var(--primary)', marginTop: '1rem', width: '100%', fontSize: '0.875rem', cursor: 'pointer' }}
                        >
                            Change Phone Number
                        </button>
                        <button
                            type="button"
                            onClick={() => navigate('/')}
                            style={{ background: 'none', border: 'none', color: 'var(--secondary)', marginTop: '0.5rem', width: '100%', fontSize: '0.875rem', cursor: 'pointer' }}
                        >
                            ← Back to Role Selection
                        </button>
                    </form>
                )}
            </div>
        </div>
    );
};

export default Login;
