import { useState } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
export default function RegisterPage() {
    const { user, register } = useAuth();
    const [form, setForm] = useState({ email: '', username: '', password: '', full_name: '' });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    if (user)
        return <Navigate to="/" replace/>;
    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await register(form);
        }
        catch {
            setError('Registration failed. Email or username may already exist.');
        }
        finally {
            setLoading(false);
        }
    };
    return (<div className="min-h-screen gradient-mesh flex items-center justify-center relative overflow-hidden">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/3 right-1/4 w-72 h-72 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"/>
        <div className="absolute bottom-1/3 left-1/4 w-80 h-80 bg-violet-500/10 rounded-full blur-3xl animate-pulse"/>
      </div>

      <div className="relative z-10 w-full max-w-md mx-4">
        <div className="text-center mb-8">
          <div className="inline-flex w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 items-center justify-center text-2xl font-bold shadow-2xl shadow-cyan-500/30 mb-4">SI</div>
          <h1 className="text-3xl font-bold text-white">Create Account</h1>
          <p className="text-slate-400 mt-2">First user becomes Admin automatically</p>
        </div>

        <form onSubmit={handleSubmit} className="glass rounded-2xl p-8 space-y-4 border border-white/10">
          {error && <p className="text-red-400 text-sm text-center bg-red-500/10 rounded-lg py-2">{error}</p>}
          {['full_name', 'email', 'username'].map((f) => (<input key={f} className="w-full px-4 py-3 rounded-xl bg-slate-800/50 border border-white/10 text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none" placeholder={f.replace('_', ' ')} value={form[f]} onChange={(e) => setForm({ ...form, [f]: e.target.value })} required/>))}
          <input className="w-full px-4 py-3 rounded-xl bg-slate-800/50 border border-white/10 text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none" type="password" placeholder="Password (min 8 chars)" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} minLength={8} required/>
          <button disabled={loading} className="w-full py-3 bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-xl font-medium hover:from-cyan-500 hover:to-blue-500 disabled:opacity-50 transition shadow-lg shadow-cyan-500/25">
            {loading ? 'Creating...' : 'Register'}
          </button>
          <p className="text-center text-sm text-slate-400">Have an account? <Link to="/login" className="text-cyan-400">Sign In</Link></p>
        </form>
      </div>
    </div>);
}
