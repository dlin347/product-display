# D E P E N D E N C I E S
from flask import Flask, render_template, request, Response, jsonify
from playwright.sync_api import sync_playwright
from googleapiclient.discovery import build
from threading import Lock, Thread
from urllib.parse import unquote
from bs4 import BeautifulSoup
from datetime import datetime
from woocommerce import API
import mariadb
import time
import os
import re
# E N D   O F   D E P E N D E N C I E S



# Fixes database concurrency problems
read_lock = Lock()
write_lock = Lock()

# Makes the connection with the Woocommerce API
woocommerce = API(
    url="https://www.organizationwebsite.com/",
    consumer_key=os.getenv("CONSUMER_KEY"),
    consumer_secret=os.getenv("CONSUMER_SECRET"),
    version="wc/v3"
)

# Makes a connection with the database
def dbConnection():
    return mariadb.connect(
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        host=os.getenv("MYSQL_HOST"),
        port=3306,
        database=os.getenv("MYSQL_DATABASE")
    )

# Waits until the database is ready, if it is not retries after 10 seconds
def wait_db_ready():
    while True:
        try:
            connection = dbConnection()
            connection.close()
            print("Successfully connected with MariaDB...")
            break
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB, retrying in 10 seconds... {e}")
            time.sleep(10)
wait_db_ready()

# Flask app
app = Flask(__name__, template_folder='./html/')




# Control panel basic authentication
def check_auth(username, password):
    return username == os.getenv("LOGIN_USER") and password == os.getenv("LOGIN_PASSWORD")
