/* ==========================================================================
   Main Application Router & Dynamic State Controller
   ========================================================================== */

let currentUser = null;
let currentProfile = null;
let currentCareerGoals = [];
let currentRoadmapData = null;
let currentAssessmentData = null;
let activeQuizTopicId = null;
let quizAnswers = {};
let activeModalTopicId = null;

document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

async function initApp() {
  setupEventListeners();
  await checkAuthStatus();
  await loadCareerGoals();
  handleHashRouting();
  window.addEventListener('hashchange', handleHashRouting);
}

/* Event Listeners Setup */
function setupEventListeners() {
  const themeToggleBtn = document.getElementById('theme-toggle-btn');
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', toggleTheme);
  }

  const mobileToggle = document.getElementById('mobile-toggle');
  const sidebar = document.getElementById('sidebar');
  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener('click', () => {
      sidebar.classList.toggle('mobile-open');
    });
  }

  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', logoutUser);
  }

  const switchRoleBtn = document.getElementById('switch-role-btn');
  if (switchRoleBtn) {
    switchRoleBtn.addEventListener('click', switchRole);
  }

  const authForm = document.getElementById('auth-form');
  if (authForm) {
    authForm.addEventListener('submit', handleAuthSubmit);
  }

  const authToggleBtn = document.getElementById('auth-toggle-btn');
  if (authToggleBtn) {
    authToggleBtn.addEventListener('click', toggleAuthMode);
  }

  const profileForm = document.getElementById('profile-form');
  if (profileForm) {
    profileForm.addEventListener('submit', handleProfileSubmit);
  }

  const recalcBtn = document.getElementById('recalculate-roadmap-btn');
  if (recalcBtn) {
    recalcBtn.addEventListener('click', async () => {
      await fetchRoadmap();
      alert("Personalized AI Roadmap recalculation complete!");
    });
  }

  const startDashAssessmentBtn = document.getElementById('start-assessment-btn');
  if (startDashAssessmentBtn) {
    startDashAssessmentBtn.addEventListener('click', () => {
      if (currentRoadmapData && currentRoadmapData.nodes.length > 0) {
        const unmastered = currentRoadmapData.nodes.find(n => n.status !== 'Mastered' && n.status !== 'Completed');
        const topicId = unmastered ? unmastered.topic_id : 1;
        startAssessment(topicId);
      } else {
        startAssessment(1);
      }
    });
  }

  const modalCloseBtn = document.getElementById('modal-close-btn');
  const nodeModal = document.getElementById('node-modal');
  if (modalCloseBtn && nodeModal) {
    modalCloseBtn.addEventListener('click', () => {
      nodeModal.classList.remove('active');
    });
  }

  const modalQuizBtn = document.getElementById('modal-start-quiz-btn');
  if (modalQuizBtn) {
    modalQuizBtn.addEventListener('click', () => {
      if (activeModalTopicId) {
        document.getElementById('node-modal').classList.remove('active');
        startAssessment(activeModalTopicId);
      }
    });
  }

  const adminForm = document.getElementById('admin-add-question-form');
  if (adminForm) {
    adminForm.addEventListener('submit', handleAdminAddQuestion);
  }
}

/* Theme Handler */
function toggleTheme() {
  const html = document.documentElement;
  const currentTheme = html.getAttribute('data-theme') || 'light';
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  html.setAttribute('data-theme', newTheme);

  const icon = document.querySelector('#theme-toggle-btn i');
  if (icon) {
    icon.className = newTheme === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
  }

  if (window.gapDataCache) {
    renderDashboardRadar(window.gapDataCache);
    renderGapPieChart(window.gapDataCache.counts || {});
    renderGapBarChart(window.gapDataCache);
  }
}

/* Authentication Handlers */
async function checkAuthStatus() {
  try {
    const res = await fetch('/api/auth/me');
    if (res.ok) {
      const data = await res.json();
      currentUser = data.user;
      currentProfile = data.profile;
      updateUserUI(data.gamification);
    } else {
      currentUser = null;
      currentProfile = null;
    }
  } catch (err) {
    console.error("Auth status check error:", err);
  }
}

