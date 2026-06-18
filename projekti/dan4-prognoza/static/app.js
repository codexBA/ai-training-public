/**
 * Dan 4 — Function calling frontend
 */
async function ucitajGradove() {
  var r = await fetch('/api/cities');
  var data = await r.json();
  var sel = document.getElementById('city-select');
  sel.innerHTML = '';
  data.gradovi.forEach(function (g) {
    var o = document.createElement('option');
    o.value = g;
    o.textContent = g;
    sel.appendChild(o);
  });
}

async function pitajAI() {
  var pitanje = document.getElementById('ask-input').value.trim();
  if (!pitanje) return;

  document.getElementById('answer').textContent = 'AI razmišlja i možda poziva alate...';
  document.getElementById('tool-trace').textContent = '[]';

  var response = await fetch('/api/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pitanje: pitanje, tool_choice: 'auto' })
  });

  if (!response.ok) {
    var err = await response.json();
    document.getElementById('answer').textContent = 'Greška: ' + (err.detail || response.status);
    return;
  }

  var data = await response.json();
  document.getElementById('answer').textContent = data.odgovor;
  document.getElementById('tool-trace').textContent = JSON.stringify(data.tool_trace, null, 2);
  document.getElementById('ask-meta').textContent =
    'Model: ' + data.model + ' | Iteracije: ' + data.iteracije +
    ' | Alati: ' + data.tool_trace.length + ' | ' + data.trajanje_ms + ' ms';
}

async function direktnaPrognoza() {
  var city = document.getElementById('city-select').value;
  var days = document.getElementById('days-input').value || 3;
  var response = await fetch('/api/weather/' + encodeURIComponent(city) + '?days=' + days);
  var data = await response.json();
  document.getElementById('direct-output').textContent = JSON.stringify(data, null, 2);
}

document.getElementById('btn-ask').addEventListener('click', pitajAI);
document.getElementById('btn-direct').addEventListener('click', direktnaPrognoza);

ucitajGradove();
