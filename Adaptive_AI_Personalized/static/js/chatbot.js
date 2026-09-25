/* ==========================================================================
   LearnMate AI Chatbot Controller (Floating Drawer & Dedicated Page)
   ========================================================================== */

let activeChatSessionId = null;
let isSpeaking = false;

document.addEventListener('DOMContentLoaded', () => {
  initChatbotUI();
});

function initChatbotUI() {
  createFloatingWidget();
  setupChatbotEventListeners();
}

function createFloatingWidget() {
  if (document.getElementById('floating-chat-container')) return;

  const container = document.createElement('div');
  container.id = 'floating-chat-container';
  container.style.cssText = 'position: fixed; bottom: 24px; right: 24px; z-index: 9000; display: flex; flex-direction: column; align-items: flex-end; gap: 12px;';

  container.innerHTML = `
    <!-- Slide-over Drawer Window -->
    <div id="chat-drawer" class="card" style="display: none; width: 380px; height: 520px; box-shadow: var(--shadow-xl); border: 1px solid var(--primary-light); flex-direction: column; padding: 0; overflow: hidden; background: var(--bg-card); animation: fadeIn 0.2s ease;">
      <div style="background: linear-gradient(135deg, var(--primary), var(--secondary)); padding: 14px 18px; color: white; display: flex; justify-content: space-between; align-items: center;">
        <div style="display: flex; align-items: center; gap: 10px;">
          <div style="width: 32px; height: 32px; border-radius: 50%; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center;"><i class="fa-solid fa-robot"></i></div>
          <div>
            <div style="font-weight: 700; font-size: 0.95rem;">LearnMate AI</div>
            <div style="font-size: 0.72rem; opacity: 0.9;">Your Personal AI Learning Mentor</div>
          </div>
        </div>
        <button id="close-drawer-btn" style="background: none; border: none; color: white; font-size: 1.2rem; cursor: pointer;">&times;</button>
      </div>

      <!-- Page Context Pill Bar -->
      <div id="drawer-context-pill-bar" style="background: var(--bg-tertiary); padding: 8px 12px; font-size: 0.78rem; display: flex; gap: 6px; overflow-x: auto; border-bottom: 1px solid var(--border-color);">
        <!-- Dynamically injected quick context chips -->
      </div>

      <!-- Messages Body -->
      <div id="drawer-messages" style="flex: 1; padding: 14px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px;">
        <!-- Injected messages -->
      </div>

      <!-- Input Footer -->
      <div style="padding: 10px 14px; border-top: 1px solid var(--border-color); display: flex; gap: 8px; align-items: center; background: var(--bg-secondary);">
        <input type="text" id="drawer-input" class="form-control" placeholder="Ask LearnMate AI..." style="padding: 8px 12px; font-size: 0.88rem;">
        <button class="btn btn-primary btn-sm" id="drawer-send-btn" style="padding: 8px 14px;"><i class="fa-solid fa-paper-plane"></i></button>
      </div>
    </div>

    <!-- Floating Trigger Button -->
    <button id="floating-chat-btn" style="width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; border: none; font-size: 1.6rem; cursor: pointer; box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4); display: flex; align-items: center; justify-content: center; transition: transform 0.2s ease;">
      <i class="fa-solid fa-robot"></i>
    </button>
  `;

  document.body.appendChild(container);
}

function setupChatbotEventListeners() {
  const floatBtn = document.getElementById('floating-chat-btn');
  const drawer = document.getElementById('chat-drawer');
  const closeBtn = document.getElementById('close-drawer-btn');
  const drawerSendBtn = document.getElementById('drawer-send-btn');
  const drawerInput = document.getElementById('drawer-input');

  if (floatBtn && drawer) {
    floatBtn.addEventListener('click', () => {
      const isVisible = drawer.style.display !== 'none';
      drawer.style.display = isVisible ? 'none' : 'flex';
      if (!isVisible) {
        updateDrawerContextPills();
        if (!activeChatSessionId) fetchChatGreeting('drawer-messages');
      }
    });
  }

  if (closeBtn && drawer) {
    closeBtn.addEventListener('click', () => {
      drawer.style.display = 'none';
    });
  }

  if (drawerSendBtn && drawerInput) {
    drawerSendBtn.addEventListener('click', () => sendDrawerMessage());
    drawerInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') sendDrawerMessage();
    });
  }

  // Dedicated Page Handlers
  const mainSendBtn = document.getElementById('main-chat-send-btn');
  const mainInput = document.getElementById('main-chat-input');
  if (mainSendBtn && mainInput) {
    mainSendBtn.addEventListener('click', () => sendMainMessage());
    mainInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') sendMainMessage();
    });
  }

  // Voice Input Button
  const micBtn = document.getElementById('voice-input-btn');
  if (micBtn) {
    micBtn.addEventListener('click', toggleSpeechRecognition);
  }

  // New Conversation Button
  const newChatBtn = document.getElementById('new-chat-btn');
  if (newChatBtn) {
    newChatBtn.addEventListener('click', startNewChatSession);
  }
}

