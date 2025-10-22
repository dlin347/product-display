/* Selects a mode according to the probabilities */
function makeChoice(probabilities) {
    const random = Math.random() * 100;
    let cumulative = 0;

    for (const { percentage, value } of probabilities) {
        cumulative += percentage;
        if (random < cumulative) return value;
    }
}


/* Selects a display product mode */
async function selectMode() {
    try {
        const response = await fetch('/probabilities').then(response => response.json())

        const probabilities = [
            { percentage: response.random_product, value: 'random_product' },
            { percentage: response.random_category_products, value: 'random_category_products' },
            { percentage: response.grid, value: 'grid' },
            { percentage: response.youtube_video, value: 'youtube_video' },
            { percentage: response.website, value: 'website' }
        ];

        return makeChoice(probabilities);
    } catch (error) {
        return console.error("Error fetching the probabilities and making a choice:", error);
    }
}


/* Displays a loading screen and after some seconds hides it */
function displayLoading() {
    const loader = document.getElementById('loader');
    const background = document.getElementById('background');

    loader.classList.add('active');
    background.classList.add('active');
    setTimeout(() => {
        loader.classList.remove('active');
    }, 2500)
    setTimeout(() => {
        background.classList.remove('active');
    }, 3100);
}


/* Calls the function according to the selected mode, when the promise is resolved recalls this function */
async function renderDisplay() {
    displayLoading()
    await new Promise(resolve => setTimeout(resolve, 500));
    const mode = await selectMode();

    if (mode === 'random_product') {
        await showRandomProducts();
    } else if (mode === 'random_category_products') {
        await showRandomCategoryProducts();
    } else if (mode === 'grid') {
        await showGrid();
    } else if (mode === 'youtube_video') {
        await showYoutubeVideo();
    } else if (mode === 'website') {
        await showwWebsite();
    }

    return renderDisplay();
}


/* Fetches the random product speed from the database */
async function getSpeed() {
    try {
        const response = await fetch('/speed').then(response => response.json())
        return response.speed
    } catch (error) {
        return console.error("Error fetching the speed of random product displaying:", error);
    }
}


/* Displays 10 random products from the database (using the set speed) */
async function showRandomProducts() {
    let products;

    try {
        const response = await fetch('/random_product');
        if (!response.ok) throw new Error('Error fetching random products from the database...');
        products = await response.json();
    } catch (err) {
        console.error('Error displaying random products from the database: ', err);
    }

    const container = document.getElementById('container');
    const productsToShow = products.products.length;

    /* Iterates through the products array displaying them */
    for (let i = 0; i < productsToShow; i++) {
        try {
            const time = await getSpeed();
            const product = products.products[i];
            const randomProductContainer = document.createElement('div');
            randomProductContainer.id = 'randomProductContainer';
            randomProductContainer.innerHTML = `
                <img src="${product.image}" alt="${product.name}" id="randomProductImage" />
                <h1 id="randomProductName">${product.name}</h1>
                <p id="randomProductDescription">${product.description}</p>
                <p id="randomProductSKU">${product.sku}</p>
                <p id="randomProductPrice">${product.price}</p>
            `;

            container.appendChild(randomProductContainer);

            await new Promise(resolve => setTimeout(resolve, time));

            container.removeChild(randomProductContainer);
        } catch (error) {
            console.error('Error displaying a random product from the database: ', error);
            break;
        }
    }
    /* Once it has finished it resolves the promise */
    return Promise.resolve();
}