function updateUserUI(gamification) {
  if (currentUser) {
    document.getElementById('user-display-name').innerText = currentUser.name;
    document.getElementById('user-display-role').innerText = currentUser.role;

    const initials = currentUser.name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
    document.getElementById('user-avatar-initials').innerText = initials || 'US';

    if (gamification) {
      document.getElementById('nav-coins-amount').innerText = gamification.coins;
    }

    const adminNavs = document.querySelectorAll('.admin-only');
    adminNavs.forEach(el => {
      el.style.display = currentUser.role === 'admin' ? 'flex' : 'none';
    });

    const switchBtn = document.getElementById('switch-role-btn');
    if (switchBtn) {
      switchBtn.innerHTML = currentUser.role === 'admin'
        ? '<i class="fa-solid fa-repeat"></i> Switch to Student'
        : '<i class="fa-solid fa-repeat"></i> Switch to Admin';
    }
  }
}

async function handleAuthSubmit(e) {
  e.preventDefault();
  const isRegister = document.getElementById('name-group').style.display !== 'none';
  const email = document.getElementById('auth-email').value;
  const password = document.getElementById('auth-password').value;

  const endpoint = isRegister ? '/api/auth/register' : '/api/auth/login';
  const payload = { email, password };

  if (isRegister) {
    payload.name = document.getElementById('auth-name').value;
    payload.role = document.getElementById('auth-role').value;
  }

  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (!res.ok) {
      alert(data.error || "Authentication failed");
      return;
    }

    await checkAuthStatus();
    window.location.hash = '#dashboard';
  } catch (err) {
    console.error("Auth submit error:", err);
    alert("Connection error during login/register.");
  }
}

function toggleAuthMode() {
  const nameGroup = document.getElementById('name-group');
  const roleGroup = document.getElementById('role-group');
  const title = document.getElementById('auth-form-title');
  const submitBtn = document.getElementById('auth-submit-btn');
  const toggleMsg = document.getElementById('auth-toggle-msg');
  const toggleBtn = document.getElementById('auth-toggle-btn');

  const isLogin = nameGroup.style.display === 'none';

  if (isLogin) {
    nameGroup.style.display = 'block';
    roleGroup.style.display = 'block';
    title.innerText = 'Create Student Account';
    submitBtn.innerText = 'Register Account';
    toggleMsg.innerText = 'Already have an account?';
    toggleBtn.innerText = 'Sign In';
  } else {
    nameGroup.style.display = 'none';
    roleGroup.style.display = 'none';
    title.innerText = 'Account Login';
    submitBtn.innerText = 'Sign In';
    toggleMsg.innerText = "Don't have an account?";
    toggleBtn.innerText = 'Register Now';
  }
}

async function logoutUser() {
  await fetch('/api/auth/logout', { method: 'POST' });
  currentUser = null;
  currentProfile = null;
  window.location.hash = '#login';
}

async function switchRole() {
  if (!currentUser) return;
  const newRole = currentUser.role === 'admin' ? 'student' : 'admin';

  try {
    await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: newRole === 'admin' ? 'admin@example.com' : 'student@example.com',
        password: newRole === 'admin' ? 'admin123' : 'student123'
      })
    });

    await checkAuthStatus();
    window.location.hash = newRole === 'admin' ? '#admin' : '#dashboard';
  } catch (e) {
    console.error(e);
  }
}

/* SPA Hash Routing */
function handleHashRouting() {
  let hash = window.location.hash.replace('#', '') || 'dashboard';

  if (hash.startsWith('assessment')) {
    const params = new URLSearchParams(hash.split('?')[1]);
    const topicId = params.get('topic') || 1;
    startAssessment(topicId);
    return;
  }

  const validViews = [
    'landing', 'login', 'dashboard', 'gamification', 'roadmap', 'gap-analysis',
    'activities', 'assessment-select', 'profile', 'recommendations',
    'history', 'admin', 'result'
  ];

  let viewId = hash + '-view';
  if (!document.getElementById(viewId)) {
    viewId = 'dashboard-view';
  }

  document.querySelectorAll('.view-section').forEach(sec => sec.classList.remove('active'));

  const targetView = document.getElementById(viewId);
  if (targetView) {
    targetView.classList.add('active');
  }

  document.querySelectorAll('.nav-item').forEach(nav => {
    nav.classList.remove('active');
    if (nav.getAttribute('data-view') === viewId) {
      nav.classList.add('active');
    }
  });

  const titleMap = {
    'landing-view': 'Landing Page',
    'login-view': 'Account Portal',
    'dashboard-view': 'Student Dashboard',
    'gamification-view': 'Gamification & AI Motivation Hub',
    'roadmap-view': 'Personalized AI Learning Roadmap',
    'gap-analysis-view': 'AI Skill Gap Analysis Report',
    'activities-view': 'Learning Activity Recommendations',
    'assessment-select-view': 'Take Skill Diagnostic Assessment',
    'profile-view': 'Student Profile & Goals',
    'recommendations-view': 'AI Recommendation Engine Log',
    'history-view': 'Learning & Performance History',
    'admin-view': 'Faculty & Admin Panel',
    'result-view': 'Assessment Diagnostic Results'
  };

  const pageHeading = document.getElementById('current-view-title');
  if (pageHeading) {
    pageHeading.innerText = titleMap[viewId] || 'Personalized AI Portal';
  }

  loadViewData(viewId);
}

