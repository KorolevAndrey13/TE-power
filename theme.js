// Блокирующая установка темы делается инлайн-скриптом в <head> каждой страницы (до отрисовки),
// чтобы избежать мигания. Этот файл обрабатывает клики по кнопкам.

function toggleTheme(){
  var current = document.documentElement.getAttribute('data-theme') || 'light';
  var next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  try{ localStorage.setItem('tepower-theme', next); }catch(e){}
}

function toggleMobileNav(){
  var nav = document.getElementById('primary-nav');
  if(nav) nav.classList.toggle('header__nav--open');
}

function openCallbackModal(){
  var modal = document.getElementById('callback-modal');
  if(modal) modal.classList.add('callback-modal--open');
  document.body.style.overflow = 'hidden';
}
function closeCallbackModal(){
  var modal = document.getElementById('callback-modal');
  if(modal) modal.classList.remove('callback-modal--open');
  document.body.style.overflow = '';
}
// Заявки («Заказать звонок», форма в «Контактах», корзина) уходят на сервер — send.php рядом с theme.js,
// он пересылает их письмом в отдел продаж. После отправки — всплывающее «Ваша заявка отправлена».
// Если сервер недоступен (например, на GitHub Pages нет PHP) — ссылка, чтобы отправить заявку письмом.
var SEND_URL = (function(){
  var s = document.currentScript;
  return s && s.src ? s.src.replace(/theme\.js(\?.*)?$/, 'send.php') : 'send.php';
})();
var SALES_EMAIL = 'russia@te-power.ru';
function sendForm(form, payload, title, lines, onDone){
  var btn = form.querySelector('button[type="submit"]');
  var label = btn.textContent;
  var errorEl = form.querySelector('.form__error');
  if(errorEl) errorEl.hidden = true;
  btn.disabled = true;
  btn.textContent = 'Отправляем…';
  payload._honey = form._honey ? form._honey.value : '';
  payload.consent = !!(form.consent && form.consent.checked);  // галочка согласия на обработку персональных данных
  payload.page = window.location.href;
  fetch(SEND_URL, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)})
    .then(function(r){
      return r.json().catch(function(){ return {}; }).then(function(data){
        if(!r.ok || !data.ok) throw new Error(data.error || '');
      });
    })
    .then(function(){
      form.reset();
      onDone();
      showDoneModal();
    })
    .catch(function(err){
      if(!errorEl) return;
      errorEl.innerHTML = '';
      errorEl.appendChild(document.createTextNode((err.message || 'Не удалось отправить заявку.') + ' Можно '));
      var a = document.createElement('a');
      a.href = 'mailto:' + SALES_EMAIL + '?subject=' + encodeURIComponent(title) +
        '&body=' + encodeURIComponent(lines.concat(['Страница - ' + window.location.href]).join('\n'));
      a.className = 'text-link';
      a.textContent = 'отправить её письмом';
      errorEl.appendChild(a);
      errorEl.appendChild(document.createTextNode('.'));
      errorEl.hidden = false;
    })
    .then(function(){
      btn.disabled = false;
      btn.textContent = label;
    });
}

// Окно «Ваша заявка оформлена» — по центру на затемнённом фоне, как окно заявки, только меньше
function showDoneModal(){
  var m = document.getElementById('done-modal');
  if(!m){
    m = document.createElement('div');
    m.id = 'done-modal';
    m.className = 'callback-modal done-modal';
    m.setAttribute('role', 'dialog');
    m.setAttribute('aria-modal', 'true');
    m.setAttribute('aria-labelledby', 'done-modal-title');
    m.innerHTML =
      '<div class="callback-modal__overlay" data-close></div>' +
      '<div class="callback-modal__panel done-modal__panel">' +
        '<div class="done-modal__icon"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg></div>' +
        '<h3 class="callback-modal__title" id="done-modal-title">Ваша заявка оформлена</h3>' +
        '<p class="callback-modal__note">С вами скоро свяжется менеджер.</p>' +
        '<button type="button" class="btn btn--accent callback-modal__submit" data-close>Хорошо</button>' +
      '</div>';
    m.addEventListener('click', function(e){ if(e.target.closest('[data-close]')) closeDoneModal(); });
    document.body.appendChild(m);
  }
  m.classList.add('callback-modal--open');
  document.body.style.overflow = 'hidden';
  m.querySelector('button').focus();
}
function closeDoneModal(){
  var m = document.getElementById('done-modal');
  if(m) m.classList.remove('callback-modal--open');
  document.body.style.overflow = '';
}

