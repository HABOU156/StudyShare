USE StudyShare;

DELIMITER //

CREATE PROCEDURE sp_AcheterAbonnement(IN p_eid INT, IN p_cout DECIMAL(10,2))
BEGIN
    DECLARE v_solde DECIMAL(10,2);
    
    -- Récupération du solde
    SELECT solde INTO v_solde FROM Wallets WHERE eid = p_eid;
    
    IF v_solde >= p_cout THEN
        UPDATE Wallets SET solde = solde - p_cout WHERE eid = p_eid;
        UPDATE Etudiants SET premium = 1 WHERE eid = p_eid;
        INSERT INTO Abonnements (date_debut, date_fin, cout, eid)
        VALUES (CURDATE(), DATE_ADD(CURDATE(), INTERVAL 6 MONTH), p_cout, p_eid);
        
        SELECT 'SUCCESS' AS result;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Fonds insuffisants pour cet achat.';
    END IF;
END //

-- Trigger pour protéger le quota des 5 fichiers
CREATE TRIGGER tg_VerifierQuotaAccès
BEFORE INSERT ON Acceder
FOR EACH ROW
BEGIN
    DECLARE v_premium TINYINT;
    DECLARE v_count INT;

    SELECT premium INTO v_premium FROM Etudiants WHERE eid = NEW.eid;

    IF v_premium = 0 THEN
        SELECT COUNT(DISTINCT fid) INTO v_count FROM Acceder WHERE eid = NEW.eid;
        
        IF v_count >= 5 THEN
            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 'Limite de 5 fichiers atteinte. Passez Premium !';
        END IF;
    END IF;
END //

DELIMITER ;