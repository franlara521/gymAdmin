/* GymAdmin — JavaScript global */

// Auto-scroll hacia abajo en el área de mensajes al cargar
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('[data-autoscroll]').forEach(function (el) {
    el.scrollTop = el.scrollHeight;
  });
});

// HTMX: hacer scroll al final de la lista de mensajes después de cada swap
document.body.addEventListener('htmx:afterSwap', function (e) {
  if (e.detail.target && e.detail.target.id === 'message-list') {
    e.detail.target.scrollTop = e.detail.target.scrollHeight;
  }
});
