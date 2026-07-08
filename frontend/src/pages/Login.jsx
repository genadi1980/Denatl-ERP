import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Activity, ShieldAlert, Lock, Mail, Loader2, ArrowLeft } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [submitting, setSubmitting] = useState(false);
  
  const { user, login } = useAuth();
  const navigate = useNavigate();

  // Redirect if already authenticated
  useEffect(() => {
    if (user) {
      navigate('/erp');
    }
  }, [user, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSubmitting(true);
    
    try {
      await login(email, password);
      navigate('/erp');
    } catch (err) {
      console.error('Login failure:', err);
      // Clean up Supabase auth error messages for the end-user
      if (err.message === 'Invalid login credentials') {
        setErrorMsg('Невалиден имейл или парола. Моля, опитайте отново.');
      } else {
        setErrorMsg(err.message || 'Възникна грешка при входа. Опитайте отново.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-clinic-ice flex flex-col items-center justify-center p-6 selection:bg-clinic-accent/30 selection:text-clinic-charcoal">
      {/* Return to home button */}
      <button 
        onClick={() => navigate('/')}
        className="absolute top-6 left-6 px-4 py-2.5 rounded-xl border border-clinic-accent/10 bg-white/50 premium-glass text-xs font-semibold text-clinic-navy tracking-wider hover:bg-clinic-navy hover:text-white transition-all duration-300 flex items-center gap-2 shadow-sm"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        КЪМ НАЧАЛОТО
      </button>

      <div className="w-full max-w-md bg-white border border-clinic-accent/10 rounded-3xl p-8 md:p-10 luxury-shadow relative overflow-hidden">
        {/* Decorative corner block */}
        <div className="absolute top-0 right-0 w-32 h-32 bg-clinic-accent/5 rounded-bl-full pointer-events-none" />
        
        {/* Brand header */}
        <div className="flex flex-col items-center space-y-4 mb-8">
          <img src="/logo.jpg" alt="Radev Clinic Logo" className="w-14 h-14 object-contain rounded-xl shadow-lg shadow-clinic-navy/10" />
          <div className="text-center">
            <h1 className="font-display text-3xl font-bold tracking-wide text-clinic-navy m-0 leading-none">РАДЕВ Клиник</h1>
            <p className="text-xs font-bold tracking-wider text-clinic-accent mt-2">ПОРТАЛ ЗА СЛУЖИТЕЛИ // ДЕНТАЛЕН ЕРП</p>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {errorMsg && (
            <div className="p-4 bg-clinic-coral/10 border border-clinic-coral/20 rounded-xl flex items-start gap-3 text-clinic-coral text-xs leading-relaxed animate-shake">
              <ShieldAlert className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{errorMsg}</span>
            </div>
          )}

          <div className="space-y-2">
            <label className="text-xs font-bold tracking-wider text-clinic-navy/80 uppercase block">Имейл Адрес</label>
            <div className="relative">
              <span className="absolute left-4 top-3.5 text-clinic-charcoal/40">
                <Mail className="w-4 h-4" />
              </span>
              <input 
                type="email" 
                placeholder="doctor@radevclinic.bg" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required 
                className="w-full pl-11 pr-4 py-3 bg-clinic-ice/50 border border-clinic-accent/10 rounded-xl focus:border-clinic-accent focus:bg-white outline-none transition-all duration-300 text-sm"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-bold tracking-wider text-clinic-navy/80 uppercase block">Парола</label>
            <div className="relative">
              <span className="absolute left-4 top-3.5 text-clinic-charcoal/40">
                <Lock className="w-4 h-4" />
              </span>
              <input 
                type="password" 
                placeholder="••••••••" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required 
                className="w-full pl-11 pr-4 py-3 bg-clinic-ice/50 border border-clinic-accent/10 rounded-xl focus:border-clinic-accent focus:bg-white outline-none transition-all duration-300 text-sm"
              />
            </div>
          </div>

          <button 
            type="submit" 
            disabled={submitting}
            className="w-full py-4 bg-clinic-navy hover:bg-clinic-blue text-white font-bold tracking-wider uppercase rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-clinic-navy/15 flex items-center justify-center gap-2"
          >
            {submitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                ВХОД...
              </>
            ) : (
              'ВХОД В ЕРП'
            )}
          </button>
        </form>

        <div className="text-center mt-8 text-[10px] text-clinic-charcoal/40 tracking-wider font-semibold">
          СИСТЕМАТА СЕ ОХРАНЯВА С КРИПТИРАНЕ НА СЕСИЯТА НА ДВЕ НИВА // GGIT
        </div>
      </div>
    </div>
  );
}
