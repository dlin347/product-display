/* Sets the time between random products */
function modify_time() {
    const speed = document.getElementById("time").value;

    fetch(`/speed/${speed}`, { method: "POST" })
        .then(response => response.json())
        .then(data => {
            Swal.fire({
                title: data.status.charAt(0).toUpperCase() + data.status.slice(1),
                text: data.message,
                icon: data.status
            });
        })
        .catch(error => {
            console.error("Error setting speed:", error);
        });
}


/* Modifies the probabilities of getting a random product, random category, products grid or random youtube video */
function modify_chances() {
    const chancesRandomProduct = document.getElementById("chancesRandomProduct").value;
    const chancesRandomCategory = document.getElementById("chancesRandomCategory").value;
    const chancesGrid = document.getElementById("chancesGrid").value;
    const chancesYoutubeVideo = document.getElementById("chancesYoutubeVideo").value;
    const chancesWebsite = document.getElementById("chancesWebsite").value;
    const total = parseInt(chancesRandomProduct) + parseInt(chancesRandomCategory) + parseInt(chancesGrid) + parseInt(chancesYoutubeVideo) + parseInt(chancesWebsite)

    if (total > 100 || total < 100) {
        load_chances()
        return Swal.fire({
            title: 'Error',
            text: 'The sum of all the chances must be equal to 100%',
            icon: 'error'
        });
    }

    fetch(`/probabilities/${chancesRandomProduct}/${chancesRandomCategory}/${chancesGrid}/${chancesYoutubeVideo}/${chancesWebsite}`, { method: "POST" })
        .catch(error => {
            console.error("Error setting all the probabilities:", error);
        });

    Swal.fire({
        title: 'Success',
        text: 'Successfully changed the probabilities',
        icon: 'success'
    });
}

/* Validates the URL */
function isValidURL(url) {
    const pattern = /^(https?:\/\/)?([\w-]+(\.[\w-]+)+)(\/[\w-]*)*$/;
    return pattern.test(url);
}

/* Adds a website id and url to the database and stores a screenshot */
async function add_website() {
    let timerInterval;
    const url = document.getElementById("websiteURL").value.trim();

    if (!isValidURL(url)) {
        return Swal.fire({
            title: "Error",
            text: "Invalid URL, please enter a valid one",
            icon: "error"
        });
    }

    Swal.fire({
        title: "Wait!",
        html: "Making and storing a screenshot of the website. This might take a while...",
        timer: 15000,
        timerProgressBar: true,
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        },
        willClose: () => {
            clearInterval(timerInterval);
        }
    })

    try {
        const encodedURL = encodeURIComponent(url);

        const response = await fetch("/add_website", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url: encodedURL })
        });

        const data = await response.json();

        loadWebsites();

        Swal.close()
        
        if (data.message) {
            Swal.fire({
                title: data.status.charAt(0).toUpperCase() + data.status.slice(1),
                text: data.message,
                icon: data.status
            });
        } else {
            Swal.fire({
                title: 'Error',
                text: 'There was an error while trying to take the screenshot...',
                icon: 'error'
            });
        }
    } catch (error) {
        console.error("Error adding website to the database:", error);
    }
}

/* Adds a youtube video id, url and length to the database */
async function add_video() {
    const url = document.getElementById("youtubeURL").value;
    video_id = url.split("v=")[1].split("&")[0]

    try {
        const response = await fetch(`/add_video/${video_id}`, { method: "POST" });
        const data = await response.json();

        Swal.fire({
            title: data.status.charAt(0).toUpperCase() + data.status.slice(1),
            text: data.message,
            icon: data.status
        });

        loadVideos();
    } catch (error) {
        console.error("Error adding video to the database:", error);
    }
}


/* Blacklists a product by its ID */
async function blacklist_product() {
    const productId = document.getElementById("product_id").value;

    try {
        const response = await fetch(`/blacklist_product/${productId}`, { method: "POST" });
        const data = await response.json();

        Swal.fire({
            title: data.status.charAt(0).toUpperCase() + data.status.slice(1),
            text: data.message,
            icon: data.status
        });

        loadBlacklistedProducts();
    } catch (error) {
        console.error("Error blacklisting a product:", error);
    }
}