function submitCallback(e){
  e.preventDefault();
  var f = e.target;
  var name = f.name.value.trim(), phone = f.phone.value.trim();
  sendForm(f, {type: 'callback', name: name, phone: phone}, 'Заказ звонка с сайта TE-POWER',
    ['Имя - ' + name, 'Телефон - ' + phone], closeCallbackModal);
  return false;
}

// Форма на странице «Контакты»
function submitContact(e){
  e.preventDefault();
  var f = e.target;
  var v = {name: f.name.value.trim(), company: f.company.value.trim(), email: f.email.value.trim(),
           phone: f.phone.value.trim(), comment: f.comment.value.trim()};
  sendForm(f, {type: 'contact', name: v.name, company: v.company, email: v.email, phone: v.phone, comment: v.comment},
    'Заявка с сайта TE-POWER',
    ['Имя - ' + v.name, 'Компания - ' + v.company, 'E-mail - ' + v.email, 'Телефон - ' + v.phone, 'Комментарий - ' + (v.comment || '—')],
    function(){});
  return false;
}

function initCarousels(){
  document.querySelectorAll('.carousel').forEach(function(carousel){
    var track = carousel.querySelector('.carousel__track');
    var slides = Array.prototype.slice.call(carousel.querySelectorAll('.carousel__slide'));
    var dots = carousel.querySelectorAll('.carousel__dot');
    var prevBtn = carousel.querySelector('.carousel__arrow--prev');
    var nextBtn = carousel.querySelector('.carousel__arrow--next');
    var n = slides.length;
    if(n === 0) return;

    // Для бесшовной прокрутки по кругу дублируем первый слайд в конец,
    // а последний — в начало: после последнего сразу едет первый
    // (визуально та же анимация), а не прыгает назад к началу дорожки.
    var loop = n > 1;
    if(loop){
      var firstClone = slides[0].cloneNode(true);
      var lastClone = slides[n - 1].cloneNode(true);
      firstClone.setAttribute('aria-hidden', 'true');
      lastClone.setAttribute('aria-hidden', 'true');
      track.appendChild(firstClone);
      track.insertBefore(lastClone, slides[0]);
    }

    var pos = loop ? 1 : 0; // позиция в дорожке (с учётом клона-заглушки в начале)
    var animating = false;

    function place(pos, withTransition){
      track.style.transition = withTransition ? '' : 'none';
      track.style.transform = 'translateX(-' + (pos * 100) + '%)';
    }

    function updateDots(){
      var real = loop ? (((pos - 1) % n) + n) % n : pos;
      dots.forEach(function(d, i){ d.classList.toggle('carousel__dot--active', i === real); });
    }

    function goTo(newPos){
      if(animating || newPos === pos) return;
      animating = true;
      pos = newPos;
      place(pos, true);
      updateDots();
    }

    track.addEventListener('transitionend', function(e){
      if(e.target !== track) return;
      animating = false;
      if(!loop) return;
      if(pos === n + 1){
        pos = 1;
        place(pos, false);
      } else if(pos === 0){
        pos = n;
        place(pos, false);
      }
    });

    function go(delta){
      goTo(pos + delta);
    }

    if(prevBtn) prevBtn.addEventListener('click', function(){ go(-1); resetAutoplay(); });
    if(nextBtn) nextBtn.addEventListener('click', function(){ go(1); resetAutoplay(); });
    dots.forEach(function(d, i){
      d.addEventListener('click', function(){ goTo(loop ? i + 1 : i); resetAutoplay(); });
    });

    place(pos, false);
    updateDots();

    var autoplayTimer = null;
    function startAutoplay(){
      if(n > 1) autoplayTimer = setInterval(function(){ go(1); }, 30000);
    }
    function resetAutoplay(){
      if(autoplayTimer) clearInterval(autoplayTimer);
      startAutoplay();
    }
    startAutoplay();
  });
}
// Новости всегда от новых к старым: сортируем по дате (ДД.ММ.ГГГГ) список на novosti.html
// и новостные слайды карусели на главной (до запуска карусели, чтобы клоны слайдов шли в верном порядке).
function newsDate(el){
  var d = el.querySelector('.news-archive__date, .carousel__news-date');
  var m = d && d.textContent.match(/(\d{2})\.(\d{2})\.(\d{4})/);
  return m ? Number(m[3] + m[2] + m[1]) : 0;
}
function sortNews(){
  document.querySelectorAll('.news-archive').forEach(function(list){
    Array.prototype.slice.call(list.querySelectorAll('.news-archive__item'))
      .sort(function(a, b){ return newsDate(b) - newsDate(a); })
      .forEach(function(item){ list.appendChild(item); });
  });
  document.querySelectorAll('.carousel__track').forEach(function(track){
    var news = Array.prototype.slice.call(track.querySelectorAll('.carousel__slide--news'))
      .filter(function(s){ return newsDate(s) > 0; });
    if(news.length < 2) return;
    var anchor = news[0];
    var marker = document.createComment('news');
    track.insertBefore(marker, anchor);
    news.sort(function(a, b){ return newsDate(b) - newsDate(a); })
      .forEach(function(s){ track.insertBefore(s, marker); });
    track.removeChild(marker);
  });
}
document.addEventListener('DOMContentLoaded', sortNews);
document.addEventListener('DOMContentLoaded', initCarousels);

