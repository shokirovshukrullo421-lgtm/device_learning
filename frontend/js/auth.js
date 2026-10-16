if (Auth.token) redirect(Auth.role);

function redirect(role) {
  location.href = role === "admin" ? "/admin.html" : "/user.html";
}

async function submit(path) {
  const msg = document.getElementById("msg");
  msg.className = "msg";
  msg.textContent = "";
  try {
    const data = await api(path, "POST", {
      username: document.getElementById("username").value.trim(),
      password: document.getElementById("password").value,
    });
    Auth.save(data);
    redirect(data.role);
  } catch (e) {
    msg.className = "msg err";
    msg.textContent = e.message;
  }
}

document.getElementById("loginBtn").onclick = () => submit("/auth/login");
document.getElementById("registerBtn").onclick = () => submit("/auth/register");
document.getElementById("password").addEventListener("keydown", (e) => {
  if (e.key === "Enter") submit("/auth/login");
});