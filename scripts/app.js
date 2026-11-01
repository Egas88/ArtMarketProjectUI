let users = {
  test: {
    password: '1111',
    name: 'Test User',
    resumes: [
      { id: 1, nickname: 'Терракотовый сад', realName: 'Мария Савельева', photos: 3, about: 'Занимаюсь ручной лепкой из глины уже более 5 лет.' },
      { id: 2, nickname: 'Для керамики', realName: 'Мария Савельева', photos: 5, about: 'Специализация на посуде и декоре.' }
    ]
  }
};
let currentUser = null;
let currentResumes = [];
let favorites = [];
let myApplications = [
  { id: 'art-dvor', status: 'participating', resumeId: 1 },
  { id: 'tsvetochny', status: 'pending', resumeId: 1 },
  { id: 'vesna', status: 'rejected', resumeId: 2 }
];
const markets = [
  { id: 'art-dvor', title: 'Маркет «Арт-Двор»', meta: '📅 8 июня, 12:00–22:00 · Санкт-Петербург', image: 'Арт-двор' },
  { id: 'tsvetochny', title: 'Маркет «Цветочный»', meta: '📅 25–26 мая, 12:00–21:00 · Санкт-Петербург', image: 'Цветочный рынок' },
  { id: 'vesna', title: 'Ярмарка «Весна»', meta: '📅 1–2 июня, 11:00–20:00 · Санкт-Петербург', image: 'Ярмарка одежды' }
];

const statusLabels = {
  participating: 'Вы участвуете',
  pending: 'Заявка на рассмотрении',
  rejected: 'Ваше участие отклонено'
};

const navByScreen = {
  main: 'main',
  favorites: 'favorites',
  cabinet: 'cabinet',
  resume: 'cabinet',
  settings: 'cabinet',
  'my-events': 'cabinet'
};

function showError(id, msg) {
  const el = document.getElementById(id);
  el.textContent = msg;
  el.classList.add('form__error_visible');
  setTimeout(() => el.classList.remove('form__error_visible'), 3000);
}

function doLogin() {
  const name = document.getElementById('loginName').value.trim();
  const pass = document.getElementById('loginPass').value;
  if (users[name] && users[name].password === pass) {
    currentUser = name;
    currentResumes = users[name].resumes || [];
    const displayName = currentResumes[0] ? currentResumes[0].nickname : (name === 'test' ? 'Test User' : name);
    document.getElementById('cabinetName').textContent = displayName;
    goTo('cabinet');
  } else {
    showError('loginError', 'Неверное имя или пароль');
  }
}

function doRegister() {
  const name = document.getElementById('regName').value.trim();
  const pass = document.getElementById('regPass').value;
  const pass2 = document.getElementById('regPass2').value;
  if (!name || name.length < 3) return showError('regError', 'Имя должно быть от 3 символов');
  if (pass.length < 4) return showError('regError', 'Пароль минимум 4 символа');
  if (pass !== pass2) return showError('regError', 'Пароли не совпадают');
  if (users[name]) return showError('regError', 'Такой пользователь уже существует');
  users[name] = { password: pass, name: name, resumes: [] };
  currentUser = name;
  currentResumes = [];
  document.getElementById('cabinetName').textContent = name;
  goTo('cabinet');
}

function logout() {
  currentUser = null;
  currentResumes = [];
  favorites = [];
  goTo('splash');
}

function goToProtected(id) {
  if (!currentUser) {
    goTo('auth-required');
    return;
  }
  if (id === 'favorites') renderFavorites();
  if (id === 'my-events') renderMyEvents();
  goTo(id);
}

function createMarketCard(market, status) {
  const card = document.createElement('div');
  card.className = 'event-card';
  card.dataset.goto = 'detail';

  const state = status ? (statusLabels[status] ? status : 'pending') : '';
  const statusMarkup = state
    ? `<div class="event-card__status event-card__status_state_${state}">${statusLabels[state]}</div>`
    : '';

  card.innerHTML = `
    <div class="event-card__image">${market.image}</div>
    <div class="event-card__body">
      <h3 class="event-card__title">${market.title}</h3>
      <div class="event-card__meta">${market.meta}</div>
      ${statusMarkup}
    </div>
  `;

  return card;
}

function renderMyEvents() {
  const list = document.getElementById('myEventsList');
  const empty = document.getElementById('myEventsEmpty');
  list.innerHTML = '';
  empty.classList.toggle('empty-state_hidden', myApplications.length > 0);
  if (myApplications.length === 0) return;

  myApplications.forEach((app) => {
    const market = markets.find((item) => item.id === app.id);
    if (!market) return;
    list.appendChild(createMarketCard(market, app.status));
  });
}

