/**
 * app.js — Dan 1: Token Vizualizator i Temperature Playground
 *
 * NAPOMENA: Tokenizacija u ovom fajlu je APROKSIMACIJA za browser demo.
 * Precizna tokenizacija radi se u Python notebooku s tiktoken bibliotekom.
 */

// ============================================================
// KORAK 1: Aproksimacija tokenizacije za browser
// ============================================================

/**
 * Aproksimacija tokenizacije za browser demo.
 * NAPOMENA: Ovo je vizualna demonstracija, ne precizna tokenizacija.
 * Precizna tokenizacija radi se u Python notebooku s tiktoken bibliotekom.
 *
 * Pravila aproksimacije:
 * - Engleski tekst: ~1 token na 4 znaka
 * - Bosanski/slavenski tekst: ~1 token na 2.5 znaka
 * - Interpunkcija: uglavnom 1 token svaki znak
 * - Brojevi: 1 token po cifri ili grupi cifara
 */
function aproksimirajTokene(tekst) {
  // Regex koji dijeli tekst na "token-like" dijelove:
  // \d+ = grupa cifara (npr. "2024" = 1 token)
  // [^\w\s] = interpunkcija (svaki znak = 1 token)
  // \s+ = razmaci (obično spojeni u 1 token)
  // [a-zA-Z]+ = engleske riječi
  // [^\x00-\x7F]+ = ne-ASCII znakovi (bosanski č, ć, š, ž, đ itd.)
  var dijelovi = tekst.match(
    /\d+|[^\w\s]|\s+|[a-zA-Z]+|[^\x00-\x7F]+/g
  ) || [];
  return dijelovi;
}

// ============================================================
// KORAK 2: Token vizualizacija
// ============================================================

/**
 * Analizira uneseni tekst, prikazuje tokene u boji i statistiku.
 */
function tokenize() {
  var inputElement = document.getElementById('token-input');
  var tekst = inputElement.value.trim();

  if (!tekst) {
    return;
  }

  // Dobijamo aproksimativne tokene
  var tokeni = aproksimirajTokene(tekst);

  // Prikazujemo tokene s naizmjeničnim bojama
  var display = document.getElementById('token-display');
  var html = '';
  for (var i = 0; i < tokeni.length; i++) {
    var colorClass = 'token-color-' + (i % 6);
    // Zamjenjujemo razmake s vidljivim znakom za prikaz
    var prikazaniTekst = tokeni[i].replace(/ /g, '·').replace(/\n/g, '↵');
    html += '<span class="token ' + colorClass + '" title="Token ' + (i + 1) + '">' +
            escapeHtml(prikazaniTekst) + '</span>';
  }
  display.innerHTML = html;

  // Računamo statistiku
  var brojTokena = tokeni.length;
  var brojZnakova = tekst.length;
  var ratio = brojZnakova > 0 ? (brojZnakova / brojTokena).toFixed(1) : '0';

  // Cijena za DeepSeek: $0.14 per 1M input tokena
  var cijena = (brojTokena / 1000000 * 0.14).toFixed(6);

  // Prikazujemo statistiku
  document.getElementById('stat-token-count').textContent = brojTokena;
  document.getElementById('stat-char-count').textContent = brojZnakova;
  document.getElementById('stat-ratio').textContent = ratio;
  document.getElementById('stat-cost').textContent = '$' + cijena;
  document.getElementById('token-stats').style.display = 'grid';
}

// ============================================================
// KORAK 3: Temperature demo — API pozivi
// ============================================================

/**
 * Šalje prompt na backend API koji ga prosljeđuje LLM-u na tri temperature.
 * Prikazuje rezultate u tri kartice za usporedbu.
 */
