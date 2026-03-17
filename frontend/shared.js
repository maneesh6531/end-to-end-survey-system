// shared.js — ALL pages import this. It handles:
// 1. JWT token storage after login
// 2. Adding Authorization header to every API call
// 3. Redirecting to login.html if token is missing or expired
// 4. Rendering the nav bar with the right links based on role

const API = window.location.origin === 'http://localhost:8000' || window.location.origin === 'http://127.0.0.1:8000' 
  ? '' // Same origin (FastAPI serves frontend)
  : "http://localhost:8000"; // Development override

// ── Token helpers ─────────────────────────────────────────────────────────────
function getToken() { return localStorage.getItem('sp_token'); }
function getRole()  { return localStorage.getItem('sp_role');  }
function getUser()  { return localStorage.getItem('sp_user');  }

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + getToken()
  };
}

// Call this at the top of every protected page.
function requireAuth() {
  if (!getToken()) { location.href = 'login.html'; return false; }
  return true;
}

function logout() {
  localStorage.removeItem('sp_token');
  localStorage.removeItem('sp_role');
  localStorage.removeItem('sp_user');
  location.href = 'login.html';
}

// ── Auth Logic ────────────────────────────────────────────────────────────────
async function doLogin(username, password, isAdmin = false) {
  if (!username || !password) { showToast('Enter username and password', 'error'); return; }

  const form = new URLSearchParams();
  form.append('username', username);
  form.append('password', password);
  if (isAdmin) form.append('admin', '1');

  try {
    const res = await fetch(API + '/login', { method: 'POST', body: form });
    const data = await res.json();
    if (!res.ok) { showToast(data.detail || 'Login failed', 'error'); return; }

    if (isAdmin && data.role !== 'admin') {
      showToast('Not an admin account', 'error');
      return;
    }

    localStorage.setItem('sp_token', data.access_token);
    localStorage.setItem('sp_role', data.role);
    localStorage.setItem('sp_user', username);

    showToast('Signed in! Redirecting…', 'success');
    setTimeout(() => location.href = 'index.html', 1000);
  } catch {
    showToast('Cannot connect to server', 'error');
  }
}

