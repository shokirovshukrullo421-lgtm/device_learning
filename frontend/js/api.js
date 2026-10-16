const API = "/api";

const Auth = {
  get token() { return localStorage.getItem("token"); },
  get role() { return localStorage.getItem("role"); },
  get username() { return localStorage.getItem("username"); },
  save(d) {
    localStorage.setItem("token", d.access_token);
    localStorage.setItem("role", d.role);
    localStorage.setItem("username", d.username);
  },
  logout() { localStorage.clear(); location.href = "/index.html"; },
  require(role) {
    if (!this.token || this.role !== role) location.href = "/index.html";
  },
};

async function api(path, method = "GET", body = null) {
  const headers = { "Content-Type": "application/json" };
  if (Auth.token) headers["Authorization"] = "Bearer " + Auth.token;
  const res = await fetch(API + path, {
    method, headers, body: body ? JSON.stringify(body) : null,
  });
  if (res.status === 401 && Auth.token) { Auth.logout(); return; }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const d = data.detail;
    throw new Error(typeof d === "string" ? d : "Xatolik yuz berdi");
  }
  return data;
}

function esc(s) {
  const d = document.createElement("div");
  d.textContent = s ?? "";
  return d.innerHTML;
}

const money = (n) => Number(n).toLocaleString("uz-UZ", { minimumFractionDigits: 2 }) + " so'm";