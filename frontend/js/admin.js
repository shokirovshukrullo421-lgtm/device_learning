Auth.require("admin");
document.getElementById("uname").textContent = Auth.username;
const $ = (id) => document.getElementById(id);

document.querySelectorAll(".tabs button").forEach((b) => {
  b.onclick = () => {
    document.querySelectorAll(".tabs button").forEach((x) => x.classList.remove("active"));
    b.classList.add("active");
    ["products", "users", "orders"].forEach((id) =>
      $(id).classList.toggle("hidden", id !== b.dataset.tab));
    if (b.dataset.tab === "products") loadProducts();
    if (b.dataset.tab === "users") loadUsers();
    if (b.dataset.tab === "orders") loadOrders();
  };
});

async function loadProducts() {
  const list = await api("/products");
  $("productBody").innerHTML = list.map((p) => `
    <tr>
      <td>${p.id}</td><td>${esc(p.name)}</td><td>${money(p.price)}</td><td>${p.stock}</td>
      <td><button class="danger" onclick="delProduct(${p.id})">O'chirish</button></td>
    </tr>`).join("") || "<tr><td colspan='5'>Mahsulot yo'q</td></tr>";
}

$("addProduct").onclick = async () => {
  const msg = $("pMsg");
  try {
    await api("/products", "POST", {
      name: $("pName").value.trim(),
      description: $("pDesc").value.trim(),
      price: parseFloat($("pPrice").value),
      stock: parseInt($("pStock").value),
    });
    msg.className = "msg ok"; msg.textContent = "Mahsulot qo'shildi";
    ["pName", "pDesc", "pPrice", "pStock"].forEach((id) => ($(id).value = ""));
    loadProducts();
  } catch (e) { msg.className = "msg err"; msg.textContent = e.message; }
};

async function delProduct(id) {
  if (!confirm("O'chirilsinmi?")) return;
  await api("/products/" + id, "DELETE");
  loadProducts();
}

async function loadUsers() {
  const list = await api("/admin/users");
  $("userBody").innerHTML = list.map((u) => `
    <tr>
      <td>${u.id}</td><td>${esc(u.username)}</td><td>${u.role}</td>
      <td>${money(u.balance)}</td><td>${new Date(u.created_at).toLocaleString()}</td>
    </tr>`).join("");
}

async function loadOrders() {
  const list = await api("/admin/orders");
  $("orderBody").innerHTML = list.map((o) => `
    <tr>
      <td>${o.id}</td><td>${esc(o.username)}</td>
      <td>${new Date(o.created_at).toLocaleString()}</td>
      <td>${o.items.map((i) => `${esc(i.product_name)} × ${i.quantity}`).join("<br>")}</td>
      <td>${money(o.total)}</td>
    </tr>`).join("") || "<tr><td colspan='5'>Xaridlar yo'q</td></tr>";
}

loadProducts();