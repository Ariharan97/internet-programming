/* ==========================================================================
   Gamification System Controller & UI Render Engine
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // Check for unread gamification notifications periodically
  setInterval(checkGamificationNotifications, 10000);
});

async function renderGamificationPage() {
  await fetchGamificationDashboard();
  await fetchBadges();
  await fetchChallenges();
  await fetchLeaderboard();
  await fetchRewards();
}

async function fetchGamificationDashboard() {
  try {
    const res = await fetch('/api/gamification/dashboard');
    const data = await res.json();
    renderGamificationBanner(data);
  } catch (err) {
    console.error("Gamification dashboard fetch error:", err);
  }
}

function renderGamificationBanner(data) {
  const container = document.getElementById('gamification-banner-container');
  if (!container) return;

  const activeMult = data.active_multiplier > 1.0 ? `<span class="badge badge-weak" style="margin-left: 10px;"><i class="fa-solid fa-bolt"></i> ${data.active_multiplier}X XP Booster Active</span>` : '';

  container.innerHTML = `
    <div class="card" style="background: linear-gradient(135deg, rgba(79,70,229,0.12), rgba(6,182,212,0.12)); border: 1px solid var(--primary-light); margin-bottom: 24px;">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px;">
        
        <div style="display: flex; align-items: center; gap: 20px;">
          <div class="stat-icon primary" style="width: 72px; height: 72px; font-size: 2.2rem; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white;">
            <i class="fa-solid fa-${data.level_icon || 'trophy'}"></i>
          </div>
          <div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="badge badge-strong" style="font-size: 0.9rem; padding: 4px 12px;">LEVEL ${data.level}</span>
              <h2 style="font-size: 1.6rem; font-weight: 800; display: inline;">"${data.level_name}"</h2>
              ${activeMult}
            </div>
            <div style="color: var(--text-secondary); font-size: 0.95rem; margin-top: 4px;">
              Total Experience: <strong>${data.total_xp.toLocaleString()} XP</strong> • Next Level: <strong>${data.xp_to_next_level} XP needed</strong>
            </div>
          </div>
        </div>

        <div style="display: flex; gap: 20px; align-items: center;">
          <div class="card stat-card" style="padding: 12px 20px; background-color: var(--bg-card);">
            <div class="stat-icon warning" style="width: 44px; height: 44px; font-size: 1.3rem;"><i class="fa-solid fa-fire"></i></div>
            <div class="stat-info">
              <div class="stat-value" style="font-size: 1.3rem;">${data.current_streak} Days</div>
              <div class="stat-label">Daily Streak (Shields: ${data.streak_shields})</div>
            </div>
          </div>

          <div class="card stat-card" style="padding: 12px 20px; background-color: var(--bg-card);">
            <div class="stat-icon secondary" style="width: 44px; height: 44px; font-size: 1.3rem;"><i class="fa-solid fa-coins"></i></div>
            <div class="stat-info">
              <div class="stat-value" style="font-size: 1.3rem;">🪙 ${data.coins}</div>
              <div class="stat-label">Learning Coins</div>
            </div>
          </div>
        </div>

      </div>

      <!-- Level Progress Bar -->
      <div style="margin-top: 20px;">
        <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 600; margin-bottom: 6px;">
          <span>Progress to Level ${data.level + 1}</span>
          <span>${data.level_progress_percentage}%</span>
        </div>
        <div class="progress-container" style="height: 12px;">
          <div class="progress-bar" style="width: ${data.level_progress_percentage}%;"></div>
        </div>
      </div>
    </div>
  `;
}

async function fetchBadges() {
  try {
    const res = await fetch('/api/gamification/badges');
    const badges = await res.json();
    renderBadgesGrid(badges);
  } catch (err) {
    console.error("Badges fetch error:", err);
  }
}

function renderBadgesGrid(badges) {
  const container = document.getElementById('badges-grid-container');
  if (!container) return;

  container.innerHTML = badges.map(b => {
    const isUnlocked = b.is_unlocked;
    const cardBg = isUnlocked ? 'var(--bg-card)' : 'var(--bg-tertiary)';
    const opacity = isUnlocked ? '1' : '0.6';
    const statusTag = isUnlocked ? '<span class="badge badge-mastered">🏆 Unlocked</span>' : '<span class="badge badge-locked">🔒 Locked</span>';

    return `
      <div class="card" style="background: ${cardBg}; opacity: ${opacity}; text-align: center; padding: 20px; border: 1px solid ${isUnlocked ? 'var(--primary-light)' : 'var(--border-color)'};">
        <div class="stat-icon ${isUnlocked ? 'primary' : 'secondary'}" style="margin: 0 auto 12px; width: 60px; height: 60px; font-size: 1.8rem;">
          <i class="fa-solid fa-${b.icon || 'trophy'}"></i>
        </div>
        <h4 style="font-size: 1.05rem; margin-bottom: 4px;">${b.title}</h4>
        <p style="font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 12px; height: 36px; overflow: hidden;">${b.description}</p>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
          <span style="font-size: 0.78rem; font-weight: 700; color: var(--primary);">+${b.bonus_xp} XP</span>
          ${statusTag}
        </div>
      </div>
    `;
  }).join('');
}

async function fetchChallenges() {
  try {
    const res = await fetch('/api/gamification/challenges');
    const challenges = await res.json();
    renderChallengesList(challenges);
  } catch (err) {
    console.error("Challenges fetch error:", err);
  }
}

function renderChallengesList(challenges) {
  const container = document.getElementById('challenges-list-container');
  if (!container) return;

  container.innerHTML = challenges.map(c => {
    const isDone = c.is_completed === 1;
    const isAi = c.is_personalized === 1;
    const badgeTag = isAi ? '<span class="badge badge-weak"><i class="fa-solid fa-wand-magic-sparkles"></i> AI Personalized</span>' : '<span class="badge badge-average">Daily</span>';

    return `
      <div class="card" style="margin-bottom: 16px; border-left: 4px solid ${isAi ? 'var(--warning)' : 'var(--primary)'};">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
              ${badgeTag}
              <h4 style="font-size: 1.1rem; font-weight: 700;">${c.title}</h4>
            </div>
            <p style="font-size: 0.88rem; color: var(--text-secondary);">${c.description}</p>
          </div>
          <div style="text-align: right;">
            <div style="font-weight: 800; font-size: 1rem; color: var(--primary);">+${c.reward_xp} XP • 🪙 +${c.reward_coins} Coins</div>
            ${isDone
              ? '<span class="badge badge-mastered" style="margin-top: 6px;"><i class="fa-solid fa-check"></i> Completed</span>'
              : `<button class="btn btn-primary btn-sm" style="margin-top: 6px;" onclick="claimChallenge(${c.id})">Claim Reward</button>`
            }
          </div>
        </div>
      </div>
    `;
  }).join('');
}

async function claimChallenge(challengeId) {
  try {
    const res = await fetch('/api/gamification/complete-challenge', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ challenge_id: challengeId })
    });
    const data = await res.json();
    if (res.ok) {
      showToast(`🎯 Challenge Completed!`, `You earned +${data.earned_xp} XP and +${data.earned_coins} Coins!`, 'success');
      await renderGamificationPage();
    } else {
      alert(data.error || "Could not claim challenge.");
    }
  } catch (err) {
    console.error(err);
  }
}

async function fetchLeaderboard(timeframe = 'all_time') {
  try {
    const res = await fetch(`/api/gamification/leaderboard?timeframe=${timeframe}`);
    const board = await res.json();
    renderLeaderboardTable(board);
  } catch (err) {
    console.error("Leaderboard fetch error:", err);
  }
}

function renderLeaderboardTable(board) {
  const container = document.getElementById('leaderboard-table-container');
  if (!container) return;

  container.innerHTML = `
    <table style="width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 0.92rem;">
      <thead>
        <tr style="border-bottom: 2px solid var(--border-color); text-align: left;">
          <th style="padding: 10px;">Rank</th>
          <th style="padding: 10px;">Student Name</th>
          <th style="padding: 10px;">Level</th>
          <th style="padding: 10px;">Total XP</th>
          <th style="padding: 10px;">Streak</th>
          <th style="padding: 10px;">Badges</th>
        </tr>
      </thead>
      <tbody>
        ${board.map(r => {
          let rankMedal = `#${r.rank}`;
          if (r.rank === 1) rankMedal = '🥇 1st';
          if (r.rank === 2) rankMedal = '🥈 2nd';
          if (r.rank === 3) rankMedal = '🥉 3rd';

          return `
            <tr style="border-bottom: 1px solid var(--border-color);">
              <td style="padding: 12px; font-weight: 800;">${rankMedal}</td>
              <td style="padding: 12px; font-weight: 600;">${r.name}</td>
              <td style="padding: 12px;"><span class="badge badge-strong">Lvl ${r.level} (${r.level_name})</span></td>
              <td style="padding: 12px; font-weight: 800; color: var(--primary);">${r.total_xp.toLocaleString()} XP</td>
              <td style="padding: 12px;">🔥 ${r.streak} Days</td>
              <td style="padding: 12px;">🏆 ${r.badge_count}</td>
            </tr>
          `;
        }).join('')}
      </tbody>
    </table>
  `;
}

async function fetchRewards() {
  try {
    const res = await fetch('/api/gamification/rewards');
    const data = await res.json();
    renderRewardShopGrid(data.rewards, data.user_coins);
  } catch (err) {
    console.error("Rewards fetch error:", err);
  }
}

function renderRewardShopGrid(rewards, userCoins) {
  const container = document.getElementById('reward-shop-grid-container');
  if (!container) return;

  container.innerHTML = rewards.map(r => {
    const isOwned = r.is_owned;
    const canAfford = userCoins >= r.cost_coins;

    let btnHtml = `<button class="btn btn-primary btn-sm" style="width: 100%;" onclick="redeemRewardItem(${r.id})">Redeem for 🪙 ${r.cost_coins}</button>`;
    if (isOwned) {
      btnHtml = `<span class="badge badge-mastered" style="width: 100%; justify-content: center; padding: 8px;"><i class="fa-solid fa-check"></i> Owned</span>`;
    } else if (!canAfford) {
      btnHtml = `<button class="btn btn-secondary btn-sm" style="width: 100%; opacity: 0.6;" disabled>Requires 🪙 ${r.cost_coins}</button>`;
    }

    return `
      <div class="card" style="text-align: center; padding: 20px;">
        <div class="stat-icon secondary" style="margin: 0 auto 12px; width: 60px; height: 60px; font-size: 1.8rem;">
          <i class="fa-solid fa-${r.icon || 'gift'}"></i>
        </div>
        <h4>${r.title}</h4>
        <p style="font-size: 0.85rem; color: var(--text-secondary); margin: 6px 0 16px; height: 36px; overflow: hidden;">${r.description}</p>
        ${btnHtml}
      </div>
    `;
  }).join('');
}

async function redeemRewardItem(rewardId) {
  try {
    const res = await fetch('/api/gamification/redeem-reward', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reward_id: rewardId })
    });
    const data = await res.json();
    if (res.ok) {
      showToast('🎁 Item Unlocked!', data.message, 'success');
      await renderGamificationPage();
    } else {
      alert(data.message || "Failed to redeem reward.");
    }
  } catch (err) {
    console.error(err);
  }
}

/* Check Unread Notifications & Toast Engine */
async function checkGamificationNotifications() {
  try {
    const res = await fetch('/api/gamification/notifications');
    if (!res.ok) return;
    const notifs = await res.json();

    if (notifs && notifs.length > 0) {
      notifs.forEach(n => {
        showToast(n.title, n.message, n.type);
      });
      // Mark as read
      await fetch('/api/gamification/notifications/read', { method: 'POST' });
    }
  } catch (err) {
    console.error("Notifications check error:", err);
  }
}

function showToast(title, message, type = 'info') {
  let toastContainer = document.getElementById('toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.style.cssText = 'position: fixed; bottom: 24px; right: 24px; z-index: 9999; display: flex; flex-direction: column; gap: 12px; max-width: 380px;';
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement('div');
  toast.className = 'card';
  toast.style.cssText = 'background: var(--bg-card); border: 1px solid var(--primary); box-shadow: var(--shadow-xl); padding: 16px 20px; border-left: 5px solid var(--primary); animation: fadeIn 0.3s ease;';

  toast.innerHTML = `
    <div style="display: flex; align-items: flex-start; gap: 12px;">
      <div style="font-size: 1.4rem; color: var(--primary);"><i class="fa-solid fa-wand-magic-sparkles"></i></div>
      <div style="flex: 1;">
        <div style="font-weight: 800; font-size: 1rem; color: var(--text-primary);">${title}</div>
        <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 2px;">${message}</div>
      </div>
      <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; font-size: 1.1rem; color: var(--text-muted); cursor: pointer;">&times;</button>
    </div>
  `;

  toastContainer.appendChild(toast);

  setTimeout(() => {
    if (toast.parentElement) toast.remove();
  }, 6000);
}
