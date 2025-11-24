const API = "http://localhost:5000";


function mostrarMensaje(texto, tipo = "error") {
    const div = document.getElementById("mensaje");
    if (!div) return;

    div.innerText = texto;
    div.className = "mensaje " + (tipo === "exito" ? "exito" : "");
    div.style.display = "block";
    setTimeout(() => {
        div.style.display = "none";
    }, 4000);
}

function mostrarSeccion(id) {
    document.querySelectorAll(".seccion").forEach(s => s.style.display = "none");
    const seccion = document.getElementById(id);
    if (!seccion) return;
    seccion.style.display = "block";

    if (id === "reservas") {
        cargarSalasParaReservar();
        cargarTurnos();
        cargarReservas();
    }

    if (id === "salas") {
        cargarEdificios();
        cargarSalas();
    }

    if (id === "participantes") {
        cargarParticipantes();
    }
}


async function cargarParticipantes() {
    try {
        const res = await fetch(`${API}/participantes`);
        const datos = await res.json();

        const lista = document.getElementById("lista_participantes");
        if (!lista) return;
        lista.innerHTML = "";

        datos.forEach(p => {
            lista.innerHTML += `<li>${p.ci} - ${p.nombre} ${p.apellido}</li>`;
        });

        mostrarMensaje("Participantes cargados correctamente", "exito");

    } catch (err) {
        console.error(err);
        mostrarMensaje("Error cargando participantes");
    }
}

