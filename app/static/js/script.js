   // Toggle sidebar
   function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('active');
}

// Toggle dropdown
function toggleDropdown(id) {
    document.getElementById(id).style.display = 
        document.getElementById(id).style.display === 'block' ? 'none' : 'block';
}

// Close dropdowns when clicking outside
window.onclick = function(event) {
    if (!event.target.matches('button') && !event.target.matches('.dropdown *')) {
        const dropdowns = document.getElementsByClassName("dropdown-content");
        for (let i = 0; i < dropdowns.length; i++) {
            const openDropdown = dropdowns[i];
            if (openDropdown.style.display === 'block') {
                openDropdown.style.display = 'none';
            }
        }
    }
}

// Select option from dropdown
function selectOption(type, value) {
    console.log(`Selected ${type}: ${value}`);
    // Here you would typically update the UI and send the selection to your backend
    document.getElementById(`${type}Dropdown`).style.display = 'none';
    
    // Show a notification
    const notification = document.createElement('div');
    notification.style.position = 'fixed';
    notification.style.bottom = '20px';
    notification.style.left = '20px';
    notification.style.backgroundColor = '#4BB543';
    notification.style.color = 'white';
    notification.style.padding = '12px 24px';
    notification.style.borderRadius = '8px';
    notification.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    notification.style.zIndex = '10000';
    notification.style.animation = 'slideIn 0.5s, fadeOut 0.5s 2.5s';
    notification.style.animationFillMode = 'forwards';
    
    if (type === 'country') {
        notification.textContent = `تم اختيار دولة جديدة: ${value}`;
    } else {
        notification.textContent = `تم اختيار لغة جديدة: ${value}`;
    }
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Carousel navigation
function moveLeft(gridId = 'productGrid') {
    const grid = document.getElementById(gridId);
    grid.scrollBy({ left: -320, behavior: 'smooth' });
}

function moveRight(gridId = 'productGrid') {
    const grid = document.getElementById(gridId);
    grid.scrollBy({ left: 320, behavior: 'smooth' });
}

function addToCart(id, name, price, image) {
    // جلب السلة الحالية من الذاكرة المحلية أو إنشاء سلة جديدة
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    
    // التحقق إذا كان المنتج موجوداً بالفعل في السلة
    const existingItem = cart.find(item => item.id === id);
    
    if (existingItem) {
        // إذا كان المنتج موجوداً، نزيد الكمية فقط
        existingItem.quantity += 1;
    } else {
        // إذا كان المنتج غير موجود، نضيفه جديداً
        cart.push({
            id: id,
            name: name,
            price: parseFloat(price), // تحويل السعر إلى رقم
            image: image,
            quantity: 1
        });
    }
    
    // حفظ السلة المحدثة في الذاكرة المحلية
    localStorage.setItem('cart', JSON.stringify(cart));
    
    // تحديث عداد السلة
    updateCartCount();
    
    // عرض الإشعار
    showNotification(`تم إضافة "${name}" إلى سلة التسوق`);
}

// دالة لتحديث عداد السلة
function updateCartCount() {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const totalItems = cart.reduce((total, item) => total + item.quantity, 0);
    document.getElementById('cart-count').textContent = totalItems;
    
    // تأثير حركة أيقونة السلة
    const cartIcon = document.querySelector('.fa-shopping-cart');
    cartIcon.style.transform = 'scale(1.3)';
    setTimeout(() => {
        cartIcon.style.transform = 'scale(1)';
    }, 300);
}

// دالة عرض الإشعارات (نفسها كما عندك)
function showNotification(message) {
    const notification = document.createElement('div');
    notification.style.position = 'fixed';
    notification.style.bottom = '20px';
    notification.style.left = '20px';
    notification.style.backgroundColor = '#4361ee';
    notification.style.color = 'white';
    notification.style.padding = '16px 24px';
    notification.style.borderRadius = '8px';
    notification.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    notification.style.zIndex = '10000';
    notification.style.display = 'flex';
    notification.style.alignItems = 'center';
    notification.style.animation = 'slideIn 0.5s, fadeOut 0.5s 2.5s';
    notification.style.animationFillMode = 'forwards';
    
    notification.innerHTML = `
        <i class="fas fa-check-circle" style="margin-left: 10px; font-size: 1.2rem;"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// عند تحميل الصفحة، نحدث عداد السلة
document.addEventListener('DOMContentLoaded', updateCartCount);

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(-100px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
    }
`;
document.head.appendChild(style);

function searchProducts() {
    let input = document.getElementById("searchInput");
    if (!input) {
        console.error("عنصر البحث غير موجود في الصفحة!");
        return;
    }

    let searchText = input.value.toLowerCase().trim();
    let productsContainers = document.querySelectorAll(".product-grid");
    let resultsDiv = document.getElementById("searchResults");

    if (!resultsDiv) {
        console.error("عنصر عرض النتائج غير موجود!");
        return;
    }

    resultsDiv.innerHTML = "";
    let matches = 0;

    productsContainers.forEach(container => {
        let products = container.querySelectorAll(".product-card");

        products.forEach(product => {
            let productNameElement = product.querySelector(".product-name");
            if (!productNameElement) {
                console.warn("عنصر اسم المنتج غير موجود في:", product);
                return;
            }

            let productName = productNameElement.textContent.toLowerCase();
            if (productName.includes(searchText)) {
                product.style.display = "block";
                matches++;
            } else {
                product.style.display = "none";
            }
        });
    });

    if (matches === 0) {
        resultsDiv.innerHTML = "<p>لم يتم العثور على نتائج</p>";
        resultsDiv.style.display = "block";
    } else {
        resultsDiv.style.display = "none";
    }
}

document.addEventListener("DOMContentLoaded", function() {
    let searchInput = document.getElementById("searchInput");
    if (searchInput) {
        searchInput.addEventListener("keyup", searchProducts);
    } else {
        console.error("عنصر البحث غير موجود، تأكد من صحة الـ HTML!");
    }
});



document.addEventListener("DOMContentLoaded", function () {
    const themeToggle = document.getElementById("dark-mode-toggle");
    const body = document.body;
    const themeIcon = themeToggle.querySelector("i"); // أيقونة القمر
    const themeText = themeToggle.childNodes[2]; // النص بجانب الأيقونة

    // التحقق من الوضع المخزن في localStorage
    if (localStorage.getItem("darkMode") === "enabled") {
        body.classList.add("dark-mode");
        themeIcon.classList.replace("fa-moon", "fa-sun");
        themeText.nodeValue = " الوضع العادي"; // تحديث النص
    }

    themeToggle.addEventListener("click", function () {
        body.classList.toggle("dark-mode");

        if (body.classList.contains("dark-mode")) {
            localStorage.setItem("darkMode", "enabled");
            themeIcon.classList.replace("fa-moon", "fa-sun");
            themeText.nodeValue = " الوضع العادي"; // تحديث النص
        } else {
            localStorage.setItem("darkMode", "disabled");
            themeIcon.classList.replace("fa-sun", "fa-moon");
            themeText.nodeValue = " الوضع الليلي"; // تحديث النص
        }
    });
});

const exchangeRates = {
    DZD: 1,
    MRU: 0.34,
    DOURO: 0.2
};

const currencySymbols = {
    DZD: "د.ج",
    MRU: "أوقية",
    DOURO: "دورو"
};

// تغيير العملة وحفظها في localStorage
function changeCurrency(currency) {
    localStorage.setItem("selectedCurrency", currency);
    updatePrices(currency);
}

// تحديث الأسعار في الصفحة
function updatePrices(currency) {
    const elements = document.querySelectorAll(".product-price");

    elements.forEach(el => {
        const basePrice = parseFloat(el.getAttribute("data-price"));
        const converted = basePrice * exchangeRates[currency];
        el.innerText = converted.toFixed(2) + " " + currencySymbols[currency];
    });
}

// عند تحميل الصفحة: استخدام العملة المحفوظة أو DZD
document.addEventListener("DOMContentLoaded", () => {
    const savedCurrency = localStorage.getItem("selectedCurrency") || "DZD";
    updatePrices(savedCurrency);
});
document.querySelectorAll('.currency-btn').forEach(btn => {
    btn.addEventListener('click', function (e) {
        e.preventDefault(); // يمنع التحديث
        const selected = this.getAttribute('data-currency');
        changeCurrency(selected);
    });
});