// Раздел «Документация» на podderzhka.html: слева серии, справа документы выбранной серии.
// Поиск по названию ищет по всем сериям; фильтр типа (ТУ / ДШ / 3D) действует всегда.
var docsSeries = null;
function selectDocsSeries(key){
  docsSeries = key;
  var search = document.getElementById('docs-search');
  if(search) search.value = '';
  filterDocs();
}
function filterDocs(){
  var browser = document.querySelector('.docs-browser');
  if(!browser) return;
  if(docsSeries === null) docsSeries = browser.getAttribute('data-first') || '';
  var q = (document.getElementById('docs-search').value || '').trim().toLowerCase();
  var type = document.getElementById('docs-filter-type').value;
  var select = document.getElementById('docs-filter-series');
  if(select) select.value = docsSeries;
  var global = q !== '' || docsSeries === '';
  var anyVisible = false;

  browser.querySelectorAll('.docs-browser__section').forEach(function(section){
    var key = section.getAttribute('data-series');
    var total = section.querySelectorAll('.docs-browser__item').length;
    var visible = 0;
    section.querySelectorAll('.docs-browser__type').forEach(function(block){
      var shown = 0;
      block.querySelectorAll('.docs-browser__item').forEach(function(item){
        var ok = (!type || item.getAttribute('data-type') === type) &&
                 (!q || item.getAttribute('data-search').indexOf(q) !== -1);
        item.hidden = !ok;
        if(ok) shown++;
      });
      block.hidden = shown === 0;
      visible += shown;
    });
    var none = section.querySelector('.docs-browser__none');
    if(global){
      section.hidden = visible === 0;
      if(none) none.hidden = true;
    }else{
      section.hidden = key !== docsSeries;
      if(none){
        none.hidden = visible > 0;
        none.firstChild.textContent = total === 0
          ? 'Документы по этой серии скоро появятся. Их можно запросить у менеджера: '
          : 'Документов выбранного типа по этой серии нет. Их можно запросить у менеджера: ';
      }
    }
    if(!section.hidden) anyVisible = true;
  });

  browser.querySelectorAll('.docs-browser__series-btn').forEach(function(btn){
    btn.classList.toggle('docs-browser__series-btn--active', !q && btn.getAttribute('data-series') === docsSeries);
  });
  var hint = browser.querySelector('.docs-browser__hint');
  if(hint){
    hint.hidden = !q;
    hint.textContent = q ? 'Результаты поиска по всем сериям' : '';
  }
  var empty = document.getElementById('docs-empty');
  if(empty) empty.hidden = anyVisible;
}
document.addEventListener('DOMContentLoaded', filterDocs);

