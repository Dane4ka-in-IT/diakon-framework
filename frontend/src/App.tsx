import { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { Play, RotateCcw, LogOut, Zap, X, AlertCircle, CheckCircle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import './index.css';

interface TrainingConfig {
  dataset: string;
  epochs: number;
  learning_rate: number;
  layers: number[];
  optimizer: string;
}

interface TaskResponse {
  id: number;
  datasetName: string;
  optimizer: string;
  status: string;
  learningRate: number;
  epochs: number;
  lossHistory: string | null;
}

interface UserData {
  id: number;
  userName: string;
  userEmail: string;
  isPremium: boolean;
}

interface PredictResult {
  predicted_class: number;
  class_name: string;
  probabilities: number[];
  error?: string;
}

interface Notification {
  id: number;
  message: string;
  type: 'error' | 'success';
  hiding?: boolean;
}

const API = '/api';

const IRIS_LABELS = ['Sepal Length', 'Sepal Width', 'Petal Length', 'Petal Width'];
const CLASS_NAMES: Record<string, string[]> = {
  iris: ['Setosa', 'Versicolor', 'Virginica'],
  mnist: ['0','1','2','3','4','5','6','7','8','9'],
};

const getErrorMessage = (err: any): string => {
  if (err.response?.data?.message) return err.response.data.message;
  if (err.response?.data && typeof err.response.data === 'string') return err.response.data;
  return err.message || 'Произошла ошибка';
};

function Toast({ notifications, remove }: { notifications: Notification[], remove: (id: number) => void }) {
  return (
    <div className="toast-container">
      {notifications.map(n => (
        <div key={n.id} className={`toast ${n.type} ${n.hiding ? 'hiding' : ''}`}>
          {n.type === 'error' ? <AlertCircle size={18} color="var(--red)" /> : <CheckCircle size={18} color="var(--green)" />}
          <div className="toast-content">{n.message}</div>
          <div className="toast-close" onClick={() => remove(n.id)}><X size={14} /></div>
        </div>
      ))}
    </div>
  );
}

function LoginPage({ onLogin, notify }: { onLogin: (user: UserData) => void, notify: (msg: string, type: 'error' | 'success') => void }) {
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isRegister) {
        await axios.post(`${API}/users/register`, { userName: name, userEmail: email, userPassword: password });
        setIsRegister(false);
        setError('');
        notify('Аккаунт создан! Теперь войдите.', 'success');
      } else {
        const res = await axios.post(`${API}/users/login`, { email, password });
        onLogin(res.data);
      }
    } catch (err: any) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <h1>DIAKON-FRAMEWORK</h1>
        <div className="subtitle">{isRegister ? 'Создание аккаунта' : 'Вход в платформу'}</div>
        
        <div className={`error-container ${error ? 'visible' : ''}`}>
          <div className="error-msg">{error}</div>
        </div>

        <form onSubmit={handleSubmit}>
          {isRegister && (
            <div className="input-group">
              <label>Имя</label>
              <input type="text" value={name} onChange={e => setName(e.target.value)} required />
            </div>
          )}
          <div className="input-group">
            <label>Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
          </div>
          <div className="input-group">
            <label>Пароль</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
          </div>
          <button className="btn btn-primary btn-full" type="submit" disabled={loading}>
            {loading ? '...' : (isRegister ? 'Зарегистрироваться' : 'Войти')}
          </button>
        </form>
        <span className="toggle-link" onClick={() => { setIsRegister(!isRegister); setError(''); }}>
          {isRegister ? 'Уже есть аккаунт? Войти' : 'Нет аккаунта? Создать'}
        </span>
      </div>
    </div>
  );
}

function DigitGrid({ pixels, setPixels }: { pixels: number[]; setPixels: (p: number[]) => void }) {
  const [isDrawing, setIsDrawing] = useState(false);

  const toggle = (idx: number) => {
    const next = [...pixels];
    next[idx] = next[idx] > 0 ? 0 : 16;
    setPixels(next);
  };

  const paint = (idx: number) => {
    if (!isDrawing) return;
    const next = [...pixels];
    next[idx] = 16;
    setPixels(next);
  };

  return (
    <div>
      <div
        className="digit-grid"
        onMouseDown={() => setIsDrawing(true)}
        onMouseUp={() => setIsDrawing(false)}
        onMouseLeave={() => setIsDrawing(false)}
      >
        {pixels.map((val, idx) => (
          <div
            key={idx}
            className={`digit-cell ${val > 0 ? 'filled' : ''}`}
            onMouseDown={() => toggle(idx)}
            onMouseEnter={() => paint(idx)}
          />
        ))}
      </div>
      <button className="btn btn-secondary btn-full" style={{marginTop: '0.5rem'}}
        onClick={() => setPixels(Array(64).fill(0))}>Очистить</button>
    </div>
  );
}

