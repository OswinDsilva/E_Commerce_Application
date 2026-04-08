-- Person 1 stored procedures
-- Objects defined in this file:
--   sp_register_user
--   sp_create_bank_account
--   sp_delete_bank_account
--   sp_delete_user
--   sp_pay_order
--   sp_create_order_with_items
--   sp_add_order_items
--   sp_generate_invoice

DROP PROCEDURE IF EXISTS sp_register_user;
DROP PROCEDURE IF EXISTS sp_create_bank_account;
DROP PROCEDURE IF EXISTS sp_delete_bank_account;
DROP PROCEDURE IF EXISTS sp_delete_user;
DROP PROCEDURE IF EXISTS sp_pay_order;
DROP PROCEDURE IF EXISTS sp_create_order_with_items;
DROP PROCEDURE IF EXISTS sp_add_order_items;
DROP PROCEDURE IF EXISTS sp_generate_invoice;

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

CREATE PROCEDURE sp_create_order_with_items(
    IN p_requesting_u_id INTEGER,
    IN p_shipping_address TEXT,
    IN p_billing_address TEXT,
    IN p_items_json JSON
)
BEGIN
    DECLARE v_order_id INTEGER;
    DECLARE v_items_count INTEGER DEFAULT 0;
    DECLARE v_valid_items_count INTEGER DEFAULT 0;
    DECLARE v_invalid_quantity_count INTEGER DEFAULT 0;
    DECLARE v_insufficient_count INTEGER DEFAULT 0;
    DECLARE v_locked_rows INTEGER DEFAULT 0;
    DECLARE v_total_amount DECIMAL(10, 2) DEFAULT 0;

    IF p_items_json IS NULL OR JSON_LENGTH(p_items_json) = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|BAD_REQUEST|400|Order must contain at least one product';
    END IF;

    IF TRIM(COALESCE(p_shipping_address, '')) = '' OR TRIM(COALESCE(p_billing_address, '')) = '' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|BAD_REQUEST|400|shipping_address and billing_address are required';
    END IF;

    DROP TEMPORARY TABLE IF EXISTS tmp_order_items;
    CREATE TEMPORARY TABLE tmp_order_items (
        p_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL
    );

    INSERT INTO tmp_order_items (p_id, quantity)
    SELECT jt.p_id, jt.quantity
    FROM JSON_TABLE(
        p_items_json,
        '$[*]' COLUMNS (
            p_id INTEGER PATH '$.p_id',
            quantity INTEGER PATH '$.quantity'
        )
    ) AS jt;

    SELECT COUNT(*) INTO v_items_count FROM tmp_order_items;
    IF v_items_count = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|BAD_REQUEST|400|Order must contain at least one product';
    END IF;

    SELECT COUNT(*) INTO v_invalid_quantity_count
    FROM tmp_order_items
    WHERE quantity <= 0;

    IF v_invalid_quantity_count > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|BAD_REQUEST|400|quantity must be greater than 0';
    END IF;

    SELECT COUNT(*) INTO v_valid_items_count
    FROM tmp_order_items t
    INNER JOIN Products p ON p.p_id = t.p_id
    INNER JOIN Inventory i ON i.p_id = t.p_id;

    IF v_valid_items_count <> v_items_count THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|BAD_REQUEST|400|One or more products are invalid';
    END IF;

    SELECT COUNT(*)
    INTO v_locked_rows
    FROM Inventory i
    INNER JOIN tmp_order_items t ON t.p_id = i.p_id
    FOR UPDATE;

    SELECT COUNT(*) INTO v_insufficient_count
    FROM (
        SELECT t.p_id
        FROM tmp_order_items t
        INNER JOIN Inventory i ON i.p_id = t.p_id
        GROUP BY t.p_id, i.quantity
        HAVING i.quantity < SUM(t.quantity)
    ) AS stock_check;

    IF v_insufficient_count > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|OUT_OF_STOCK|409|Insufficient stock for one or more products';
    END IF;

    SELECT COALESCE(MAX(o_id), 0) + 1
    INTO v_order_id
    FROM Orders;

    INSERT INTO Orders (
        o_id,
        order_date,
        status,
        total_amount,
        u_id,
        acc_no,
        shipping_address,
        billing_address
    )
    VALUES (
        v_order_id,
        CURDATE(),
        'CREATED',
        0,
        p_requesting_u_id,
        NULL,
        p_shipping_address,
        p_billing_address
    );

    INSERT INTO ordered_items (o_id, p_id, quantity, price_at_purchase)
    SELECT
        v_order_id,
        t.p_id,
        SUM(t.quantity) AS quantity,
        p.price
    FROM tmp_order_items t
    INNER JOIN Products p ON p.p_id = t.p_id
    GROUP BY t.p_id, p.price;

    UPDATE Inventory i
    INNER JOIN (
        SELECT p_id, SUM(quantity) AS ordered_quantity
        FROM tmp_order_items
        GROUP BY p_id
    ) qty ON qty.p_id = i.p_id
    SET
        i.quantity = i.quantity - qty.ordered_quantity,
        i.last_updated = CURRENT_TIMESTAMP;

    SELECT COALESCE(SUM(oi.quantity * oi.price_at_purchase), 0)
    INTO v_total_amount
    FROM ordered_items oi
    WHERE oi.o_id = v_order_id;

    UPDATE Orders
    SET total_amount = v_total_amount
    WHERE o_id = v_order_id;

    SELECT o_id, order_date, status, total_amount, u_id, acc_no
    FROM Orders
    WHERE o_id = v_order_id
    LIMIT 1;

    DROP TEMPORARY TABLE IF EXISTS tmp_order_items;