/* Displays a random category and its products in a grid (that automatically scrolls down) */
async function showRandomCategoryProducts() {
    let categoryandproducts;

    try {
        const response = await fetch('/random_category_products');
        if (!response.ok) throw new Error('Error fetching a random category from the database...');
        categoryandproducts = await response.json();
    } catch (err) {
        console.error('Error fetching a random category:', err);
        return;
    }

    const container = document.getElementById('container');
    const durationSeconds = categoryandproducts.products.length;


    const grid = document.createElement('div');
    grid.id = 'productGrid';
    grid.style.display = 'grid';
    grid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(300px, 1fr))';
    grid.style.gap = '15px';
    grid.style.marginTop = '10px';
    /* Fixes the category for 5 seconds */
    setTimeout(() => {
        grid.style.animation = `scrollDown ${durationSeconds}s linear forwards`;
    }, 5000)

    /* Makes the category take the entire screen */
    const categoryHeader = document.createElement('div');
    categoryHeader.id = 'categoryHeader';
    categoryHeader.style.gridColumn = '1 / -1';
    categoryHeader.style.textAlign = 'center';
    categoryHeader.style.height = '100vh';
    categoryHeader.style.display = 'flex';
    categoryHeader.style.flexDirection = 'column';
    categoryHeader.style.alignItems = 'center';
    categoryHeader.style.justifyContent = 'center';
    categoryHeader.innerHTML = `
        <img src="${categoryandproducts.category.image}" alt="${categoryandproducts.category.name}" />
        <h1 style="margin-top: 10px;">${categoryandproducts.category.name}</h1>
    `;
    grid.appendChild(categoryHeader);

    categoryandproducts.products.forEach(product => {
        const productCard = document.createElement('div');
        productCard.className = 'productCard';
        productCard.style.border = '1px solid #ccc';
        productCard.style.padding = '10px';
        productCard.style.textAlign = 'center';

        productCard.innerHTML = `
            <img src="${product.image}" alt="${product.name}" style="width: 95%; max-height: 250px; object-fit: contain;" loading="auto"/>
            <p><strong>${product.name}</strong></p>
            <p>${product.price}</p>
        `;

        grid.appendChild(productCard);
    });

    /* When the autoscroll reaches the end of the site the promise gets resolved so it recalls the function */
    container.appendChild(grid);
    await new Promise(resolve => {
        function checkScroll() {
            if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 10) {
                setTimeout(() => {
                    resolve();
                }, 1000)
            } else {
                requestAnimationFrame(checkScroll);
            }
        }

        checkScroll();
    });

    container.removeChild(grid);
    return Promise.resolve();
}


/* Displays a grid of 198 random products */
async function showGrid() {
    let products;

    try {
        const response = await fetch('/product_grid');
        if (!response.ok) throw new Error('Error fetching grid from the database...');
        products = await response.json();
    } catch (err) {
        console.error('Error displaying grid from the database:', err);
        return;
    }

    const container = document.getElementById('container');

    const grid = document.createElement('div');
    grid.id = 'productGrid';
    grid.style.animation = `scrollDown 198s linear forwards`;

    try {
        products.products.forEach(product => {
            const productCard = document.createElement('div');
            productCard.className = 'productCard';
            productCard.style.border = '1px solid #ccc'
            productCard.style.padding = '10px'
            productCard.style.textAlign = 'center'

            productCard.innerHTML = `
            <img src="${product.image}" alt="${product.name}" style="width: 95%; max-height: 250px;" loading="lazy"/>
            <p><strong>${product.name}</strong></p>
            <p>${product.price}</p>
            `;

            grid.appendChild(productCard);
        });
    } catch (error) {
        console.error('Error displaying grid from the database:', error);
    }

    container.appendChild(grid);

    /* When the autoscroll reaches the end of the site the promise gets resolved so it recalls the function */
    await new Promise(resolve => {
        function checkScroll() {
            if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 10) {
                setTimeout(() => {
                    resolve();
                }, 1000)
            } else {
                requestAnimationFrame(checkScroll);
            }
        }

        checkScroll();
    });

    container.removeChild(grid);
    return Promise.resolve();
}


/* Displays a random youtube video from the database */
async function showYoutubeVideo() {
    let video;

    try {
        const response = await fetch('/youtube_video');
        if (!response.ok) throw new Error('Error fetching the youtube video from the database...');
        video = await response.json();
    } catch (err) {
        console.error('Error displaying the youtube video: ', err);
        return;
    }

    const container = document.getElementById('container');

    const iframe = document.createElement('iframe');
    iframe.src = video.video_url + '?autoplay=1&controls=0&modestbranding=1&rel=0';
    iframe.allow = 'autoplay; fullscreen';
    container.appendChild(iframe);

    /* Resolves the promise when the youtube video has finished */
    await new Promise(resolve => setTimeout(resolve, video.video_length));

    container.removeChild(iframe);
    return Promise.resolve();
}


/* Displays a website screenshot */
async function showwWebsite() {
    try {
        const response = await fetch('/website');
        if (!response.ok) throw new Error('Error fetching a website from the database...');
        website = await response.json();
    } catch (err) {
        console.error('Error displaying a website from the database: ', err);
        return;
    }

    const container = document.getElementById("container");

    const screenshot = document.createElement("img");
        screenshot.src = `/static/img/${website.website_id}.png`;
        screenshot.style.position = "absolute";
        screenshot.style.width = "100vw";
        screenshot.style.height = "auto";
        screenshot.style.top = "0";
        screenshot.style.left = "0";
    setTimeout(() => {
        screenshot.style.animation = `scrollDown 20s linear forwards`;
    }, 2000)


    container.appendChild(screenshot);

    await new Promise(resolve => setTimeout(resolve, 25000));

    container.removeChild(screenshot);
}

/* When the DOM is loaded it calls the renderDisplay() function */
document.addEventListener('DOMContentLoaded', () => {
    renderDisplay();
});