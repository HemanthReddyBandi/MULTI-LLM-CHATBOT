import React, { useState } from 'react';
import { registerUser } from '../services/auth';
import { Link, useNavigate } from 'react-router-dom';

const Register = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    setLoading(true);
    try {
      await registerUser(email, password);
      setSuccess('Registration successful');
      setTimeout(() => navigate('/login'), 800);
    } catch (err) {
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-sky-700 via-indigo-700 to-blue-700 px-4">
      {/* animated background blobs */}
      <div className="absolute -top-24 -left-16 w-80 h-80 bg-sky-400 opacity-50 rounded-full blur-3xl animate-blob"></div>
      <div className="absolute top-1/4 -right-20 w-72 h-72 bg-indigo-400 opacity-50 rounded-full blur-3xl animate-blob animation-delay-2000"></div>
      <div className="absolute -bottom-28 left-1/3 w-80 h-80 bg-cyan-400 opacity-50 rounded-full blur-3xl animate-blob animation-delay-4000"></div>

      <div className="relative w-full max-w-md bg-white/85 backdrop-blur-md rounded-xl shadow-2xl p-8 border border-white/40">
        <h2 className="text-2xl font-bold text-gray-900 text-center">Create an account</h2>
        <p className="text-sm text-gray-500 text-center mt-1">Register to continue</p>

        {error && <div className="mt-4 text-sm text-red-600 bg-red-50 border border-red-200 p-2 rounded">{error}</div>}
        {success && <div className="mt-4 text-sm text-green-700 bg-green-50 border border-green-200 p-2 rounded">{success}</div>}

        <form className="mt-6 space-y-4" onSubmit={onSubmit}>
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input type="email" value={email} onChange={(e)=>setEmail(e.target.value)} required className="mt-1 w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="you@example.com" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Password</label>
            <input type="password" value={password} onChange={(e)=>setPassword(e.target.value)} required className="mt-1 w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="••••••••" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Confirm Password</label>
            <input type="password" value={confirmPassword} onChange={(e)=>setConfirmPassword(e.target.value)} required className="mt-1 w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="••••••••" />
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Already have an account?</span>
            <Link to="/login" className="text-sm text-blue-600 hover:underline">Login</Link>
          </div>
          <button type="submit" disabled={loading} className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">{loading ? 'Creating...' : 'Create account'}</button>
        </form>
      </div>
    </div>
  );
};

export default Register;