function updateDrawerContextPills() {
  const bar = document.getElementById('drawer-context-pill-bar');
  if (!bar) return;

  const currentHash = window.location.hash.replace('#', '') || 'dashboard';

  let pills = [
    { label: "Explain weak topics", prompt: "Explain my weak topics" },
    { label: "What's next?", prompt: "What should I learn next?" },
    { label: "Today's plan", prompt: "Create a study plan for today" }
  ];

  if (currentHash === 'roadmap') {
    pills = [
      { label: "Why this order?", prompt: "Why is my roadmap in this order?" },
      { label: "What-If Simulator", prompt: "What if I study 1 hour per day?" },
      { label: "Skip topic impact", prompt: "What happens if I skip SQL?" }
    ];
  } else if (currentHash === 'gap-analysis') {
    pills = [
      { label: "Fix weak skills", prompt: "Give me a weak skill recovery quest" },
      { label: "Skill Hunter", prompt: "How do I turn weak skills into strong?" }
    ];
  } else if (currentHash === 'quiz-view' || currentHash.startsWith('assessment')) {
    pills = [
      { label: "Need a hint", prompt: "Give me a hint for this topic" },
      { label: "Test me", prompt: "Test me on Java OOP concepts" }
    ];
  }

  bar.innerHTML = pills.map(p => `
    <button class="btn btn-secondary btn-sm" style="font-size: 0.72rem; padding: 2px 8px; white-space: nowrap;" onclick="sendQuickPrompt('${p.prompt.replace(/'/g, "\\'")}')">
      ${p.label}
    </button>
  `).join('');
}

async function fetchChatGreeting(containerId) {
  try {
    const res = await fetch('/api/chat/greeting');
    const data = await res.json();
    const box = document.getElementById(containerId);
    if (!box) return;

    box.innerHTML = `
      <div style="display: flex; gap: 8px; align-items: flex-start;">
        <div style="width: 28px; height: 28px; border-radius: 50%; background: var(--primary); color: white; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; flex-shrink: 0;"><i class="fa-solid fa-robot"></i></div>
        <div style="background: var(--bg-tertiary); padding: 10px 14px; border-radius: var(--radius-md); font-size: 0.88rem;">
          ${data.greeting.replace(/\n/g, '<br>')}
        </div>
      </div>
    `;
  } catch (err) {
    console.error(err);
  }
}

async function sendDrawerMessage() {
  const input = document.getElementById('drawer-input');
  if (!input || !input.value.strip ? !input.value.trim() : !input.value) return;

  const prompt = input.value.trim();
  input.value = '';

  appendUserMessage('drawer-messages', prompt);

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: prompt, session_id: activeChatSessionId, page_context: window.location.hash })
    });
    const data = await res.json();
    activeChatSessionId = data.session_id;

    appendBotMessage('drawer-messages', data.response, data.agent_type);
  } catch (err) {
    console.error(err);
  }
}

async function sendMainMessage() {
  const input = document.getElementById('main-chat-input');
  if (!input || !input.value.trim()) return;

  const prompt = input.value.trim();
  input.value = '';

  appendUserMessage('main-chat-messages', prompt);

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: prompt, session_id: activeChatSessionId, page_context: window.location.hash })
    });
    const data = await res.json();
    activeChatSessionId = data.session_id;

    appendBotMessage('main-chat-messages', data.response, data.agent_type);
    
    if (data.metadata && data.metadata.earned_xp) {
      showToast('⚡ LearnMate AI Bonus', `Earned +${data.metadata.earned_xp} XP for learning interaction!`, 'success');
    }
  } catch (err) {
    console.error(err);
  }
}

function sendQuickPrompt(prompt) {
  const mainView = document.getElementById('chatbot-view');
  if (mainView && mainView.classList.contains('active')) {
    document.getElementById('main-chat-input').value = prompt;
    sendMainMessage();
  } else {
    document.getElementById('chat-drawer').style.display = 'flex';
    document.getElementById('drawer-input').value = prompt;
    sendDrawerMessage();
  }
}

function appendUserMessage(containerId, text) {
  const box = document.getElementById(containerId);
  if (!box) return;

  const msgDiv = document.createElement('div');
  msgDiv.style.cssText = 'display: flex; justify-content: flex-end; margin-bottom: 8px;';
  msgDiv.innerHTML = `
    <div style="background: linear-gradient(135deg, var(--primary), var(--primary-hover)); color: white; padding: 10px 14px; border-radius: var(--radius-md); max-width: 80%; font-size: 0.9rem;">
      ${text}
    </div>
  `;
  box.appendChild(msgDiv);
  box.scrollTop = box.scrollHeight;
}

