Product Display Application1. IntroductionPurpose: Product display application with 5 different display modes and a control panel. The content to be displayed will be configured from the control panel, which only the administrator user can access. For security reasons, the application will only be accessible through an HTTPs reverse proxy. Additionally, the displays where the application will be shown will turn on at 8:00 am and turn off at 17:00 pm automatically.2. RequirementsHardwareCPU: $>= 1$ GHzRAM: $>= 8$ GBHDD: $>= 50$ GBSoftwareDocker Engine: 20.10.24Docker Compose: 1.29.2Jenkins: 2.504.1MariaDB: 11.7.2Python: 3.13Git: 2.49.0Proxmox: 8.4Apache: 2.4.63 (Unix)Flask: 3.1.1Operating SystemsDebian (Linux GNU): 12 Bookworm3. General Architecture3.1 Component DiagramJenkins docker container: Orchestration.Jenkins agent (build node 1):Apache reverse proxy container: Allows access to the application through ports 80 and 443.Flask app container: Runs the application.MariaDB container: Stores the database in a docker volume.ADB container: Turns the store displays on and off (8:00 am to 17:00 pm) and runs the "Kiosk Fully Browser" app.Jenkins agent (build node 2):Test environment: For testing purposes.3.2 Deployment (Docker Compose)Services:JenkinsMariaDBApp (Depends on MariaDB)ApacheADB ServerNetworks:product-display_default: MariaDB & Appproxy_network: Apache & Appadb-docker_default: ADB Serverjenkins-docker_default: JenkinsVolumes:database: Stores the MariaDB database.screenshots: Stores screenshots taken by the application with playwright.adb_keys: Stores fingerprints of the ADB Server.jenkins-data: Stores all jenkins information.4. Database Structure4.1 Creation Script (init.sql)CREATE TABLE categories (
    category_id INT PRIMARY KEY,
    category_name VARCHAR(256) NOT NULL,
    category_image VARCHAR (256) NULL
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
    FOREIGN KEY (product_category) REFERENCES categories (category_id)
);

