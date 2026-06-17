/**
 * Dan 2 — Film Chat frontend
 * Historija razgovora se drži u memoriji browsera i šalje cijela na svaki API poziv.
 */
var historija = [];

function renderChat() {
    var box = document.getElementById('chat-messages');
    var html = '';
    for (var i = 0; i < historija.length; i++) {
        var m = historija[i];
        html += '<div class="msg ' + m.role + '">' +
            '<div class="msg-role">' + m.role + '</div>' +
            '<div>' + escapeHtml(m.content) + '</div></div>';
    }
    box.innerHTML = html;
    box.scrollTop = box.scrollHeight;
}

async function posaljiPoruku() {
    var input = document.getElementById('chat-input');
    var tekst = input.value.trim();
    if (!tekst) return;

    var btnSend = document.getElementById('btn-send');
    btnSend.disabled = true;
    btnSend.textContent = 'Šaljem...';

    historija.push({ role: 'user', content: tekst });
    input.value = '';
    renderChat();

    var box = document.getElementById('chat-messages');
    box.innerHTML += '<div class="msg assistant loader" id="chat-loader"><div class="msg-role">assistant</div><div class="typing-indicator"><span></span><span></span><span></span></div></div>';
    box.scrollTop = box.scrollHeight;

    var systemPrompt = document.getElementById('system-prompt').value.trim();

    try {
        var response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                poruke: historija,
                system_prompt: systemPrompt || null,
                temperature: 0.7
            })
        });
        if (!response.ok) throw new Error('HTTP ' + response.status);
        var data = await response.json();
        historija = data.poruke;
        renderChat();
        document.getElementById('chat-meta').textContent =
            'Tokeni: in=' + data.tokeni_input + ' out=' + data.tokeni_output +
            ' | ' + data.trajanje_ms + ' ms | Poruka u historiji: ' + historija.length;
    } catch (e) {
        alert('Greška: ' + e.message);
        var loader = document.getElementById('chat-loader');
        if (loader) loader.remove();
    } finally {
        btnSend.disabled = false;
        btnSend.textContent = 'Pošalji';
    }
}

async function jsonPreporuka() {
    var btnJson = document.getElementById('btn-json');
    btnJson.disabled = true;
    btnJson.textContent = 'Dohvatam...';

    var zanr = document.getElementById('json-zanr').value.trim() || null;
    var raspolozenje = document.getElementById('json-raspolozenje').value.trim();
    try {
        var response = await fetch('/api/preporuci', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ zanr: zanr, raspolozenje: raspolozenje })
        });
        var data = await response.json();
        document.getElementById('json-output').textContent = JSON.stringify(data, null, 2);
    } catch (e) {
        alert('Greška: ' + e.message);
    } finally {
        btnJson.disabled = false;
        btnJson.textContent = 'Dohvati JSON preporuku';
    }
}

function escapeHtml(t) {
    var d = document.createElement('div');
    d.textContent = t;
    return d.innerHTML;
}

document.getElementById('btn-send').addEventListener('click', posaljiPoruku);
document.getElementById('chat-input').addEventListener('keydown', function (e) {
    if (e.key === 'Enter') posaljiPoruku();
});
document.getElementById('btn-clear').addEventListener('click', function () {
    historija = [];
    renderChat();
    document.getElementById('chat-meta').textContent = '';
});
document.getElementById('btn-json').addEventListener('click', jsonPreporuka);
