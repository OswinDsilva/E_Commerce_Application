-- This file contains the SQL statements to create the database schema for the application.

-- LOOKUP TABLES

CREATE TABLE `roles` (
    `id`   INTEGER      NOT NULL,
    `role` VARCHAR(255) NOT NULL
);
ALTER TABLE `roles` ADD PRIMARY KEY (`id`);


CREATE TABLE `categories` (
    `id`       BIGINT       NOT NULL,
    `category` VARCHAR(255) NOT NULL
);
ALTER TABLE `categories` ADD PRIMARY KEY (`id`);

-- USERS

CREATE TABLE `Users` (
    `u_id`          INTEGER                      NOT NULL,
    `username`      VARCHAR(255)                 NOT NULL,
    `password_hash` VARCHAR(255)                 NOT NULL,
    `email`         VARCHAR(255)                 NOT NULL,
    `phone`         VARCHAR(20)                  NOT NULL,
    `created_at`    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `role_id`       INTEGER                      NOT NULL
);
ALTER TABLE `Users` ADD PRIMARY KEY (`u_id`);
ALTER TABLE `Users` ADD CONSTRAINT `users_username_unique` UNIQUE (`username`);
ALTER TABLE `Users` ADD CONSTRAINT `users_email_unique`    UNIQUE (`email`);
ALTER TABLE `Users` ADD CONSTRAINT `users_role_id_foreign`
    FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
    ON DELETE RESTRICT;

-- BANK ACCOUNTS

CREATE TABLE `Bank_acc` (
    `acc_no`      INTEGER      NOT NULL,
    `bank_name`   VARCHAR(255) NOT NULL,
    `expiry_date` DATE         NOT NULL,
    `u_id`        INTEGER      NOT NULL
);
ALTER TABLE `Bank_acc` ADD PRIMARY KEY (`acc_no`);
ALTER TABLE `Bank_acc` ADD CONSTRAINT `bank_acc_u_id_foreign`
    FOREIGN KEY (`u_id`) REFERENCES `Users` (`u_id`)
    ON DELETE CASCADE;

-- PRODUCTS

CREATE TABLE `Products` (
    `p_id`         INTEGER        NOT NULL,
    `product_name` VARCHAR(255)   NOT NULL,
    `brand`        VARCHAR(255)   NOT NULL,
    `price`        DECIMAL(10, 2) NOT NULL CHECK (`price` >= 0),
    `category_id`  BIGINT         NOT NULL,
    `description`  TEXT           NOT NULL,
    `thumbnail_url` VARCHAR(1024) NULL
);
ALTER TABLE `Products` ADD PRIMARY KEY (`p_id`);
ALTER TABLE `Products` ADD CONSTRAINT `products_category_foreign`
    FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`)
    ON DELETE RESTRICT;

-- INVENTORY (Weak Entity — 1:1 with Products)

CREATE TABLE `Inventory` (
    `p_id`         INTEGER                     NOT NULL,
    `quantity`     INTEGER                     NOT NULL CHECK (`quantity` >= 0),
    `last_updated` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE `Inventory` ADD PRIMARY KEY (`p_id`);
ALTER TABLE `Inventory` ADD CONSTRAINT `inventory_p_id_foreign`
    FOREIGN KEY (`p_id`) REFERENCES `Products` (`p_id`)
    ON DELETE CASCADE;

-- ORDERS

CREATE TABLE `Orders` (
    `o_id`         INTEGER        NOT NULL,
    `order_date`   DATE           NOT NULL,
    `status`       VARCHAR(255)   NOT NULL CHECK (
        `status` IN ('CREATED', 'PAID', 'SHIPPED', 'DELIVERED', 'CANCELLED')
    ),
    `total_amount` DECIMAL(10, 2) NOT NULL CHECK (`total_amount` >= 0),
    `u_id`         INTEGER        NOT NULL,
    `acc_no`       INTEGER        NULL,
    `shipping_address` TEXT       NULL,
    `billing_address`  TEXT       NULL
);
ALTER TABLE `Orders` ADD PRIMARY KEY (`o_id`);
ALTER TABLE `Orders` ADD CONSTRAINT `orders_u_id_foreign`
    FOREIGN KEY (`u_id`) REFERENCES `Users` (`u_id`)
    ON DELETE CASCADE;
ALTER TABLE `Orders` ADD CONSTRAINT `orders_acc_no_foreign`
    FOREIGN KEY (`acc_no`) REFERENCES `Bank_acc` (`acc_no`)
    ON DELETE SET NULL;

-- INVOICE (1:1 with Orders)

CREATE TABLE `Invoice` (
    `i_id`             INTEGER        NOT NULL,
    `invoice_date`     DATE           NOT NULL,
    `total_amount`     DECIMAL(10, 2) NOT NULL CHECK (`total_amount` >= 0),
    `shipping_address` TEXT           NOT NULL,
    `billing_address`  TEXT           NOT NULL,
    `o_id`             INTEGER        NOT NULL
);
ALTER TABLE `Invoice` ADD PRIMARY KEY (`i_id`);
ALTER TABLE `Invoice` ADD CONSTRAINT `invoice_o_id_unique` UNIQUE (`o_id`);
ALTER TABLE `Invoice` ADD CONSTRAINT `invoice_o_id_foreign`
    FOREIGN KEY (`o_id`) REFERENCES `Orders` (`o_id`)
    ON DELETE CASCADE;

-- ORDERED ITEMS (Junction Table — Orders ↔ Products)

CREATE TABLE `ordered_items` (
    `o_id`              INTEGER        NOT NULL,
    `p_id`              INTEGER        NOT NULL,
    `quantity`          INTEGER        NOT NULL CHECK (`quantity` > 0),
    `price_at_purchase` DECIMAL(10, 2) NOT NULL CHECK (`price_at_purchase` >= 0)
);
ALTER TABLE `ordered_items` ADD PRIMARY KEY (`o_id`, `p_id`);
ALTER TABLE `ordered_items` ADD CONSTRAINT `ordered_items_o_id_foreign`
    FOREIGN KEY (`o_id`) REFERENCES `Orders` (`o_id`)
    ON DELETE CASCADE;
ALTER TABLE `ordered_items` ADD CONSTRAINT `ordered_items_p_id_foreign`
    FOREIGN KEY (`p_id`) REFERENCES `Products` (`p_id`)
    ON DELETE CASCADE;

-- SEED DATA

INSERT INTO `roles` (`id`, `role`)
VALUES
    (1, 'USER'),
    (2, 'ADMIN')
ON DUPLICATE KEY UPDATE
    `role` = VALUES(`role`);

-- Default admin login password: admin123
INSERT INTO `Users` (`u_id`, `username`, `password_hash`, `email`, `phone`, `role_id`)
VALUES
    (
        1,
        'admin',
        'pbkdf2_sha256$100000$276b73592aa043f65069b3fa6197e5b6$d6b7faba7705aea6ee33459b3b424bee573dac471de2cb1985fc1b5e34b7f5fd',
        'admin@atelier.local',
        '9999999999',
        2
    )
ON DUPLICATE KEY UPDATE
    `username` = VALUES(`username`),
    `password_hash` = VALUES(`password_hash`),
    `email` = VALUES(`email`),
    `phone` = VALUES(`phone`),
    `role_id` = VALUES(`role_id`);