/* Blacklists a category by its ID */
async function blacklist_category() {
    const categoryId = document.getElementById("category_id").value;

    try {
        const response = await fetch(`/blacklist_category/${categoryId}`, { method: "POST" });
        const data = await response.json();

        Swal.fire({
            title: data.status.charAt(0).toUpperCase() + data.status.slice(1),
            text: data.message,
            icon: data.status
        });

        loadBlacklistedCategories();
    } catch (error) {
        console.error("Error blacklisting a category:", error);
    }
}






/* Sets the time value in the slider and in the span on site load */
function load_time() {
    const time = document.getElementById("time");
    const slider = document.getElementById("sliderValue");

    fetch('/speed')
        .then(response => response.json())
        .then(data => {
            time.value = (data.speed / 1000)
            slider.textContent = (data.speed / 1000)
        })
        .catch(error => console.error("Error fetching the speed and loading the time:", error));
}


/* Loads the probabilities in the slider and in the span */
function load_chances() {
    const sliderValueRandomProduct = document.getElementById("sliderValueRandomProduct");
    const chancesRandomProduct = document.getElementById("chancesRandomProduct");
    const sliderValueRandomCategory = document.getElementById("sliderValueRandomCategory");
    const chancesRandomCategory = document.getElementById("chancesRandomCategory");
    const sliderValueGrid = document.getElementById("sliderValueGrid");
    const chancesGrid = document.getElementById("chancesGrid");
    const sliderValueYoutubeVideo = document.getElementById("sliderValueYoutubeVideo");
    const chancesYoutubeVideo = document.getElementById("chancesYoutubeVideo");
    const sliderValueWebsite = document.getElementById("sliderValueWebsite");
    const chancesWebsite = document.getElementById("chancesWebsite");

    fetch('/probabilities')
        .then(response => response.json())
        .then(data => {
            chancesRandomProduct.value = data.random_product
            chancesRandomProduct.dataset.prevValue = data.random_product;
            sliderValueRandomProduct.textContent = data.random_product

            chancesRandomCategory.value = data.random_category_products
            chancesRandomCategory.dataset.prevValue = data.random_category_products;
            sliderValueRandomCategory.textContent = data.random_category_products

            chancesGrid.value = data.grid
            chancesGrid.dataset.prevValue = data.grid;
            sliderValueGrid.textContent = data.grid

            chancesYoutubeVideo.value = data.youtube_video
            chancesYoutubeVideo.dataset.prevValue = data.youtube_video;
            sliderValueYoutubeVideo.textContent = data.youtube_video

            chancesWebsite.value = data.website
            chancesWebsite.dataset.prevValue = data.website;
            sliderValueWebsite.textContent = data.website
        })
        .catch(error => console.error("Error fetching the probabilities, so cannot display them in the control panel:", error));
}


/* Gets the websites information from the database table and inserts them into their corresponding container */
function loadWebsites() {
    fetch('/get_websites')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('websites_urls');
            container.innerHTML = "";

            if (data.length == 0) {
                const h4 = document.createElement("h4");
                h4.innerText = "There are not websites in the database..."
                h4.style.marginTop = "10px"
                h4.style.fontWeight = "lighter"
                return container.appendChild(h4)
            }

            data.forEach(website => {
                const websiteElement = document.createElement("p");
                websiteElement.innerText = website.website_url;
                websiteElement.style.cursor = "pointer";
                websiteElement.style.backgroundColor = '#007bff';
                websiteElement.style.color = "white";
                websiteElement.onclick = () => deleteWebsite(website.website_id, website.website_url);
                container.appendChild(websiteElement);
            });
        })
        .catch(error => console.error("Error getting the websites, so not displaying them in the control panel:", error));
}