async function crearParticipante(e) {
    e.preventDefault();

    const data = {
        ci: document.getElementById("p_ci").value,
        nombre: document.getElementById("p_nombre").value,
        apellido: document.getElementById("p_apellido").value,
        email: document.getElementById("p_email").value,
        id_login: document.getElementById("p_login").value
    };

    const res = await fetch(`${API}/participante`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    const resp = await res.json();

    if (!res.ok) {
        mostrarMensaje(resp.error || "Error al crear participante");
        return;
    }

    mostrarMensaje("Participante creado con éxito", "exito");
    cargarParticipantes();
}


async function cargarSalas() {
    try {
        const res = await fetch(`${API}/salas`);
        const datos = await res.json();

        const lista = document.getElementById("lista_salas");
        if (!lista) return;

        lista.innerHTML = "";

        datos.forEach(s => {
            lista.innerHTML += `
                <li>
                    ${s.id_sala} - ${s.nombre_sala}
                    (${s.tipo_sala}) - ${s.nombre_edificio}
                    [cap: ${s.capacidad}]
                </li>`;
        });

        mostrarMensaje("Salas cargadas correctamente", "exito");

    } catch (err) {
        console.error(err);
        mostrarMensaje("Error cargando salas");
    }
}

async function crearSala(e) {
    e.preventDefault();

    const data = {
        nombre_sala: document.getElementById("s_nombre").value,
        id_edificio: document.getElementById("s_edificio").value,
        capacidad: document.getElementById("s_capacidad").value,
        tipo_sala: document.getElementById("s_tipo").value
    };

    const res = await fetch(`${API}/salas`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    const resp = await res.json();

    if (!res.ok) {
        mostrarMensaje(resp.error || "Error al crear sala");
        return;
    }

    mostrarMensaje("Sala creada con éxito", "exito");
    cargarSalas();
}

async function cargarEdificios() {
    try {
        const res = await fetch(`${API}/edificios`);
        const edificios = await res.json();

        const select = document.getElementById("s_edificio");
        if (!select) return;

        select.innerHTML = "";

        edificios.forEach(e => {
            select.innerHTML += `
                <option value="${e.id_edificio}">
                    ${e.nombre_edificio}
                </option>
            `;
        });
    } catch (err) {
        console.error(err);
        mostrarMensaje("Error cargando edificios");
    }
}

async function verParticipantes(id_reserva) {
    const res = await fetch(`${API}/reserva/${id_reserva}/participantes`);
    const datos = await res.json();

    if (!res.ok) {
        mostrarMensaje(datos.error || "Error al obtener participantes");
        return;
    }

    let texto = `Participantes de la reserva ${id_reserva}:\n\n`;

    if (datos.length === 0) {
        texto += "No hay participantes en esta reserva.";
    } else {
        datos.forEach(p => {
            texto += `${p.ci_participante} - ${p.nombre} ${p.apellido}\n`;
        });
    }

    alert(texto);
}

async function cargarReservas() {
    try {
        const res = await fetch(`${API}/reservas`);
        const datos = await res.json();

        const lista = document.getElementById("lista_reservas");
        if (!lista) return;

        lista.innerHTML = "";

        datos.forEach(r => {
            lista.innerHTML += `
                <li>
                    <strong>ID:</strong> ${r.id_reserva} |
                    Sala: ${r.id_sala} |
                    Turno: ${r.id_turno} |
                    Fecha: ${r.fecha} |
                    Estado: ${r.estado}
                    <br>
                    <button class="btn-secundario" onclick="cancelarReserva(${r.id_reserva})">Cancelar</button>
                    <button class="btn-secundario" onclick="finalizarReserva(${r.id_reserva})">Finalizar</button>
                    <button class="btn" onclick="verParticipantes(${r.id_reserva})">Ver Participantes</button>
                </li>
            `;
        });

        mostrarMensaje("Reservas cargadas correctamente", "exito");

    } catch (err) {
        console.error(err);
        mostrarMensaje("Error cargando reservas");
    }
}

async function crearReserva(e) {
    e.preventDefault();

    const data = {
        id_sala: document.getElementById("r_sala").value,
        fecha: document.getElementById("r_fecha").value,
        id_turno: document.getElementById("r_turno").value,
        ci_participante: document.getElementById("r_ci").value
    };

    const res = await fetch(`${API}/reservas`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    const resp = await res.json();

    if (!res.ok) {
        mostrarMensaje(resp.error || "Error al crear la reserva");
        return;
    }

    mostrarMensaje("Reserva creada con éxito", "exito");
    cargarReservas();
}

async function cargarSalasParaReservar() {
    try {
        const res = await fetch(`${API}/salas`);
        const salas = await res.json();

        const select = document.getElementById("r_sala");
        if (!select) return;

        select.innerHTML = "";

        salas.forEach(s => {
            select.innerHTML += `
                <option value="${s.id_sala}">
                    ${s.nombre_sala} - ${s.nombre_edificio} (cap: ${s.capacidad}, ${s.tipo_sala})
                </option>
            `;
        });
    } catch (err) {
        console.error(err);
        mostrarMensaje("Error cargando salas para reservar");
    }
}

async function cargarTurnos() {
    try {
        const res = await fetch(`${API}/turnos`);
        const turnos = await res.json();

        const select = document.getElementById("r_turno");
        if (!select) return;

        select.innerHTML = "";

        turnos.forEach(t => {
            select.innerHTML += `
                <option value="${t.id_turno}">
                    ${t.hora_inicio} - ${t.hora_fin}
                </option>
            `;
        });
    } catch (err) {
        console.error(err);
        mostrarMensaje("Error cargando turnos");
    }
}

async function agregarParticipanteReserva(e) {
    e.preventDefault();

    const idReserva = document.getElementById("ap_id_reserva").value;
    const ci = document.getElementById("ap_ci").value;

    const res = await fetch(`${API}/reserva/${idReserva}/participantes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ci_participante: ci })
    });

    const resp = await res.json();

    if (!res.ok) {
        mostrarMensaje(resp.error || "Error al agregar participante a la reserva");
        return;
    }

    mostrarMensaje("Participante agregado con éxito", "exito");
    cargarReservas();
}

async function cancelarReserva(id) {
    const res = await fetch(`${API}/reserva/${id}/cancelar`, {
        method: "PUT"
    });

    const resp = await res.json();

    if (!res.ok) {
        mostrarMensaje(resp.error || "Error al cancelar reserva");
        return;
    }

    mostrarMensaje("Reserva cancelada", "exito");
    cargarReservas();
}

async function finalizarReserva(id) {
    const res = await fetch(`${API}/reserva/${id}/finalizar`, {
        method: "PUT"
    });

    const resp = await res.json();

    if (!res.ok) {
        mostrarMensaje(resp.error || "Error al finalizar reserva");
        return;
    }

    mostrarMensaje("Reserva finalizada", "exito");
    cargarReservas();
}

console.log("Admin JS cargado");
mostrarSeccion('participantes');