END$$

CREATE PROCEDURE sp_add_order_items(
    IN p_o_id INTEGER,
    IN p_requesting_u_id INTEGER,
    IN p_items_json JSON
)
BEGIN
    DECLARE v_order_exists INTEGER DEFAULT 0;
    DECLARE v_order_status VARCHAR(255);
    DECLARE v_order_user_id INTEGER;
    DECLARE v_items_count INTEGER DEFAULT 0;
    DECLARE v_valid_items_count INTEGER DEFAULT 0;
    DECLARE v_invalid_quantity_count INTEGER DEFAULT 0;
    DECLARE v_insufficient_count INTEGER DEFAULT 0;
    DECLARE v_locked_rows INTEGER DEFAULT 0;
    DECLARE v_total_amount DECIMAL(10, 2) DEFAULT 0;

    IF p_items_json IS NULL OR JSON_LENGTH(p_items_json) = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|BAD_REQUEST|400|Order must contain at least one product';
    END IF;

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

    IF v_order_status <> 'CREATED' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|BAD_REQUEST|400|Order cannot be modified in its current state';
    END IF;

    DROP TEMPORARY TABLE IF EXISTS tmp_order_items;
    CREATE TEMPORARY TABLE tmp_order_items (
        p_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL
    );

    INSERT INTO tmp_order_items (p_id, quantity)
    SELECT jt.p_id, jt.quantity
    FROM JSON_TABLE(
        p_items_json,
        '$[*]' COLUMNS (
            p_id INTEGER PATH '$.p_id',
            quantity INTEGER PATH '$.quantity'
        )
    ) AS jt;

    SELECT COUNT(*) INTO v_items_count FROM tmp_order_items;
    IF v_items_count = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|BAD_REQUEST|400|Order must contain at least one product';
    END IF;

    SELECT COUNT(*) INTO v_invalid_quantity_count
    FROM tmp_order_items
    WHERE quantity <= 0;

    IF v_invalid_quantity_count > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|BAD_REQUEST|400|quantity must be greater than 0';
    END IF;

    SELECT COUNT(*) INTO v_valid_items_count
    FROM tmp_order_items t
    INNER JOIN Products p ON p.p_id = t.p_id
    INNER JOIN Inventory i ON i.p_id = t.p_id;

    IF v_valid_items_count <> v_items_count THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|BAD_REQUEST|400|One or more products are invalid';
    END IF;

    SELECT COUNT(*)
    INTO v_locked_rows
    FROM Inventory i
    INNER JOIN tmp_order_items t ON t.p_id = i.p_id
    FOR UPDATE;

    SELECT COUNT(*) INTO v_insufficient_count
    FROM (
        SELECT t.p_id
        FROM tmp_order_items t
        INNER JOIN Inventory i ON i.p_id = t.p_id
        GROUP BY t.p_id, i.quantity
        HAVING i.quantity < SUM(t.quantity)
    ) AS stock_check;

    IF v_insufficient_count > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|OUT_OF_STOCK|409|Insufficient stock for one or more products';
    END IF;

    INSERT INTO ordered_items (o_id, p_id, quantity, price_at_purchase)
    SELECT
        p_o_id,
        t.p_id,
        SUM(t.quantity) AS quantity,
        p.price
    FROM tmp_order_items t
    INNER JOIN Products p ON p.p_id = t.p_id
    GROUP BY t.p_id, p.price
    ON DUPLICATE KEY UPDATE
        quantity = ordered_items.quantity + VALUES(quantity),
        price_at_purchase = VALUES(price_at_purchase);

    UPDATE Inventory i
    INNER JOIN (
        SELECT p_id, SUM(quantity) AS ordered_quantity
        FROM tmp_order_items
        GROUP BY p_id
    ) qty ON qty.p_id = i.p_id
    SET
        i.quantity = i.quantity - qty.ordered_quantity,
        i.last_updated = CURRENT_TIMESTAMP;

    SELECT COALESCE(SUM(oi.quantity * oi.price_at_purchase), 0)
    INTO v_total_amount
    FROM ordered_items oi
    WHERE oi.o_id = p_o_id;

    UPDATE Orders
    SET total_amount = v_total_amount
    WHERE o_id = p_o_id;

    SELECT o_id, order_date, status, total_amount, u_id, acc_no
    FROM Orders
    WHERE o_id = p_o_id
    LIMIT 1;

    DROP TEMPORARY TABLE IF EXISTS tmp_order_items;