function ProbBars({ probabilities, dataset }: { probabilities: number[]; dataset: string }) {
  const names = CLASS_NAMES[dataset] || probabilities.map((_, i) => String(i));
  const maxP = Math.max(...probabilities, 0.01);
  return (
    <div className="prob-bar-container">
      {probabilities.map((p, i) => (
        <div key={i} className="prob-bar-row">
          <span className="prob-bar-label">{names[i] || i}</span>
          <div className="prob-bar-track">
            <div className="prob-bar-fill" style={{width: `${(p / maxP) * 100}%`}} />
          </div>
          <span className="prob-bar-value">{(p * 100).toFixed(1)}%</span>
        </div>
      ))}
    </div>
  );
}

function Dashboard({ user, onLogout, notify }: { user: UserData; onLogout: () => void, notify: (msg: string, type: 'error' | 'success') => void }) {
  const [config, setConfig] = useState<TrainingConfig>({
    dataset: 'iris', epochs: 10, learning_rate: 0.01, layers: [10, 5], optimizer: 'SGD'
  });
  const [hiddenLayers, setHiddenLayers] = useState(2);
  const [neuronsPerLayer, setNeuronsPerLayer] = useState(5);
  const [isRunning, setIsRunning] = useState(false);
  const [tasksHistory, setTasksHistory] = useState<TaskResponse[]>([]);
  const [lossData, setLossData] = useState<any[]>([]);
  const [taskStatus, setTaskStatus] = useState('idle');
  const [lastLoss, setLastLoss] = useState(0);

  const [irisInputs, setIrisInputs] = useState([5.1, 3.5, 1.4, 0.2]);
  const [mnistPixels, setMnistPixels] = useState<number[]>(Array(64).fill(0));
  const [predictResult, setPredictResult] = useState<PredictResult | null>(null);
  const [predicting, setPredicting] = useState(false);

  const activeTaskRef = useRef<number | null>(null);

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API}/tasks/user/${user.id}`);
      setTasksHistory(res.data.reverse());
    } catch (e) { console.error(e); }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  useEffect(() => {
    setConfig(c => ({...c, layers: Array(hiddenLayers).fill(neuronsPerLayer)}));
  }, [hiddenLayers, neuronsPerLayer]);

  const parseHistory = (s: string | null) => {
    if (!s) return [];
    try { return (JSON.parse(s) as number[]).map((v, i) => ({epoch: i+1, loss: v})); }
    catch { return []; }
  };

  const handleStart = async () => {
    setIsRunning(true); setLossData([]); setLastLoss(0); setTaskStatus('STARTING...');
    try {
      const res = await axios.post(`${API}/tasks/start?userId=${user.id}`, config);
      activeTaskRef.current = res.data.id;
      pollStatus(res.data.id);
      fetchHistory();
    } catch (e: any) {
      notify(getErrorMessage(e), 'error');
      setIsRunning(false); setTaskStatus('FAILED');
    }
  };

  const pollStatus = (taskId: number) => {
    const iv = setInterval(async () => {
      try {
        const res = await axios.get(`${API}/tasks/${taskId}`);
        const t: TaskResponse = res.data;
        setTaskStatus(t.status);
        if (t.status === 'COMPLETED' || t.status === 'FAILED') {
          clearInterval(iv); setIsRunning(false); activeTaskRef.current = null; fetchHistory();
          if (t.lossHistory) {
            const d = parseHistory(t.lossHistory);
            setLossData(d);
            if (d.length) setLastLoss(d[d.length-1].loss);
          }
          if (t.status === 'COMPLETED') notify('Обучение завершено успешно!', 'success');
          if (t.status === 'FAILED') notify('Задача завершилась с ошибкой на сервере.', 'error');
        }
      } catch { clearInterval(iv); setIsRunning(false); }
    }, 1000);
  };

  const loadItem = (t: TaskResponse) => {
    if (t.status !== 'COMPLETED') return;
    const d = parseHistory(t.lossHistory);
    setLossData(d); setTaskStatus(`Task #${t.id}`);
    if (d.length) setLastLoss(d[d.length-1].loss);
  };

  const handlePredict = async () => {
    setPredicting(true); setPredictResult(null);
    const features = config.dataset === 'mnist' ? mnistPixels.map(v => Number(v)) : irisInputs;
    try {
      const res = await axios.post(`${API}/tasks/predict`, { features, dataset: config.dataset });
      setPredictResult(res.data);
    } catch (e: any) {
      notify(getErrorMessage(e), 'error');
    } finally { setPredicting(false); }
  };

  const dims = config.dataset === 'mnist' ? {in: 64, out: 10} : config.dataset === 'iris' ? {in: 4, out: 3} : {in: 10, out: 2};
  const structure = [dims.in, ...config.layers, dims.out];
  const topologyStr = structure.map((n, i) => {
    if (i === 0) return `In(${n})`;
    if (i === structure.length - 1) return `Out(${n})`;
    return `Hidden(${n})`;
  }).join(' ➔ ');

  return (
    <div className="app-layout">
      <header className="top-header">
        <div className="logo-text">DIAKON-FRAMEWORK</div>
        <div className="user-badge">
          <span className="name">{user.userName}</span>
          {user.isPremium && <span style={{color: 'var(--accent-cyan)', fontSize: '0.7rem'}}>★ PRO</span>}
          <span className="logout" onClick={onLogout}><LogOut size={14}/></span>
        </div>
      </header>

      <div className="controls-bar">
        <div className="control-group">
          <label>Набор данных</label>
          <select value={config.dataset} onChange={e => setConfig({...config, dataset: e.target.value})}
            style={{background: 'rgba(10,15,37,0.6)', border: '1px solid var(--border-subtle)', color: 'var(--text-main)', padding: '0.45rem 0.6rem', borderRadius: '8px', fontFamily: 'Outfit, sans-serif', fontSize: '0.82rem'}}>
            <option value="iris">Iris</option>
            <option value="mnist">MNIST (Digits 8x8)</option>
            <option value="custom">Custom</option>
          </select>
        </div>

        <div className="control-group">
          <label>Скрытые слои: {hiddenLayers}</label>
          <input type="range" min="1" max="5" value={hiddenLayers} onChange={e => setHiddenLayers(+e.target.value)} />
        </div>

        <div className="control-group">
          <label>Нейроны/слой: {neuronsPerLayer}</label>
          <input type="range" min="2" max="15" value={neuronsPerLayer} onChange={e => setNeuronsPerLayer(+e.target.value)} />
        </div>

        <div className="control-group">
          <label>Оптимизатор</label>
          <select value={config.optimizer} onChange={e => setConfig({...config, optimizer: e.target.value})}
            style={{background: 'rgba(10,15,37,0.6)', border: '1px solid var(--border-subtle)', color: 'var(--text-main)', padding: '0.45rem 0.6rem', borderRadius: '8px', fontFamily: 'Outfit, sans-serif', fontSize: '0.82rem'}}>
            <option value="SGD">SGD</option>
            <option value="Momentum">Momentum</option>
            <option value="Clipping">Grad Clipping</option>
          </select>
        </div>

        <div className="control-group">
          <label>Learning Rate: {config.learning_rate}</label>
          <input type="range" min="0.001" max="0.1" step="0.001" value={config.learning_rate}
            onChange={e => setConfig({...config, learning_rate: +e.target.value})} />
        </div>

        <div className="control-group" style={{minWidth: '80px'}}>
          <label>Эпохи</label>
          <input type="number" value={config.epochs} onChange={e => setConfig({...config, epochs: +e.target.value})}
            style={{background: 'rgba(10,15,37,0.6)', border: '1px solid var(--border-subtle)', color: 'var(--text-main)', padding: '0.45rem 0.6rem', borderRadius: '8px', fontFamily: 'Outfit, sans-serif', fontSize: '0.82rem', width: '80px'}} />
        </div>

        <div className="start-btn-wrapper">
          <button className="btn btn-primary" onClick={handleStart} disabled={isRunning}>
            <Play size={15}/> {isRunning ? 'Обучаем...' : 'СТАРТ'}
          </button>
          <button className="btn btn-secondary" onClick={() => setLossData([])} disabled={isRunning}>
            <RotateCcw size={15}/>
          </button>
        </div>

        <div className="topology-badge">
          <span style={{opacity: 0.6, fontSize: '0.7rem'}}>Топология:</span> {topologyStr}
        </div>
      </div>

      <div className="main-grid">
        <div className="glass-panel" style={{display: 'flex', flexDirection: 'column'}}>
          <div className="panel-title">Динамика ошибки</div>

          <div className="stats-row">
            <div className="stat-card">
              <span className="stat-value">{lossData.length || '—'}</span>
              <span className="stat-label">Эпохи</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">{lastLoss ? lastLoss.toFixed(4) : '—'}</span>
              <span className="stat-label">Loss</span>
            </div>
            <div className="stat-card">
              <span className="stat-value" style={{fontSize: '0.9rem', color: taskStatus === 'COMPLETED' ? 'var(--green)' : taskStatus === 'FAILED' ? 'var(--red)' : 'var(--accent-cyan)'}}>{taskStatus}</span>
              <span className="stat-label">Статус</span>
            </div>
          </div>

          <div className="chart-area" style={{flex: 1, minHeight: '200px'}}>
            {lossData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={lossData}>
                  <XAxis dataKey="epoch" stroke="#6b7fa3" fontSize={11} tickLine={false} axisLine={false}/>
                  <YAxis stroke="#6b7fa3" fontSize={11} tickLine={false} axisLine={false}/>
                  <Tooltip contentStyle={{backgroundColor:'rgba(13,27,42,0.95)', border:'1px solid rgba(0,240,255,0.2)', borderRadius:'8px', color:'#e0eaff', backdropFilter:'blur(8px)'}}/>
                  <Line type="monotone" dataKey="loss" stroke="#00f0ff" strokeWidth={2} dot={false} style={{filter: 'drop-shadow(0 0 4px rgba(0,240,255,0.5))'}}/>
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="empty-state">
                {isRunning ? <span className="loading">Ожидание данных...</span> : 'Нажмите «СТАРТ» для обучения'}
              </div>
            )}
          </div>
        </div>

        <div style={{display: 'flex', flexDirection: 'column', gap: '1rem'}}>
          <div className="glass-panel" style={{flex: 1}}>
            <div className="panel-title"><Zap size={13}/> Модуль предсказаний</div>
            {config.dataset === 'custom' ? (
              <div style={{color:'var(--text-muted)', fontSize:'0.85rem'}}>Предсказание недоступно для Custom датасета</div>
            ) : (
              <div className="predict-section">
                <div className="predict-inputs">
                  {config.dataset === 'iris' && (
                    <>
                      {IRIS_LABELS.map((label, i) => (
                        <div key={i} className="input-group" style={{marginBottom:'0.4rem'}}>
                          <label>{label}</label>
                          <input type="number" step="0.1" value={irisInputs[i]}
                            onChange={e => { const n = [...irisInputs]; n[i] = +e.target.value; setIrisInputs(n); }}/>
                        </div>
                      ))}
                    </>
                  )}
                  {config.dataset === 'mnist' && <DigitGrid pixels={mnistPixels} setPixels={setMnistPixels}/>}
                  <button className="btn btn-cyan btn-full" onClick={handlePredict} disabled={predicting}
                    style={{marginTop:'0.5rem'}}>
                    <Zap size={14}/> {predicting ? 'Считаем...' : 'Предсказать'}
                  </button>
                </div>
                <div className="predict-result">
                  {predictResult?.error && (
                    <div className="error-msg" style={{marginBottom:'1rem'}}>{predictResult.error}</div>
                  )}
                  {predictResult && !predictResult.error && (
                    <>
                      <div className="result-class">{predictResult.class_name}</div>
                      <ProbBars probabilities={predictResult.probabilities} dataset={config.dataset}/>
                    </>
                  )}
                  {!predictResult && (
                    <div style={{color:'var(--text-muted)', textAlign:'center', padding:'2rem 0', fontSize:'0.85rem', fontWeight: 300}}>
                      Сначала обучите модель, затем нажмите «Предсказать»
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="glass-panel">
            <div className="panel-title">Журнал экспериментов</div>
            <div className="history-list">
              {tasksHistory.map(t => (
                <div key={t.id} className="history-item" onClick={() => loadItem(t)}>
                  <span>#{t.id} {t.datasetName}</span>
                  <span style={{color: t.status==='COMPLETED' ? 'var(--green)' : t.status==='FAILED' ? 'var(--red)' : 'var(--accent-cyan)', fontWeight: 500}}>
                    {t.status}
                  </span>
                </div>
              ))}
              {tasksHistory.length === 0 && <div style={{color:'var(--text-muted)', fontSize:'0.75rem', fontWeight: 300}}>Пока пусто</div>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [user, setUser] = useState<UserData | null>(() => {
    const saved = localStorage.getItem('nocode_user');
    return saved ? JSON.parse(saved) : null;
  });

  const [notifications, setNotifications] = useState<Notification[]>([]);

  const notify = useCallback((message: string, type: 'error' | 'success') => {
    const id = Date.now();
    setNotifications(prev => [...prev, { id, message, type }]);
    
    // Auto-hide after 5s
    setTimeout(() => {
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, hiding: true } : n));
      setTimeout(() => {
        setNotifications(prev => prev.filter(n => n.id !== id));
      }, 300);
    }, 5000);
  }, []);

  const removeNotification = useCallback((id: number) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  const handleLogin = (u: UserData) => {
    setUser(u);
    localStorage.setItem('nocode_user', JSON.stringify(u));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('nocode_user');
  };

  return (
    <>
      <Toast notifications={notifications} remove={removeNotification} />
      {!user ? (
        <LoginPage onLogin={handleLogin} notify={notify} />
      ) : (
        <Dashboard user={user} onLogout={handleLogout} notify={notify} />
      )}
    </>
  );
}
