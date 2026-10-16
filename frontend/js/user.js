Auth.require("user");
document.getElementById("uname").textContent = Auth.username;

const $ = (id) => document.getElementById(id);

function flash(el, text, ok = false) {
  el.className = "msg " + (ok ? "ok" : "err");
  el.textContent = text;
}

// Tablar
document.querySelectorAll(".tabs button").forEach((b) => {
  b.onclick = () => {
    document.querySelectorAll(".tabs button").forEach((x) => x.classList.remove("active"));
    b.classList.add("active");
    ["products", "cart", "balanceTab", "orders"].forEach((id) =>
      $(id).classList.toggle("hidden", id !== b.dataset.tab));
    if (b.dataset.tab === "cart") loadCart();
    if (b.dataset.tab === "orders") loadOrders();
    if (b.dataset.tab === "products") loadProducts();
  };
});

async function loadBalance() {
  const me = await api("/auth/me");
  $("balance").textContent = money(me.balance);
}

async function loadProducts() {
  const list = await api("/products");
  $("productList").innerHTML = list.map((p) => `
    <div class="product">
      <h4>${esc(p.name)}</h4>
      <div>${esc(p.description)}</div>
      <div class="price">${money(p.price)}</div>
      <div>Omborda: ${p.stock}</div>
      <div style="margin-top:10px">
        <input type="number" min="1" value="1" id="qty${p.id}">
        <button onclick="addToCart(${p.id})" ${p.stock === 0 ? "disabled" : ""}>Savatga</button>
      </div>
    </div>`).join("") || "<p>Mahsulotlar yo'q</p>";
}

async function addToCart(id) {
  const qty = parseInt($("qty" + id).value) || 1;
  try {
    await api("/cart", "POST", { product_id: id, quantity: qty });
    alert("Savatga qo'shildi");
  } catch (e) { alert(e.message); }
}

async function loadCart() {
  const c = await api("/cart");
  $("cartBody").innerHTML = c.items.map((i) => `
    <tr>
      <td>${esc(i.name)}</td><td>${money(i.price)}</td><td>${i.quantity}</td>
      <td>${money(i.subtotal)}</td>
      <td><button class="danger" onclick="removeItem(${i.product_id})">O'chirish</button></td>
    </tr>`).join("") || "<tr><td colspan='5'>Savat bo'sh</td></tr>";
  $("cartTotal").textContent = money(c.total);
}

async function removeItem(id) {
  await api("/cart/" + id, "DELETE");
  loadCart();
}

$("payBtn").onclick = async () => {
  try {
    const r = await api("/cart/checkout", "POST");
    flash($("cartMsg"), `To'lov muvaffaqiyatli! Buyurtma #${r.order_id}`, true);
    loadCart(); loadBalance();
  } catch (e) { flash($("cartMsg"), e.message); }
};

$("topupBtn").onclick = async () => {
  try {
    const r = await api("/balance/topup", "POST", { amount: parseFloat($("amount").value) });
    flash($("balMsg"), "Balans to'ldirildi", true);
    $("amount").value = "";
    $("balance").textContent = money(r.balance);
  } catch (e) { flash($("balMsg"), e.message); }
};

async function loadOrders() {
  const list = await api("/orders/my");
  $("ordersBody").innerHTML = list.map((o) => `
    <tr>
      <td>${o.id}</td>
      <td>${new Date(o.created_at).toLocaleString()}</td>
      <td>${o.items.map((i) => `${esc(i.product_name)} × ${i.quantity}`).join("<br>")}</td>
      <td>${money(o.total)}</td>
    </tr>`).join("") || "<tr><td colspan='4'>Xaridlar yo'q</td></tr>";
}

loadBalance();
loadProducts();