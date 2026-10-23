// Nine shots, one editing table. The video is attached only after a solved board.
(() => {
  const root = document.querySelector('[data-opening-puzzle]');
  if (!root) return;
  const grid = root.querySelector('.opening-grid');
  const original = [...grid.children].sort((a, b) => sequence(a) - sequence(b));
  const count = root.querySelector('[data-opening-count]');
  const status = root.querySelector('[data-opening-status]');
  const hint = root.querySelector('[data-opening-hint]');
  const reset = root.querySelector('[data-opening-reset]');
  const enlarge = root.querySelector('[data-opening-enlarge]');
  const gate = root.querySelector('[data-opening-gate]');
  const play = root.querySelector('[data-opening-play]');
  const screen = root.querySelector('[data-opening-screen]');
  const video = root.querySelector('[data-opening-video]');
  const videoStatus = root.querySelector('[data-opening-video-status]');
  const dialog = root.querySelector('[data-opening-dialog]');
  const large = root.querySelector('[data-opening-large]');
  const detailTitle = root.querySelector('#opening-detail-title');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let order = [], selected = null, dragged = null, solved = false, revealTimer;
  let suppressClickUntil = 0, playAttempt = 0;

  function tile(cell) { return cell.querySelector('.opening-tile'); }
  function sequence(cell) { return Number(tile(cell).dataset.sequence); }
  function title(cell) { return cell.querySelector('img').alt; }
  function animate() { return !reduced.matches && !document.body.classList.contains('tas-still'); }

  function draw() {
    if (order.some((cell, index) => grid.children[index] !== cell)) grid.replaceChildren(...order);
    order.forEach((cell, index) => {
      const button = tile(cell);
      button.setAttribute('aria-label', `位置${index + 1}：${title(cell)}`);
      button.setAttribute('aria-pressed', String(cell === selected));
      button.style.setProperty('--slot', index);
      button.draggable = !solved;
      button.disabled = false;
      cell.querySelector('.opening-position').textContent = String(index + 1).padStart(2, '0');
    });
    count.textContent = `${order.filter((cell, index) => sequence(cell) === index).length} / 9`;
    enlarge.disabled = !selected;
    hint.disabled = solved;
    reset.disabled = false;
  }

  function finish() {
    solved = true;
    selected = null;
    clearDrag();
    draw();
    root.classList.add('is-solved');
    status.textContent = '九个镜头已归位。哥谭之夜，即将开场。';
    gate.textContent = '完整片头已解锁。';
    const reveal = () => { play.hidden = false; play.disabled = false; };
    if (animate()) revealTimer = setTimeout(reveal, 1000);
    else reveal();
  }

  function swap(first, second, message) {
    if (solved || first === second || first < 0 || second < 0) return;
    [order[first], order[second]] = [order[second], order[first]];
    selected = null;
    draw();
    if (order.every((cell, index) => sequence(cell) === index)) finish();
    else status.textContent = message || `已交换第${first + 1}格与第${second + 1}格。`;
    tile(order[second]).focus({preventScroll: true});
  }

  function select(cell) {
    if (solved) {
      selected = cell;
      draw();
      status.textContent = `已选中「${title(cell)}」，可以放大查看。`;
      return;
    }
    if (selected === cell) {
      selected = null;
      status.textContent = '已取消选择。点选两格即可交换。';
    } else if (selected) {
      swap(order.indexOf(selected), order.indexOf(cell));
      return;
    } else {
      selected = cell;
      status.textContent = `已选中「${title(cell)}」。再点一格交换，或放大查看。`;
    }
    draw();
    tile(cell).focus({preventScroll: true});
  }

  function clearDrag() {
    dragged = null;
    original.forEach(cell => tile(cell).classList.remove('is-dragging', 'is-drop-target'));
  }

  function closeScreen(restoreFocus = false) {
    playAttempt += 1;
    video.pause();
    screen.hidden = true;
    grid.inert = false;
    grid.removeAttribute('aria-hidden');
    original.forEach(cell => { tile(cell).disabled = false; });
    videoStatus.textContent = '';
    if (restoreFocus) play.focus({preventScroll: true});
  }

  function newRound() {
    clearTimeout(revealTimer);
    closeScreen();
    video.removeAttribute('src');
    video.load();
    play.hidden = true;
    play.disabled = true;
    play.textContent = '播放完整片头';
    gate.textContent = '完成九格，解锁完整片头。';
    if (dialog.open) dialog.close();
    selected = null;
    solved = false;
    clearDrag();
    root.classList.remove('is-solved');
    order = [...original];
    for (let index = order.length - 1; index > 0; index--) {
      const next = Math.floor(Math.random() * (index + 1));
      [order[index], order[next]] = [order[next], order[index]];
    }
    if (order.every((cell, index) => sequence(cell) === index)) order.push(order.shift());
    draw();
    status.textContent = '分镜已打乱。找出哥谭之夜的第一个镜头。';
  }

  original.forEach(cell => {
    const button = tile(cell);
    button.addEventListener('click', () => {
      if (performance.now() >= suppressClickUntil) select(cell);
    });
    button.addEventListener('keydown', event => {
      const index = order.indexOf(cell);
      const moves = {ArrowLeft: -1, ArrowRight: 1, ArrowUp: -3, ArrowDown: 3};
      if (event.key in moves) {
        event.preventDefault();
        tile(order[Math.max(0, Math.min(8, index + moves[event.key]))]).focus();
      } else if (event.key === 'Escape' && !dialog.open) {
        selected = null; draw();
        status.textContent = '已取消选择。点选两格即可交换。';
        button.focus({preventScroll: true});
      }
    });
    button.addEventListener('dragstart', event => {
      if (solved) { event.preventDefault(); return; }
      selected = null;
      draw();
      dragged = cell;
      button.classList.add('is-dragging');
      event.dataTransfer.effectAllowed = 'move';
      event.dataTransfer.setData('text/plain', button.dataset.frame);
    });
    button.addEventListener('dragover', event => {
      if (!dragged || dragged === cell || solved) return;
      event.preventDefault();
      event.dataTransfer.dropEffect = 'move';
      button.classList.add('is-drop-target');
    });
    button.addEventListener('dragleave', () => button.classList.remove('is-drop-target'));
    button.addEventListener('drop', event => {
      if (!dragged || solved) return;
      event.preventDefault();
      const from = order.indexOf(dragged), to = order.indexOf(cell);
      clearDrag();
      suppressClickUntil = performance.now() + 250;
      swap(from, to);
    });
    button.addEventListener('dragend', clearDrag);
  });

  hint.addEventListener('click', () => {
    if (solved) return;
    const index = order.findIndex((cell, position) => sequence(cell) !== position);
    const source = order.findIndex(cell => sequence(cell) === index);
    swap(source, index, `第${index + 1}格「${title(order[source])}」已归位。`);
  });
  reset.addEventListener('click', () => {
    newRound();
    tile(order[0]).focus({preventScroll: true});
  });
  enlarge.addEventListener('click', () => {
    if (!selected) return;
    large.src = selected.querySelector('img').src;
    large.alt = title(selected);
    detailTitle.textContent = title(selected);
    dialog.showModal();
  });
  root.querySelector('[data-opening-close]').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });

  play.addEventListener('click', async () => {
    if (!solved || play.disabled) return;
    const attempt = ++playAttempt;
    screen.hidden = false;
    grid.inert = true;
    grid.setAttribute('aria-hidden', 'true');
    original.forEach(cell => { tile(cell).disabled = true; });
    videoStatus.textContent = '正在载入片头…';
    if (!video.hasAttribute('src')) video.src = video.dataset.videoSrc;
    else if (video.error) video.load();
    else video.currentTime = 0;
    video.focus({preventScroll: true});
    screen.scrollIntoView({behavior: animate() ? 'smooth' : 'instant', block: 'center'});
    play.textContent = '重新播放片头';
    try {
      await video.play();
    } catch {
      if (attempt === playAttempt && solved) videoStatus.textContent = '点击视频中的播放键，继续观看。';
    }
  });
  root.querySelector('[data-opening-back]').addEventListener('click', () => closeScreen(true));
  video.addEventListener('playing', () => { videoStatus.textContent = ''; });
  video.addEventListener('error', () => {
    if (solved && video.hasAttribute('src')) videoStatus.textContent = '视频暂时无法播放，请点击「重新播放片头」重试。';
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden) video.pause(); });
  window.addEventListener('pagehide', () => { clearDrag(); video.pause(); });
  newRound();
})();
