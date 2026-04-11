const API = 'http://127.0.0.1:8000';
let currentUserId = null;

// ── Page navigation ──────────────────────────────────────
function showPage(pageId, btn) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('nav button').forEach(b => b.classList.remove('active'));
    document.getElementById(pageId).classList.add('active');
    btn.classList.add('active');
}

function showMsg(id, text, type) {
    const el = document.getElementById(id);
    el.className = 'msg ' + type;
    el.textContent = text;
}

// ── Load products ────────────────────────────────────────
async function getProducts() {
    const container = document.getElementById('products-container');
    container.innerHTML = '<p class="empty">Loading products...</p>';
    try {
        const res = await fetch(`${API}/products/`);
        if (!res.ok) throw new Error();
        const products = await res.json();
        container.innerHTML = '';
        if (!products.length) {
            container.innerHTML = '<p class="empty">No products found.</p>';
            return;
        }
        products.forEach(product => {
            const div = document.createElement('div');
            div.className = 'product-card';
            div.innerHTML = `
                <img src="${product.img || 'https://placehold.co/150x150?text=No+Image'}" alt="${product.product_name}" />
                <h3>${product.product_name}</h3>
                <p>${product.Product_Description || ''}</p>
                <p class="price">$${parseFloat(product.price).toFixed(2)}</p>
                <p class="stock ${product.quantity > 0 ? 'in' : 'out'}">
                    ${product.quantity > 0 ? 'In stock (' + product.quantity + ')' : 'Out of stock'}
                </p>
                <button class="add-to-cart" ${product.quantity === 0 ? 'disabled' : ''}>
                    Add to cart
                </button>
            `;
            div.querySelector('.add-to-cart').addEventListener('click', () => {
                addToCart(product.id, product.product_name);
            });
            container.appendChild(div);
        });
    } catch (err) {
        container.innerHTML = '<p class="empty">Failed to load products. Is the backend running?</p>';
    }
}

