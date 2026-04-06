-- Person 1 stored procedures
-- Objects defined in this file:
--   sp_register_user
--   sp_create_bank_account
--   sp_delete_bank_account
--   sp_delete_user
--   sp_pay_order

DROP PROCEDURE IF EXISTS sp_register_user;
DROP PROCEDURE IF EXISTS sp_create_bank_account;
DROP PROCEDURE IF EXISTS sp_delete_bank_account;
DROP PROCEDURE IF EXISTS sp_delete_user;
DROP PROCEDURE IF EXISTS sp_pay_order;

DELIMITER $$

CREATE PROCEDURE sp_register_user(
    IN p_u_id INTEGER,
    IN p_username VARCHAR(255),
    IN p_password_hash VARCHAR(255),
    IN p_email VARCHAR(255),
    IN p_phone VARCHAR(20),
    IN p_role_id INTEGER
)
BEGIN
    DECLARE v_role_exists INTEGER DEFAULT 0;
    DECLARE v_username_exists INTEGER DEFAULT 0;
    DECLARE v_email_exists INTEGER DEFAULT 0;

    SELECT COUNT(*) INTO v_role_exists
    FROM roles
    WHERE id = p_role_id;

    IF v_role_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|SERVER_ERROR|500|Default USER role is not configured in roles table';
    END IF;

    SELECT COUNT(*) INTO v_username_exists
    FROM Users
    WHERE username = p_username;

    IF v_username_exists > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|BAD_REQUEST|400|Username already exists';
    END IF;

    SELECT COUNT(*) INTO v_email_exists
    FROM Users
    WHERE email = p_email;

    IF v_email_exists > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|BAD_REQUEST|400|Email already exists';
    END IF;

    INSERT INTO Users (u_id, username, password_hash, email, phone, role_id)
    VALUES (p_u_id, p_username, p_password_hash, p_email, p_phone, p_role_id);

    SELECT
        u.u_id,
        u.username,
        u.email,
        u.phone,
        u.created_at,
        u.role_id,
        r.role
    FROM Users u
    INNER JOIN roles r ON r.id = u.role_id
    WHERE u.u_id = p_u_id
    LIMIT 1;
END$$

CREATE PROCEDURE sp_create_bank_account(
    IN p_acc_no INTEGER,
    IN p_bank_name VARCHAR(255),
    IN p_expiry_date DATE,
    IN p_u_id INTEGER
)
BEGIN
    DECLARE v_user_exists INTEGER DEFAULT 0;
    DECLARE v_account_exists INTEGER DEFAULT 0;

    SELECT COUNT(*) INTO v_user_exists
    FROM Users
    WHERE u_id = p_u_id;

    IF v_user_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|BAD_REQUEST|400|A bank account must belong to a valid user';
    END IF;

    IF p_expiry_date < CURDATE() THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|BAD_REQUEST|400|expiry_date cannot be in the past';
    END IF;

    SELECT COUNT(*) INTO v_account_exists
    FROM Bank_acc
    WHERE acc_no = p_acc_no;

    IF v_account_exists > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|BAD_REQUEST|400|Bank account already exists';
    END IF;

    INSERT INTO Bank_acc (acc_no, bank_name, expiry_date, u_id)
    VALUES (p_acc_no, p_bank_name, p_expiry_date, p_u_id);

    SELECT acc_no, bank_name, expiry_date, u_id
    FROM Bank_acc
    WHERE acc_no = p_acc_no
    LIMIT 1;
END$$

CREATE PROCEDURE sp_delete_bank_account(
    IN p_acc_no INTEGER,
    IN p_u_id INTEGER
)
BEGIN
    DELETE FROM Bank_acc
    WHERE acc_no = p_acc_no AND u_id = p_u_id;

    IF ROW_COUNT() <> 1 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|NOT_FOUND|404|Bank account not found';
    END IF;

    SELECT p_acc_no AS acc_no, p_u_id AS u_id;
END$$

CREATE PROCEDURE sp_delete_user(IN p_u_id INTEGER)
BEGIN
    DELETE FROM Users
    WHERE u_id = p_u_id;

    IF ROW_COUNT() <> 1 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|NOT_FOUND|404|User not found';
    END IF;

    SELECT p_u_id AS u_id;
END$$

CREATE PROCEDURE sp_pay_order(
    IN p_o_id INTEGER,
    IN p_requesting_u_id INTEGER,
    IN p_acc_no INTEGER
)
BEGIN
    DECLARE v_order_exists INTEGER DEFAULT 0;
    DECLARE v_account_exists INTEGER DEFAULT 0;
    DECLARE v_order_user_id INTEGER;
    DECLARE v_order_status VARCHAR(255);
    DECLARE v_account_user_id INTEGER;
    DECLARE v_expiry_date DATE;

    SELECT COUNT(*) INTO v_order_exists
    FROM Orders
    WHERE o_id = p_o_id;

    IF v_order_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|NOT_FOUND|404|Order not found';
    END IF;

    SELECT u_id, status
    INTO v_order_user_id, v_order_status
    FROM Orders
    WHERE o_id = p_o_id
    LIMIT 1
    FOR UPDATE;

    IF v_order_user_id <> p_requesting_u_id THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|UNAUTHORIZED|403|You are not allowed to access this resource';
    END IF;

    IF v_order_status = 'PAID' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|ALREADY_PAID|409|Order has already been paid';
    END IF;

    IF v_order_status <> 'CREATED' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|BAD_REQUEST|400|Order cannot be paid in its current state';
    END IF;

    SELECT COUNT(*) INTO v_account_exists
    FROM Bank_acc
    WHERE acc_no = p_acc_no;

    IF v_account_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|INVALID_ACCOUNT|400|Selected bank account is invalid';
    END IF;

    SELECT u_id, expiry_date
    INTO v_account_user_id, v_expiry_date
    FROM Bank_acc
    WHERE acc_no = p_acc_no
    LIMIT 1;

    IF v_account_user_id <> p_requesting_u_id OR v_expiry_date < CURDATE() THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|INVALID_ACCOUNT|400|Selected bank account is invalid';
    END IF;

    UPDATE Orders
    SET status = 'PAID', acc_no = p_acc_no
    WHERE o_id = p_o_id AND status = 'CREATED';

    IF ROW_COUNT() <> 1 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|ALREADY_PAID|409|Order has already been paid';
    END IF;

    SELECT o_id, order_date, status, total_amount, u_id, acc_no
    FROM Orders
    WHERE o_id = p_o_id
    LIMIT 1;
END$$

DELIMITER ;
