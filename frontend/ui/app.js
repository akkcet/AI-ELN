
function toggleSidebar() {
  document.getElementById("sidebar").classList.toggle("collapsed");
}


function toggleSection(header) {
  const group = header.closest(".menu-group");
  group.classList.toggle("collapsed");
}


function togglePanel(header) {
  const card = header.closest(".content-card");
  card.classList.toggle("collapsed");
}


function nav(page) {
  window.location.search = "?page=" + page;
}


function goNewExperiment() {
  window.location.href = "?page=new-experiment-template";
}

function openBlankExperiment() {
  window.open("?page=experiment-editor", "_blank");
}
function toggleexpSection(header) {
  const group = header.closest(".section-group");
  group.classList.toggle("collapsed");
}

function toggleSectionSidebar() {
  document.getElementById("sectionsidebar").classList.toggle("collapsed");
}
