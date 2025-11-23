const API = "http://localhost:5000";

function mostrarMensaje(texto, tipo = "error") {
    const div = document.getElementById("mensaje");
    div.innerText = texto;
    div.className = "mensaje " + (tipo === "exito" ? "exito" : "");
    div.style.display = "block";
    setTimeout(() => div.style.display = "none", 4000);
}

async function hacerLogin(e) {
    e.preventDefault();

    const usuario = document.getElementById("usuario").value;
    const contrasena = document.getElementById("contrasena").value;

    const res = await fetch(`${API}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ usuario, contrasena })
    });

    const data = await res.json();

    if (!res.ok) {
        mostrarMensaje(data.error || "Error de login");
        return;
    }

    localStorage.setItem("rol", data.rol);
    localStorage.setItem("usuario", data.usuario);
    localStorage.setItem("ci", data.ci);

    mostrarMensaje("Ingreso exitoso", "exito");

    if (data.rol === "admin") {
        window.location.href = "admin.html";
    } else {
        window.location.href = "usuario.html";
    }
}