def authenticate():
    return Response("Login Required to Access This Page", 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

# Function to convert youtube video duration formatted in (ISO 8601) into milliseconds
def convert_youtube_duration_to_ms(duration):
    match = re.match(r'PT(\d+H)?(\d+M)?(\d+S)?', duration)
    hours = int(match.group(1)[:-1]) if match.group(1) else 0
    minutes = int(match.group(2)[:-1]) if match.group(2) else 0
    seconds = int(match.group(3)[:-1]) if match.group(3) else 0
    total_ms = (hours * 3600 + minutes * 60 + seconds) * 1000
    return int(total_ms)

# Gets information of a youtube video making a request to the YouTube API
def get_video_info(url):
    video_id = url.split("v=")[1].split("&")[0]
    youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"))
    request = youtube.videos().list(
        part="snippet,contentDetails",
        id=video_id
    )
    print("Making the request to Youtube API...")
    response = request.execute()
    print("Request to Youtube API executed successfully...")
    if response["items"]:
        video_title = response["items"][0]["snippet"]["title"]
        raw_duration = response["items"][0]["contentDetails"]["duration"]
        video_length = convert_youtube_duration_to_ms(raw_duration)
        return video_id, video_title, video_length
    
# Administration control panel authentication
@app.route('/admin')
def protected():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()
    return render_template('control_panel.html')

# At root, render index.html template
@app.route('/')
def index():
    return render_template('index.html')




""" E N D P O I N T S """
# Gets 10 random products from the database and returns them in JSON
@app.route('/random_product')
def random_product():
    print("Getting 10 random products from the database...")
    with dbConnection() as connection:
        with connection.cursor() as cursor:
            with read_lock:
                cursor.execute("""
                    SELECT product_name, product_image, product_description, product_sku, product_price 
                    FROM products 
                    WHERE product_id NOT IN (SELECT id FROM blacklisted WHERE type = 'product') 
                    AND product_category NOT IN (SELECT id FROM blacklisted WHERE type = 'category')
                    ORDER BY RAND() LIMIT 10
                """)
                products = cursor.fetchall()
                
    print("Returning a 10 random products from the database...")
    list_products = []
    for product in products:
        sku = f"SKU: {product[3]}" if product[3] else ""
        price = f"Hinta: {product[4]}"
        list_products.append({
            "name": product[0],
            "image": product[1],
            "description": product[2],
            "sku": sku,
            "price": price
        })
    return jsonify({ "products": list_products})

# Gets a random category and its corresponding products from the database and returns them in JSON
@app.route('/random_category_products')
def random_category_products():
    with dbConnection() as connection:
        with connection.cursor() as cursor:
            with read_lock:
                cursor.execute("""
                    SELECT category_id, category_name, category_image 
                    FROM categories 
                    WHERE category_id IN (
                        SELECT category_id 
                        FROM product_categories 
                        GROUP BY category_id 
                        HAVING COUNT(*) >= 18
                    ) 
                    AND category_image IS NOT NULL
                    ORDER BY RAND() 
                    LIMIT 1;
                """)
                category = cursor.fetchone()

                cursor.execute("""
                    SELECT product_name, product_image, product_description, product_sku, product_price 
                    FROM products 
                    WHERE product_id IN (
                        SELECT product_id
                        FROM product_categories
                        WHERE category_id = %s
                    )
                    AND product_id NOT IN (SELECT id FROM blacklisted WHERE type = 'product') 
                    AND product_category NOT IN (SELECT id FROM blacklisted WHERE type = 'category')
                """, (category[0],))
                products = cursor.fetchall()

    list_products = []
    for product in products:
        price = f"Hinta: {product[4]}"
        list_products.append({
            "name": product[0],
            "image": product[1],
            "price": price
        })

    return jsonify({
        "category": {
            "name": category[1],
            "image": category[2]
        },
        "products": list_products
    })

# Gets 198 random products from the database and returns them in JSOn
@app.route('/product_grid')
def product_grid():
    with dbConnection() as connection:
        with connection.cursor() as cursor:
            with read_lock:
                cursor.execute("""
                    SELECT product_name, product_image, product_price 
                    FROM products 
                    WHERE product_id NOT IN (SELECT id FROM blacklisted WHERE type = 'product') 
                    AND product_category NOT IN (SELECT id FROM blacklisted WHERE type = 'category')
                    ORDER BY RAND() 
                    LIMIT 198
                """)
                products = cursor.fetchall()

    list_products = []
    for product in products:
        price = f"Hinta: {product[2]}"
        list_products.append({
            "name": product[0],
            "image": product[1],
            "price": price
        })

    return jsonify({
        "products": list_products
    })

# Gets a random youtube information from the database and returns it in JSON
@app.route('/youtube_video')
def youtube_video():
    with dbConnection() as connection:
        with connection.cursor() as cursor:
            with read_lock:
                cursor.execute("SELECT video_url, video_length FROM videos ORDER BY RAND() LIMIT 1")
                video = cursor.fetchone()
                video_url = video[0]
                video_length = video[1]
                embed_url = video_url.replace("watch?v=", "embed/")
                
    return jsonify({
        "video_url": embed_url,
        "video_length": video_length
    })

# Gets a random website from the database    
@app.route('/website')
def website():
    with dbConnection() as connection:
        with connection.cursor() as cursor:
            with read_lock:
                cursor.execute("SELECT id, website_url FROM websites ORDER BY RAND() LIMIT 1")
                website = cursor.fetchone()
    return jsonify({
        "website_id": website[0],
        "website_url": website[1]
    })



# Gets the blacklisted products from the database and returns them in JSON
@app.route('/get-blacklisted-products')
def blacklisted_products():
    print("Fetching blacklisted products from the database...")
    with dbConnection() as connection:
        with connection.cursor() as cursor:
            with read_lock:
                cursor.execute("SELECT id product_id, name product_name FROM blacklisted WHERE type = 'product'")
                products = cursor.fetchall()
                
    products_list = [
        {"product_id": product[0], "product_name": product[1]}
        for product in products
    ]
    print("Successfully fetched blacklisted products from the database...")
    return jsonify(products_list)

# Gets the blacklisted categories from the database and returns them in JSON
@app.route('/get-blacklisted-categories')
def blacklisted_categories():
    print("Fetching blacklisted categories from the database...")
    with dbConnection() as connection:
        with connection.cursor() as cursor:
            with read_lock:
                cursor.execute("SELECT id, name FROM blacklisted WHERE type = 'category'")
                categories = cursor.fetchall()
                
    categories_list = [
        {"category_id": category[0], "category_name": category[1]}
        for category in categories
    ]
    print("Successfully fetched blacklisted categories from the database...")
    return jsonify(categories_list)

# Gets the youtube videos information from the database and returns them in JSON
@app.route('/get_videos')
def get_videos():
    print("Fetching youtube videos from the database...")
    with dbConnection() as connection:
        with connection.cursor() as cursor:
            with read_lock:
                cursor.execute("SELECT id, video_title, video_length FROM videos")
                videos = cursor.fetchall()
                
    print("Getting youtube videos...")
    videos_list = [
        {"video_id": video[0], "video_title": video[1], "video_length": video[2]}
        for video in videos
    ]
    print("Successfully fetched youtube videos from the database...")
    return jsonify(videos_list)

# Gets the websites information from the database and returns them in JSON
@app.route('/get_websites')
def get_websites():
    print("Fetching websites from the database...")
    with dbConnection() as connection:
        with connection.cursor() as cursor:
            with read_lock:
                cursor.execute("SELECT id, website_url FROM websites")
                websites = cursor.fetchall()
                
    print("Getting websites...")
    websites_list = [
        {"website_id": website[0], "website_url": website[1]}
        for website in websites
    ]
    print("Successfully fetched the websites from the database...")
    return jsonify(websites_list)



# Fetches ALL probabilities from the database and returns them in JSON
@app.route('/probabilities')
def probabilities():
    print(f"Fetching the probabilities from the database...")
    with dbConnection() as connection:
        with connection.cursor() as cursor:
            with read_lock:
                cursor.execute(f"SELECT * FROM probabilities WHERE id = 1")
                probability = cursor.fetchone()
                
    print("Successfully fetched the probabilities from the database...")
    return jsonify({"random_product": probability[1], "random_category_products": probability[2], "grid": probability[3], "youtube_video": probability[4], "website": probability[5]})
    
# Updates the probabilties in the database
@app.route('/probabilities/<int:random_product>/<int:random_category_products>/<int:grid>/<int:youtube_video>/<int:website>', methods=['POST'])
def set_probability(random_product, random_category_products, grid, youtube_video, website):
    print(f"Updating all the probabilities in the database...")
    try:
        with dbConnection() as connection:
            with connection.cursor() as cursor:
                with write_lock:
                    cursor.execute("UPDATE probabilities SET random_product = ?, random_category_products = ?, grid = ?, youtube_video = ?, website = ? WHERE id = 1", (random_product, random_category_products, grid, youtube_video, website,))
                    connection.commit()
                    
        print("Successfully updated the probabilities in the database...")
        return jsonify({"status": "OK"})
    except Exception as e:
        print(f"Error: {str(e)}")



# Gets the speed to display a random product from the database and returns it in JSON
@app.route('/speed')
def get_speed():
    print("Fetching random product display speed from the database...")
    with dbConnection() as connection:
        with connection.cursor() as cursor:
            with read_lock:
                cursor.execute("SELECT speed_ms FROM speed WHERE id = 1")
                speed = cursor.fetchone()
    
    print("Sucessfully fetched random product display speed from the database...")         
    return jsonify({"speed": speed[0]})

# Updates the speed to displau a random product from the database and returns it in JSON
@app.route('/speed/<int:speed>', methods=['POST'])
def set_speed(speed):
    print(f"Updating random product display speed in the database...")
    try:
        if speed <= 0:
            return jsonify({"message": "Speed must be greater than zero", "status": "warning"})
        
        with dbConnection() as connection:
            with connection.cursor() as cursor:
                with write_lock:
                    cursor.execute("UPDATE speed SET speed_ms = ? WHERE id = 1", (speed * 1000,))
                    connection.commit()
                    
        print(f"Successfully updated the random product display speed to {speed} seconds...")                       
        return jsonify({"message": f"Successfully set the speed to {speed} seconds", "status": "success"})
    except Exception as e:
        return jsonify({"message": f"There was an error while setting the speed. Error: {str(e)}", "status": "error"})
    
# Inserts a website to the database and stores a screenshot
@app.route('/add_website', methods=['POST'])
def add_website():
    print("Adding website to the database...")

    try:
        data = request.get_json()
        url = data.get("url", "").strip()

        if not url:
            return jsonify({"message": "Invalid website URL", "status": "error"})

        decoded_url = unquote(url)

        with dbConnection() as connection:
            with connection.cursor() as cursor:
                with write_lock:
                    cursor.execute("INSERT INTO websites (website_url) VALUES (%s) RETURNING id", (decoded_url,))
                    website_id = cursor.fetchone()[0]
                    connection.commit()

        with sync_playwright() as playwright:
            image_path = f"/static/img/{website_id}.png"
            browser = playwright.chromium.launch()
            page = browser.new_page()
            page.goto(decoded_url, timeout=15000)
            page.wait_for_timeout(5000)
            page.screenshot(path=image_path, full_page=True)
            browser.close()

        return jsonify({"message": f"Successfully made and saved a screenshot of: {decoded_url}", "status": "success"})
    except Exception as e:
        return jsonify({"message": f"Error while adding a website to the database: {str(e)}", "status": "error"})
    
# Deletes a website from the database    
@app.route('/delete-website/<int:website_id>', methods=['DELETE'])
def delete_website(website_id):
    print("Removing website from the database...")
    try:
        with dbConnection() as connection:
            with connection.cursor() as cursor:
                with write_lock:
                    cursor.execute("DELETE FROM websites WHERE id = ?", (website_id,))
                    connection.commit()
                    
        image_path = f"/static/img/{website_id}.png"
        if os.path.exists(image_path):
            os.remove(image_path)
            print(f"Successfully deleted associated image: {image_path}")
        
        print("Successfully removed website from the database...")           
        return jsonify({"message": f"Successfully deleted the website and the related screenshot from the database", "status": "success"})
    except Exception as e:
        return jsonify({"message": f"Cannot find the website in the database or there was an error while processing your request. Error: {str(e)}", "status": "error"})    
    
    
    
# Inserts a youtube video to the database    
@app.route('/add_video/<string:video_id>', methods=['POST'])
def add_video(video_id):
    print("Inserting youtube video to the database...")
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        video_id, video_title, video_length = get_video_info(video_url)
        
        if not video_title:
            return jsonify({"message": "Invalid video URL", "status": "error"})

        with dbConnection() as connection:
            with connection.cursor() as cursor:
                with write_lock:
                    cursor.execute("INSERT INTO videos (id, video_url, video_title, video_length) VALUES (%s, %s, %s, %s)", (video_id, video_url, video_title, video_length))
                    connection.commit()

        print("Successfully inserted youtube video to the database...")
        return jsonify({"message": f"Successfully added video {video_title} ({video_length} ms)", "status": "success"})
    except Exception as e:
        return jsonify({"message": f"There was an error while adding the video. Error: {str(e)}", "status": "error"})    

# Deletes a youtube video from the database    
@app.route('/delete-video/<string:video_id>', methods=['DELETE'])
def delete_video(video_id):
    print("Removing youtube video from the database...")
    try:
        with dbConnection() as connection:
            with connection.cursor() as cursor:
                with write_lock:
                    cursor.execute("DELETE FROM videos WHERE id = ?", (video_id,))
                    connection.commit()
        
        print("Successfully removed youtube video from the database...")           
        return jsonify({"message": f"Successfully deleted the video from the database", "status": "success"})
    except Exception as e:
        return jsonify({"message": f"Cannot find the video in the database or there was an error while processing your request. Error: {str(e)}", "status": "error"})




# Blacklists a product in the database
@app.route('/blacklist_product/<int:product_id>', methods=['POST'])
def blacklist_product(product_id):
    print("Blacklisting product in the database...")
    try:
        response = woocommerce.get(f"products/{product_id}")
        product_data = response.json()
        if not product_data or "name" not in product_data:
            return jsonify({"message": f"The product with ID {product_id} could not be found in the database", "status": "error"})
        
        with dbConnection() as connection:
            with connection.cursor() as cursor:
                with write_lock:
                    cursor.execute("INSERT INTO blacklisted (id, type, name) VALUES (?, ?, ?)", (product_id, 'product', product_data["name"]))
                    connection.commit()
        
        print(f"Successfully blacklisted {product_data['name']} in the database...")
        return jsonify({"message": f"Successfully blacklisted product {product_data['name']} with ID {product_id}", "status": "success"})
    except Exception as e:
        return jsonify({"message": f"The product is already blacklisted or there was an error while processing the request. Error: {str(e)}", "status": "warning"})

# Blacklists a category in the database
@app.route('/blacklist_category/<int:category_id>', methods=['POST'])
def blacklist_category(category_id):
    print("Blacklisting category in the database...")
    try:
        response = woocommerce.get(f"products/categories/{category_id}")
        category_data = response.json()
        if not category_data or "name" not in category_data:
            return jsonify({"message": f"The category with ID {category_id} could not be found in the database", "status": "error"})
        
        with dbConnection() as connection:
            with connection.cursor() as cursor:
                with write_lock:
                    cursor.execute("INSERT INTO blacklisted (id, type, name) VALUES (?, ?, ?)", (category_id, 'category', category_data["name"]))
                    connection.commit()
                    
        print(f"Successfully blacklisted category {category_data['name']} in the database...")            
        return jsonify({"message": f"Successfully blacklisted category {category_data['name']} with ID {category_id}", "status": "success"})
    except Exception as e:
        return jsonify({"message": f"The category is already blacklisted or there was an error while processing the request. Error: {str(e)}", "status": "warning"})
 
 
 

# Deletes a blacklisted product from the database
@app.route('/delete-blacklisted-product/<int:product_id>', methods=['DELETE'])
def delete_blacklisted_product(product_id):
    print("Deleting blacklisted product from the database...")
    try:
        response = woocommerce.get(f"products/{product_id}")
        product_data = response.json()
        if not product_data or "name" not in product_data:
            return jsonify({"message": f"The product with ID {product_id} could not be found in the database", "status": "error"})
        
        with dbConnection() as connection:
            with connection.cursor() as cursor:
                with write_lock:
                    cursor.execute("DELETE FROM blacklisted WHERE id = ?", (product_id,))
                    connection.commit()
                    
        print("Successfully deleted blacklisted product from the database...")            
        return jsonify({"message": f"Successfully unblacklisted product {product_data['name']} with ID {product_id}", "status": "success"})
    except Exception as e:
        return jsonify({"message": f"The product is not blacklisted or there was an error while processing the request. Error: {str(e)}", "status": "warning"})

# Deletes a blacklisted category from the database
@app.route('/delete-blacklisted-category/<int:category_id>', methods=['DELETE'])
def delete_blacklisted_category(category_id):
    print("Deleting blacklisted category from the database...")
    try:
        response = woocommerce.get(f"products/categories/{category_id}")
        category_data = response.json()
        if not category_data or "name" not in category_data:
            return jsonify({"message": f"The category with ID {category_id} could not be found in the database", "status": "error"})
        
        with dbConnection() as connection:
            with connection.cursor() as cursor:
                with write_lock:
                    cursor.execute("DELETE FROM blacklisted WHERE id = ?", (category_id,))
                    connection.commit()
                    
        print("Successfully deleted blacklisted category from the database...")             
        return jsonify({"message": f"Successfully unblacklisted category {category_data['name']} with ID {category_id}", "status": "success"})
    except Exception as e:
        return jsonify({"message": f"The category is not blacklisted or there was an error while processing the request. Error: {str(e)}", "status": "warning"})




# Checks for updates in the woocommerce and updates the database
def check_updates():
    
    print("Checking for products/categories updates and updating the database...")
    try:
        with dbConnection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT category_id FROM categories")
                stored_categories = {row[0] for row in cursor.fetchall()}


                # C A T E G O R I E S
                page = 1
                woocommerce_categories = set()

                while True:
                    response = woocommerce.get("products/categories", params={"per_page": 100, "page": page})
                    categories = response.json()
                    if not categories:
                        break
                
                    # Iterates through each category and updates the database
                    for category in categories:
                        category_id = category["id"]
                        woocommerce_categories.add(category_id)

                        query_category = """INSERT INTO categories 
                            (category_id, category_name, category_image)
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                            category_name=VALUES(category_name),
                            category_image=VALUES(category_image)"""

                        try:
                            with write_lock:
                                cursor.execute(query_category, (
                                    category_id,
                                    category["name"].upper(),
                                    category["image"]["src"] if category.get("image") else None
                                ))
                            connection.commit()
                        except mariadb.Error as e:
                            print(f"Error updating category {category_id}: {e}")

                    page += 1

                # Deletes those categories that have been removed in woocommerce from the database
                categories_to_delete = stored_categories - woocommerce_categories
                if categories_to_delete:
                    with write_lock:
                        cursor.executemany("DELETE FROM categories WHERE category_id = %s", [(cid,) for cid in categories_to_delete])
                        connection.commit()
                        print(f"Deleted {len(categories_to_delete)} categories from the database...")

                cursor.execute("SELECT product_id FROM products")
                stored_products = {row[0] for row in cursor.fetchall()}



                # P R O D U C T S
                page = 1
                woocommerce_products = set()

                while True:
                    response = woocommerce.get("products", params={"per_page": 100, "page": page, "status": "publish", "dates_are_gmt": True})
                    products = response.json()
                    if not products:
                        break

                    # Iterates through each product and updates the database
                    for product in products:
                        if product.get("catalog_visibility") != "visible":
                            continue

                        product_id = product["id"]
                        woocommerce_products.add(product_id)
                        product_modification = product.get("date_modified_gmt")

                        with read_lock:
                            cursor.execute("SELECT product_modification FROM products WHERE product_id = %s FOR UPDATE", (product_id,))
                            existing_entry = cursor.fetchone()

                        # Use the product modification date to see if it was updated
                        if existing_entry and existing_entry[0] == product_modification:
                            continue

                        product_description = BeautifulSoup(product.get("description", "--"), "html.parser").get_text()
                        get_price = product.get("price")

                        try:
                            price = f"{float(get_price):.2f}".replace('.', ',')
                        except (ValueError, TypeError):
                            price = "0,00"

                        formatted_price = f'{price}€' if product["type"] == "simple" else f"Alkaen {price}€"

                        # Gets the main category of the product (the first one)
                        main_category_id = None
                        if product.get("categories"):
                            main_category_id = product["categories"][0]["id"]

                        if main_category_id:
                            cursor.execute("SELECT category_id FROM categories WHERE category_id = %s", (main_category_id,))
                            if cursor.fetchone() is None:
                                main_category_id = None

                        query_product = """INSERT INTO products 
                            (product_id, product_name, product_description, product_sku, product_image, product_price, product_modification, product_category) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                            ON DUPLICATE KEY UPDATE 
                            product_name=VALUES(product_name), 
                            product_description=VALUES(product_description),
                            product_sku=VALUES(product_sku),
                            product_image=VALUES(product_image),
                            product_price=VALUES(product_price),
                            product_modification=VALUES(product_modification),
                            product_category=VALUES(product_category)"""

                        try:
                            with write_lock:
                                cursor.execute(query_product, (
                                    product_id,
                                    product["name"].upper(),
                                    product_description,
                                    product.get("sku"),
                                    product["images"][0]["src"] if product.get("images") else None,
                                    formatted_price,
                                    product_modification,
                                    main_category_id
                                ))
                        except mariadb.Error as e:
                            print(f"Error updating product {product_id}: {e}")

                        # Inserts into the database the categories of each product (id = id)
                        if product.get("categories"):
                            for category in product["categories"]:
                                category_id = category["id"]    
                                try:
                                    with write_lock:
                                        cursor.execute("INSERT INTO product_categories (product_id, category_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE category_id=VALUES(category_id)", (product_id, category_id))
                                        connection.commit()
                                except mariadb.Error as e:
                                    print(f"Error inserting product {product_id} with category {category_id}: {e}")

                    page += 1

                # Deletes those products that have been removed in woocommerce from the database
                products_to_delete = stored_products - woocommerce_products
                if products_to_delete:
                    with write_lock:
                        cursor.executemany("DELETE FROM products WHERE product_id = %s", [(pid,) for pid in products_to_delete])
                        connection.commit()
                        print(f"Deleted {len(products_to_delete)} products from the database...")
            
    except mariadb.Error as e:
        print(f"There was an error in the database: {e}")

    print("Database successfully updated... Awaiting next cycle (at 2 am)")
    
def is_init():
    with dbConnection() as connection:
        with connection.cursor() as cursor:
            with read_lock:
                cursor.execute("SELECT COUNT(*) FROM products")
                response = cursor.fetchone()[0]

    if response == 0:
        print("Database is empty, so updating the database tables...")
        check_updates()
    
def schedule_update():
    while True:
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        
        if hour == 2 and minute == 0:
            print("Checking for updates...")
            check_updates()
        time.sleep(5)
                
if __name__ == '__main__':
    # Check if the database is empty, if it is fill it with information
    is_init()
    
    # Independent thread for the schedule update function
    update_thread = Thread(target=schedule_update)
    update_thread.start()
    
    app.run(host='0.0.0.0', port=5040, debug=True)