// Фильтры таблицы модельного ряда на страницах типоразмеров (serii/tesd10.html и т.п.):
// каждый select в шапке сравнивает своё значение с data-атрибутом строки (data-power, data-in, ...).
// В свёрнутом виде показываются только первые MODEL_ROWS_COLLAPSED подходящих строк.
var MODEL_ROWS_COLLAPSED = 6;
function initModelFilters(){
  document.querySelectorAll('table[data-model-filter]').forEach(function(table){
    var selects = table.querySelectorAll('.size-models__select');
    var rows = table.querySelectorAll('tbody tr:not(.size-models__empty)');
    var empty = table.querySelector('.size-models__empty');
    var section = table.closest('.series-models');
    var toggle = section.querySelector('.series-models__toggle');
    var collapsed = true;
    function apply(){
      var matched = 0;
      rows.forEach(function(row){
        var ok = true;
        selects.forEach(function(s){
          if(s.value && row.getAttribute('data-' + s.getAttribute('data-key')) !== s.value) ok = false;
        });
        if(ok) matched++;
        row.hidden = !ok || (collapsed && matched > MODEL_ROWS_COLLAPSED);
      });
      if(empty) empty.hidden = matched > 0;
      if(toggle){
        toggle.hidden = matched <= MODEL_ROWS_COLLAPSED;
        section.classList.toggle('series-models--collapsed', collapsed && !toggle.hidden);
        toggle.textContent = collapsed ? 'Развернуть' : 'Свернуть';
      }
      if(window.updateScrollShades) updateScrollShades();
    }
    selects.forEach(function(s){ s.addEventListener('change', apply); });
    if(toggle) toggle.addEventListener('click', function(){
      collapsed = !collapsed;
      apply();
      if(collapsed) section.scrollIntoView({behavior:'smooth', block:'start'});
    });
    apply();
  });
}
document.addEventListener('DOMContentLoaded', initModelFilters);

// Затемнение у края таблицы, пока её можно прокрутить вбок (узкие экраны).
// Каждый .table-scroll оборачивается в .scroll-shade; классы --left/--right включают тень.
function initScrollShades(){
  document.querySelectorAll('.table-scroll').forEach(function(box){
    if(box.parentNode.classList.contains('scroll-shade')) return;
    var wrap = document.createElement('div');
    wrap.className = 'scroll-shade';
    box.parentNode.insertBefore(wrap, box);
    wrap.appendChild(box);
    box.addEventListener('scroll', updateScrollShades, {passive: true});
  });
  updateScrollShades();
}
function updateScrollShades(){
  document.querySelectorAll('.scroll-shade').forEach(function(wrap){
    var box = wrap.firstElementChild;
    var rest = box.scrollWidth - box.clientWidth - box.scrollLeft;
    wrap.classList.toggle('scroll-shade--left', box.scrollLeft > 1);
    wrap.classList.toggle('scroll-shade--right', rest > 1);
  });
}
document.addEventListener('DOMContentLoaded', initScrollShades);
window.addEventListener('resize', updateScrollShades);

// ---------- Корзина ----------
// Хранится в localStorage браузера посетителя: [{id, name, desc, qty}]. id = название@типоразмер:
// один и тот же модуль (напр. TESD10) бывает в разных корпусах — это разные позиции.
// Заявка отправляется письмом
// (mailto), как и «Заказать звонок».
var CART_KEY = 'tepower-cart';
function getCart(){
  try{ return JSON.parse(localStorage.getItem(CART_KEY)) || []; }catch(e){ return []; }
}
function saveCart(cart){
  try{ localStorage.setItem(CART_KEY, JSON.stringify(cart)); }catch(e){}
  updateCartBadge();
}
function cartIndex(cart, id){
  for(var i = 0; i < cart.length; i++){ if((cart[i].id || cart[i].name) === id) return i; }
  return -1;
}
function cartBtnId(btn){
  return btn.getAttribute('data-cart-id') || btn.getAttribute('data-cart-name');
}
function cartCount(){
  return getCart().reduce(function(n, item){ return n + item.qty; }, 0);
}

// Базовый путь сайта берём из адреса подключённого theme.js ('' или '../')
function siteBase(){
  var s = document.querySelector('script[src*="theme.js"]');  // адрес может быть с меткой версии: theme.js?v=…
  return s ? s.getAttribute('src').replace(/theme\.js(\?.*)?$/, '') : '';
}

var CART_ICON = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M3 4h2.2l2.1 10.2a1.5 1.5 0 0 0 1.5 1.2h8.4a1.5 1.5 0 0 0 1.5-1.1L20.5 8H6.1" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><circle cx="9.5" cy="19.5" r="1.4" fill="currentColor"/><circle cx="17" cy="19.5" r="1.4" fill="currentColor"/></svg>';

