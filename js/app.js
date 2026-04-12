(function () {
  'use strict';

  function showAlert(message, type, container) {
    if (!message || typeof message !== 'string') return;
    var containerEl = container || document.querySelector('main .container') || document.body;
    var div = document.createElement('div');
    div.className = 'alert alert-' + (type || 'info');
    div.setAttribute('role', 'alert');
    div.textContent = message;
    containerEl.insertBefore(div, containerEl.firstChild);
    return div;
  }

  function clearAlerts(container) {
    var selector = container || document;
    var alerts = selector.querySelectorAll('.alert');
    alerts.forEach(function (el) { el.remove(); });
  }

  function setFieldError(field, message) {
    if (!field) return;
    field.classList.add('error');
    var help = field.closest('.form-group');
    if (help) {
      var errEl = help.querySelector('.form-error');
      if (errEl) errEl.textContent = message;
      else {
        var span = document.createElement('span');
        span.className = 'form-error';
        span.textContent = message;
        help.appendChild(span);
      }
    }
  }

  function clearFieldError(field) {
    if (!field) return;
    field.classList.remove('error');
    var help = field.closest('.form-group');
    if (help) {
      var errEl = help.querySelector('.form-error');
      if (errEl) errEl.remove();
    }
  }

  function clearFormErrors(form) {
    if (!form) return;
    form.querySelectorAll('.error').forEach(function (el) { el.classList.remove('error'); });
    form.querySelectorAll('.form-error').forEach(function (el) { el.remove(); });
  }

  window.StudyShare = window.StudyShare || {};
  window.StudyShare.showAlert = showAlert;
  window.StudyShare.clearAlerts = clearAlerts;
  window.StudyShare.setFieldError = setFieldError;
  window.StudyShare.clearFieldError = clearFieldError;
  window.StudyShare.clearFormErrors = clearFormErrors;
})();