async function temperatureDemo() {
  var promptElement = document.getElementById('temp-prompt');
  var prompt = promptElement.value.trim();

  if (!prompt) {
    return;
  }

  var sliderValue = parseFloat(document.getElementById('temp-slider').value);

  // Prikazujemo loading, sakrivamo prethodne rezultate i greške
  document.getElementById('temp-loading').classList.add('active');
  document.getElementById('temp-error').classList.remove('active');
  document.getElementById('temperature-results').innerHTML = '';
  document.getElementById('btn-temperature').disabled = true;

  try {
    var response = await fetch('/api/temperature-demo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt: prompt,
        temperature_custom: sliderValue
      })
    });

    if (!response.ok) {
      var errorData = await response.json().catch(function () { return {}; });
      throw new Error(errorData.detail || 'Greška pri komunikaciji s API-jem (HTTP ' + response.status + ')');
    }

    var rezultati = await response.json();
    prikaziTemperatureRezultate(rezultati);

  } catch (error) {
    var errorEl = document.getElementById('temp-error');
    errorEl.textContent = 'Greška: ' + error.message +
      '\n\nProvjerite da je server pokrenut (uvicorn main:app --reload --port 8001) ' +
      'i da imate konfigurisan DeepSeek API key ili pokrenut Ollama.';
    errorEl.classList.add('active');
  } finally {
    document.getElementById('temp-loading').classList.remove('active');
    document.getElementById('btn-temperature').disabled = false;
  }
}

/**
 * Prikazuje rezultate temperature eksperimenta u karticama.
 */
function prikaziTemperatureRezultate(rezultati) {
  var container = document.getElementById('temperature-results');
  var labele = ['Deterministički', 'Balansirano', 'Kreativno'];

  var html = '';
  for (var i = 0; i < rezultati.length; i++) {
    var r = rezultati[i];
    html += '<div class="temp-card">' +
      '<div class="temp-card-header">' +
        '<span class="temp-label">' + labele[i] + '</span>' +
        '<span class="temp-value">t=' + r.temperatura.toFixed(1) + '</span>' +
      '</div>' +
      '<div class="temp-card-body">' + escapeHtml(r.tekst) + '</div>' +
      '<div class="temp-card-meta">' +
        '<span>Input: ' + r.tokeni_input + ' tok</span>' +
        '<span>Output: ' + r.tokeni_output + ' tok</span>' +
        '<span>' + r.trajanje_ms + ' ms</span>' +
      '</div>' +
    '</div>';
  }
  container.innerHTML = html;
}

// ============================================================
// KORAK 4: Učitavanje informacija o modelima
// ============================================================

/**
 * Dohvata informacije o modelima s API-ja i prikazuje ih u tabeli.
 */
async function ucitajModelInfo() {
  try {
    var response = await fetch('/api/model-info');
    var data = await response.json();

    var container = document.getElementById('model-info-container');
    var html = '<table class="model-table">' +
      '<thead><tr>' +
        '<th>Model</th><th>Tip</th><th>Kontekst</th>' +
        '<th>Input $/1M</th><th>Output $/1M</th><th>Napomena</th>' +
      '</tr></thead><tbody>';

    for (var i = 0; i < data.modeli.length; i++) {
      var m = data.modeli[i];
      var badgeClass = m.tip === 'cloud' ? 'badge-cloud' : 'badge-local';
      html += '<tr>' +
        '<td><strong>' + escapeHtml(m.naziv) + '</strong></td>' +
        '<td><span class="badge ' + badgeClass + '">' + escapeHtml(m.tip) + '</span></td>' +
        '<td>' + (m.kontekst_tokena / 1000) + 'K</td>' +
        '<td>$' + m.cijena_input_per_1m.toFixed(2) + '</td>' +
        '<td>$' + m.cijena_output_per_1m.toFixed(2) + '</td>' +
        '<td>' + escapeHtml(m.napomena) + '</td>' +
      '</tr>';
    }

    html += '</tbody></table>';
    container.innerHTML = html;

  } catch (error) {
    document.getElementById('model-info-container').innerHTML =
      '<p style="color: var(--color-error);">Nije moguće učitati informacije o modelima. ' +
      'Provjerite da je server pokrenut.</p>';
  }
}

// ============================================================
// KORAK 5: Pomoćne funkcije
// ============================================================

/**
 * Sprječava XSS — escapira HTML specijalne znakove.
 */
function escapeHtml(text) {
  var div = document.createElement('div');
  div.appendChild(document.createTextNode(text));
  return div.innerHTML;
}

// ============================================================
// KORAK 6: Inicijalizacija — temperature slider i učitavanje podataka
// ============================================================

// Ažuriramo prikaz vrijednosti slidera u realnom vremenu
document.getElementById('temp-slider').addEventListener('input', function () {
  document.getElementById('temp-slider-value').textContent = this.value;
});

// Učitavamo informacije o modelima kad se stranica otvori
document.addEventListener('DOMContentLoaded', function () {
  ucitajModelInfo();
});
