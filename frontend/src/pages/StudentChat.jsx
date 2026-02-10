import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { auth, db } from '../firebase';
import { collection, query, where, getDocs, orderBy } from 'firebase/firestore';
import axios from 'axios';
import { Send, User, Bot, History, LogOut, Loader2, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const API_URL = `http://${window.location.hostname}:5000/create-ticket`;

const CHAT_STATES = {
    IDLE: 'idle',
    TRIAGING: 'triaging',
    ANALYZING: 'analyzing',
    COMPLETED: 'completed'
};

const CRITICAL_KEYWORDS = ["rat", "fire", "leak", "danger", "hazard", "injury", "blood", "poison", "harassment", "shocks", "snake", "lizard"];

const StudentChat = () => {
    const { user, logout } = useAuth();
    const [messages, setMessages] = useState([
        { id: 1, text: "Hello! I am **NPGENIE**, your advanced AI college assistant. \n\nHow can I help you today? I can answer questions about library timings, fees, campus facilities, or help you raise a grievance ticket.", sender: 'bot' }
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [chatState, setChatState] = useState(CHAT_STATES.IDLE);
    const [pendingComplaint, setPendingComplaint] = useState('');
    const [severityDetected, setSeverityDetected] = useState(false);
    const scrollRef = useRef(null);
    const navigate = useNavigate();

    // 🕵️ Real-time Severity Monitoring
    useEffect(() => {
        const hasCritical = CRITICAL_KEYWORDS.some(word => input.toLowerCase().includes(word));
        setSeverityDetected(hasCritical);
    }, [input]);

    useEffect(() => {
        scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        const currentInput = input.trim();
        if (!currentInput) return;

        const userMessage = { id: Date.now(), text: currentInput, sender: 'user' };
        setMessages(prev => [...prev, userMessage]);
        setInput('');

        // 🧠 Intent Detection (Manual Tracking Bypass)
        const trackingKeywords = ['track', 'status', 'update', 'show my tickets', 'history', 'check my ticket'];
        if (trackingKeywords.some(key => currentInput.toLowerCase().includes(key))) {
            handleTrackTickets();
            return;
        }



        // 🔄 STATE: IDLE (Triage Flow)
        setChatState(CHAT_STATES.TRIAGING);
        setIsTyping(true);
        try {
            // STEP 1: Call Triage Agent (BhavaniBot Triage)
            const response = await axios.post(`${API_URL.replace('/create-ticket', '/chat')}`, {
                message: currentInput,
                user_uid: user?.uid
            });

            const data = response.data;

            if (data.action === "resolve" || data.action === "chat" || data.action === "reject") {
                // Case: Resolved via Knowledge Base (RAG), Casual Chat, or Rejected (non-college topic)
                setMessages(prev => [...prev, { id: Date.now(), text: data.message, sender: 'bot' }]);
                setChatState(CHAT_STATES.IDLE);
            } else if (data.action === "create_ticket") {
                // Case: escalated to Ticket Creation - Process IMMEDIATELY
                setMessages(prev => [...prev, { id: Date.now(), text: data.message, sender: 'bot' }]);
                processTicket(currentInput, 1); // Default to 1, backend will auto-increment if duplicate
            }
        } catch (err) {
            setMessages(prev => [...prev, { id: Date.now(), text: "I'm having trouble connecting to the college server. Please try again later. 🔌", sender: 'bot' }]);
            setChatState(CHAT_STATES.IDLE);
        } finally {
            setIsTyping(false);
        }
    };

    const processTicket = async (complaint, affectedCount) => {
        setIsTyping(true);
        setChatState(CHAT_STATES.ANALYZING);
        try {
            const response = await axios.post(API_URL, {
                complaint: complaint,
                affected_student_count: affectedCount,
                user_uid: user?.uid
            });

            const data = response.data;
            let botResponse = "";

            if (data.duplicate) {
                botResponse = `🔍 **Duplicate Detected**: This issue has already been reported (Ticket ID: **${data.ticket_id}**). \n\nOur system detected a similar report: _"${data.original_complaint}"_. Your account has been linked to this existing ticket for updates. 👋`;
            } else {
                const sentiment = data.sentiment || "Calm";
                const priority = data.priority || "Low";
                const categoryName = data.category || "General";

                let empathyText = "";
                if (sentiment === "Angry" || sentiment === "Frustrated") {
                    empathyText = "I understand this is frustrating, and I'm here to ensure it gets the attention it deserves. 😞 ";
                } else {
                    empathyText = "I've successfully registered your concern. ";
                }

                if (priority === "High" || priority === "Critical") {
                    empathyText += `\n\n⚡ **Escalated**: This has been flagged for urgent attention to ensure a swift resolution.`;
                }

                botResponse = `### ✅ Ticket Registered
${empathyText}

**Ticket ID:** **${data.ticket_id}**
**Category:** ${categoryName}
**Status:** Ticket Created

The college administration will review your ticket shortly. Thank you! ✨`;
            }

            setMessages(prev => [...prev, { id: Date.now(), text: botResponse, sender: 'bot' }]);
            setChatState(CHAT_STATES.IDLE);
            setPendingComplaint('');
        } catch (err) {
            setMessages(prev => [...prev, { id: Date.now(), text: "I'm having trouble creating your ticket. Please try again later. 🔌", sender: 'bot' }]);
            setChatState(CHAT_STATES.IDLE);
        } finally {
            setIsTyping(false);
        }
    };

    const handleTrackTickets = async () => {
        setIsTyping(true);
        try {
            const q = query(
                collection(db, "tickets"),
                where("user_uid", "==", user.uid), // Filter by user's UID
                orderBy("timestamp", "desc")
            );

            const querySnapshot = await getDocs(q);
            if (querySnapshot.empty) {
                setMessages(prev => [...prev, { id: Date.now(), text: "I couldn't find any tickets raised by you.", sender: 'bot' }]);
            } else {
                let ticketList = "Your recent tickets:\n";
                querySnapshot.forEach((doc) => {
                    const d = doc.data();
                    ticketList += `\n• **${d.ticket_id}**: ${d.status}`;
                });
                setMessages(prev => [...prev, { id: Date.now(), text: ticketList, sender: 'bot' }]);
            }
        } catch (err) {
            console.error(err);
            setMessages(prev => [...prev, { id: Date.now(), text: "Error fetching tickets. If this is a new feature, index might be building.", sender: 'bot' }]);
        } finally {
            setIsTyping(false);
        }
    };

    const renderText = (text) => {
        return text.split('\n').map((line, i) => {
            if (line.startsWith('### ')) {
                return <h4 key={i} style={{ margin: '0.5rem 0', color: 'var(--primary)', borderBottom: '1px solid rgba(99, 102, 241, 0.2)', paddingBottom: '4px' }}>{line.replace('### ', '')}</h4>;
            }

            // Handle Bold **text**
            const parts = line.split(/(\*\*.*?\*\*)/g);
            return (
                <p key={i} style={{ margin: '0.25rem 0', lineHeight: '1.5' }}>
                    {parts.map((part, j) => {
                        if (part.startsWith('**') && part.endsWith('**')) {
                            return <strong key={j} style={{ color: 'var(--primary)' }}>{part.slice(2, -2)}</strong>;
                        }
                        return part;
                    })}
                </p>
            );
        });
    };

    return (
        <div className="chat-container">
            <header className="dashboard-header glass-card" style={{ marginBottom: '1rem', padding: '1rem 1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div style={{ background: 'var(--primary)', padding: '0.5rem', borderRadius: '12px', color: 'white' }}>
                        <Bot size={24} />
                    </div>
                    <div>
                        <h3 className="outfit" style={{ fontSize: '1.1rem' }}>NP Genie</h3>
                        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                            <span style={{ fontSize: '0.75rem', color: 'var(--accent)', fontWeight: '600' }}>● Online</span>
                            <span style={{ fontSize: '0.65rem', background: 'rgba(99, 102, 241, 0.2)', color: '#818cf8', padding: '2px 6px', borderRadius: '4px', border: '1px solid rgba(99, 102, 241, 0.3)', fontWeight: '700' }}>GENIE AI POWERED</span>
                        </div>
                    </div>
                </div>
                <button onClick={logout} className="btn" style={{ width: 'auto', background: 'none', color: 'var(--secondary)' }}>
                    <LogOut size={18} />
                </button>
            </header>

            <div className="glass-card chat-messages">
                {messages.map(msg => (
                    <div key={msg.id} className={`message ${msg.sender === 'user' ? 'message-user' : 'message-bot'} fade-in`}>
                        {renderText(msg.text)}
                    </div>
                ))}
                {isTyping && (
                    <div className="message message-bot fade-in" style={{ display: 'flex', gap: '8px', padding: '0.75rem 1rem', alignItems: 'center' }}>
                        <Loader2 size={16} className="animate-spin" />
                        <span style={{ fontSize: '0.8rem', color: 'var(--secondary)', fontWeight: '500' }}>AI is analyzing... 🧠</span>
                    </div>
                )}
                <div ref={scrollRef} />
            </div>

            {/* 🔥 Real-time Intel Bar */}
            <div style={{ padding: '0 1rem', display: 'flex', gap: '8px', minHeight: '24px' }}>
                {severityDetected && (
                    <div className="badge-critical fade-in" style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.7rem' }}>
                        <AlertCircle size={12} /> High Severity Language Detected
                    </div>
                )}
                {chatState !== CHAT_STATES.IDLE && (
                    <div className="badge fade-in" style={{ background: 'rgba(99, 102, 241, 0.1)', color: 'var(--primary)', border: '1px solid rgba(99, 102, 241, 0.2)', fontSize: '0.7rem' }}>
                        Status: {chatState.toUpperCase()}
                    </div>
                )}
            </div>

            <form onSubmit={handleSend} className="chat-input-area" style={{ marginTop: '0.5rem' }}>
                <input
                    type="text"
                    className="input-field glass"
                    placeholder="Describe your issue..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                />
                <button type="submit" className="btn btn-primary" style={{ width: '56px' }}>
                    <Send size={20} />
                </button>
            </form>
        </div>
    );
};

export default StudentChat;
