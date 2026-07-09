import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Activity, 
  LogOut, 
  Search, 
  RefreshCw, 
  SlidersHorizontal, 
  Sliders, 
  Plus, 
  Minus, 
  Play, 
  Brain, 
  Loader2, 
  AlertTriangle, 
  CheckCircle, 
  X, 
  Layers, 
  Database,
  Building,
  ArrowRight
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export default function Erp() {
  const { user, session, logout, loading: authLoading } = useAuth();
  const navigate = useNavigate();

  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [loadingProducts, setLoadingProducts] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedBrand, setSelectedBrand] = useState('all');
  const [selectedSource, setSelectedSource] = useState('all');

  // Inventory Editor Modal state
  const [editingProduct, setEditingProduct] = useState(null);
  const [editQuantity, setEditingQuantity] = useState(0);
  const [editMaxQuantity, setEditingMaxQuantity] = useState(10);
  const [savingInventory, setSavingInventory] = useState(false);

  // Scraper status
  const [scraperTriggering, setScraperTriggering] = useState(false);
  const [scraperMessage, setScraperMessage] = useState('');

  // AI Analysis Panel
  const [aiReport, setAiReport] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [aiError, setAiError] = useState('');

  // Protect route
  useEffect(() => {
    if (!authLoading && !user) {
      navigate('/login');
    }
  }, [user, authLoading, navigate]);

  // Load products
  const fetchProducts = async () => {
    setLoadingProducts(true);
    try {
      const response = await fetch(`${API_BASE_URL}/products`);
      if (response.ok) {
        const data = await response.json();
        setProducts(data);
      } else {
        console.error('Failed to load products');
      }
    } catch (err) {
      console.error('Error fetching products:', err);
    } finally {
      setLoadingProducts(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchProducts();
    }
  }, [user]);

  // Filter products
  useEffect(() => {
    let result = [...products];

    // Search query
    if (search.trim()) {
      const query = search.toLowerCase();
      result = result.filter(p => 
        p.name.toLowerCase().includes(query) || 
        (p.brand && p.brand.toLowerCase().includes(query))
      );
    }

    // Brand filter
    if (selectedBrand !== 'all') {
      result = result.filter(p => p.brand === selectedBrand);
    }

    // Source site filter
    if (selectedSource !== 'all') {
      result = result.filter(p => p.source === selectedSource);
    }

    setFilteredProducts(result);
  }, [products, search, selectedBrand, selectedSource]);

  // Unique filters lists
  const brands = ['all', ...new Set(products.map(p => p.brand).filter(Boolean))];
  const sources = ['all', ...new Set(products.map(p => p.source).filter(Boolean))];

  // Open inventory editor
  const handleOpenEditInventory = (product) => {
    setEditingProduct(product);
    setEditingQuantity(product.quantity);
    setEditingMaxQuantity(product.max_quantity || 10);
  };

  // Close editor
  const handleCloseEditInventory = () => {
    setEditingProduct(null);
  };

  // Save stock quantities
  const handleSaveInventory = async () => {
    if (!editingProduct) return;
    setSavingInventory(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/products/${editingProduct.id}/inventory`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify({
          quantity: editQuantity,
          max_quantity: editMaxQuantity
        })
      });

      if (response.ok) {
        // Update local list
        setProducts(prev => prev.map(p => 
          p.id === editingProduct.id 
            ? { ...p, quantity: editQuantity, max_quantity: editMaxQuantity, low_stock_alert: editQuantity <= 0.2 * editMaxQuantity }
            : p
        ));
        handleCloseEditInventory();
      } else {
        const errData = await response.json();
        alert(`Грешка: ${errData.detail || 'Неуспешна актуализация'}`);
      }
    } catch (err) {
      console.error('Error updating stock:', err);
      alert('Грешка при връзката със сървъра.');
    } finally {
      setSavingInventory(false);
    }
  };

  // Run scraper background worker
  const triggerScraper = async () => {
    setScraperTriggering(true);
    setScraperMessage('');
    
    try {
      const response = await fetch(`${API_BASE_URL}/scraper/run`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setScraperMessage('Скрейпърът стартира успешно в облака. Данните ще се актуализират автоматично след няколко минути.');
        // Refresh product list in a short bit
        setTimeout(fetchProducts, 8000);
      } else {
        const errData = await response.json();
        setScraperMessage(`Грешка при старт: ${errData.detail || 'Неочакван отговор'}`);
      }
    } catch (err) {
      console.error('Failed to trigger scraper:', err);
      setScraperMessage('Грешка при комуникация със сървъра.');
    } finally {
      setScraperTriggering(false);
    }
  };

  // Get AI promos report (Gemini Serverless)
  const runAiAnalysis = async () => {
    setAnalyzing(true);
    setAiReport('');
    setAiError('');

    try {
      const response = await fetch(`${API_BASE_URL}/promotions/analyze?provider=gemini`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setAiReport(data.ai_report || 'Няма данни');
      } else {
        const errData = await response.json();
        setAiError(errData.detail || 'Грешка при генериране на доклада.');
      }
    } catch (err) {
      console.error('Failed to run AI analysis:', err);
      setAiError('Грешка при комуникация с облачното ядро.');
    } finally {
      setAnalyzing(false);
    }
  };

  // Render markdown inline safely
  const renderAiReportText = (text) => {
    if (!text) return null;
    
    // Quick simple markdown parser to format headings, bullet points, and warning banners nicely in Bulgarian
    const lines = text.split('\n');
    return lines.map((line, idx) => {
      if (line.startsWith('### ')) {
        return <h4 key={idx} className="font-display text-lg font-bold text-clinic-navy mt-6 mb-2 border-b border-clinic-accent/15 pb-1">{line.replace('### ', '').replace(/\*\*/g, '')}</h4>;
      }
      if (line.startsWith('## ')) {
        return <h3 key={idx} className="font-display text-xl font-bold text-clinic-navy mt-8 mb-3">{line.replace('## ', '').replace(/\*\*/g, '')}</h3>;
      }
      if (line.startsWith('* ') || line.startsWith('- ')) {
        return (
          <div key={idx} className="flex items-start gap-2 pl-4 py-1 text-sm text-clinic-charcoal/80">
            <span className="text-clinic-accent mt-1.5 shrink-0 font-bold">•</span>
            <span>{line.replace(/^[\*\-\s]+/, '')}</span>
          </div>
        );
      }
      if (line.startsWith('⚠️')) {
        return (
          <div key={idx} className="p-4 bg-yellow-50 border border-yellow-200 text-yellow-800 text-xs rounded-xl flex items-center gap-3 my-4">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{line}</span>
          </div>
        );
      }
      if (line.trim() === '') return <div key={idx} className="h-2" />;
      return <p key={idx} className="text-sm leading-relaxed text-clinic-charcoal/70">{line}</p>;
    });
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-clinic-ice flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-clinic-navy" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-clinic-ice p-6 selection:bg-clinic-accent/30 selection:text-clinic-charcoal">
      {/* Navbar header */}
      <header className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6 mb-8 premium-glass border border-clinic-accent/10 rounded-2xl p-6 shadow-sm">
        <div className="flex items-center gap-4">
          <img src="/logo.jpg" alt="Radev Clinic Logo" className="w-12 h-12 object-contain rounded-xl shadow-md shadow-clinic-navy/10" />
          <div>
            <div className="flex items-center gap-2">
              <span className="font-display text-2xl font-bold text-clinic-navy">РАДЕВ</span>
              <span className="font-display text-2xl font-light text-clinic-accent">Клиник // ЕРП</span>
            </div>
            <p className="text-[10px] font-bold text-clinic-charcoal/40 tracking-wider">ДЕНТАЛНА ЕРП СИСТЕМА // ПОТРЕБИТЕЛ: {user?.email}</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button 
            onClick={() => navigate('/')}
            className="px-4 py-2.5 rounded-xl border border-clinic-accent/10 bg-white/50 text-xs font-semibold text-clinic-navy tracking-wider hover:bg-clinic-navy hover:text-white transition-all duration-300"
          >
            САЙТ НА КЛИНИКАТА
          </button>
          
          <button 
            onClick={logout}
            className="px-4 py-2.5 rounded-xl bg-clinic-coral/10 hover:bg-clinic-coral text-clinic-coral hover:text-white text-xs font-bold tracking-wider flex items-center gap-2 transition-all duration-300 shadow-sm"
          >
            ИЗХОД
            <LogOut className="w-3.5 h-3.5" />
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left column - ERP Operations & AI Analytics */}
        <div className="lg:col-span-4 space-y-8">
          {/* Operations Panel */}
          <section className="bg-white border border-clinic-accent/10 rounded-3xl p-6 shadow-sm space-y-6">
            <div className="flex items-center gap-3 pb-4 border-b border-clinic-ice">
              <Sliders className="w-5 h-5 text-clinic-accent" />
              <h2 className="text-lg font-bold text-clinic-navy">Оперативен Контрол</h2>
            </div>

            <div className="space-y-4">
              <div>
                <button 
                  onClick={triggerScraper}
                  disabled={scraperTriggering}
                  className="w-full py-4 bg-clinic-navy hover:bg-clinic-blue text-white font-bold tracking-wider uppercase rounded-xl transition-all duration-300 hover:shadow-lg disabled:opacity-50 flex items-center justify-center gap-2 text-xs"
                >
                  {scraperTriggering ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      СВЪРЗВАНЕ...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 text-clinic-accent" />
                      СТАРТИРАЙ СКРЕЙПЪР
                    </>
                  )}
                </button>
              </div>

              <div>
                <button 
                  onClick={runAiAnalysis}
                  disabled={analyzing}
                  className="w-full py-4 border border-clinic-accent text-clinic-navy hover:bg-clinic-accent hover:text-white font-bold tracking-wider uppercase rounded-xl transition-all duration-300 disabled:opacity-50 flex items-center justify-center gap-2 text-xs"
                >
                  {analyzing ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      АНАЛИЗИРАНЕ...
                    </>
                  ) : (
                    <>
                      <Brain className="w-4 h-4 text-clinic-accent" />
                      AI ЦЕНОВИ АНАЛИЗ
                    </>
                  )}
                </button>
              </div>
            </div>

            {scraperMessage && (
              <div className="p-4 bg-clinic-accent/10 border border-clinic-accent/20 rounded-xl flex items-start gap-3 text-clinic-navy text-xs leading-relaxed">
                <CheckCircle className="w-4 h-4 text-clinic-gold shrink-0 mt-0.5" />
                <span>{scraperMessage}</span>
              </div>
            )}
          </section>

          {/* AI Report desk */}
          {(analyzing || aiReport || aiError) && (
            <section className="bg-white border border-clinic-accent/10 rounded-3xl p-6 shadow-sm space-y-6">
              <div className="flex items-center justify-between pb-4 border-b border-clinic-ice">
                <div className="flex items-center gap-3">
                  <Brain className="w-5 h-5 text-clinic-gold animate-pulse" />
                  <h2 className="text-lg font-bold text-clinic-navy">AI Ценови Преглед</h2>
                </div>
                {aiReport && (
                  <button 
                    onClick={() => setAiReport('')}
                    className="p-1.5 rounded-lg hover:bg-clinic-ice text-clinic-charcoal/50 hover:text-clinic-charcoal"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>

              {analyzing && (
                <div className="flex flex-col items-center justify-center py-12 space-y-4">
                  <Loader2 className="w-8 h-8 animate-spin text-clinic-accent" />
                  <p className="text-xs text-clinic-charcoal/50 font-bold tracking-wider animate-pulse">ЗАРЕЖДАНЕ НА ОБЛАЧЕН AI АНАЛИЗ...</p>
                </div>
              )}

              {aiError && (
                <div className="p-4 bg-clinic-coral/10 border border-clinic-coral/20 rounded-xl flex items-start gap-3 text-clinic-coral text-xs leading-relaxed">
                  <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                  <span>{aiError}</span>
                </div>
              )}

              {aiReport && (
                <div className="max-h-[400px] overflow-y-auto pr-2 space-y-4">
                  {renderAiReportText(aiReport)}
                </div>
              )}
            </section>
          )}
        </div>

        {/* Right column - Products Stock Level Workspace */}
        <div className="lg:col-span-8 space-y-6">
          <section className="bg-white border border-clinic-accent/10 rounded-3xl p-6 shadow-sm">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-clinic-ice">
              <div>
                <h2 className="text-xl font-bold text-clinic-navy">Материални Наличности</h2>
                <p className="text-xs text-clinic-charcoal/40 font-medium">Следете складовите нива и координирайте поръчките спрямо пазарните промоции.</p>
              </div>
              <button 
                onClick={fetchProducts}
                disabled={loadingProducts}
                className="self-start md:self-auto p-2.5 bg-clinic-ice text-clinic-navy hover:bg-clinic-navy hover:text-white rounded-xl transition-all duration-300 disabled:opacity-50 flex items-center justify-center"
              >
                {loadingProducts ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
              </button>
            </div>

            {/* Filter controls */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-4 py-4">
              <div className="md:col-span-6 relative">
                <span className="absolute left-3.5 top-3 text-clinic-charcoal/40">
                  <Search className="w-4 h-4" />
                </span>
                <input 
                  type="text" 
                  placeholder="Търсене на продукти..." 
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-clinic-ice/50 border border-clinic-accent/10 rounded-xl focus:border-clinic-accent focus:bg-white outline-none transition-all duration-300 text-xs"
                />
              </div>

              <div className="md:col-span-3">
                <select 
                  value={selectedBrand}
                  onChange={(e) => setSelectedBrand(e.target.value)}
                  className="w-full px-3 py-2.5 bg-clinic-ice/50 border border-clinic-accent/10 rounded-xl outline-none text-xs text-clinic-charcoal/80"
                >
                  <option value="all">Всички Марки</option>
                  {brands.filter(b => b !== 'all').map(brand => (
                    <option key={brand} value={brand}>{brand}</option>
                  ))}
                </select>
              </div>

              <div className="md:col-span-3">
                <select 
                  value={selectedSource}
                  onChange={(e) => setSelectedSource(e.target.value)}
                  className="w-full px-3 py-2.5 bg-clinic-ice/50 border border-clinic-accent/10 rounded-xl outline-none text-xs text-clinic-charcoal/80"
                >
                  <option value="all">Всички Сайтове</option>
                  {sources.filter(s => s !== 'all').map(source => (
                    <option key={source} value={source}>{source}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Catalog list */}
            {loadingProducts && products.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20 space-y-4">
                <Loader2 className="w-8 h-8 animate-spin text-clinic-navy" />
                <p className="text-xs text-clinic-charcoal/50 font-bold tracking-wider">ЗАРЕЖДАНЕ НА КАТАЛОГА...</p>
              </div>
            ) : filteredProducts.length === 0 ? (
              <div className="text-center py-16 text-sm text-clinic-charcoal/40 font-semibold tracking-wider uppercase">
                Няма съвпадащи продукти в базата данни
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-clinic-ice text-clinic-navy text-xs font-bold uppercase tracking-wider">
                      <th className="py-4 px-3">Марка // Зъболекарски Материал</th>
                      <th className="py-4 px-3">Доставчик</th>
                      <th className="py-4 px-3">Актуална Цена</th>
                      <th className="py-4 px-3">Наличност</th>
                      <th className="py-4 px-3">Статус</th>
                      <th className="py-4 px-3 text-right">Управление</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredProducts.map(product => {
                      const percentStock = product.max_quantity > 0 
                        ? (product.quantity / product.max_quantity) * 100 
                        : 0;
                        
                      return (
                        <tr key={product.id} className="border-b border-clinic-ice/50 text-sm hover:bg-clinic-ice/30 transition-all duration-150">
                          <td className="py-4 px-3">
                            <a 
                              href={product.url} 
                              target="_blank" 
                              rel="noopener noreferrer" 
                              className="font-semibold text-clinic-navy hover:text-clinic-blue hover:underline transition-colors duration-200"
                            >
                              {product.name}
                            </a>
                            <div className="text-[10px] font-bold text-clinic-accent uppercase tracking-wider">{product.brand || 'GC'}</div>
                          </td>
                          <td className="py-4 px-3 text-clinic-charcoal/70 text-xs">
                            <div className="flex items-center gap-1.5">
                              <Building className="w-3.5 h-3.5 text-clinic-charcoal/40" />
                              {product.source}
                            </div>
                          </td>
                          <td className="py-4 px-3 text-xs">
                            {product.latest_price ? (
                              <div>
                                <span className="font-bold text-clinic-navy">{product.latest_price.toFixed(2)} лв.</span>
                                {product.is_promotion && product.old_price && (
                                  <span className="text-clinic-coral font-semibold line-through ml-2">{product.old_price.toFixed(2)} лв.</span>
                                )}
                              </div>
                            ) : (
                              <span className="text-clinic-charcoal/40 font-medium italic">Липсва цена</span>
                            )}
                          </td>
                          <td className="py-4 px-3">
                            <div className="w-24">
                              <div className="flex items-center justify-between text-[10px] font-bold text-clinic-navy/70 mb-1">
                                <span>{product.quantity} бр.</span>
                                <span>/ {product.max_quantity}</span>
                              </div>
                              <div className="w-full bg-clinic-ice h-1.5 rounded-full overflow-hidden">
                                <div 
                                  className={`h-full rounded-full ${product.low_stock_alert ? 'bg-clinic-coral animate-pulse' : 'bg-clinic-emerald'}`}
                                  style={{ width: `${Math.min(percentStock, 100)}%` }}
                                />
                              </div>
                            </div>
                          </td>
                          <td className="py-4 px-3 text-xs">
                            {product.low_stock_alert ? (
                              <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-clinic-coral/10 text-clinic-coral font-bold rounded-lg uppercase tracking-wider text-[9px] animate-pulse">
                                <AlertTriangle className="w-3 h-3" />
                                КРИТИЧНО
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-clinic-emerald/10 text-clinic-emerald font-bold rounded-lg uppercase tracking-wider text-[9px]">
                                <CheckCircle className="w-3 h-3" />
                                ДОСТАТЪЧНО
                              </span>
                            )}
                          </td>
                          <td className="py-4 px-3 text-right">
                            <button 
                              onClick={() => handleOpenEditInventory(product)}
                              className="px-3.5 py-1.5 border border-clinic-accent/30 hover:bg-clinic-navy hover:text-white rounded-xl text-xs font-semibold text-clinic-navy transition-all duration-300"
                            >
                              РЕДАКЦИЯ
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </div>
      </main>

      {/* 7. Quantity Editor Modal */}
      {editingProduct && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-clinic-charcoal/60 backdrop-blur-sm animate-fadeIn">
          <div className="w-full max-w-md bg-white border border-clinic-accent/15 rounded-3xl p-8 shadow-2xl space-y-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-clinic-accent/5 rounded-bl-full pointer-events-none" />
            
            <div className="flex items-center justify-between pb-4 border-b border-clinic-ice">
              <div>
                <h3 className="text-lg font-bold text-clinic-navy">Корекция на склад</h3>
                <p className="text-[10px] font-bold text-clinic-accent uppercase tracking-wider mt-1">{editingProduct.brand} // {editingProduct.name}</p>
              </div>
              <button 
                onClick={handleCloseEditInventory}
                className="p-1.5 rounded-lg hover:bg-clinic-ice text-clinic-charcoal/50 hover:text-clinic-charcoal transition-all duration-200"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-6">
              {/* Quantity input with stepper */}
              <div className="space-y-2">
                <label className="text-xs font-bold tracking-wider text-clinic-navy/80 uppercase block">Наличност (Количество)</label>
                <div className="flex items-center gap-4">
                  <button 
                    onClick={() => setEditingQuantity(q => Math.max(q - 1, 0))}
                    className="w-12 h-12 rounded-xl bg-clinic-ice border border-clinic-accent/10 hover:border-clinic-accent flex items-center justify-center text-clinic-navy font-bold text-lg hover:bg-white transition-all duration-200"
                  >
                    <Minus className="w-4 h-4" />
                  </button>
                  <input 
                    type="number" 
                    value={editQuantity}
                    onChange={(e) => setEditingQuantity(Math.max(parseInt(e.target.value) || 0, 0))}
                    className="flex-1 h-12 text-center bg-clinic-ice border border-clinic-accent/10 rounded-xl focus:border-clinic-accent focus:bg-white outline-none transition-all duration-300 font-bold text-lg text-clinic-navy"
                  />
                  <button 
                    onClick={() => setEditingQuantity(q => q + 1)}
                    className="w-12 h-12 rounded-xl bg-clinic-ice border border-clinic-accent/10 hover:border-clinic-accent flex items-center justify-center text-clinic-navy font-bold text-lg hover:bg-white transition-all duration-200"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Max quantity input */}
              <div className="space-y-2">
                <label className="text-xs font-bold tracking-wider text-clinic-navy/80 uppercase block">Максимално Количество (Капацитет)</label>
                <input 
                  type="number" 
                  value={editMaxQuantity}
                  onChange={(e) => setEditingMaxQuantity(Math.max(parseInt(e.target.value) || 1, 1))}
                  className="w-full h-12 px-4 bg-clinic-ice border border-clinic-accent/10 rounded-xl focus:border-clinic-accent focus:bg-white outline-none transition-all duration-300 font-bold text-sm text-clinic-navy"
                />
              </div>

              <div className="flex items-center gap-4 pt-4">
                <button 
                  onClick={handleCloseEditInventory}
                  className="flex-1 py-3.5 border border-clinic-accent/20 text-clinic-charcoal hover:bg-clinic-ice font-bold rounded-xl text-xs uppercase tracking-wider transition-all duration-300"
                >
                  Отказ
                </button>
                <button 
                  onClick={handleSaveInventory}
                  disabled={savingInventory}
                  className="flex-1 py-3.5 bg-clinic-navy hover:bg-clinic-blue text-white font-bold rounded-xl text-xs uppercase tracking-wider hover:shadow-lg hover:shadow-clinic-navy/15 transition-all duration-300 flex items-center justify-center gap-2"
                >
                  {savingInventory ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      ЗАПИС...
                    </>
                  ) : (
                    'Запази'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