// Значок корзины в шапке добавляется на всех страницах перед переключателем темы
function initHeaderCart(){
  var actions = document.querySelector('.header__actions');
  if(!actions || actions.querySelector('.header-cart')) return;
  var a = document.createElement('a');
  a.className = 'header-cart';
  a.href = siteBase() + 'korzina.html';
  a.title = 'Корзина';
  a.setAttribute('aria-label', 'Корзина');
  a.innerHTML = CART_ICON + '<span class="header-cart__count" hidden></span>';
  actions.insertBefore(a, actions.firstChild);
}
function updateCartBadge(){
  var n = cartCount();
  document.querySelectorAll('.header-cart__count').forEach(function(el){
    el.textContent = n;
    el.hidden = n === 0;
  });
  var cart = getCart();
  document.querySelectorAll('.cart-btn').forEach(function(btn){
    var i = cartIndex(cart, cartBtnId(btn));
    var step = btn.nextElementSibling;
    if(!step || !step.classList.contains('cart-step')){
      step = document.createElement('span');
      step.className = 'cart-step';
      step.innerHTML = '<button type="button" class="cart-step__btn" data-d="-1" aria-label="Меньше">−</button>' +
        '<span class="cart-step__qty" aria-live="polite"></span>' +
        '<button type="button" class="cart-step__btn" data-d="1" aria-label="Больше">+</button>';
      btn.parentNode.insertBefore(step, btn.nextSibling);
    }
    btn.hidden = i !== -1;
    step.hidden = i === -1;
    if(i !== -1) step.querySelector('.cart-step__qty').textContent = cart[i].qty;
  });
}

