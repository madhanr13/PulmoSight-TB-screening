import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, ArrowUpRight, Check, FileImage, LogIn, LogOut, ShieldCheck, UserPlus } from 'lucide-react';
import './styles.css';

const api = async (path, options = {}) => {
  const response = await fetch(path, { credentials: 'include', ...options });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Something went wrong.');
  return data;
};

function Brand() {
  return <a className="brand" href="/"><span className="brand-mark">+</span><span>Pulmo<span className="teal">Sight</span></span></a>;
}

function Auth({ mode, onSuccess }) {
  const register = mode === 'register';
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const submit = async (event) => {
    event.preventDefault(); setError(''); setBusy(true);
    try {
      const data = await api(register ? '/api/register' : '/api/login', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form)
      });
      onSuccess(data.user);
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  };

  return <main className="auth-page">
    <section className="auth-layout">
      <div className="auth-visual">
        <div className="visual-badge"><ShieldCheck size={14} /> Secure workspace</div>
        <h1>{register ? 'Join the review workflow.' : 'Welcome back to clearer review.'}</h1>
        <p>Keep case review focused, organized, and ready for the next clinical conversation.</p>
        <div className="auth-points"><span><Check size={15} /> Protected case access</span><span><Check size={15} /> Activity at a glance</span><span><Check size={15} /> Simple team handoff</span></div>
      </div>
      <form className="auth-card" onSubmit={submit}>
        <div className="eyebrow"><span className="eyebrow-line" /> {register ? 'Create account' : 'Sign in'}</div>
        <h2>{register ? 'Start your account' : 'Enter your workspace'}</h2>
        {error && <div className="error-box">{error}</div>}
        <label>Email address<input type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} placeholder="you@example.com" required /></label>
        <label>Password<input type="password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} placeholder="Minimum 6 characters" minLength={register ? 6 : undefined} required /></label>
        <button className="button primary-button" disabled={busy}>{busy ? 'Please wait...' : register ? <><UserPlus size={16} /> Create account</> : <><LogIn size={16} /> Sign in</>}</button>
        <div className="auth-footer"><span className="footer-rule" /> <small>{register ? 'Already registered?' : 'New to PulmoSight?'} <a href={register ? '/login' : '/register'}>{register ? 'Sign in' : 'Create an account'}</a></small></div>
      </form>
    </section>
  </main>;
}

function Workspace({ user, onLogout }) {
  const [file, setFile] = useState(null); const [result, setResult] = useState(null); const [busy, setBusy] = useState(false); const [error, setError] = useState('');
  const analyze = async () => {
    if (!file) return; setBusy(true); setError('');
    const body = new FormData(); body.append('image', file);
    try { setResult(await api('/api/predict', { method: 'POST', body })); } catch (err) { setError(err.message); } finally { setBusy(false); }
  };
  return <>
    <header className="topbar"><Brand /><nav><a href="/">Review</a><a href="/dashboard">Dashboard</a><a href="/reports">Reports</a></nav><div className="user-menu"><span>{user.email}</span><button onClick={onLogout}><LogOut size={15} /> Log out</button></div></header>
    <main className="shell"><section className="hero"><div className="eyebrow"><span className="eyebrow-line" /> CASE REVIEW</div><h1>Make each case<br /><em>more actionable.</em></h1><p>Upload a chest radiograph to create a focused screening result for clinician review.</p></section>
      <section className="workspace"><div className="upload-panel"><div className="panel-kicker">UPLOAD CASE <span>JPG · PNG · WEBP / 12 MB</span></div><label className="upload-body" htmlFor="file"><FileImage size={38} /><h2>{file ? file.name : 'Choose a radiograph'}</h2><p>{file ? 'Ready for review' : 'Select an image from your device'}</p><input id="file" type="file" accept="image/jpeg,image/png,image/webp" hidden onChange={e => setFile(e.target.files[0])} /></label>{error && <div className="error-box">{error}</div>}</div><div className="result-panel"><div className="panel-kicker">SCREENING RESULT <span>{result ? 'READY' : 'WAITING'}</span></div>{result ? <><div className="result-status"><Activity size={18} /><span>{result.status}</span></div><h2>{result.prediction}</h2><div className="score">{result.score}<small>%</small></div><p>{result.disclaimer}</p></> : <div className="result-empty"><Activity size={42} /><p>Your result will appear here after review.</p></div>}<button className="button primary-button analyze" disabled={!file || busy} onClick={analyze}>{busy ? 'Reviewing...' : 'Analyze radiograph'} <ArrowUpRight size={16} /></button></div></section>
      <section className="feature-row"><article><span>CASE QUEUE</span><h3>Keep reviews moving</h3><p>Move from upload to a clear next step without losing context.</p></article><article><span>TEAM READY</span><h3>Share the signal</h3><p>Keep case outcomes easy to understand during handoff and follow-up.</p></article><article><span>CLINICAL CARE</span><h3>Human judgment first</h3><p>Use every result as decision support alongside qualified review.</p></article></section>
    </main>
  </>;
}

function App() {
  const [user, setUser] = useState(null); const [checking, setChecking] = useState(true);
  useEffect(() => { api('/api/auth/status').then(data => setUser(data.user)).catch(() => {}).finally(() => setChecking(false)); }, []);
  if (checking) return <div className="loading">Loading workspace...</div>;
  if (!user) return <><header className="public-topbar"><Brand /><div><a href="/login"><LogIn size={15} /> Login</a><a className="accent-link" href="/register"><UserPlus size={15} /> Register</a></div></header>{window.location.pathname === '/register' ? <Auth mode="register" onSuccess={setUser} /> : <Auth mode="login" onSuccess={setUser} />}</>;
  return <Workspace user={user} onLogout={() => api('/api/logout', { method: 'POST' }).then(() => setUser(null))} />;
}

createRoot(document.getElementById('root')).render(<App />);
