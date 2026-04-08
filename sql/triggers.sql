-- Person 1 triggers
-- Objects defined in this file:
--   before_orders_mark_paid
--   before_ordered_items_insert
--   before_ordered_items_update
--   after_ordered_items_insert
--   after_ordered_items_update
--   after_ordered_items_delete

DROP TRIGGER IF EXISTS before_orders_mark_paid;
DROP TRIGGER IF EXISTS before_ordered_items_insert;
DROP TRIGGER IF EXISTS before_ordered_items_update;
DROP TRIGGER IF EXISTS after_ordered_items_insert;
DROP TRIGGER IF EXISTS after_ordered_items_update;
DROP TRIGGER IF EXISTS after_ordered_items_delete;

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

CREATE TRIGGER before_ordered_items_insert
BEFORE INSERT ON ordered_items
FOR EACH ROW
BEGIN
    DECLARE v_status VARCHAR(255);

    SELECT status INTO v_status
    FROM Orders
    WHERE o_id = NEW.o_id
    LIMIT 1;

    IF v_status IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|NOT_FOUND|404|Order not found';
    END IF;

    IF v_status <> 'CREATED' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|BAD_REQUEST|400|Order cannot be modified in its current state';
    END IF;
END$$

CREATE TRIGGER before_ordered_items_update
BEFORE UPDATE ON ordered_items
FOR EACH ROW
BEGIN
    DECLARE v_status VARCHAR(255);

    SELECT status INTO v_status
    FROM Orders
    WHERE o_id = NEW.o_id
    LIMIT 1;

    IF v_status <> 'CREATED' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|BAD_REQUEST|400|Order cannot be modified in its current state';
    END IF;

    IF NEW.quantity <= 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|BAD_REQUEST|400|quantity must be greater than 0';
    END IF;
END$$

CREATE TRIGGER after_ordered_items_insert
AFTER INSERT ON ordered_items
FOR EACH ROW
BEGIN
    UPDATE Orders
    SET total_amount = (
        SELECT COALESCE(SUM(quantity * price_at_purchase), 0)
        FROM ordered_items
        WHERE o_id = NEW.o_id
    )
    WHERE o_id = NEW.o_id;
END$$

CREATE TRIGGER after_ordered_items_update
AFTER UPDATE ON ordered_items
FOR EACH ROW
BEGIN
    UPDATE Orders
    SET total_amount = (
        SELECT COALESCE(SUM(quantity * price_at_purchase), 0)
        FROM ordered_items
        WHERE o_id = NEW.o_id
    )
    WHERE o_id = NEW.o_id;
END$$

CREATE TRIGGER after_ordered_items_delete
AFTER DELETE ON ordered_items
FOR EACH ROW
BEGIN
    UPDATE Orders
    SET total_amount = (
        SELECT COALESCE(SUM(quantity * price_at_purchase), 0)
        FROM ordered_items
        WHERE o_id = OLD.o_id
    )
    WHERE o_id = OLD.o_id;
END$$

DELIMITER ;
