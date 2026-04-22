const API = '';
let sessionId = null;

const uploadArea   = document.getElementById('uploadArea');
const fileInput    = document.getElementById('fileInput');
const uploadProgress = document.getElementById('uploadProgress');
const docList      = document.getElementById('docList');
const emptyMsg     = document.getElementById('emptyMsg');
const messages     = document.getElementById('messages');
const userInput    = document.getElementById('userInput');
const btnSend      = document.getElementById('btnSend');
const btnNewChat   = document.getElementById('btnNewChat');
const toast        = document.getElementById('toast');

// ── 초기화 ──
loadDocuments();

// ── 업로드 이벤트 ──
uploadArea.addEventListener('click', () => fileInput.click());
uploadArea.addEventListener('dragover', e => { e.preventDefault(); uploadArea.style.background = '#f5f3ff'; });
uploadArea.addEventListener('dragleave', () => uploadArea.style.background = '');
uploadArea.addEventListener('drop', e => {
  e.preventDefault();
  uploadArea.style.background = '';
  if (e.dataTransfer.files[0]) uploadFile(e.dataTransfer.files[0]);
});
fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) uploadFile(fileInput.files[0]);
  fileInput.value = '';
});

async function uploadFile(file) {
  uploadArea.hidden = true;
  uploadProgress.hidden = false;

  const form = new FormData();
  form.append('file', file);

  try {
    const res = await fetch(`${API}/documents/upload`, { method: 'POST', body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || '업로드 실패');
    showToast(`✅ "${file.name}" 업로드 완료 (${data.chunk_count}개 청크)`);
    loadDocuments();
  } catch (e) {
    showToast(`❌ ${e.message}`, true);
  } finally {
    uploadArea.hidden = false;
    uploadProgress.hidden = true;
  }
}

// ── 문서 목록 ──
async function loadDocuments() {
  try {
    const res = await fetch(`${API}/documents`);
    const data = await res.json();
    renderDocList(data.documents);
  } catch {
    showToast('문서 목록을 불러오지 못했습니다.', true);
  }
}

function renderDocList(docs) {
  const items = docList.querySelectorAll('.doc-item');
  items.forEach(el => el.remove());

  emptyMsg.style.display = docs.length ? 'none' : 'block';

  docs.forEach(doc => {
    const item = document.createElement('div');
    item.className = 'doc-item';
    item.innerHTML = `
      <span class="doc-name" title="${doc.filename}">${doc.filename}</span>
      <span class="doc-meta">${doc.chunk_count}청크</span>
      <button class="btn-del" title="삭제" data-id="${doc.doc_id}">✕</button>`;
    item.querySelector('.btn-del').addEventListener('click', () => deleteDoc(doc.doc_id, doc.filename));
    docList.appendChild(item);
  });
}

async function deleteDoc(docId, filename) {
  if (!confirm(`"${filename}"을(를) 삭제할까요?`)) return;
  try {
    const res = await fetch(`${API}/documents/${docId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error();
    showToast(`🗑 "${filename}" 삭제 완료`);
    loadDocuments();
  } catch {
    showToast('삭제에 실패했습니다.', true);
  }
}

// ── 채팅 ──
btnSend.addEventListener('click', sendMessage);
userInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});
userInput.addEventListener('input', () => {
  userInput.style.height = 'auto';
  userInput.style.height = userInput.scrollHeight + 'px';
});

btnNewChat.addEventListener('click', () => {
  sessionId = null;
  messages.innerHTML = `<div class="msg assistant"><div class="bubble">새 대화를 시작합니다. 질문해 주세요!</div></div>`;
});

async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  appendMessage('user', text);
  userInput.value = '';
  userInput.style.height = 'auto';
  btnSend.disabled = true;

  const typingEl = appendTyping();

  try {
    const res = await fetch(`${API}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, session_id: sessionId }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || '응답 실패');

    sessionId = data.session_id;
    typingEl.remove();
    appendMessage('assistant', data.answer, data.sources);
  } catch (e) {
    typingEl.remove();
    appendMessage('assistant', `오류가 발생했습니다: ${e.message}`);
  } finally {
    btnSend.disabled = false;
    userInput.focus();
  }
}

function appendMessage(role, text, sources = []) {
  const div = document.createElement('div');
  div.className = `msg ${role}`;

  const sourcesHtml = sources.length
    ? `<div class="sources">📎 출처: ${sources.join(', ')}</div>` : '';

  div.innerHTML = `<div class="bubble">${escapeHtml(text)}${sourcesHtml}</div>`;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
  return div;
}

function appendTyping() {
  const div = document.createElement('div');
  div.className = 'msg assistant typing';
  div.innerHTML = `<div class="bubble"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>`;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
  return div;
}

// ── 유틸 ──
function escapeHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

let toastTimer;
function showToast(msg, isError = false) {
  toast.textContent = msg;
  toast.style.background = isError ? '#b91c1c' : '#1f2937';
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 3000);
}