async function doSignup(username, email, password) {
  if (!username || !email || !password) { showToast('Fill all fields', 'error'); return; }
  if (password.length < 6) { showToast('Password must be at least 6 characters', 'error'); return; }

  try {
    const res = await fetch(API + '/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    });
    const data = await res.json();
    if (!res.ok) { showToast(data.detail || 'Signup failed', 'error'); return; }

    showToast('Account created! Please sign in.', 'success');
    return true; // success
  } catch {
    showToast('Cannot connect to server', 'error');
  }
}

// ── Nav builder ───────────────────────────────────────────────────────────────
function renderNav(activePage) {
  const isAdmin = getRole() === 'admin';
  const user    = getUser() || '';

  const pages = [
    { href: 'index.html',  label: 'Home' },
    { href: 'add.html',    label: 'Add',      adminOnly: true },
    { href: 'update.html', label: 'Update',   adminOnly: true },
    { href: 'delete.html', label: 'Delete',   adminOnly: true },
    { href: 'view.html',   label: 'View All' },
  ];

  const links = pages
    .filter(p => !p.adminOnly || isAdmin)
    .map(p => `<a href="${p.href}" class="${p.href === activePage ? 'active' : ''}">${p.label}</a>`)
    .join('');

  const badge = isAdmin
    ? `<span class="tag tag-indigo" style="font-size:10px">Admin</span>`
    : `<span class="tag tag-cyan"   style="font-size:10px">User</span>`;

  document.querySelector('nav').innerHTML = `
    <a class="nav-logo" href="index.html">
      <div class="nav-logo-icon">
        <svg viewBox="0 0 24 24" fill="none">
          <rect x="3" y="14" width="3" height="7" rx="1.2" fill="white"/>
          <rect x="8" y="9"  width="3" height="12" rx="1.2" fill="white" opacity="0.8"/>
          <rect x="13" y="5" width="3" height="16" rx="1.2" fill="white" opacity="0.6"/>
          <rect x="18" y="2" width="3" height="19" rx="1.2" fill="white" opacity="0.45"/>
        </svg>
      </div>
      <span class="nav-brand">SurveyPulse</span>
    </a>
    <div class="nav-links">${links}</div>
    <div style="display:flex;align-items:center;gap:8px;">
      ${badge}
      <span style="font-size:11.5px;color:var(--muted)">${user}</span>
      <button onclick="logout()" class="btn btn-ghost btn-sm" style="padding:5px 10px;">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>
        </svg>
        Logout
      </button>
    </div>
    <div class="nav-shine"></div>
  `;
}

// ── API calls — all include the JWT token in the header ───────────────────────
async function apiGet(path) {
  const res = await fetch(API + path, { headers: authHeaders() });
  if (res.status === 401) { logout(); return; }
  if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Request failed'); }
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(API + path, {
    method: 'POST', headers: authHeaders(), body: JSON.stringify(body)
  });
  if (res.status === 401) { logout(); return; }
  if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Request failed'); }
  return res.json();
}

async function apiPut(path, body) {
  const res = await fetch(API + path, {
    method: 'PUT', headers: authHeaders(), body: JSON.stringify(body)
  });
  if (res.status === 401) { logout(); return; }
  if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Request failed'); }
  return res.json();
}

async function apiDelete(path) {
  const res = await fetch(API + path, { method: 'DELETE', headers: authHeaders() });
  if (res.status === 401) { logout(); return; }
  if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Request failed'); }
  return res.json();
}

// ── Autocomplete data ─────────────────────────────────────────────────────────
const CITIES = [
  "Agra","Ahmedabad","Amritsar","Bangalore","Bhopal","Bhubaneswar","Chandigarh",
  "Chennai","Coimbatore","Dehradun","Delhi","Faridabad","Ghaziabad","Goa",
  "Gurgaon","Guwahati","Hyderabad","Indore","Jaipur","Jamshedpur","Jodhpur",
  "Kanpur","Kochi","Kolkata","Lucknow","Ludhiana","Madurai","Mangalore",
  "Mumbai","Mysore","Nagpur","Nashik","Noida","Patna","Pune","Raipur",
  "Rajkot","Ranchi","Surat","Thiruvananthapuram","Vadodara","Varanasi",
  "Vijayawada","Visakhapatnam","Bangkok","Barcelona","Beijing","Berlin",
  "Brussels","Buenos Aires","Cairo","Cape Town","Chicago","Dubai","Dublin",
  "Frankfurt","Hong Kong","Istanbul","Jakarta","Karachi","Kuala Lumpur",
  "Lagos","Lima","Lisbon","London","Los Angeles","Madrid","Manila",
  "Melbourne","Mexico City","Miami","Milan","Moscow","New York","Oslo",
  "Paris","Rome","San Francisco","Seoul","Shanghai","Singapore","Sydney",
  "Tokyo","Toronto","Vienna","Zurich"
];
const PROFESSIONS = [
  "Accountant","Actor","Architect","Artist","Banker","Business Analyst",
  "Chef","Civil Engineer","Consultant","Content Writer","Cybersecurity Analyst",
  "Data Scientist","Designer","DevOps Engineer","Doctor","Economist",
  "Educator","Electrical Engineer","Entrepreneur","Finance Manager",
  "Financial Analyst","Fitness Trainer","Full Stack Developer","Game Developer",
  "Graphic Designer","HR Manager","Interior Designer","Investment Banker",
  "Journalist","Lawyer","Machine Learning Engineer","Marketing Manager",
  "Mechanical Engineer","Mobile Developer","Nurse","Operations Manager",
  "Pharmacist","Photographer","Pilot","Product Manager","Project Manager",
  "Psychologist","Quality Analyst","Real Estate Agent","Researcher",
  "Sales Manager","Software Engineer","System Administrator","Teacher",
  "UI/UX Designer","Videographer","Web Developer","Writer"
];

function createAutocomplete(inputId, listId, data) {
  const inp = document.getElementById(inputId);
  const box = document.getElementById(listId);
  if (!inp || !box) return;
  let idx = -1;
  const hi = (t,q) => { const i=t.toLowerCase().indexOf(q.toLowerCase()); if(i<0)return t; return t.slice(0,i)+'<span class="match">'+t.slice(i,i+q.length)+'</span>'+t.slice(i+q.length); };
  const close = () => { box.innerHTML=''; box.classList.remove('open'); idx=-1; };
  const show  = q => {
    const hits=data.filter(d=>d.toLowerCase().includes(q.toLowerCase())).slice(0,8);
    if(!hits.length||!q.trim()){close();return;}
    idx=-1; box.innerHTML='';
    hits.forEach((item,i)=>{ const li=document.createElement('li'); li.innerHTML=hi(item,q); li.addEventListener('mousedown',e=>{e.preventDefault();inp.value=item;close();}); li.addEventListener('mouseover',()=>setIdx(i)); box.appendChild(li); });
    box.classList.add('open');
  };
  const setIdx = i => { const els=box.querySelectorAll('li'); els.forEach(l=>l.classList.remove('active')); if(i>=0&&i<els.length){els[i].classList.add('active');idx=i;} };
  inp.addEventListener('input',()=>show(inp.value));
  inp.addEventListener('blur', ()=>setTimeout(close,150));
  inp.addEventListener('keydown',e=>{ const els=box.querySelectorAll('li'); if(!els.length)return; if(e.key==='ArrowDown'){e.preventDefault();setIdx(Math.min(idx+1,els.length-1));} else if(e.key==='ArrowUp'){e.preventDefault();setIdx(Math.max(idx-1,0));} else if(e.key==='Enter'&&idx>=0){e.preventDefault();inp.value=els[idx].textContent;close();} else if(e.key==='Escape')close(); });
}

// ── Toast ─────────────────────────────────────────────────────────────────────
function showToast(msg, type='success') {
  let t=document.getElementById('toast');
  if(!t){t=document.createElement('div');t.id='toast';document.body.appendChild(t);}
  const icon={success:'✓',error:'✕',info:'ℹ'}[type]||'✓';
  t.className=type; t.id='toast';
  t.innerHTML=`<span>${icon}</span><span>${msg}</span>`;
  t.classList.add('show');
  clearTimeout(t._t); t._t=setTimeout(()=>t.classList.remove('show'),3000);
}

// ── Progress bar ──────────────────────────────────────────────────────────────
function initProgress(ids) {
  const fill=document.getElementById('pFill'), pct=document.getElementById('pPct');
  if(!fill||!pct) return;
  const upd=()=>{ const n=ids.filter(id=>{const el=document.getElementById(id);return el&&el.value.trim()!='';}).length; const p=Math.round(n/ids.length*100); fill.style.width=p+'%'; pct.textContent=p+'%'; };
  ids.forEach(id=>{const el=document.getElementById(id);if(el)el.addEventListener('input',upd);});
  upd();
}
