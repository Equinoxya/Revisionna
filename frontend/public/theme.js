// Choix du thème avant le premier affichage, pour éviter un éclair de la mauvaise couleur.
// Clé `revisionna.theme` : "light", "dark", ou absente (= suivre le système).
(function () {
  var choice = null;
  try {
    choice = localStorage.getItem("revisionna.theme");
  } catch (error) {
    /* stockage indisponible : on suit le système */
  }
  var dark =
    choice === "dark" ||
    (choice !== "light" && window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches);
  document.documentElement.setAttribute("data-theme", dark ? "dark" : "light");
})();
