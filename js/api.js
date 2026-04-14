(function () {
  'use strict';

  var STORAGE_KEY = 'studyshare_user';

  function getBase() {
    if (typeof window !== 'undefined' && window.STUDYSHARE_API_BASE) {
      return String(window.STUDYSHARE_API_BASE).replace(/\/$/, '');
    }
    // Site servi par Flask sur le même hôte/port → API en relatif (aucun port codé en dur)
    if (typeof window !== 'undefined' && window.location && window.location.protocol &&
        window.location.protocol.indexOf('http') === 0) {
      return window.location.origin;
    }
    return 'http://127.0.0.1:5050';
  }

  function parseJsonSafe(res) {
    return res.text().then(function (text) {
      try {
        return text ? JSON.parse(text) : {};
      } catch (e) {
        return {};
      }
    });
  }

  function requestJson(path, options) {
    var url = getBase() + path;
    var opts = options || {};
    var headers = opts.headers || {};
    if (opts.body && typeof opts.body === 'string' && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }
    return fetch(url, {
      method: opts.method || 'GET',
      headers: headers,
      body: opts.body,
      credentials: 'omit'
    }).then(function (res) {
      return parseJsonSafe(res).then(function (data) {
        if (!res.ok) {
          var err = new Error((data && data.message) || res.statusText || 'Erreur réseau');
          err.status = res.status;
          err.data = data;
          throw err;
        }
        return data;
      });
    });
  }

  function getCurrentUser() {
    try {
      var raw = sessionStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function setCurrentUser(user) {
    if (!user) {
      sessionStorage.removeItem(STORAGE_KEY);
      return;
    }
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(user));
  }

  function clearCurrentUser() {
    sessionStorage.removeItem(STORAGE_KEY);
  }

  function titreDepuisLien(lien) {
    if (!lien) return 'Document';
    var base = String(lien).split('/').pop() || lien;
    return base.replace(/\.[^.]+$/, '').replace(/_/g, ' ');
  }

  function mapFichierPourUi(row) {
    if (!row) return null;
    var note = row.note_moyenne != null ? Number(row.note_moyenne) : 0;
    return {
      id: row.fid,
      type: row.type,
      titre: titreDepuisLien(row.lien_access),
      cours: row.sigle_cours || '—',
      date: row.mise_en_ligne ? String(row.mise_en_ligne) : '',
      note: note > 0 ? Math.min(5, Math.max(1, Math.round(note))) : 0,
      lien_access: row.lien_access,
      raw: row
    };
  }

  window.StudyShareApi = {
    getBase: getBase,
    getCurrentUser: getCurrentUser,
    setCurrentUser: setCurrentUser,
    clearCurrentUser: clearCurrentUser,
    requestJson: requestJson,
    titreDepuisLien: titreDepuisLien,
    mapFichierPourUi: mapFichierPourUi,

    login: function (courriel, password) {
      return requestJson('/api/connexion', {
        method: 'POST',
        body: JSON.stringify({ courriel: courriel, password: password })
      });
    },

    register: function (payload) {
      return requestJson('/api/inscription', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
    },

    getUniversites: function () {
      return requestJson('/api/universites');
    },

    getFichiers: function () {
      return requestJson('/api/fichiers');
    },

    getFichier: function (fid) {
      return requestJson('/api/fichiers/' + encodeURIComponent(fid));
    },

    getCours: function () {
      return requestJson('/api/cours');
    },

    getWallet: function (eid) {
      return requestJson('/api/wallet/' + encodeURIComponent(eid));
    },

    depotWallet: function (eid, montant) {
      return requestJson('/api/wallet/depot', {
        method: 'POST',
        body: JSON.stringify({ eid: eid, montant: montant })
      });
    },

    devenirPremium: function (eid) {
      return requestJson('/api/devenir-premium', {
        method: 'POST',
        body: JSON.stringify({ eid: eid })
      });
    },

    uploadFichier: function (formData) {
      var url = getBase() + '/api/fichiers/upload';
      return fetch(url, { method: 'POST', body: formData, credentials: 'omit' }).then(function (res) {
        return parseJsonSafe(res).then(function (data) {
          if (!res.ok) {
            var err = new Error((data && data.message) || 'Échec du téléversement');
            err.status = res.status;
            err.data = data;
            throw err;
          }
          return data;
        });
      });
    },

    postReview: function (body) {
      return requestJson('/api/fichiers/review', {
        method: 'POST',
        body: JSON.stringify(body)
      });
    },

    getReviewsFichier: function (fid) {
      return requestJson('/api/fichiers/' + encodeURIComponent(fid) + '/reviews');
    },

    downloadUrlPourFid: function (fid) {
      return getBase() + '/api/fichiers/' + encodeURIComponent(fid) + '/download';
    },

    previewUrlPourFid: function (fid) {
      return getBase() + '/api/fichiers/' + encodeURIComponent(fid) + '/preview';
    }
  };
})();