function loadViewData(viewId) {
  switch (viewId) {
    case 'dashboard-view':
      fetchDashboard();
      break;
    case 'gamification-view':
      renderGamificationPage();
      break;
    case 'roadmap-view':
      fetchRoadmap();
      break;
    case 'gap-analysis-view':
      fetchSkillGap();
      break;
    case 'activities-view':
      fetchActivities();
      break;
    case 'assessment-select-view':
      fetchAssessmentTopics();
      break;
    case 'profile-view':
      fetchProfileData();
      break;
    case 'recommendations-view':
      fetchRecommendations();
      break;
    case 'history-view':
      fetchHistory();
      break;
    case 'admin-view':
      fetchAdminData();
      break;
    case 'landing-view':
      renderLandingCareers();
      break;
  }
}

/* Data Fetchers & View Renderers */

async function loadCareerGoals() {
  try {
    const res = await fetch('/api/career-goals');
    currentCareerGoals = await res.json();
    populateCareerSelects();
  } catch (err) {
    console.error("Error loading career goals:", err);
  }
}

function populateCareerSelects() {
  const profSelect = document.getElementById('prof-career-goal');
  if (!profSelect) return;
  profSelect.innerHTML = currentCareerGoals.map(cg => `<option value="${cg.id}">${cg.title}</option>`).join('');
}

function renderLandingCareers() {
  const container = document.getElementById('landing-career-cards');
  if (!container) return;

  container.innerHTML = currentCareerGoals.map(cg => `
    <div class="card">
      <div class="stat-icon primary" style="margin-bottom: 12px;"><i class="fa-solid fa-${cg.icon || 'code'}"></i></div>
      <h4>${cg.title}</h4>
      <p style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 6px;">${cg.description}</p>
      <button class="btn btn-primary btn-sm" style="margin-top: 14px; width: 100%;" onclick="selectCareerGoal(${cg.id})">
        Select Career Roadmap
      </button>
    </div>
  `).join('');
}

async function selectCareerGoal(careerId) {
  if (!currentUser) {
    window.location.hash = '#login';
    return;
  }
  await fetch('/api/student/profile', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ career_goal_id: careerId })
  });
  window.location.hash = '#dashboard';
}

