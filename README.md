# 1. Introduction
- **Purpose**: Product display with 5 different modes of display and control panel, the content to display will be according to the control panel settings where only the administrator user can access. For security reasons, the application only will be accessible through a HTTPs reverse proxy. Additionally the displays where the application will be displayed will turn on at 8:00 am and turn off at 17:00 pm automatically.
- **Scope of the documentation**: Hardware and software requirements, diagrams of the application and the database, structure of the application and installation & deployment
- **Audience**: Store customers
# 2. General Architecture
## 2.1 Diagram of Components
- Jenkins docker container
- Jenkins agent (build node 1)
    - Apache reverse proxy docker container: Allows the access to the application through the ports 80 and 443
    - MariaDB docker container: Stores the database in docker volume
    - Flask app docker container: Runs the application
    - ADB docker container: Turns on and off the displays of the shop (8:00 am to 17:00 pm) and executes the “Kiosk Fully Browser” app
- Jenkins agent (build node 2)
    - Test environment: For testing purposes
<img name="figure1" width="2196" height="1395" alt="image" src="https://github.com/user-attachments/assets/640711d4-35f6-4ff8-9325-06b3f791031f" />

## 2.2 Deployment (Docker Compose)
- Services:
    - Jenkins
    - MariaDB
    - App: Depends on MariaDB
    - Apache
    - ADB Server
- Networks:
    - product-display_default: MariaDB & App
    - proxy_network: Apache & App
    - adb-docker_default: ADB Server
    - jenkins-docker_default: Jenkins
- Volumes:
    - database: Stores the MariaDB database
    - screenshots: Stores screenshots made by the application with playwright
    - adb_keys: Stores fingerprints of the ADB Server
    - jenkins-data: Stores all the information of jenkins
## 2.3 Structure of the Database
### 2.3.1 Creation Script (init.sql)
```sql
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
```
## 2.3.2 Indexes
- category_id in categories (primary key)
- product_id in products (primary key)
- product_id and category_id in product_categories (composite primary key)
- Foreign key indexes for product_category in products and both keys in product_categories
## 2.3.3 Tables
- products: Contains the information of all the products in the woocommerce shop
- product_categories: Contains the relation between products and their categories
- categories: Contains the information of all categories in the woocommerce shop
- blacklisted: Contains blacklisted products and categories (type)
- probabilities: Contains the probabilities of the modes
- speed: Contains the speed of the random product mode
- videos: Contains the information of the youtube videos
- websites: Contains the information of the websites. The ID is related with the screenshot name
## 2.3.4 Diagram of the database
<img width="2365" height="869" alt="image" src="https://github.com/user-attachments/assets/8dc54b07-ccd1-4e22-8dd6-2f49ada0823b" />

## 2.3.5 Backup, restoring and transferring
The following package must be installed: mysql-client
Backup
```console
mysqldump -u root -p --opt --column-statistics=0 db > backup.sql
```
Restoring database
```console
mysql -u root -p -e "CREATE DATABASE db;"
mysql -u root -p db < backup.sql
```

Transferring the database to a new server
```console
scp backup.sql user@server:/path
```

# 3. Structure and operation of the flask app
## 3.1 Structure
```
product-display/
├─ app/
│  ├─ html/
│  │  ├─ control_panel.html
│  │  ├─ index.html/
│  ├─ static/
│  │  ├─ css/
│  │  │  ├─ index.css
│  │  │  ├─ control_panel.css
│  │  ├─ js/
│  │  │  ├─ index.js
│  │  │  ├─ control_panel.js/
│  │  ├─ img/
│  ├─ app.py
│  ├─ Dockerfile
│  ├─ requirements.txt
├─ mariadb/
│  ├─ Dockerfile
│  ├─ init.sql
├─ docker-compose.yml
├─ Jenkinsfile
```

## 3.2 Description of the folders
- product-display: Contains the application and the mariadb
- app: Contains the application build files
    - html: Contains the html template files for the flask app
    - static
        - css: Contains the index.html and control_panel.html styles
        - js: Contains the javascript for the index.html and control_panel.html
        - img: Contains the screenshots made by the application. This folder is mounted in a docker volume
- mariadb: Contains the mariadb build files

