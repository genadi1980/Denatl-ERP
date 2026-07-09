import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Activity, 
  Stethoscope, 
  Sparkles, 
  ShieldAlert, 
  ChevronRight, 
  Phone, 
  Mail, 
  MapPin, 
  Clock, 
  UserCheck, 
  CheckCircle2, 
  TrendingDown, 
  ArrowRight
} from 'lucide-react';

export default function Landing() {
  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-clinic-ice selection:bg-clinic-accent/30 selection:text-clinic-charcoal">
      {/* 1. Header/Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 premium-glass border-b border-clinic-accent/10 transition-all duration-300">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="/logo.jpg" alt="Radev Clinic Logo" className="w-10 h-10 object-contain rounded-lg shadow-sm" />
            <div>
              <span className="font-display text-2xl font-bold tracking-wide text-clinic-navy">РАДЕВ</span>
              <span className="font-display text-2xl font-light text-clinic-accent ml-1">Клиник</span>
            </div>
          </div>
          
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-clinic-charcoal/80">
            <button onClick={() => scrollToSection('services')} className="hover:text-clinic-blue transition-colors duration-200 outline-none">Услуги</button>
            <button onClick={() => scrollToSection('about')} className="hover:text-clinic-blue transition-colors duration-200 outline-none">За нас</button>
            <button onClick={() => scrollToSection('stats')} className="hover:text-clinic-blue transition-colors duration-200 outline-none">Доверие</button>
            <button onClick={() => scrollToSection('contact')} className="hover:text-clinic-blue transition-colors duration-200 outline-none">Контакти</button>
          </div>

          <div className="flex items-center gap-4">
            <Link 
              to="/erp" 
              className="px-5 py-2.5 rounded-xl border border-clinic-accent/30 text-xs font-semibold text-clinic-navy tracking-wider hover:bg-clinic-navy hover:text-white transition-all duration-300 flex items-center gap-2 shadow-sm"
            >
              ДЕНТАЛЕН ЕРП
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </nav>

      {/* 2. Hero Section */}
      <section id="about" className="pt-40 pb-20 px-6 max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
        <div className="lg:col-span-7 space-y-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-clinic-accent/10 border border-clinic-accent/20 text-clinic-navy text-xs font-semibold tracking-wide">
            <Sparkles className="w-3.5 h-3.5 text-clinic-accent" />
            НОВО ИЗДАТЕЛСТВО В ДЕНТАЛНАТА ГРИЖА
          </div>
          
          <h1 className="font-display text-5xl md:text-7xl font-bold tracking-tight text-clinic-navy leading-[1.1]">
            Безкомпромисно качество в <br />
            <span className="font-display italic font-light text-clinic-accent">дигиталната</span> стоматология.
          </h1>
          
          <p className="text-lg text-clinic-charcoal/70 max-w-xl leading-relaxed">
            В Радев Клиник съчетаваме медицински професионализъм с най-съвременните AI технологии за проследяване на пазара. Ние гарантираме най-висок клас материали за Вашето здраве и дълготрайна сигурност.
          </p>
          
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 pt-4">
            <a 
              href="https://calendar.app.google/TQf6uDGi9GoUjz2G6" 
              target="_blank" 
              rel="noopener noreferrer" 
              className="px-8 py-4 bg-clinic-navy text-white font-semibold rounded-xl text-center shadow-lg shadow-clinic-navy/20 hover:bg-clinic-blue hover:-translate-y-0.5 transition-all duration-300"
            >
              Запишете Час
            </a>
            <Link 
              to="/erp" 
              className="px-8 py-4 border border-clinic-accent/30 text-clinic-navy font-semibold rounded-xl text-center hover:bg-clinic-accent/10 hover:border-clinic-accent/60 transition-all duration-300"
            >
              Вход за Персонал
            </Link>
          </div>
        </div>
        
        <div className="lg:col-span-5 relative">
          <div className="absolute inset-0 bg-gradient-to-tr from-clinic-accent/10 to-transparent rounded-[32px] blur-2xl" />
          <div className="relative border border-clinic-accent/20 rounded-[32px] p-2 bg-white/50 premium-glass luxury-shadow">
            <img 
              src="https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&q=80&w=600" 
              alt="Radev Clinic Dental Consultation" 
              className="rounded-[24px] w-full object-cover aspect-[4/3] shadow-inner"
            />
            {/* Overlay interactive mini-badge */}
            <div className="absolute -bottom-6 -left-6 bg-white border border-clinic-accent/20 rounded-2xl p-4 shadow-xl flex items-center gap-3 animate-bounce" style={{ animationDuration: '4s' }}>
              <div className="w-10 h-10 bg-clinic-emerald/10 text-clinic-emerald rounded-xl flex items-center justify-center">
                <TrendingDown className="w-5 h-5" />
              </div>
              <div>
                <div className="text-[10px] text-clinic-charcoal/50 font-medium">АКТИВНИ ПРЕДЛОЖЕНИЯ</div>
                <div className="text-sm font-bold text-clinic-navy">Промоция &gt; 15% Налична</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 3. Services Section */}
      <section id="services" className="py-24 bg-white border-y border-clinic-accent/10">
        <div className="max-w-7xl mx-auto px-6 space-y-16">
          <div className="text-center space-y-4 max-w-xl mx-auto">
            <h2 className="font-display text-4xl font-bold tracking-tight text-clinic-navy">Нашите Специализирани Услуги</h2>
            <div className="h-1 w-20 bg-clinic-accent mx-auto rounded-full" />
            <p className="text-clinic-charcoal/60 leading-relaxed">
              Ние се стремим да осигурим безкомпромисно стоматологично лечение чрез високи технологии и сертифицирани материали.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Service 1 */}
            <div className="p-8 border border-clinic-accent/10 rounded-2xl bg-clinic-ice/30 hover:bg-clinic-ice/70 transition-all duration-300 space-y-6 group">
              <div className="w-12 h-12 rounded-xl bg-clinic-navy/5 text-clinic-navy flex items-center justify-center group-hover:bg-clinic-navy group-hover:text-white transition-all duration-300">
                <Stethoscope className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-clinic-navy">Естетични Композити</h3>
              <p className="text-clinic-charcoal/60 text-sm leading-relaxed">
                Възстановяване с най-висок клас нанокомпозити (GC everX Flow, G-aenial Posterior) за перфектна естетика и здравина.
              </p>
            </div>

            {/* Service 2 */}
            <div className="p-8 border border-clinic-accent/10 rounded-2xl bg-clinic-ice/30 hover:bg-clinic-ice/70 transition-all duration-300 space-y-6 group">
              <div className="w-12 h-12 rounded-xl bg-clinic-navy/5 text-clinic-navy flex items-center justify-center group-hover:bg-clinic-navy group-hover:text-white transition-all duration-300">
                <Sparkles className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-clinic-navy">Адхезивни Системи</h3>
              <p className="text-clinic-charcoal/60 text-sm leading-relaxed">
                Свързващи агенти (G-Premio Bond) за максимално дълготрайна връзка и превенция на микропропускливост.
              </p>
            </div>

            {/* Service 3 */}
            <div className="p-8 border border-clinic-accent/10 rounded-2xl bg-clinic-ice/30 hover:bg-clinic-ice/70 transition-all duration-300 space-y-6 group">
              <div className="w-12 h-12 rounded-xl bg-clinic-navy/5 text-clinic-navy flex items-center justify-center group-hover:bg-clinic-navy group-hover:text-white transition-all duration-300">
                <Activity className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-clinic-navy">Микроскопска Ендодонтия</h3>
              <p className="text-clinic-charcoal/60 text-sm leading-relaxed">
                Кореново лечение с прецизни C-Pilot пили и биокерамични силанти за спасяване на увредени зъби под силно увеличение.
              </p>
            </div>

            {/* Service 4 */}
            <div className="p-8 border border-clinic-accent/10 rounded-2xl bg-clinic-ice/30 hover:bg-clinic-ice/70 transition-all duration-300 space-y-6 group">
              <div className="w-12 h-12 rounded-xl bg-clinic-navy/5 text-clinic-navy flex items-center justify-center group-hover:bg-clinic-navy group-hover:text-white transition-all duration-300">
                <ShieldAlert className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-clinic-navy">Превантивна Профилактика</h3>
              <p className="text-clinic-charcoal/60 text-sm leading-relaxed">
                Глас-йономерни обтурации, силанизиране и орална хигиена от най-ранна възраст за защита от кариес и усложнения.
              </p>
            </div>

            {/* Service 5 */}
            <div className="p-8 border border-clinic-accent/10 rounded-2xl bg-clinic-ice/30 hover:bg-clinic-ice/70 transition-all duration-300 space-y-6 group">
              <div className="w-12 h-12 rounded-xl bg-clinic-navy/5 text-clinic-navy flex items-center justify-center group-hover:bg-clinic-navy group-hover:text-white transition-all duration-300">
                <Clock className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-clinic-navy">Имплантология и Хирургия</h3>
              <p className="text-clinic-charcoal/60 text-sm leading-relaxed">
                Възстановяване на липсващи зъби с дигитално планирани титаниеви импланти и максимален комфорт по време на манипулацията.
              </p>
            </div>

            {/* Service 6 */}
            <div className="p-8 border border-clinic-accent/10 rounded-2xl bg-clinic-ice/30 hover:bg-clinic-ice/70 transition-all duration-300 space-y-6 group">
              <div className="w-12 h-12 rounded-xl bg-clinic-navy/5 text-clinic-navy flex items-center justify-center group-hover:bg-clinic-navy group-hover:text-white transition-all duration-300">
                <UserCheck className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-clinic-navy">Детска Дентална Медицина</h3>
              <p className="text-clinic-charcoal/60 text-sm leading-relaxed">
                Специален приятелски подход към най-малките ни пациенти, осигуряващ безболезнено лечение без страх и стрес.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 4. Trust and Statistics Pillar */}
      <section id="stats" className="py-20 bg-clinic-navy text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-clinic-blue/50 to-clinic-navy opacity-30" />
        <div className="relative max-w-7xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          <div className="space-y-2">
            <div className="text-4xl md:text-5xl font-extrabold text-clinic-accent">15+</div>
            <div className="text-xs md:text-sm font-medium tracking-wider text-white/60">ГОДИНИ ОПИТ</div>
          </div>
          <div className="space-y-2">
            <div className="text-4xl md:text-5xl font-extrabold text-clinic-accent">10k+</div>
            <div className="text-xs md:text-sm font-medium tracking-wider text-white/60">КЛИЕНТСКИ УСМИВКИ</div>
          </div>
          <div className="space-y-2">
            <div className="text-4xl md:text-5xl font-extrabold text-clinic-accent">99.8%</div>
            <div className="text-xs md:text-sm font-medium tracking-wider text-white/60">ПАТИЕНТСКО ДОВЕРИЕ</div>
          </div>
          <div className="space-y-2">
            <div className="text-4xl md:text-5xl font-extrabold text-clinic-accent">100%</div>
            <div className="text-xs md:text-sm font-medium tracking-wider text-white/60">СЕРТИФИЦИРАНИ МАТЕРИАЛИ</div>
          </div>
        </div>
      </section>

      {/* 5. Contact Section */}
      <section id="contact" className="py-24 max-w-7xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-12 gap-16 items-start">
        <div className="lg:col-span-5 space-y-8">
          <div className="space-y-4">
            <h2 className="font-display text-4xl font-bold tracking-tight text-clinic-navy">Контакти & Локация</h2>
            <div className="h-1 w-20 bg-clinic-accent rounded-full" />
            <p className="text-clinic-charcoal/60 leading-relaxed">
              Свържете се с нас, за да планирате Вашата персонална консултация. Нашият екип е на разположение за Вашите въпроси.
            </p>
          </div>

          <div className="space-y-6">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-lg bg-clinic-accent/10 border border-clinic-accent/20 text-clinic-blue flex items-center justify-center shrink-0">
                <MapPin className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-clinic-navy">Адрес</h4>
                <p className="text-sm text-clinic-charcoal/70">бул. „Цар Освободител“ №6, Шумен, България, 9700</p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-lg bg-clinic-accent/10 border border-clinic-accent/20 text-clinic-blue flex items-center justify-center shrink-0">
                <Phone className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-clinic-navy">Телефон</h4>
                <p className="text-sm text-clinic-charcoal/70">088 836 6068</p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-lg bg-clinic-accent/10 border border-clinic-accent/20 text-clinic-blue flex items-center justify-center shrink-0">
                <Mail className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-clinic-navy">Имейл</h4>
                <p className="text-sm text-clinic-charcoal/70">radevdent@gmail.com</p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-lg bg-clinic-accent/10 border border-clinic-accent/20 text-clinic-blue flex items-center justify-center shrink-0">
                <Clock className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-clinic-navy">Работно Време</h4>
                <p className="text-sm text-clinic-charcoal/70">Понеделник - Петък: 08:30 - 19:30</p>
                <p className="text-sm text-clinic-charcoal/70">Събота: С предварително записване</p>
              </div>
            </div>
          </div>
        </div>

        {/* Dynamic Booking Card */}
        <div className="lg:col-span-7 bg-white p-8 md:p-10 border border-clinic-accent/10 rounded-3xl luxury-shadow relative">
          <h3 className="font-display text-2xl font-bold text-clinic-navy mb-6">Заявете Консултация</h3>
          
          <form onSubmit={(e) => { e.preventDefault(); alert('Благодарим Ви! Вашата заявка за час бе получена успешно. Наш консултант ще се свърже с Вас за потвърждение.'); }} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-xs font-bold tracking-wider text-clinic-navy/80 uppercase">Имена</label>
                <input 
                  type="text" 
                  placeholder="Иван Иванов" 
                  required 
                  className="w-full px-4 py-3 bg-clinic-ice/50 border border-clinic-accent/10 rounded-xl focus:border-clinic-accent focus:bg-white outline-none transition-all duration-300 text-sm"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-bold tracking-wider text-clinic-navy/80 uppercase">Телефонен Номер</label>
                <input 
                  type="tel" 
                  placeholder="+359 888 111 222" 
                  required 
                  className="w-full px-4 py-3 bg-clinic-ice/50 border border-clinic-accent/10 rounded-xl focus:border-clinic-accent focus:bg-white outline-none transition-all duration-300 text-sm"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold tracking-wider text-clinic-navy/80 uppercase">Желана Услуга</label>
              <select className="w-full px-4 py-3 bg-clinic-ice/50 border border-clinic-accent/10 rounded-xl focus:border-clinic-accent focus:bg-white outline-none transition-all duration-300 text-sm text-clinic-charcoal/80">
                <option>Естетични Композити & Бондинг</option>
                <option>Микроскопско Кореново Лечение</option>
                <option>Дентална Имплантология</option>
                <option>Детска Стоматология</option>
                <option>Професионално Почистване & Избелване</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold tracking-wider text-clinic-navy/80 uppercase">Бележки / Въпроси</label>
              <textarea 
                rows="4" 
                placeholder="Споделете накратко за състоянието си или желан ден и час..."
                className="w-full px-4 py-3 bg-clinic-ice/50 border border-clinic-accent/10 rounded-xl focus:border-clinic-accent focus:bg-white outline-none transition-all duration-300 text-sm"
              />
            </div>

            <button 
              type="submit" 
              className="w-full py-4 bg-clinic-navy hover:bg-clinic-blue text-white font-bold tracking-wider uppercase rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-clinic-navy/15 flex items-center justify-center gap-2"
            >
              ИЗПРАТИ ЗАЯВКА
              <CheckCircle2 className="w-4 h-4" />
            </button>
          </form>
        </div>
      </section>

      {/* 6. Footer */}
      <footer className="bg-clinic-charcoal text-white/50 py-12 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <img src="/logo.jpg" alt="Radev Clinic Logo" className="w-8 h-8 object-contain rounded-lg border border-clinic-accent/15" />
            <span className="font-display font-semibold tracking-wide text-white text-lg">РАДЕВ Клиник</span>
          </div>
          
          <div className="text-xs text-center md:text-right">
            &copy; 2026 Дентална Клиника Радев - Всички права запазени. <br className="hidden sm:inline" />
            Захранвано от Global Group Intelligence Technology.
          </div>
        </div>
      </footer>
    </div>
  );
}
