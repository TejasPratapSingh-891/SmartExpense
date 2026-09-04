/**
 * SmartExpense Client Core Utilities
 * Theme switching, modals, toast alerts, mobile navigation, Lucide initialization
 */

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initMobileSidebar();
  initToasts();
  initModals();
  if (window.lucide) {
    window.lucide.createIcons();
  }
});

// Theme Management
function initTheme() {
  const toggleBtn = document.getElementById('themeToggleBtn');
  const storedTheme = localStorage.getItem('smartexpense_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', storedTheme);

  updateThemeIcon(storedTheme);

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('smartexpense_theme', newTheme);
      updateThemeIcon(newTheme);

      // Trigger custom event so Chart.js charts can re-render with appropriate colors
      window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: newTheme } }));
    });
  }
}

function updateThemeIcon(theme) {
  const sunIcon = document.getElementById('themeSunIcon');
  const moonIcon = document.getElementById('themeMoonIcon');
  if (sunIcon && moonIcon) {
    if (theme === 'light') {
      sunIcon.style.display = 'none';
      moonIcon.style.display = 'block';
    } else {
      sunIcon.style.display = 'block';
      moonIcon.style.display = 'none';
    }
  }
}

// Mobile Sidebar
function initMobileSidebar() {
  const toggle = document.getElementById('mobileMenuBtn');
  const sidebar = document.getElementById('sidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', () => {
      sidebar.classList.toggle('mobile-open');
    });

    // Close when clicking outside on mobile
    document.addEventListener('click', (e) => {
      if (sidebar.classList.contains('mobile-open') &&
          !sidebar.contains(e.target) &&
          !toggle.contains(e.target)) {
        sidebar.classList.remove('mobile-open');
      }
    });
  }
}

// Toast Notifications Auto-Dismiss
function initToasts() {
  const toasts = document.querySelectorAll('.toast');
  toasts.forEach(toast => {
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4500);

    const closeBtn = toast.querySelector('.toast-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => toast.remove());
    }
  });
}

// Modals
function initModals() {
  // Close buttons inside modals
  document.querySelectorAll('.modal-close-trigger').forEach(btn => {
    btn.addEventListener('click', () => {
      const modal = btn.closest('.modal-overlay');
      if (modal) {
        closeModal(modal.id);
      }
    });
  });

  // Close when clicking backdrop
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        closeModal(overlay.id);
      }
    });
  });
}

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }
}

// Global Currency Formatter
function formatCurrency(val, symbol = '₹') {
  const num = parseFloat(val) || 0;
  return symbol + num.toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}