function appendBotMessage(containerId, text, agentType = 'MentorAgent') {
  const box = document.getElementById(containerId);
  if (!box) return;

  const formattedText = text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/```([\s\S]*?)```/g, '<pre style="background: var(--bg-primary); padding: 12px; border-radius: 8px; font-family: monospace; font-size: 0.82rem; overflow-x: auto;"><code>$1</code></pre>')
    .replace(/\n/g, '<br>');

  const msgDiv = document.createElement('div');
  msgDiv.style.cssText = 'display: flex; gap: 10px; align-items: flex-start; margin-bottom: 12px;';
  msgDiv.innerHTML = `
    <div style="width: 32px; height: 32px; border-radius: 50%; background: var(--primary); color: white; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; flex-shrink: 0;">
      <i class="fa-solid fa-robot"></i>
    </div>
    <div style="background: var(--bg-tertiary); padding: 12px 16px; border-radius: var(--radius-md); max-width: 85%; font-size: 0.9rem; border: 1px solid var(--border-color);">
      <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted); margin-bottom: 6px;">
        <span class="badge badge-average">${agentType}</span>
        <div style="display: flex; gap: 8px;">
          <button onclick="speakText(this)" title="Listen" style="background:none; border:none; cursor:pointer; color:var(--text-muted);"><i class="fa-solid fa-volume-high"></i></button>
          <button onclick="copyToClipboard(this)" title="Copy" style="background:none; border:none; cursor:pointer; color:var(--text-muted);"><i class="fa-solid fa-copy"></i></button>
        </div>
      </div>
      <div>${formattedText}</div>
    </div>
  `;
  box.appendChild(msgDiv);
  box.scrollTop = box.scrollHeight;
}

async function renderChatbotPage() {
  await fetchChatSessions();
  if (!activeChatSessionId) {
    await startNewChatSession();
  } else {
    await fetchChatHistory(activeChatSessionId);
  }
}

async function fetchChatSessions() {
  try {
    const res = await fetch('/api/chat/sessions');
    const sessions = await res.json();
    const list = document.getElementById('chat-sessions-list');
    if (!list) return;

    list.innerHTML = sessions.map(s => `
      <div class="nav-item ${s.id === activeChatSessionId ? 'active' : ''}" onclick="switchChatSession(${s.id})" style="cursor: pointer; justify-content: space-between; padding: 10px 12px; font-size: 0.85rem;">
        <span style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"><i class="fa-solid fa-message"></i> ${s.title}</span>
      </div>
    `).join('');
  } catch (e) { console.error(e); }
}

async function startNewChatSession() {
  try {
    const res = await fetch('/api/chat/new', { method: 'POST' });
    const data = await res.json();
    activeChatSessionId = data.session_id;

    const box = document.getElementById('main-chat-messages');
    if (box) {
      box.innerHTML = '';
      appendBotMessage('main-chat-messages', data.greeting, 'LearnMate AI');
    }
    await fetchChatSessions();
  } catch (e) { console.error(e); }
}

async function switchChatSession(sessionId) {
  activeChatSessionId = sessionId;
  await fetchChatHistory(sessionId);
  await fetchChatSessions();
}

async function fetchChatHistory(sessionId) {
  try {
    const res = await fetch(`/api/chat/history?session_id=${sessionId}`);
    const data = await res.json();
    const box = document.getElementById('main-chat-messages');
    if (!box) return;

    box.innerHTML = '';
    data.messages.forEach(m => {
      if (m.sender === 'user') {
        appendUserMessage('main-chat-messages', m.message);
      } else {
        appendBotMessage('main-chat-messages', m.message, m.agent_type);
      }
    });
  } catch (e) { console.error(e); }
}

function toggleSpeechRecognition() {
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    alert("Speech recognition is not supported in this browser. Please use Google Chrome or Edge.");
    return;
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();
  recognition.lang = 'en-US';

  const micBtn = document.getElementById('voice-input-btn');
  if (micBtn) micBtn.style.color = 'var(--danger)';

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    const input = document.getElementById('main-chat-input');
    if (input) input.value = transcript;
    if (micBtn) micBtn.style.color = 'var(--text-muted)';
  };

  recognition.onerror = () => {
    if (micBtn) micBtn.style.color = 'var(--text-muted)';
  };

  recognition.start();
}

function speakText(btn) {
  const card = btn.closest('.card, div');
  const text = card ? card.innerText : '';

  if ('speechSynthesis' in window) {
    if (speechSynthesis.speaking) {
      speechSynthesis.cancel();
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text.replace(/[\#\*\`]/g, ''));
    utterance.rate = 1.0;
    speechSynthesis.speak(utterance);
  }
}

function copyToClipboard(btn) {
  const card = btn.closest('.card, div');
  const text = card ? card.innerText : '';

  navigator.clipboard.writeText(text).then(() => {
    showToast('Copied!', 'Response copied to clipboard.', 'info');
  });
}