// Кнопки корзины в таблице модельного ряда: клик добавляет модель, дальше в строке — счётчик «− 1 +»
function initCartButtons(){
  document.addEventListener('click', function(e){
    var stepBtn = e.target.closest('.cart-step__btn');
    var btn = stepBtn ? stepBtn.closest('.cart-step').previousElementSibling : e.target.closest('.cart-btn');
    if(!btn || !btn.classList.contains('cart-btn')) return;
    var cart = getCart();
    var name = btn.getAttribute('data-cart-name');
    var id = cartBtnId(btn);
    var i = cartIndex(cart, id);
    if(!stepBtn){  // кнопка корзины: добавить одну штуку
      if(i === -1){
        cart.push({id: id, name: name, desc: btn.getAttribute('data-cart-desc') || '', qty: 1});
        showCartToast(name + ' добавлен в корзину');
      }
    }else if(i !== -1){  // счётчик «− 1 +»; минус на единице убирает модель из корзины
      cart[i].qty += parseInt(stepBtn.getAttribute('data-d'), 10);
      if(cart[i].qty < 1){
        cart.splice(i, 1);
        showCartToast(name + ' убран из корзины');
      }
    }
    saveCart(cart);
    if(!stepBtn && i === -1){  // фокус — на «+», чтобы с клавиатуры можно было сразу менять количество
      var plus = btn.nextElementSibling && btn.nextElementSibling.querySelector('[data-d="1"]');
      if(plus) plus.focus();
    }
  });
}
var toastTimer = null;
// Всплывающее уведомление внизу экрана; link — необязательная ссылка {href, text}
function showToast(text, link){
  var t = document.querySelector('.toast');
  if(!t){
    t = document.createElement('div');
    t.className = 'toast';
    t.setAttribute('role', 'status');
    document.body.appendChild(t);
  }
  t.innerHTML = '';
  t.appendChild(document.createTextNode(text));
  if(link){
    t.appendChild(document.createTextNode(' · '));
    var a = document.createElement('a');
    a.href = link.href;
    a.textContent = link.text;
    t.appendChild(a);
  }
  t.classList.add('toast--show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(function(){ t.classList.remove('toast--show'); }, 4500);
}
function showCartToast(text){
  showToast(text, {href: siteBase() + 'korzina.html', text: 'Перейти в корзину'});
}

// Страница корзины (korzina.html)
function renderCartPage(){
  var root = document.getElementById('cart-page');
  if(!root) return;
  var cart = getCart();
  var list = root.querySelector('.cart__list');
  root.querySelector('.cart__empty').hidden = cart.length > 0;
  root.querySelector('.cart__filled').hidden = cart.length === 0;
  list.innerHTML = '';
  cart.forEach(function(item){
    var tr = document.createElement('tr');
    tr.innerHTML =
      '<td class="cart__name"></td><td class="cart__desc"></td>' +
      '<td><div class="cart__qty"><button type="button" class="cart__qty-btn" data-d="-1" aria-label="Меньше">−</button>' +
      '<input class="cart__qty-input" type="number" min="1" inputmode="numeric" aria-label="Количество">' +
      '<button type="button" class="cart__qty-btn" data-d="1" aria-label="Больше">+</button></div></td>' +
      '<td><button type="button" class="cart__remove" aria-label="Убрать из корзины" title="Убрать">×</button></td>';
    tr.querySelector('.cart__name').textContent = item.name;
    tr.querySelector('.cart__desc').textContent = item.desc;
    var input = tr.querySelector('.cart__qty-input');
    input.value = item.qty;
    function setQty(q){
      var c = getCart(), i = cartIndex(c, item.id || item.name);
      if(i === -1) return;
      c[i].qty = Math.max(1, q || 1);
      saveCart(c);
      input.value = c[i].qty;
    }
    tr.querySelectorAll('.cart__qty-btn').forEach(function(b){
      b.addEventListener('click', function(){ setQty(parseInt(input.value, 10) + parseInt(b.getAttribute('data-d'), 10)); });
    });
    input.addEventListener('change', function(){ setQty(parseInt(input.value, 10)); });
    tr.querySelector('.cart__remove').addEventListener('click', function(){
      var c = getCart(), i = cartIndex(c, item.id || item.name);
      if(i !== -1){ c.splice(i, 1); saveCart(c); }
      renderCartPage();
    });
    list.appendChild(tr);
  });
  updateScrollShades();
}
function clearCart(){
  saveCart([]);
  renderCartPage();
}
// Окно «Оформить заявку» на странице корзины
function openOrderModal(){
  var modal = document.getElementById('order-modal');
  if(!modal || !getCart().length) return;
  modal.querySelector('.order-modal__form-wrap').hidden = false;
  modal.querySelector('.form__error').hidden = true;
  modal.classList.add('callback-modal--open');
  document.body.style.overflow = 'hidden';
  var first = modal.querySelector('input');
  if(first) first.focus();
}
function closeOrderModal(){
  var modal = document.getElementById('order-modal');
  if(modal) modal.classList.remove('callback-modal--open');
  document.body.style.overflow = '';
}

// Заявка из корзины — на сервер, как и остальные формы (sendForm выше)
function submitCartOrder(e){
  e.preventDefault();
  var f = e.target;
  var cart = getCart();
  if(!cart.length) return false;
  var v = {fio: f.fio.value.trim(), company: f.company.value.trim(), phone: f.phone.value.trim(),
           email: f.email.value.trim(), comment: f.comment.value.trim()};
  var lines = cart.map(function(item, i){
    return (i + 1) + '. ' + item.name + ' — ' + item.qty + ' шт.' + (item.desc ? ' (' + item.desc + ')' : '');
  });
  sendForm(f, {type: 'order', fio: v.fio, company: v.company, phone: v.phone, email: v.email, comment: v.comment,
               items: cart.map(function(item){ return {name: item.name, qty: item.qty, desc: item.desc || ''}; })},
    'Заявка с сайта TE-POWER (' + cart.length + ' поз.)',
    ['ФИО - ' + v.fio, 'Компания - ' + v.company, 'Телефон - ' + v.phone, 'E-mail - ' + v.email,
     'Комментарий - ' + (v.comment || '—'), 'Состав заявки:'].concat(lines),
    function(){
      saveCart([]);
      renderCartPage();
      closeOrderModal();
    });
  return false;
}
document.addEventListener('keydown', function(e){ if(e.key === 'Escape'){ closeOrderModal(); closeDoneModal(); } });

document.addEventListener('DOMContentLoaded', function(){
  initHeaderCart();
  initCartButtons();
  renderCartPage();
  updateCartBadge();
});
// Синхронизация между вкладками и при возврате кнопкой «назад»
window.addEventListener('storage', function(e){ if(e.key === CART_KEY){ updateCartBadge(); renderCartPage(); } });
window.addEventListener('pageshow', function(e){ if(e.persisted){ updateCartBadge(); renderCartPage(); } });
