
CREATE TABLE IF NOT EXISTS Universite ( uid int,
					nom varchar(50),
                    
					PRIMARY KEY (uid));
                                
CREATE TABLE IF NOT EXISTS Cours ( 	cid int,
					sigle varchar(8),
					uid int,
                    
					PRIMARY KEY (cid),
					CONSTRAINT FK_C_Universite FOREIGN KEY (uid) REFERENCES Universite(uid));

CREATE TABLE IF NOT EXISTS Etudiants (  eid int,
					nom varchar(50),
					uid int,
					email varchar(100) UNIQUE,
					passwordHash varchar(100),
                    
					PRIMARY KEY (eid),
					CONSTRAINT FK_E_Universite FOREIGN KEY (uid) REFERENCES Universite(uid));

CREATE TABLE IF NOT EXISTS Fichiers ( 	fid int,
					lien_daccess varchar(100),
					type_document ENUM('Cours', 'Résumé', 'Examen', 'Exercices'),
					cid int,
					mise_en_ligne DATE,
                    
					PRIMARY KEY (fid),
					CONSTRAINT FK_F_Cours FOREIGN KEY (cid) REFERENCES Cours(cid));

CREATE TABLE IF NOT EXISTS Wallets ( 	wid int,
					solde int,
					payment_method varchar(50),
                    
					PRIMARY KEY (wid));
				
CREATE TABLE IF NOT EXISTS Reviews ( 	rid int,
					eid int,
					fid int,
					mise_en_ligne DATE,
					note int CHECK (note > 0 AND note < 6),
					
					PRIMARY KEY (rid),
					CONSTRAINT FK_R_Etudiant FOREIGN KEY (eid) REFERENCES Etudiants(eid),
					CONSTRAINT FK_R_Fichier FOREIGN KEY (fid) REFERENCES Fichiers(fid));


CREATE TABLE IF NOT EXISTS Comments ( 	cid int,
					rid int,
					titre varchar(50),
					commentaire varchar(200),
					
					PRIMARY KEY (cid),
					CONSTRAINT FK_C_Review FOREIGN KEY (rid) REFERENCES Reviews(rid));

CREATE TABLE IF NOT EXISTS Abonnements (aid int,
					date_debut DATE,
					date_fin DATE,
					cout int,
					eid int,
					
					PRIMARY KEY (aid),
					CONSTRAINT FK_A_Etudiant FOREIGN KEY (eid) REFERENCES Etudiants(eid));

