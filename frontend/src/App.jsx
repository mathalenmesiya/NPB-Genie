import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import RoleSelection from './pages/RoleSelection';
import Login from './pages/Login';
import AdminLogin from './pages/AdminLogin';
import StudentChat from './pages/StudentChat';
import AdminDashboard from './pages/AdminDashboard';

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, role, loading } = useAuth();

  if (loading) return <div>Loading...</div>;
  if (!user) return <Navigate to="/" />;
  if (allowedRoles && !allowedRoles.includes(role)) {
    return <Navigate to={role === 'admin' ? '/admin' : '/student'} />;
  }

  return children;
};

const LoginRoute = ({ children }) => {
  const { user, role, loading } = useAuth();
  if (loading) return <div>Loading...</div>;
  if (user) return <Navigate to={role === 'admin' ? '/admin' : '/student'} />;
  return children;
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<LoginRoute><RoleSelection /></LoginRoute>} />
          <Route path="/student-login" element={<LoginRoute><Login /></LoginRoute>} />
          <Route path="/admin-login" element={<LoginRoute><AdminLogin /></LoginRoute>} />
          <Route
            path="/student"
            element={
              <ProtectedRoute allowedRoles={['student']}>
                <StudentChat />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