function tryParticipate() {
  if (!currentUser) {
    goTo('auth-required');
    return;
  }
  if (!currentResumes || currentResumes.length === 0) {
    alert('У вас нет резюме. Создайте его в кабинете.');
    goTo('resume');
    return;
  }
  renderApplyResumes();
  goTo('apply');
}

function saveResume() {
  const nickname = document.getElementById('resumeNickname').value || 'Новый бренд';
  if (!currentResumes.length) {
    currentResumes.push({ id: Date.now(), nickname: nickname, realName: 'Пользователь', photos: 0, about: '' });
  } else {
    currentResumes[0].nickname = nickname;
  }
  users[currentUser].resumes = currentResumes;
  document.getElementById('cabinetName').textContent = nickname;
  goTo('cabinet');
}

function renderApplyResumes() {
  const container = document.getElementById('resumeSelect');
  if (!container) return;
  container.innerHTML = '';
  currentResumes.forEach((resume, index) => {
    const item = document.createElement('button');
    item.type = 'button';
    item.className = 'menu__item' + (index === 0 ? ' menu__item_selected' : '');
    item.innerHTML = `
      <span class="menu__content">
        <span class="menu__label">● ${resume.nickname}</span>
        <span class="menu__note">${resume.realName} · ${resume.photos} фото товаров</span>
      </span>
    `;
    item.addEventListener('click', () => {
      container.querySelectorAll('.menu__item').forEach((el) => el.classList.remove('menu__item_selected'));
      item.classList.add('menu__item_selected');
    });
    container.appendChild(item);
  });
}

function toggleFavorite() {
  if (!currentUser) {
    goTo('auth-required');
    return;
  }
  const marketId = 'art-dvor';
  const index = favorites.indexOf(marketId);
  const button = document.getElementById('favBtn');
  if (index === -1) {
    favorites.push(marketId);
    button.textContent = '♥ В избранном';
    button.classList.add('button_active');
  } else {
    favorites.splice(index, 1);
    button.textContent = '♡ В избранное';
    button.classList.remove('button_active');
  }
}

function renderFavorites() {
  const list = document.getElementById('favoritesList');
  const empty = document.getElementById('favoritesEmpty');
  list.innerHTML = '';
  empty.classList.toggle('empty-state_hidden', favorites.length > 0);
  if (favorites.length === 0) return;

  favorites.forEach((id) => {
    const market = markets.find((item) => item.id === id) || markets[0];
    list.appendChild(createMarketCard(market));
  });
}

function updateNavigation(screenId) {
  const activeNav = navByScreen[screenId];
  document.querySelectorAll('.bottom-nav__item').forEach((item) => {
    item.classList.toggle('bottom-nav__item_active', item.dataset.nav === activeNav);
  });
}

function goTo(id) {
  document.querySelectorAll('.screen').forEach((screen) => screen.classList.remove('screen_active'));
  document.getElementById(id).classList.add('screen_active');
  updateNavigation(id);

  if (id === 'detail') {
    const button = document.getElementById('favBtn');
    const isFavorite = favorites.includes('art-dvor');
    button.textContent = isFavorite ? '♥ В избранном' : '♡ В избранное';
    button.classList.toggle('button_active', isFavorite);
  }
}

document.getElementById('loginForm').addEventListener('submit', (event) => {
  event.preventDefault();
  doLogin();
});

document.getElementById('registerForm').addEventListener('submit', (event) => {
  event.preventDefault();
  doRegister();
});

['resumeForm', 'applyForm'].forEach((id) => {
  document.getElementById(id).addEventListener('submit', (event) => event.preventDefault());
});

document.addEventListener('click', (event) => {
  const protectedTrigger = event.target.closest('[data-goto-protected]');
  if (protectedTrigger) {
    goToProtected(protectedTrigger.dataset.gotoProtected);
    return;
  }

  const actionTrigger = event.target.closest('[data-action]');
  if (actionTrigger) {
    const action = actionTrigger.dataset.action;
    if (action === 'logout') logout();
    if (action === 'participate') tryParticipate();
    if (action === 'toggle-favorite') toggleFavorite();
    if (action === 'save-resume') saveResume();
    return;
  }

  const gotoTrigger = event.target.closest('[data-goto]');
  if (gotoTrigger) goTo(gotoTrigger.dataset.goto);
});