/* Gets the youtube videos stored in the database table and inserts them into their corresponding container */
function loadVideos() {
    fetch('/get_videos')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('videos_urls');
            container.innerHTML = "";

            if (data.length == 0) {
                const h4 = document.createElement("h4");
                h4.innerText = "There are not videos in the database..."
                h4.style.marginTop = "10px"
                h4.style.fontWeight = "lighter"
                return container.appendChild(h4)
            }

            data.forEach(video => {
                const videoElement = document.createElement("p");
                videoElement.innerText = `${video.video_title} (${video.video_length} ms)`;
                videoElement.style.cursor = "pointer";
                videoElement.style.backgroundColor = '#007bff';
                videoElement.style.color = "white";
                videoElement.onclick = () => deleteVideo(video.video_id, video.video_title);
                container.appendChild(videoElement);
            });
        })
        .catch(error => console.error("Error getting the youtube videos, so not displaying them in the control panel:", error));
}


/* Gets the blacklisted products stored in the database table and inserts them into their corresponding container */
function loadBlacklistedProducts() {
    fetch('/get-blacklisted-products')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('products_ids');
            container.innerHTML = "";

            if (data.length == 0) {
                const h4 = document.createElement("h4");
                h4.innerText = "There are not blacklisted products in the database..."
                h4.style.marginTop = "10px"
                h4.style.fontWeight = "lighter"
                return container.appendChild(h4)
            }

            data.forEach(product => {
                const productElement = document.createElement("p");
                productElement.innerText = `${product.product_name} (ID: ${product.product_id})`;
                productElement.style.cursor = "pointer";
                productElement.style.backgroundColor = '#007bff';
                productElement.style.color = "white";
                productElement.onclick = () => deleteBlacklistedProduct(product.product_id, product.product_name);
                container.appendChild(productElement);
            });
        })
        .catch(error => console.error("Error fetching blacklisted products, so not displaying them in the control panel:", error));
}


/* Gets the blacklisted categories stored in the database table and inserts them into their corresponding container */
function loadBlacklistedCategories() {
    fetch('/get-blacklisted-categories')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('categories_ids');
            container.innerHTML = "";

            if (data.length == 0) {
                const h4 = document.createElement("h4");
                h4.innerText = "There are not blacklisted categories in the database..."
                h4.style.marginTop = "10px"
                h4.style.fontWeight = "lighter"
                return container.appendChild(h4)
            }

            data.forEach(category => {
                const categoryElement = document.createElement("p");
                categoryElement.innerText = `${category.category_name} (ID: ${category.category_id})`;
                categoryElement.style.cursor = "pointer";
                categoryElement.style.backgroundColor = '#007bff';
                categoryElement.style.color = "white";
                categoryElement.onclick = () => deleteBlacklistedCategory(category.category_id, category.category_name);
                container.appendChild(categoryElement);
            });
        })
        .catch(error => console.error("Error fetching blacklisted categories, so not displaying them in the control panel:", error));
}




/* Asks for confimation and deletes the website from the database table */
function deleteWebsite(websiteId, websiteURL) {
    Swal.fire({
        title: "Confirmation",
        text: `Are you sure that you want to remove the website ${websiteURL} with ID ${websiteId} from the database?`,
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Yes",
        cancelButtonText: "No"
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/delete-website/${websiteId}`, { method: "DELETE" })
                .then(response => response.json())
                .then(data => {
                    Swal.fire({
                        title: data.status.charAt(0).toUpperCase() + data.status.slice(1),
                        text: data.message,
                        icon: data.status
                    });
                    loadWebsites();
                })
                .catch(error => console.error("Error deleting the video from the database:", error));
        }
    });
}


/* Asks for confimation and deletes the youtube video from the database table */
function deleteVideo(videoId, videoTitle) {
    Swal.fire({
        title: "Confirmation",
        text: `Are you sure that you want to remove the video ${videoTitle} with ID ${videoId} from the database?`,
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Yes",
        cancelButtonText: "No"
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/delete-video/${videoId}`, { method: "DELETE" })
                .then(response => response.json())
                .then(data => {
                    Swal.fire({
                        title: data.status.charAt(0).toUpperCase() + data.status.slice(1),
                        text: data.message,
                        icon: data.status
                    });
                    loadVideos();
                })
                .catch(error => console.error("Error deleting the video from the database:", error));
        }
    });
}


