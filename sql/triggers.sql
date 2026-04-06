-- Person 1 triggers
-- Objects defined in this file:
--   before_orders_mark_paid

DROP TRIGGER IF EXISTS before_orders_mark_paid;

DELIMITER $$

CREATE TRIGGER before_orders_mark_paid
BEFORE UPDATE ON Orders
FOR EACH ROW
BEGIN
    DECLARE v_valid_account_count INTEGER DEFAULT 0;

    IF NEW.status = 'PAID' AND OLD.status <> 'PAID' THEN
        IF OLD.status <> 'CREATED' THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'APP_ERROR|BAD_REQUEST|400|Order cannot be paid in its current state';
        END IF;

        IF NEW.acc_no IS NULL THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'APP_ERROR|INVALID_ACCOUNT|400|Selected bank account is invalid';
        END IF;

        SELECT COUNT(*)
        INTO v_valid_account_count
        FROM Bank_acc
        WHERE acc_no = NEW.acc_no
          AND u_id = OLD.u_id
          AND expiry_date >= CURDATE();

        IF v_valid_account_count = 0 THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'APP_ERROR|INVALID_ACCOUNT|400|Selected bank account is invalid';
        END IF;
    END IF;
END$$

DELIMITER ;