// ── Register ─────────────────────────────────────────────
async function registerUser() {
    const name = document.getElementById('reg-name').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const pass = document.getElementById('reg-pass').value;
    const phone = document.getElementById('reg-phone').value.trim();
    if (!name || !email || !pass) {
        showMsg('reg-msg', 'Please fill in name, email and password.', 'error');
        return;
    }
    try {
        const res = await fetch(`${API}/users/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password: pass, phone: phone || null, address: null })
        });
        const data = await res.json();
        if (res.ok) {
            currentUserId = data.id;
            document.getElementById('cart-user-id').value = data.id;
            document.getElementById('orders-user-id').value = data.id;
            const info = document.getElementById('user-info');
            info.textContent = `Hi, ${data.name} (ID: ${data.id})`;
            info.style.display = 'block';
            showMsg('reg-msg', `Account created! Your user ID is ${data.id} — keep this safe.`, 'success');
        } else {
            showMsg('reg-msg', data.detail || 'Something went wrong.', 'error');
        }
    } catch (err) {
        showMsg('reg-msg', 'Cannot connect to backend.', 'error');
    }
}

// ── Add to cart ──────────────────────────────────────────
async function addToCart(productId, productName) {
    const userId = currentUserId || document.getElementById('cart-user-id').value;
    if (!userId) {
        alert('Please register first or enter your user ID in the Cart tab.');
        return;
    }
    try {
        const res = await fetch(`${API}/cart/${userId}/items`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId, quantity: 1 })
        });
        const data = await res.json();
        if (res.ok) {
            alert(`${productName} added to cart!`);
        } else {
            alert(data.detail || 'Could not add to cart.');
        }
    } catch (err) {
        alert('Cannot connect to backend.');
    }
}

// ── Load cart ────────────────────────────────────────────
async function loadCart() {
    const userId = document.getElementById('cart-user-id').value;
    const el = document.getElementById('cart-items-list');
    if (!userId) return;
    try {
        const res = await fetch(`${API}/cart/${userId}`);
        const data = await res.json();
        if (!res.ok) { el.innerHTML = '<p class="empty">Could not load cart.</p>'; return; }
        const items = data.items || [];
        if (!items.length) {
            el.innerHTML = '<p class="empty">Your cart is empty. Go add something!</p>';
            return;
        }
        el.innerHTML = `
            <div id="cart-items">
                ${items.map(item => `
                    <div class="cart-item" id="cart-item-${item.cart_item_id}">
                        <div>
                            <div class="name">${item.product_name || 'Product #' + item.product_id}</div>
                            <div class="qty">
                                Qty: ${item.quantity}
                                <button class="btn-qty" onclick="removeItem(${userId}, ${item.cart_item_id})">Remove</button>
                            </div>
                        </div>
                        <div class="item-price">$${parseFloat(item.subtotal || 0).toFixed(2)}</div>
                    </div>
                `).join('')}
            </div>
            <div class="cart-total">
                Total: <strong>$${parseFloat(data.total || 0).toFixed(2)}</strong>
            </div>

            <!-- ✅ Checkout section -->
            <div class="checkout-box">
                <label>Shipping address</label>
                <input id="shipping-addr" type="text" placeholder="123 Street, City, Country" />
                <div style="display:flex; gap:10px; margin-top:12px;">
                    <button class="btn btn-dark" style="flex:1" onclick="checkout(${userId})">
                        Place order
                    </button>
                    <button class="btn" style="flex:1" onclick="clearCart(${userId})">
                        Clear cart
                    </button>
                </div>
                <div id="checkout-msg"></div>
            </div>
        `;
    } catch (err) {
        el.innerHTML = '<p class="empty">Cannot connect to backend.</p>';
    }
}

// ── Remove single item ───────────────────────────────────
async function removeItem(userId, cartItemId) {
    try {
        const res = await fetch(`${API}/cart/${userId}/items/${cartItemId}`, { method: 'DELETE' });
        if (res.ok) loadCart();
        else alert('Could not remove item.');
    } catch (err) {
        alert('Cannot connect to backend.');
    }
}

// ── Clear cart ───────────────────────────────────────────
async function clearCart(userId) {
    try {
        const res = await fetch(`${API}/cart/${userId}/clear`, { method: 'DELETE' });
        if (res.ok) loadCart();
        else alert('Could not clear cart.');
    } catch (err) {
        alert('Cannot connect to backend.');
    }
}

// ── Checkout ─────────────────────────────────────────────
async function checkout(userId) {
    const addr = document.getElementById('shipping-addr').value.trim();
    if (!addr) {
        showMsg('checkout-msg', 'Please enter a shipping address.', 'error');
        return;
    }
    try {
        // shipping_addr is a query param in your router: POST /{user_id}/checkout?shipping_addr=...
        const res = await fetch(`${API}/orders/${userId}/checkout?shipping_addr=${encodeURIComponent(addr)}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await res.json();
        if (res.ok) {
            showMsg('checkout-msg', `Order placed! Order ID: ${data.id} — Total: $${parseFloat(data.total_amount).toFixed(2)}`, 'success');
            // pre-fill orders page and reload cart
            document.getElementById('orders-user-id').value = userId;
            setTimeout(() => loadCart(), 1500);
        } else {
            showMsg('checkout-msg', data.detail || 'Could not place order.', 'error');
        }
    } catch (err) {
        showMsg('checkout-msg', 'Cannot connect to backend.', 'error');
    }
}

// ── Load all orders ──────────────────────────────────────
async function loadOrders() {
    const userId = document.getElementById('orders-user-id').value;
    const el = document.getElementById('orders-list');
    if (!userId) return;
    try {
        const res = await fetch(`${API}/orders/${userId}`);
        const orders = await res.json();
        if (!res.ok || !orders.length) {
            el.innerHTML = '<p class="empty">No orders found.</p>';
            return;
        }
        el.innerHTML = orders.map(order => `
            <div class="order-card" onclick="loadOrderDetail(${userId}, ${order.id}, this)">
                <div class="order-header">
                    <div>
                        <div class="order-id">Order #${order.id}</div>
                        <div class="order-date">${new Date(order.created_at).toLocaleDateString()}</div>
                    </div>
                    <div style="text-align:right">
                        <div class="order-total">$${parseFloat(order.total_amount).toFixed(2)}</div>
                        <span class="status-badge ${order.status}">${order.status}</span>
                    </div>
                </div>
                <div class="order-detail" id="detail-${order.id}"></div>
            </div>
        `).join('');
    } catch (err) {
        el.innerHTML = '<p class="empty">Cannot connect to backend.</p>';
    }
}

// ── Load single order detail (click to expand) ───────────
async function loadOrderDetail(userId, orderId, card) {
    const detailEl = document.getElementById(`detail-${orderId}`);

    // toggle — click again to close
    if (detailEl.innerHTML) {
        detailEl.innerHTML = '';
        return;
    }

    try {
        const res = await fetch(`${API}/orders/${userId}/${orderId}`);
        const data = await res.json();
        if (!res.ok) { detailEl.innerHTML = '<p class="empty">Could not load details.</p>'; return; }

        detailEl.innerHTML = `
            <div class="order-items">
                ${data.items.map(item => `
                    <div class="order-item-row">
                        <span>${item.product_name} × ${item.quantity}</span>
                        <span>$${parseFloat(item.subtotal).toFixed(2)}</span>
                    </div>
                `).join('')}
            </div>
            <div class="order-addr">Shipping to: ${data.shipping_addr}</div>
        `;
    } catch (err) {
        detailEl.innerHTML = '<p class="empty">Cannot connect to backend.</p>';
    }
}

window.addEventListener('DOMContentLoaded', getProducts);