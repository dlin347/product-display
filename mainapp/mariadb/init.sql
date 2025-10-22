CREATE TABLE categories (
    category_id INT PRIMARY KEY,
    category_name VARCHAR(256) NOT NULL,
    category_image VARCHAR(256) NULL
);

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(128) NOT NULL,
    product_description TEXT,
    product_sku VARCHAR(64),
    product_image VARCHAR(256) NOT NULL,
    product_price VARCHAR(32) NOT NULL,
    product_modification DATETIME NOT NULL,
    product_category INT,
    FOREIGN KEY (product_category) REFERENCES categories(category_id)
);

CREATE TABLE product_categories (
    product_id INT,
    category_id INT,
    PRIMARY KEY (product_id, category_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE probabilities (
    id INT PRIMARY KEY AUTO_INCREMENT,
    random_product INT NOT NULL,
    random_category_products INT NOT NULL,
    grid INT NOT NULL,
    youtube_video INT NOT NULL,
    website INT NOT NULL
);

CREATE TABLE videos (
    id VARCHAR(16) PRIMARY KEY,
    video_url VARCHAR(256) NOT NULL,
    video_title VARCHAR(256) NOT NULL,
    video_length INT NOT NULL
);

CREATE TABLE websites (
    id INT PRIMARY KEY AUTO_INCREMENT,
    website_url VARCHAR(256) NOT NULL
);

CREATE TABLE blacklisted (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type ENUM('product', 'category') NOT NULL,
    name VARCHAR(256) NOT NULL
);

CREATE TABLE speed (
    id INT PRIMARY KEY AUTO_INCREMENT,
    speed_ms INT NOT NULL
);