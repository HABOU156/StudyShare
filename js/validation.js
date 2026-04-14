(function () {
  'use strict';

  var LIMITS = {
    emailMin: 5,
    emailMax: 255,
    passwordMin: 8,
    passwordMax: 128,
    nomMax: 100,
    universiteMax: 200,
    titreMax: 200,
    commentMax: 2000,
    nomGroupeMax: 100,
    noteMin: 1,
    noteMax: 5
  };

  var EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

  function validateEmail(value) {
    if (value === undefined || value === null) {
      return { valid: false, message: 'Le courriel est requis.' };
    }
    var str = String(value).trim();
    if (str.length === 0) {
      return { valid: false, message: 'Le courriel est requis.' };
    }
    if (str.length < LIMITS.emailMin || str.length > LIMITS.emailMax) {
      return { valid: false, message: 'Le courriel doit contenir entre ' + LIMITS.emailMin + ' et ' + LIMITS.emailMax + ' caractères.' };
    }
    if (!EMAIL_REGEX.test(str)) {
      return { valid: false, message: 'Le format du courriel est invalide.' };
    }
    return { valid: true };
  }

  function validatePassword(value, confirm) {
    if (value === undefined || value === null) {
      return { valid: false, message: 'Le mot de passe est requis.' };
    }
    var str = String(value);
    if (str.length < LIMITS.passwordMin) {
      return { valid: false, message: 'Le mot de passe doit contenir au moins ' + LIMITS.passwordMin + ' caractères.' };
    }
    if (str.length > LIMITS.passwordMax) {
      return { valid: false, message: 'Le mot de passe ne doit pas dépasser ' + LIMITS.passwordMax + ' caractères.' };
    }
    if (confirm !== undefined && confirm !== null && String(confirm) !== str) {
      return { valid: false, message: 'Les deux mots de passe ne correspondent pas.' };
    }
    return { valid: true };
  }

  function validateNom(value) {
    if (value === undefined || value === null) {
      return { valid: false, message: 'Le nom est requis.' };
    }
    var str = String(value).trim();
    if (str.length === 0) {
      return { valid: false, message: 'Le nom est requis.' };
    }
    if (str.length > LIMITS.nomMax) {
      return { valid: false, message: 'Le nom ne doit pas dépasser ' + LIMITS.nomMax + ' caractères.' };
    }
    return { valid: true };
  }

  function validateUniversite(value) {
    if (value === undefined || value === null) {
      return { valid: false, message: "L'université est requise." };
    }
    var str = String(value).trim();
    if (str.length === 0) {
      return { valid: false, message: "L'université est requise." };
    }
    if (str.length > LIMITS.universiteMax) {
      return { valid: false, message: "L'université ne doit pas dépasser " + LIMITS.universiteMax + " caractères." };
    }
    return { valid: true };
  }

  function validateTitre(value, required) {
    var str = value === undefined || value === null ? '' : String(value).trim();
    if (required && str.length === 0) {
      return { valid: false, message: 'Le titre est requis.' };
    }
    if (str.length > LIMITS.titreMax) {
      return { valid: false, message: 'Le titre ne doit pas dépasser ' + LIMITS.titreMax + ' caractères.' };
    }
    return { valid: true };
  }

  function validateComment(value, required) {
    var str = value === undefined || value === null ? '' : String(value).trim();
    if (required && str.length === 0) {
      return { valid: false, message: 'Le commentaire est requis.' };
    }
    if (str.length > LIMITS.commentMax) {
      return { valid: false, message: 'Le commentaire ne doit pas dépasser ' + LIMITS.commentMax + ' caractères.' };
    }
    return { valid: true };
  }

  function validateNote(value) {
    if (value === undefined || value === null || value === '') {
      return { valid: false, message: 'La note est requise.' };
    }
    var num = parseInt(value, 10);
    if (isNaN(num) || num < LIMITS.noteMin || num > LIMITS.noteMax) {
      return { valid: false, message: 'La note doit être entre ' + LIMITS.noteMin + ' et ' + LIMITS.noteMax + '.' };
    }
    return { valid: true };
  }

  function validateNomGroupe(value) {
    if (value === undefined || value === null) {
      return { valid: false, message: 'Le nom du groupe est requis.' };
    }
    var str = String(value).trim();
    if (str.length === 0) {
      return { valid: false, message: 'Le nom du groupe est requis.' };
    }
    if (str.length > LIMITS.nomGroupeMax) {
      return { valid: false, message: 'Le nom du groupe ne doit pas dépasser ' + LIMITS.nomGroupeMax + ' caractères.' };
    }
    return { valid: true };
  }

  function validateTypeFichier(value) {
    var allowed = ['Cours', 'Résumé', 'Examen', 'Exercices'];
    if (value === undefined || value === null || value === '') {
      return { valid: false, message: 'Le type de document est requis.' };
    }
    if (allowed.indexOf(String(value)) === -1) {
      return { valid: false, message: 'Type de document invalide.' };
    }
    return { valid: true };
  }

  function validateMontant(value) {
    if (value === undefined || value === null || value === '') {
      return { valid: false, message: 'Le montant est requis.' };
    }
    var num = parseFloat(String(value).replace(',', '.'));
    if (isNaN(num) || num <= 0) {
      return { valid: false, message: 'Le montant doit être supérieur à 0.' };
    }
    return { valid: true };
  }

  function validateFileUpload(file, maxSizeBytes) {
    if (!file || !(file instanceof File)) {
      return { valid: false, message: 'Veuillez sélectionner un fichier.' };
    }
    var max = maxSizeBytes || 10 * 1024 * 1024;
    if (file.size > max) {
      return { valid: false, message: 'Le fichier ne doit pas dépasser ' + (max / (1024 * 1024)) + ' Mo.' };
    }
    var allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'image/jpeg', 'image/png'];
    if (file.type && allowedTypes.indexOf(file.type) === -1) {
      return { valid: false, message: 'Type de fichier non autorisé. Autorisés : PDF, Word, TXT, images.' };
    }
    return { valid: true };
  }

  window.StudyShare = window.StudyShare || {};
  window.StudyShare.validation = {
    validateEmail: validateEmail,
    validatePassword: validatePassword,
    validateNom: validateNom,
    validateUniversite: validateUniversite,
    validateTitre: validateTitre,
    validateComment: validateComment,
    validateNote: validateNote,
    validateNomGroupe: validateNomGroupe,
    validateTypeFichier: validateTypeFichier,
    validateMontant: validateMontant,
    validateFileUpload: validateFileUpload,
    LIMITS: LIMITS
  };
})();
