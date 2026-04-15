//aide chatgpt pour implementer la gestion de connection et deconnection 

(function () {
  'use strict';

  function updateNav(loggedIn) {
    var nav = document.querySelector('.site-nav');
    if (!nav) return;

    var connexionLink = nav.querySelector('a[href="connexion.html"]');
    if (!connexionLink) return;

    if (loggedIn) {
      var logoutLink = document.createElement('a');
      logoutLink.href = '#';
      logoutLink.textContent = 'Déconnexion';
      logoutLink.addEventListener('click', function (e) {
        e.preventDefault();
        fetch('/api/deconnexion', { method: 'POST', credentials: 'include' })
          .then(function () {
            if (window.StudyShareApi) {
              window.StudyShareApi.clearCurrentUser();
            }
            window.location.href = 'index.html';
          });
      });
      connexionLink.parentNode.replaceChild(logoutLink, connexionLink);
    }
  }

  fetch('/api/session-check', { credentials: 'include' })
    .then(function (res) { return res.json(); })
    .then(function (data) {
      updateNav(data && data.logged_in);
    })
    .catch(function () {
    });
})();
