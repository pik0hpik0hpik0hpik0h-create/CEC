const checkbox = document.getElementById("cambio_tema");

// Tema inicial
const tema_guardado = localStorage.getItem("theme") || "cec-claro";
document.documentElement.setAttribute("data-theme", tema_guardado);

// Si está en claro → mostrar sol (checked)
checkbox.checked = tema_guardado === "cec-claro";

checkbox.addEventListener("change", () => {
    const next = checkbox.checked ? "cec-claro" : "cec-oscuro";
    localStorage.setItem("theme", next);
    document.documentElement.setAttribute("data-theme", next);
});
