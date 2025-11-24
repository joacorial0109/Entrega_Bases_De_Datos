const API = "http://localhost:5000";

function mensaje(t, tipo="error") {
    const div = document.getElementById("mensaje");
    div.innerText = t;
    div.className = "mensaje " + (tipo === "exito" ? "exito" : "");
    div.style.display = "block";
    setTimeout(() => div.style.display = "none", 3000);
}

async function cargarSalasUsuario() {
    const res = await fetch(`${API}/salas`);
    const salas = await res.json();

    const select = document.getElementById("u_sala");
    select.innerHTML = "";

    salas.forEach(s => {
        select.innerHTML += `
            <option value="${s.id_sala}">
                ${s.nombre_sala} - ${s.nombre_edificio}
                (cap: ${s.capacidad}, ${s.tipo_sala})
            </option>
        `;
    });
}

async function cargarTurnosUsuario() {
    const res = await fetch(`${API}/turnos`);
    const turnos = await res.json();

    const select = document.getElementById("u_turno");
    select.innerHTML = "";

    turnos.forEach(t => {
        select.innerHTML += `
            <option value="${t.id_turno}">
                ${t.hora_inicio.slice(0,5)} - ${t.hora_fin.slice(0,5)}
            </option>
        `;
    });
}

async function crearReservaUsuario(e) {
    e.preventDefault();

    const ci_usuario = localStorage.getItem("ci");
    if (!ci_usuario) {
        mensaje("No se encontró sesión", "error");
        return;
    }

    const data = {
        id_sala: document.getElementById("u_sala").value,
        fecha: document.getElementById("u_fecha").value,
        id_turno: document.getElementById("u_turno").value,
        ci_participante: ci_usuario
    };

    const res = await fetch(`${API}/reservas`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    const resp = await res.json();

    if (!res.ok) {
        mensaje(resp.error || "Error al crear reserva");
        return;
    }

    mensaje("Reserva creada con éxito", "exito");
    cargarMisReservas();
}

async function cargarMisReservas() {
    const ci = localStorage.getItem("ci");

    const res = await fetch(`${API}/reservas`);
    const reservas = await res.json();

    const lista = document.getElementById("u_lista_reservas");
    lista.innerHTML = "";

    reservas
        .filter(r => r.ci_participante === ci || true)
        .forEach(r => {
            lista.innerHTML += `
                <li>
                    <strong>${r.fecha}</strong> -
                    Sala ${r.id_sala} |
                    Turno ${r.id_turno} |
                    Estado: ${r.estado}

                    <button class="btn-secundario"
                        onclick="cancelarReservaUsuario(${r.id_reserva})">
                        Cancelar
                    </button>
                </li>
            `;
        });
}

async function cancelarReservaUsuario(id) {
    const res = await fetch(`${API}/reserva/${id}/cancelar`, {
        method: "PUT"
    });

    const data = await res.json();

    if (!res.ok) {
        mensaje(data.error || "Error al cancelar reserva");
        return;
    }

    mensaje("Reserva cancelada", "exito");
    cargarMisReservas();
}

cargarSalasUsuario();
cargarTurnosUsuario();
cargarMisReservas();