/* Dashboard Loader */
async function fetchDashboard() {
  try {
    const res = await fetch('/api/dashboard');
    if (!res.ok) return;
    const data = await res.json();

    document.getElementById('dash-career-goal').innerText = data.career_goal;
    document.getElementById('dash-readiness').innerText = `${data.overall_progress_percentage}%`;
    document.getElementById('dash-streak').innerText = `${data.gamification.current_streak} Days`;

    document.getElementById('dash-level-title').innerText = `Level ${data.gamification.level}`;
    document.getElementById('dash-xp-sublabel').innerText = `"${data.gamification.level_name}" (${data.gamification.total_xp} XP)`;

    const recText = data.recommendations && data.recommendations.length > 0
      ? data.recommendations[0].message
      : "You are making steady progress! Continue following your prerequisite roadmap.";
    document.getElementById('dash-ai-recommendation-text').innerText = recText;

    if (data.current_topic) {
      document.getElementById('dash-topic-title').innerText = data.current_topic.topic_name;
      document.getElementById('dash-topic-desc').innerText = data.current_topic.description || '';
      document.getElementById('dash-topic-hours').innerText = `${data.current_topic.estimated_hours}h`;
      document.getElementById('dash-topic-diff').innerText = data.current_topic.difficulty;
      document.getElementById('dash-topic-status').innerText = data.current_topic.status;
    }

    const actBox = document.getElementById('dash-todays-activities');
    if (actBox && data.todays_tasks) {
      actBox.innerHTML = data.todays_tasks.map(t => `
        <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background-color: var(--bg-tertiary); border-radius: var(--radius-md);">
          <div>
            <div style="font-weight: 600; font-size: 0.88rem;">${t.title}</div>
            <div style="font-size: 0.78rem; color: var(--text-muted);">${t.type.toUpperCase()} • ${t.estimated_mins} mins</div>
          </div>
          <button class="btn btn-secondary btn-sm" onclick="completeActivity(${t.id})">Complete (+20 XP)</button>
        </div>
      `).join('');
    }

    const summary = data.roadmap_summary;
    const pct = summary.total_topics > 0 ? Math.round((summary.completed_topics / summary.total_topics) * 100) : 0;
    document.getElementById('dash-roadmap-percent').innerText = `${pct}%`;
    document.getElementById('dash-roadmap-progressbar').style.width = `${pct}%`;
    document.getElementById('dash-topics-completed').innerText = summary.completed_topics;
    document.getElementById('dash-topics-total').innerText = summary.total_topics;
    document.getElementById('dash-completion-date').innerText = summary.estimated_completion_date || 'N/A';

    const historyBox = document.getElementById('dash-history-log');
    if (historyBox && data.recent_history) {
      historyBox.innerHTML = data.recent_history.map(h => `
        <div style="font-size: 0.84rem; border-left: 3px solid var(--primary); padding-left: 10px;">
          <div style="font-weight: 600;">${h.description}</div>
          <div style="color: var(--text-muted); font-size: 0.75rem;">${h.timestamp} • ${h.score_or_metric || ''}</div>
        </div>
      `).join('');
    }

    const gapRes = await fetch('/api/skill-gap-analysis');
    const gapData = await gapRes.json();
    window.gapDataCache = gapData;
    renderDashboardRadar(gapData);

  } catch (err) {
    console.error("Dashboard fetch error:", err);
  }
}

/* Roadmap Loader */
async function fetchRoadmap() {
  try {
    const res = await fetch('/api/roadmap');
    currentRoadmapData = await res.json();
    renderRoadmapTimeline(currentRoadmapData, 'roadmap-nodes-container');
  } catch (err) {
    console.error("Roadmap fetch error:", err);
  }
}

async function openTopicModal(topicId) {
  activeModalTopicId = topicId;
  const modal = document.getElementById('node-modal');
  if (!modal || !currentRoadmapData) return;

  const node = currentRoadmapData.nodes.find(n => n.topic_id === topicId);
  if (!node) return;

  document.getElementById('modal-topic-name').innerText = node.topic_name;
  document.getElementById('modal-topic-desc').innerText = node.description || 'Core roadmap module.';
  document.getElementById('modal-topic-diff').innerText = node.difficulty;
  document.getElementById('modal-topic-hours').innerText = `${node.estimated_hours} Hours`;
  document.getElementById('modal-topic-status-badge').innerText = node.status;
  document.getElementById('modal-topic-mastery').innerText = `${node.mastery_score}%`;

  const actContainer = document.getElementById('modal-topic-activities');
  actContainer.innerHTML = node.recommended_activities.map(a => `
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background-color: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: var(--radius-md);">
      <div>
        <div style="font-weight: 600; font-size: 0.88rem;">${a.title}</div>
        <div style="font-size: 0.78rem; color: var(--text-muted);">${a.type.toUpperCase()} • ${a.estimated_mins} mins</div>
      </div>
      <button class="btn btn-secondary btn-sm" onclick="completeActivity(${a.id})">Mark Done (+20 XP)</button>
    </div>
  `).join('');

  modal.classList.add('active');
}