END$$

CREATE PROCEDURE sp_generate_invoice(
    IN p_o_id INTEGER,
    IN p_requesting_u_id INTEGER
)
BEGIN
    DECLARE v_order_exists INTEGER DEFAULT 0;
    DECLARE v_order_user_id INTEGER;
    DECLARE v_order_status VARCHAR(255);
    DECLARE v_invoice_exists INTEGER DEFAULT 0;
    DECLARE v_invoice_id INTEGER;
    DECLARE v_total_amount DECIMAL(10, 2);
    DECLARE v_shipping_address TEXT;
    DECLARE v_billing_address TEXT;

    SELECT COUNT(*) INTO v_order_exists
    FROM Orders
    WHERE o_id = p_o_id;

    IF v_order_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|NOT_FOUND|404|Order not found';
    END IF;

    SELECT u_id, status, total_amount, shipping_address, billing_address
    INTO v_order_user_id, v_order_status, v_total_amount, v_shipping_address, v_billing_address
    FROM Orders
    WHERE o_id = p_o_id
    LIMIT 1
    FOR UPDATE;

    IF v_order_user_id <> p_requesting_u_id THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|UNAUTHORIZED|403|You are not allowed to access this resource';
    END IF;

    IF v_order_status <> 'PAID' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'APP_ERROR|BAD_REQUEST|400|Invoice can only be generated for paid orders';
    END IF;

    SELECT COUNT(*) INTO v_invoice_exists
    FROM Invoice
    WHERE o_id = p_o_id;

    IF v_invoice_exists > 0 THEN
        SELECT i_id, invoice_date, total_amount, shipping_address, billing_address, o_id
        FROM Invoice
        WHERE o_id = p_o_id
        LIMIT 1;
    ELSE
        SELECT COALESCE(MAX(i_id), 0) + 1
        INTO v_invoice_id
        FROM Invoice;

        INSERT INTO Invoice (
            i_id,
            invoice_date,
            total_amount,
            shipping_address,
            billing_address,
            o_id
        )
        VALUES (
            v_invoice_id,
            CURDATE(),
            v_total_amount,
            COALESCE(NULLIF(TRIM(v_shipping_address), ''), 'N/A'),
            COALESCE(NULLIF(TRIM(v_billing_address), ''), 'N/A'),
            p_o_id
        );

        SELECT i_id, invoice_date, total_amount, shipping_address, billing_address, o_id
        FROM Invoice
        WHERE i_id = v_invoice_id
        LIMIT 1;
    END IF;
END$$

DELIMITER ;
