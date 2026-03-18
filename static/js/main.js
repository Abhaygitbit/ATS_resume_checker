// Shared utilities for ATS Pro

/**
 * Lightweight toast notification
 */
function showToast(message, type = 'info') {
  const colors = { info: '#3B82F6', success: '#10B981', error: '#EF4444', warning: '#F59E0B' };
  const toast = document.createElement('div');
  toast.style.cssText = `
    position:fixed; bottom:24px; right:24px; z-index:9999;
    background:#1E2535; border:1px solid ${colors[type]};
    color:#F1F5F9; padding:14px 20px; border-radius:12px;
    font-family:'DM Sans',sans-serif; font-size:14px; font-weight:500;
    box-shadow:0 8px 32px rgba(0,0,0,0.5);
    transform:translateY(20px); opacity:0;
    transition:all 0.3s ease; max-width:360px;
  `;
  toast.textContent = message;
  document.body.appendChild(toast);
  requestAnimationFrame(() => { toast.style.opacity = '1'; toast.style.transform = 'translateY(0)'; });
  setTimeout(() => {
    toast.style.opacity = '0'; toast.style.transform = 'translateY(20px)';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

/**
 * Format date string
 */
function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

/**
 * Score color utility
 */
function getScoreColor(score) {
  if (score >= 75) return '#10B981';
  if (score >= 50) return '#F59E0B';
  return '#EF4444';
}