## 3.3 Application operation and display modes
The application has five different display modes that are executed depending on what the main function returns (depends on the chances set in the control panel). These modes are:
- Random product: Displays a random product from the database for an amount of time (set in the control panel)
- Random category products: Displays the products of a random category/subcategory in a auto scrollable grid
- Grid of random products: Displays an auto scrollable grid of 198 random products
- Youtube video: Displays a random youtube video from the database (set in the control panel)
- Random website: Displays the screenshot of a random website (set in the control panel). “Since iframe was getting rejected I think that this was the most suitable option”

## 3.4 Application demo
https://github.com/user-attachments/assets/2eba62eb-9856-44b8-97d7-ec18dc110255

## 3.5 Application control panel
The application control panel can be accessed through the following route: /admin. There you can control parameters like blacklisted products, blacklisted categories, youtube videos and websites to display, seconds between random products and chances between modes

## 3.6 Application control panel demo
https://github.com/user-attachments/assets/42da849a-0f3b-41d4-9c64-5e602e191cc3

# 4. Disaster recovery plan (replicate)
## 4.1 Impact analysis
| Component             | Impact IF Fails                                                                 | Criticity Level                                                                 |
|----------------------|----------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| MariaDB              | Loss of Products                                                                 | High (Not critic since the database can be rebuilt from WooCommerce by executing the check_updates() function in app.py) |
| Flask App            | Product Display Not Available                                                    | High                                                                             |
| Apache Reverse Proxy | Web Access Not Available                                                         | High                                                                             |
| ADB Server           | Displays Do Not Turn On/Off Automatically and The Product Display App is Not Opened | Medium                                                                           |
| Jenkins              | Automatization and Deploys Interruption                                          | Low                                                                              |

## 4.2 Recovery strategy
For the database as mentioned before we can backup, restore and transfer to another server using the described method in 2.3.5
For the critical docker volumes, we can backup them using the following commands:
```console
docker run --rm -v product-display_screenshots:/volume -v $(pwd):/backup alpine \
tar czf /backup/screenshots_backup.tar.gz -C /volume .


docker run --rm -v product-display_database:/volume -v $(pwd):/backup alpine \
tar czf /backup/database_backup.tar.gz -C /volume .


docker run --rm -v adb-docker_adb_keys:/volume -v $(pwd):/backup alpine \
tar czf /backup/adb_keys_backup.tar.gz -C /volume .


docker run --rm -v jenkins-docker_jenkins-data:/volume -v $(pwd):/backup alpine \
tar czf /backup/jenkins_data_backup.tar.gz -C /volume .
```

And restore them using the following commands:
```console
docker volume create product-display_screenshots
docker volume create product-display_database
docker volume create adb-docker_adb_keys
docker volume create jenkins-docker_jenkins-data


docker run --rm -v product-display_screenshots:/volume -v $(pwd):/backup alpine \
tar xzf /backup/screenshots_backup.tar.gz -C /volume


docker run --rm -v product-display_database:/volume -v $(pwd):/backup alpine \
tar xzf /backup/database_backup.tar.gz -C /volume


docker run --rm -v adb-docker_adb_keys:/volume -v $(pwd):/backup alpine \
tar xzf /backup/adb_keys_backup.tar.gz -C /volume


docker run --rm -v jenkins-docker_jenkins-data:/volume -v $(pwd):/backup alpine \
tar xzf /backup/jenkins_data_backup.tar.gz -C /volume
```

## 4.2.1 Recovery Procedure Step-To-Step
1. Set up the new physical or cloud server
2. Create required virtual machines with Debian 12 Bookworm
3. Assign static IPs (if needed) and proper hostnames
4. Install docker engine and docker compose in each virtual machine
```console
apt update
apt install docker.io docker-compose -y
```
5. Create and join them in the same docker swarm
```console
docker swarm init
docker swarm join --token <TOKEN>
```
6. Restore the volumes
Transfer .tar.gz backups to the corresponding VM
Execute the following commands for each volume
```console
docker volume create <volume-name>
docker run --rm -v <volume-name>:/volume -v $(pwd):/backup alpine \ tar xzf /backup/<volume-name>_backup.tar.gz -C /volume
```
7. Deploy jenkins
```console
docker-compose up -d jenkins-docker
```
8. Deploy all the applications through jenkins
9. Validations:
    1. Jenkins web user interface is reachable at port 8080
    2. App is reachable and functional
    3. Control panel is reachable and functional
    4. Screenshots are displayed
    5. Displays turn on/off via ADB