async function fetchSkillGap() {
  try {
    const res = await fetch('/api/skill-gap-analysis');
    const data = await res.json();
    window.gapDataCache = data;

    renderGapPieChart(data.counts || {});
    renderGapBarChart(data);

    const tableBox = document.getElementById('gap-skills-table-box');
    if (!tableBox) return;

    const allSkills = [
      ...(data.strong_skills || []),
      ...(data.average_skills || []),
      ...(data.weak_skills || []),
      ...(data.missing_skills || [])
    ];

    tableBox.innerHTML = `
      <table style="width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 0.9rem;">
        <thead>
          <tr style="border-bottom: 2px solid var(--border-color); text-align: left;">
            <th style="padding: 10px;">Skill Name</th>
            <th style="padding: 10px;">Category</th>
            <th style="padding: 10px;">Required Level</th>
            <th style="padding: 10px;">Mastery Score</th>
            <th style="padding: 10px;">AI Classification</th>
          </tr>
        </thead>
        <tbody>
          ${allSkills.map(s => {
            let bClass = 'badge-strong';
            if (s.status === 'Average') bClass = 'badge-average';
            if (s.status === 'Weak') bClass = 'badge-weak';
            if (s.status.includes('Missing')) bClass = 'badge-missing';

            return `
              <tr style="border-bottom: 1px solid var(--border-color);">
                <td style="padding: 12px; font-weight: 600;">${s.skill_name}</td>
                <td style="padding: 12px; color: var(--text-secondary);">${s.category}</td>
                <td style="padding: 12px;">${s.required_level}</td>
                <td style="padding: 12px; font-weight: 700;">${s.mastery_score}%</td>
                <td style="padding: 12px;"><span class="badge ${bClass}">${s.status}</span></td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    `;

  } catch (err) {
    console.error("Skill gap fetch error:", err);
  }
}

async function fetchActivities() {
  if (!currentRoadmapData) {
    await fetchRoadmap();
  }
  const grid = document.getElementById('activities-grid');
  if (!grid || !currentRoadmapData) return;

  let allActivities = [];
  currentRoadmapData.nodes.forEach(n => {
    n.recommended_activities.forEach(a => {
      allActivities.push({ ...a, topic_name: n.topic_name });
    });
  });

  grid.innerHTML = allActivities.map(a => `
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <span class="badge badge-average">${a.type.toUpperCase()}</span>
        <span style="font-size: 0.8rem; color: var(--text-muted);"><i class="fa-solid fa-clock"></i> ${a.estimated_mins} mins</span>
      </div>
      <h4>${a.title}</h4>
      <p style="font-size: 0.85rem; color: var(--text-muted); margin: 6px 0 16px;">Topic: ${a.topic_name}</p>
      <button class="btn btn-primary btn-sm" style="width: 100%;" onclick="completeActivity(${a.id})">
        <i class="fa-solid fa-check"></i> Complete (+20 XP, 🪙 +5 Coins)
      </button>
    </div>
  `).join('');
}

async function completeActivity(actId) {
  try {
    const res = await fetch('/api/activity/complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ activity_id: actId })
    });
    const data = await res.json();
    if (res.ok) {
      showToast('⚡ Activity Completed!', `+${data.earned_xp} XP • 🪙 +${data.coins_earned} Coins Earned!`, 'success');
      await checkAuthStatus();
      await fetchDashboard();
    }
  } catch (e) {
    console.error(e);
  }
}

async function fetchAssessmentTopics() {
  if (!currentRoadmapData) {
    await fetchRoadmap();
  }
  const list = document.getElementById('assessment-topic-list');
  if (!list || !currentRoadmapData) return;

  list.innerHTML = currentRoadmapData.nodes.map(n => `
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span class="badge badge-weak">${n.difficulty}</span>
        <span style="font-size: 0.8rem; color: var(--text-muted);">Mastery: ${n.mastery_score}%</span>
      </div>
      <h4>${n.topic_name}</h4>
      <p style="font-size: 0.85rem; color: var(--text-secondary); margin: 6px 0 16px;">${n.description}</p>
      <button class="btn btn-primary btn-sm" style="width: 100%;" onclick="startAssessment(${n.topic_id})">
        <i class="fa-solid fa-vial"></i> Launch Quiz (+30 XP)
      </button>
    </div>
  `).join('');
}

async function startAssessment(topicId) {
  activeQuizTopicId = topicId;
  quizAnswers = {};

  try {
    const res = await fetch(`/api/assessment/${topicId}`);
    currentAssessmentData = await res.json();

    document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
    document.getElementById('quiz-view').classList.add('active');

    document.getElementById('quiz-title').innerText = currentAssessmentData.assessment.title;
    renderQuizQuestions();
  } catch (err) {
    console.error("Assessment fetch error:", err);
  }
}

function renderQuizQuestions() {
  const card = document.getElementById('quiz-question-card');
  if (!card || !currentAssessmentData) return;

  const questions = currentAssessmentData.questions;
  if (!questions || questions.length === 0) {
    card.innerHTML = `<p>No questions configured for this topic yet.</p>`;
    return;
  }

  card.innerHTML = `
    <form id="quiz-form">
      ${questions.map((q, idx) => `
        <div style="margin-bottom: 28px;">
          <h4 style="font-size: 1.05rem; margin-bottom: 12px;">
            Question ${idx + 1} of ${questions.length}: ${q.question_text}
          </h4>
          <div>
            ${(q.options || []).map(opt => `
              <label class="quiz-option" onclick="selectQuizOption(${q.id}, '${opt.replace(/'/g, "\\'")}', this)">
                <input type="radio" name="q_${q.id}" value="${opt}" style="margin-right: 8px;">
                <span>${opt}</span>
              </label>
            `).join('')}
          </div>
        </div>
      `).join('')}
      <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 16px;">
        <i class="fa-solid fa-paper-plane"></i> Submit Assessment to AI Engine
      </button>
    </form>
  `;

  document.getElementById('quiz-form').addEventListener('submit', submitQuizAnswers);
}

function selectQuizOption(qId, val, labelEl) {
  quizAnswers[qId] = val;
  const parent = labelEl.parentElement;
  parent.querySelectorAll('.quiz-option').forEach(opt => opt.classList.remove('selected'));
  labelEl.classList.add('selected');
  const radio = labelEl.querySelector('input[type="radio"]');
  if (radio) radio.checked = true;
}

async function submitQuizAnswers(e) {
  e.preventDefault();
  if (!currentAssessmentData) return;

  try {
    const res = await fetch('/api/assessment/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        assessment_id: currentAssessmentData.assessment.id,
        answers: quizAnswers,
        time_taken_seconds: 120
      })
    });

    const data = await res.json();
    await checkAuthStatus();
    renderAssessmentResults(data);
  } catch (err) {
    console.error("Quiz submit error:", err);
  }
}

function renderAssessmentResults(data) {
  document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
  document.getElementById('result-view').classList.add('active');

  document.getElementById('result-score-title').innerText = `Assessment Score: ${data.score_percentage}%`;
  document.getElementById('result-score-subtitle').innerText = `Accuracy: ${data.accuracy}% • Evaluation Completed`;
  document.getElementById('result-ai-adaptation-msg').innerText = data.adaptation.message;

  const rewards = data.gamification_rewards;
  document.getElementById('result-gamification-rewards-text').innerText = `+${rewards.earned_xp} XP Earned! Level: ${rewards.level} (${rewards.level_name}) • 🔥 ${rewards.streak} Day Streak!`;

  if (rewards.leveled_up) {
    showToast(`🎉 LEVEL UP! Level ${rewards.level}`, `Congratulations! You reached Level ${rewards.level} - '${rewards.level_name}'!`, 'success');
  }
}

async function fetchProfileData() {
  try {
    const res = await fetch('/api/student/profile');
    const profile = await res.json();
    if (!profile) return;

    if (profile.career_goal_id) document.getElementById('prof-career-goal').value = profile.career_goal_id;
    if (profile.target_role) document.getElementById('prof-target-role').value = profile.target_role;
    if (profile.academic_year) document.getElementById('prof-academic-year').value = profile.academic_year;
    if (profile.department) document.getElementById('prof-department').value = profile.department;
    if (profile.cgpa) document.getElementById('prof-cgpa').value = profile.cgpa;
    if (profile.available_hours_per_day) document.getElementById('prof-hours').value = profile.available_hours_per_day;
    if (profile.current_skills) document.getElementById('prof-current-skills').value = profile.current_skills;
    if (profile.preferred_learning_style) document.getElementById('prof-learning-style').value = profile.preferred_learning_style;

    if (currentUser) {
      document.getElementById('prof-leaderboard-privacy').checked = currentUser.is_leaderboard_hidden === 1;
    }
  } catch (err) {
    console.error("Profile fetch error:", err);
  }
}

async function handleProfileSubmit(e) {
  e.preventDefault();
  const payload = {
    career_goal_id: document.getElementById('prof-career-goal').value,
    target_role: document.getElementById('prof-target-role').value,
    academic_year: document.getElementById('prof-academic-year').value,
    department: document.getElementById('prof-department').value,
    cgpa: document.getElementById('prof-cgpa').value,
    available_hours_per_day: document.getElementById('prof-hours').value,
    current_skills: document.getElementById('prof-current-skills').value,
    preferred_learning_style: document.getElementById('prof-learning-style').value
  };

  const isHidden = document.getElementById('prof-leaderboard-privacy').checked;

  try {
    await fetch('/api/student/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    await fetch('/api/gamification/toggle-leaderboard', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ hide: isHidden })
    });

    alert("Profile and Leaderboard Privacy updated!");
    window.location.hash = '#dashboard';
  } catch (err) {
    console.error("Profile update error:", err);
  }
}

async function fetchRecommendations() {
  try {
    const res = await fetch('/api/dashboard');
    const data = await res.json();
    const container = document.getElementById('recommendations-list-container');
    if (!container) return;

    container.innerHTML = (data.recommendations || []).map(r => `
      <div class="card" style="border-left: 4px solid var(--primary);">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
          <span class="badge badge-strong">${r.type.toUpperCase()}</span>
          <span style="font-size: 0.8rem; color: var(--text-muted);">${r.created_at}</span>
        </div>
        <p style="font-size: 0.95rem; font-weight: 500;">${r.message}</p>
      </div>
    `).join('');
  } catch (e) { console.error(e); }
}

async function fetchHistory() {
  try {
    const res = await fetch('/api/learning-history');
    const data = await res.json();
    const container = document.getElementById('full-history-table-container');
    if (!container) return;

    container.innerHTML = `
      <table style="width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 0.9rem;">
        <thead>
          <tr style="border-bottom: 2px solid var(--border-color); text-align: left;">
            <th style="padding: 10px;">Timestamp</th>
            <th style="padding: 10px;">Type</th>
            <th style="padding: 10px;">Description</th>
            <th style="padding: 10px;">Score / Metric</th>
          </tr>
        </thead>
        <tbody>
          ${data.map(h => `
            <tr style="border-bottom: 1px solid var(--border-color);">
              <td style="padding: 12px; color: var(--text-muted); font-size: 0.82rem;">${h.timestamp}</td>
              <td style="padding: 12px;"><span class="badge badge-average">${h.activity_type}</span></td>
              <td style="padding: 12px; font-weight: 500;">${h.description}</td>
              <td style="padding: 12px; font-weight: 700; color: var(--primary);">${h.score_or_metric || '-'}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
  } catch (e) { console.error(e); }
}

async function fetchAdminData() {
  try {
    const res = await fetch('/api/admin/analytics');
    const data = await res.json();

    document.getElementById('admin-total-students').innerText = data.total_students;
    document.getElementById('admin-total-courses').innerText = data.total_courses;
    document.getElementById('admin-total-topics').innerText = data.total_topics;
    document.getElementById('admin-total-questions').innerText = data.total_questions;

    const studentTable = document.getElementById('admin-students-table');
    if (studentTable) {
      studentTable.innerHTML = `
        <table style="width: 100%; border-collapse: collapse; font-size: 0.88rem;">
          <thead>
            <tr style="border-bottom: 2px solid var(--border-color); text-align: left;">
              <th style="padding: 8px;">Name</th>
              <th style="padding: 8px;">Email</th>
              <th style="padding: 8px;">Goal</th>
            </tr>
          </thead>
          <tbody>
            ${data.students.map(s => `
              <tr style="border-bottom: 1px solid var(--border-color);">
                <td style="padding: 8px; font-weight: 600;">${s.name}</td>
                <td style="padding: 8px; color: var(--text-secondary);">${s.email}</td>
                <td style="padding: 8px;">${s.career_goal || 'Java Developer'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `;
    }

    if (currentRoadmapData && currentRoadmapData.nodes) {
      const qTopicSelect = document.getElementById('admin-q-topic');
      if (qTopicSelect) {
        qTopicSelect.innerHTML = currentRoadmapData.nodes.map(n => `<option value="${n.topic_id}">${n.topic_name}</option>`).join('');
      }
    }

  } catch (e) { console.error(e); }
}

async function handleAdminAddQuestion(e) {
  e.preventDefault();
  const payload = {
    assessment_id: document.getElementById('admin-q-topic').value,
    question_text: document.getElementById('admin-q-text').value,
    options: [
      document.getElementById('admin-q-opt-a').value,
      document.getElementById('admin-q-opt-b').value
    ],
    correct_answer: document.getElementById('admin-q-correct').value,
    difficulty: document.getElementById('admin-q-diff').value
  };

  try {
    const res = await fetch('/api/admin/questions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      alert("New question added to AI Question Bank!");
      document.getElementById('admin-add-question-form').reset();
      fetchAdminData();
    }
  } catch (err) {
    console.error("Add question error:", err);
  }
}