CREATE TABLE product_categories (
    product_id INT,
    category_id INT,
    PRIMARY KEY (product_id, category_id),
    FOREIGN KEY (product_id) REFERENCES products (product_id),
    FOREIGN KEY (category_id) REFERENCES categories (category_id)
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
4.2 Indexescategory_id in categories (primary key)product_id in products (primary key)product_id and category_id in product_categories (composite primary key)Foreign key indexes for product_category in products and both keys in product_categories.4.3 Tablesproducts: Contains information for all products from the woocommerce shop.product_categories: Contains the relationship between products and their categories.categories: Contains information for all categories in the woocommerce shop.blacklisted: Contains blacklisted products and categories (type).probabilities: Contains the probabilities for the display modes.speed: Contains the speed for the random product mode.videos: Contains information about the youtube videos.websites: Contains information about the websites. The ID is related to the screenshot name.4.4 Backup, Restore, and TransferThe mysql-client package must be installed.Backupmysqldump -u root -p --opt --column-statistics=0 db > backup.sql
Database Restoremysql -u root -p -e "CREATE DATABASE db;"
mysql -u root -p db < backup.sql
Transferring the database to a new serverscp backup.sql user@server:/path
5. Flask App Structure and Operation5.1 File Structureproduct-display/
├── app/
│   ├── html/
│   │   ├── control_panel.html
│   │   └── index.html
│   ├── static/
│   │   ├── css/
│   │   │   ├── index.css
│   │   │   └── control_panel.css
│   │   ├── js/
│   │   │   ├── index.js
│   │   │   └── control_panel.js
│   │   └── img/  (Docker Volume for screenshots)
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── mariadb/
│   ├── Dockerfile
│   └── init.sql
├── docker-compose.yml
└── Jenkinsfile
5.2 Folder Descriptionproduct-display: Contains the application and mariadb.app: Contains the application build files.html: Contains the html template files for the flask app.static:css: Contains the styles for index.html and control_panel.html.js: Contains the javascript for index.html and control_panel.html.img: Contains screenshots taken by the application. This folder is mounted in a docker volume.mariadb: Contains the mariadb build files.5.3 Operation and Display ModesThe application has five different display modes that run depending on the probabilities set in the control panel:Random product: Displays a random product from the database for a set amount of time.Random category products: Displays products from a random category/subcategory in an auto-scrolling grid.Grid of random products: Displays an auto-scrolling grid of 198 random products.Youtube video: Displays a random youtube video from the database.Random website: Displays a screenshot of a random website.5.4 Application Control PanelThe application control panel can be accessed through the route: /admin.From there, parameters can be controlled such as:Blacklisted productsBlacklisted categoriesYoutube videos and websites to displaySeconds between random productsProbabilities between the different display modes6. Disaster Recovery Plan6.1 Impact AnalysisComponentImpact if FailsCriticality LevelMariaDBLoss of ProductsHigh (Not critical as the DB can be rebuilt from WooCommerce)Flask AppProduct Display Not AvailableHighApache Reverse ProxyWeb Access Not AvailableHighADB ServerDisplays do not turn on/off automaticallyMediumJenkinsAutomation and Deployments InterruptionLow6.2 Recovery Strategy (Docker Volumes)Volume Backup# Backup screenshots
docker run --rm -v product-display_screenshots:/volume -v $(pwd):/backup alpine \
tar czf /backup/screenshots_backup.tar.gz -C /volume .

# Backup database
docker run --rm -v product-display_database:/volume -v $(pwd):/backup alpine \
tar czf /backup/database_backup.tar.gz -C /volume .

# Backup adb_keys
docker run --rm -v adb-docker_adb_keys:/volume -v $(pwd):/backup alpine \
tar czf /backup/adb_keys_backup.tar.gz -C /volume .

# Backup jenkins-data
docker run --rm -v jenkins-docker_jenkins-data:/volume -v $(pwd):/backup alpine \
tar czf /backup/jenkins_data_backup.tar.gz -C /volume .
Volume Restore# Create empty volumes
docker volume create product-display_screenshots
docker volume create product-display_database
docker volume create adb-docker_adb_keys
docker volume create jenkins-docker_jenkins-data

# Restore screenshots
docker run --rm -v product-display_screenshots:/volume -v $(pwd):/backup alpine \
tar xzf /backup/screenshots_backup.tar.gz -C /volume

# Restore database
docker run --rm -v product-display_database:/volume -v $(pwd):/backup alpine \
tar xzf /backup/database_backup.tar.gz -C /volume

# Restore adb_keys
docker run --rm -v adb-docker_adb_keys:/volume -v $(pwd):/backup alpine \
tar xzf /backup/adb_keys_backup.tar.gz -C /volume

# Restore jenkins-data
docker run --rm -v jenkins-docker_jenkins-data:/volume -v $(pwd):/backup alpine \
tar xzf /backup/jenkins_data_backup.tar.gz -C /volume
6.3 Step-by-Step Recovery ProcedureSet up the new server (physical or cloud):1.1. Create the required VMs with Debian 12 Bookworm.1.2. Assign static IPs (if needed) and proper hostnames.Install Docker Engine and Docker Compose on each VM:apt update
apt install docker.io docker-compose -y
Create and join them to the same Docker Swarm:docker swarm init
docker swarm join --token <TOKEN>
Restore the volumes:4.1. Transfer the .tar.gz backups to the corresponding VM.4.2. Run the volume restore commands (see section 6.2).Deploy Jenkins:docker-compose up -d jenkins-docker
Deploy all applications through Jenkins.Validations:7.1. Jenkins web interface is reachable on port 8080.7.2. The application is reachable and functional.7.3. The control panel is reachable and functional.7.4. Screenshots are displayed.7.5. Displays turn on/off via ADB.Note: In case you cannot restore the Jenkins volume, you will have to reconfigure it and add the credentials again.