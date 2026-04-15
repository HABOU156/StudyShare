
--STUDYSHARE


DROP DATABASE IF EXISTS StudyShare;
CREATE DATABASE StudyShare;
USE StudyShare;

-- 1. Tables de base
CREATE TABLE IF NOT EXISTS Universite ( 
    uid INT AUTO_INCREMENT,
    nom VARCHAR(50),
    PRIMARY KEY (uid)
);

CREATE TABLE IF NOT EXISTS Cours (  
    cid INT AUTO_INCREMENT,
    sigle VARCHAR(8),
    uid INT,
    PRIMARY KEY (cid),
    CONSTRAINT FK_C_Universite FOREIGN KEY (uid) REFERENCES Universite(uid)
);

-- 2. Utilisateurs et accès
CREATE TABLE IF NOT EXISTS Etudiants (  
    eid INT AUTO_INCREMENT,
    nom VARCHAR(50),
    uid INT,
    courriel VARCHAR(100) UNIQUE,
    passwordHash VARCHAR(255), 
    premium TINYINT(1) DEFAULT 0,
    PRIMARY KEY (eid),
    CONSTRAINT FK_E_Universite FOREIGN KEY (uid) REFERENCES Universite(uid)
);

CREATE TABLE IF NOT EXISTS Wallets (    
    wid INT AUTO_INCREMENT,
    solde DECIMAL(10,2) DEFAULT 0.00,
    payment_method VARCHAR(50),
    eid INT UNIQUE, 
    PRIMARY KEY (wid),
    CONSTRAINT FK_W_Etudiant FOREIGN KEY (eid) REFERENCES Etudiants(eid) ON DELETE CASCADE
);

-- 3. Fichiers et contenu
CREATE TABLE IF NOT EXISTS Fichiers (   
    fid INT AUTO_INCREMENT,
    lien_access VARCHAR(100),
    type ENUM('Cours', 'Résumé', 'Examen', 'Exercices'),
    cid INT, -- Ajouté : nécessaire pour la FK ci-dessous
    mise_en_ligne DATE,
    PRIMARY KEY (fid),
    CONSTRAINT FK_F_Cours FOREIGN KEY (cid) REFERENCES Cours(cid)
);

CREATE TABLE IF NOT EXISTS Acceder (
    aid INT AUTO_INCREMENT,
    eid INT,
    fid INT,
    date_visite DATE,
    nom_fichier VARCHAR(100),
    PRIMARY KEY (aid),
    CONSTRAINT FK_Acc_Etudiant FOREIGN KEY (eid) REFERENCES Etudiants(eid),
    CONSTRAINT FK_Acc_Fichier FOREIGN KEY (fid) REFERENCES Fichiers(fid)
);

-- 4. Social et Abonnements
CREATE TABLE IF NOT EXISTS Reviews (    
    rid INT AUTO_INCREMENT,
    eid INT,
    fid INT,
    date_de_mise_enligne DATE,
    note INT CHECK (note >= 1 AND note <= 5),
    PRIMARY KEY (rid),
    CONSTRAINT FK_R_Etudiant FOREIGN KEY (eid) REFERENCES Etudiants(eid),
    CONSTRAINT FK_R_Fichier FOREIGN KEY (fid) REFERENCES Fichiers(fid)
);

CREATE TABLE IF NOT EXISTS Comments (   
    com_id INT AUTO_INCREMENT, -- Renommé pour éviter conflit avec cid
    rid INT,
    titre VARCHAR(50),
    commentaire VARCHAR(200),
    PRIMARY KEY (com_id),
    CONSTRAINT FK_C_Review FOREIGN KEY (rid) REFERENCES Reviews(rid)
);

CREATE TABLE IF NOT EXISTS Abonnements (
    aid INT AUTO_INCREMENT,
    date_debut DATE,
    date_fin DATE,
    cout INT,
    eid INT,
    PRIMARY KEY (aid),
    CONSTRAINT FK_A_Etudiant FOREIGN KEY (eid) REFERENCES Etudiants(eid)
);
