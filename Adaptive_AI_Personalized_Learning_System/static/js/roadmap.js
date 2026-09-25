/* ==========================================================================
   Interactive Roadmap Timeline Visualizer
   ========================================================================== */

function renderRoadmapTimeline(roadmapData, containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  if (!roadmapData || !roadmapData.nodes || roadmapData.nodes.length === 0) {
    container.innerHTML = `
      <div class="card" style="text-align: center; padding: 40px;">
        <i class="fa-solid fa-route" style="font-size: 2.5rem; color: var(--text-muted); margin-bottom: 12px;"></i>
        <h3>No AI Roadmap Nodes Found</h3>
        <p style="color: var(--text-secondary);">Select a target career goal in your student profile to generate your roadmap.</p>
      </div>
    `;
    return;
  }

  let html = `
    <!-- Top Summary Banner -->
    <div class="grid-cols-4" style="margin-bottom: 24px;">
      <div class="card stat-card" style="padding: 16px;">
        <div class="stat-icon primary"><i class="fa-solid fa-list-ol"></i></div>
        <div class="stat-info">
          <div class="stat-value" style="font-size: 1.4rem;">${roadmapData.total_topics}</div>
          <div class="stat-label">Total Modules</div>
        </div>
      </div>
      <div class="card stat-card" style="padding: 16px;">
        <div class="stat-icon success"><i class="fa-solid fa-check-double"></i></div>
        <div class="stat-info">
          <div class="stat-value" style="font-size: 1.4rem;">${roadmapData.completed_topics}</div>
          <div class="stat-label">Completed</div>
        </div>
      </div>
      <div class="card stat-card" style="padding: 16px;">
        <div class="stat-icon warning"><i class="fa-solid fa-clock"></i></div>
        <div class="stat-info">
          <div class="stat-value" style="font-size: 1.4rem;">${roadmapData.total_estimated_hours}h</div>
          <div class="stat-label">Total Est. Hours</div>
        </div>
      </div>
      <div class="card stat-card" style="padding: 16px;">
        <div class="stat-icon secondary"><i class="fa-solid fa-calendar-day"></i></div>
        <div class="stat-info">
          <div class="stat-value" style="font-size: 1.4rem;">${roadmapData.estimated_completion_days} Days</div>
          <div class="stat-label">Est. Completion</div>
        </div>
      </div>
    </div>

    <!-- Node Graph Step Banner -->
    <div style="background-color: var(--bg-tertiary); padding: 12px 20px; border-radius: var(--radius-md); font-size: 0.85rem; font-weight: 600; display: flex; gap: 8px; align-items: center; margin-bottom: 20px;">
      <i class="fa-solid fa-circle-info" style="color: var(--primary);"></i>
      <span>Interactive Nodes: Click any topic card to view prerequisite details, recommended practice, and launch diagnostic quizzes.</span>
    </div>
  `;

  roadmapData.nodes.forEach((node) => {
    let statusBadgeClass = 'badge-weak';
    let statusText = node.status;
    let numberClass = '';
    let icon = '<i class="fa-solid fa-book-open"></i>';

    if (node.status === 'Mastered' || node.status === 'Completed') {
      statusBadgeClass = 'badge-mastered';
      numberClass = 'mastered';
      icon = '<i class="fa-solid fa-check"></i>';
    } else if (node.status.includes('Weak') || node.status.includes('Missing')) {
      statusBadgeClass = 'badge-missing';
      numberClass = 'weak';
      icon = '<i class="fa-solid fa-triangle-exclamation"></i>';
    } else if (node.priority.includes('High')) {
      statusBadgeClass = 'badge-weak';
      icon = '<i class="fa-solid fa-play"></i>';
    }

    const prereqsHtml = node.prerequisites && node.prerequisites.length > 0
      ? node.prerequisites.map(p => `<span class="badge badge-locked" style="font-size:0.72rem; padding: 2px 8px;"><i class="fa-solid fa-link"></i> ${p}</span>`).join(' ')
      : '<span style="color: var(--text-muted); font-size: 0.8rem;">None (Foundational)</span>';

    html += `
      <div class="roadmap-node-card" onclick="openTopicModal(${node.topic_id})">
        <div class="node-number ${numberClass}">
          ${icon}
        </div>
        <div class="node-content">
          <div class="node-title-row">
            <h4 class="node-title">${node.sequence_order}. ${node.topic_name}</h4>
            <div>
              <span class="badge ${statusBadgeClass}">${statusText}</span>
              <span class="badge badge-average" style="margin-left: 6px;">${node.priority}</span>
            </div>
          </div>

          <p style="font-size: 0.9rem; color: var(--text-secondary);">${node.description || 'Core module for target career path.'}</p>

          <div class="node-meta">
            <span><i class="fa-solid fa-clock"></i> ${node.estimated_hours} Hours</span>
            <span><i class="fa-solid fa-signal"></i> ${node.difficulty}</span>
            <span><i class="fa-solid fa-award"></i> Mastery: <strong>${node.mastery_score}%</strong></span>
          </div>

          <div style="margin-top: 10px; display: flex; align-items: center; gap: 8px; font-size: 0.82rem; color: var(--text-muted);">
            <span>Prerequisites:</span>
            <div style="display: flex; gap: 4px; flex-wrap: wrap;">${prereqsHtml}</div>
          </div>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}
