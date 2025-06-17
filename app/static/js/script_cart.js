function loadCart() {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const cartContent = document.getElementById('cart-content');
    const totalPriceElement = document.getElementById('total-price');
    const checkoutForm = document.getElementById('checkout-form');
    let totalPrice = 0;

    // حالة: السلة فارغة
    if (cart.length === 0) {
        cartContent.innerHTML = `
            <div class="empty-cart">
                <i class="fas fa-shopping-cart"></i>
                <h2>سلة التسوق فارغة</h2>
                <p>لم تقم بإضافة أي منتجات إلى سلة التسوق بعد</p>
                <a href="/" class="continue-shopping">استمر في التسوق</a>
            </div>
        `;
        if (checkoutForm) checkoutForm.style.display = 'none';
        if (totalPriceElement) totalPriceElement.textContent = '0';
        return;
    }

    // بداية بناء جدول السلة
    let tableHTML = `
        <table class="cart-table">
            <thead>
                <tr>
                    <th>الصورة</th>
                    <th>المنتج</th>
                    <th>السعر</th>
                    <th>الكمية</th>
                    <th>الإجمالي</th>
                    <th>إزالة</th>
                </tr>
            </thead>
            <tbody>
    `;

    cart.forEach((item, index) => {
        const price = parseFloat(item.price);
        const quantity = parseInt(item.quantity);

        // تحقق من صحة البيانات
        if (isNaN(price) || isNaN(quantity)) {
            console.warn("بيانات غير صالحة في عنصر العربة:", item);
            return;
        }

        const itemTotal = price * quantity;
        totalPrice += itemTotal;

        tableHTML += `
            <tr>
                <td><img src="${UPLOAD_BASE_URL}${item.image}" alt="${item.name}" width="50"></td>
                <td class="product-name">${item.name}</td>
                <td class="product-price">${price.toFixed(2)} د.ج</td>
                <td>
                    <div class="product-quantity">
                        <button class="quantity-btn" onclick="updateQuantity(${index}, -1)">-</button>
                        <span>${quantity}</span>
                        <button class="quantity-btn" onclick="updateQuantity(${index}, 1)">+</button>
                    </div>
                </td>
                <td class="product-price">${itemTotal.toFixed(2)} د.ج</td>
                <td>
                    <button class="remove-btn" onclick="removeFromCart(${index})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });

    // إغلاق الجدول وإظهار الإجمالي
    tableHTML += `
            </tbody>
        </table>
        <div class="total-section">
            <h3>المجموع الكلي:</h3>
            <div class="total-price">${totalPrice.toFixed(2)} د.ج</div>
        </div>
    `;

    // عرض المحتوى في الصفحة
    cartContent.innerHTML = tableHTML;
    if (totalPriceElement) totalPriceElement.textContent = totalPrice.toFixed(2);
    if (checkoutForm) checkoutForm.style.display = 'block';
}


function updateQuantity(index, change) {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    if (cart[index]) {
        cart[index].quantity += change;
        if (cart[index].quantity < 1) cart[index].quantity = 1;
        localStorage.setItem('cart', JSON.stringify(cart));
        loadCart();
    }
}

function removeFromCart(index) {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    cart.splice(index, 1);
    localStorage.setItem('cart', JSON.stringify(cart));
    loadCart();
    showNotification('تمت إزالة المنتج من السلة');
}

function showNotification(message) {
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
    notification.innerHTML = `<i class="fas fa-check-circle" style="margin-left: 8px;"></i> ${message}`;
    
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

if (document.getElementById('checkout-form')) {
    document.getElementById('checkout-form').addEventListener('submit', function() {
        document.getElementById('cart_data').value = localStorage.getItem('cart');
    });
}

document.addEventListener('DOMContentLoaded', function () {
    if (!document.querySelector('style[data-cart-animations]')) {
        const style = document.createElement('style');
        style.setAttribute('data-cart-animations', 'true');
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
    }
    loadCart();
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