/* Asks for confimation and deletes the blacklisted product from the database table */
function deleteBlacklistedProduct(productId, productName) {
    Swal.fire({
        title: "Confirmation",
        text: `Are you sure that you want to remove the product ${productName} with ID ${productId} from blacklist?`,
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Yes",
        cancelButtonText: "No"
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/delete-blacklisted-product/${productId}`, { method: "DELETE" })
                .then(response => response.json())
                .then(data => {
                    Swal.fire({
                        title: data.status.charAt(0).toUpperCase() + data.status.slice(1),
                        text: data.message,
                        icon: data.status
                    });
                    loadBlacklistedProducts();
                })
                .catch(error => console.error("Error deleting a blacklisted product:", error));
        }
    });
}


/* Asks for confimation and deletes the blacklisted category from the database table */
function deleteBlacklistedCategory(categoryId, categoryName) {
    Swal.fire({
        title: "Confirmation",
        text: `Are you sure that you want to remove the category ${categoryName} with ID ${categoryId} from blacklist?`,
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Yes",
        cancelButtonText: "No"
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/delete-blacklisted-category/${categoryId}`, { method: "DELETE" })
                .then(response => response.json())
                .then(data => {
                    Swal.fire({
                        title: data.status.charAt(0).toUpperCase() + data.status.slice(1),
                        text: data.message,
                        icon: data.status
                    });
                    loadBlacklistedCategories();
                })
                .catch(error => console.error("Error deleting a blacklisted category:", error));
        }
    });
}




/* Updates the span element when the slide value changes (oninput) */
function update_value(slider, targetElement) {
    document.getElementById(targetElement).textContent = parseInt(slider);
}


let locked = {
    chancesRandomProduct: false,
    chancesRandomCategory: false,
    chancesGrid: false,
    chancesYoutubeVideo: false,
    chancesWebsite: false
}


/* Testing Function */
function smartSlider(input) {
    const ids = ["chancesRandomProduct", "chancesRandomCategory", "chancesGrid", "chancesYoutubeVideo", "chancesWebsite"];

    locked[input.id] = true;

    let freeInputs = [];
    let total = 0;

    ids.forEach(id => {
        const slider = document.getElementById(id);
        total += Number(slider.value);
        if (!locked[id]) {
            freeInputs.push(slider);
        }
    });

    let d = total - 100;

    if (freeInputs.length === 0) return;

    let freeTotal = freeInputs.reduce((sum, slider) => sum + Number(slider.value), 0);

    freeInputs.forEach(slider => {
        let v = Number(slider.value);
        let adjustment = freeTotal === 0 ? (d / freeInputs.length) : ((v / freeTotal) * d);
        let newVal = Math.max(0, Math.min(100, v - adjustment));
        newVal = Math.round(newVal);
        slider.value = newVal;

        let targetId = "sliderValue" + slider.id.replace("chances", "");
        update_value(newVal, targetId);
    });

    let finalSum = ids.reduce((sum, id) => sum + Number(document.getElementById(id).value), 0);
    let diffRound = 100 - finalSum;

    if (diffRound !== 0) {
        let sliderToAdjust = freeInputs.reduce((a, b) => Number(a.value) < Number(b.value) ? a : b);
        sliderToAdjust.value = Math.max(0, Math.min(100, Number(sliderToAdjust.value) + diffRound));

        let targetId = "sliderValue" + sliderToAdjust.id.replace("chances", "");
        update_value(sliderToAdjust.value, targetId);
    }

    input.dataset.prevValue = input.value;
}


/* Loads all the information in the control panel when the window loads */
function load() {
    load_time();
    load_chances();
    loadVideos();
    loadWebsites();
    loadBlacklistedProducts();
    loadBlacklistedCategories();

    locked = {
        chancesRandomProduct: false,
        chancesRandomCategory: false,
        chancesGrid: false,
        chancesYoutubeVideo: false,
        chancesWebsite: false
    }
}
window.onload = load;