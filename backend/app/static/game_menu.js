const state = {
  templates: [],
  runs: [],
  currentRunId: null,
  participantId: null,
  socket: null,
  snapshot: null,
};

const config = window.WOS_GAME_CONFIG || {};
const apiBase = (config.apiBase || '/api/v1/game').replace(/\/$/, '');

const el = {
  displayName: document.getElementById('gameDisplayName'),
  characterName: document.getElementById('gameCharacterName'),
  preferredRole: document.getElementById('gamePreferredRole'),
  templateSelect: document.getElementById('templateSelect'),
  activeRunSelect: document.getElementById('activeRunSelect'),
  createRunButton: document.getElementById('createRunButton'),
  joinRunButton: document.getElementById('joinRunButton'),
  connectionStatus: document.getElementById('connectionStatus'),
  currentRunLabel: document.getElementById('currentRunLabel'),
  roomTitle: document.getElementById('roomTitle'),
  roomDescription: document.getElementById('roomDescription'),
  beatBadge: document.getElementById('beatBadge'),
  tensionBadge: document.getElementById('tensionBadge'),
  exitList: document.getElementById('exitList'),
  actionList: document.getElementById('actionList'),
  propList: document.getElementById('propList'),
  occupantList: document.getElementById('occupantList'),
  transcript: document.getElementById('transcript'),
  sayText: document.getElementById('sayText'),
  emoteText: document.getElementById('emoteText'),
  inspectTarget: document.getElementById('inspectTarget'),
  sayButton: document.getElementById('sayButton'),
  emoteButton: document.getElementById('emoteButton'),
  inspectButton: document.getElementById('inspectButton'),
};

async function getJson(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    credentials: 'same-origin',
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || data.detail || `Request failed: ${response.status}`);
  }
  return data;
}

function getDisplayName() {
  return (el.characterName.value.trim() || el.displayName.value.trim() || 'Player');
}

function getCharacterPayload() {
  const characterName = el.characterName.value.trim();
  return {
    display_name: el.displayName.value.trim() || 'Player',
    character_name: characterName || null,
    preferred_role_id: el.preferredRole.value.trim() || null,
  };
}

function setStatus(text) {
  el.connectionStatus.textContent = text;
}

function renderSelectOptions() {
  el.templateSelect.innerHTML = state.templates
    .map(template => `<option value="${template.id}">${template.title} — ${template.kind}</option>`)
    .join('');

  el.activeRunSelect.innerHTML = state.runs
    .map(run => `<option value="${run.id}">${run.template_title} | ${run.id} | beat=${run.beat_id} | humans=${run.total_humans}</option>`)
    .join('');
}

function currentRoom() {
  if (!state.snapshot) return null;
  return state.snapshot.rooms.find(room => room.id === state.snapshot.viewer_room_id) || null;
}

function renderTokenButtonList(container, items, emptyText) {
  container.innerHTML = items.length ? items.join('') : `<div class="muted">${emptyText}</div>`;
}

function renderSnapshot(snapshot) {
  state.snapshot = snapshot;
  const room = currentRoom();
  el.currentRunLabel.textContent = `Run: ${snapshot.run_id} | Template: ${snapshot.template_title} | Role: ${snapshot.viewer_role_id}`;
  el.beatBadge.textContent = `Beat: ${snapshot.beat_id}`;
  el.tensionBadge.textContent = `Tension: ${snapshot.tension}`;

  if (room) {
    el.roomTitle.textContent = room.name;
    el.roomDescription.textContent = room.description;

    renderTokenButtonList(
      el.exitList,
      room.exits.map(exit => `
        <div style="display:flex; justify-content:space-between; align-items:center; gap:0.75rem; margin-bottom:0.5rem;">
          <span>${exit.label}</span>
          <button data-room="${exit.target_room_id}" class="move-button btn">Go</button>
        </div>`),
      'No exits from here.'
    );

    const visibleProps = room.props || [];
    renderTokenButtonList(
      el.propList,
      visibleProps.map(prop => `
        <div style="display:flex; justify-content:space-between; align-items:center; gap:0.75rem; margin-bottom:0.5rem;">
          <span>${prop.name} <small>(${prop.state})</small></span>
          <button data-inspect="${prop.id}" class="inspect-button btn">Inspect</button>
        </div>`),
      'No props in this room.'
    );

    const occupants = snapshot.room_occupants[room.id] || [];
    renderTokenButtonList(
      el.occupantList,
      occupants.map(occupant => `
        <div style="display:flex; justify-content:space-between; align-items:center; gap:0.75rem; margin-bottom:0.5rem;">
          <span>${occupant.display_name}</span>
          <small>${occupant.mode}</small>
        </div>`),
      'Nobody else is here.'
    );
  }

  renderTokenButtonList(
    el.actionList,
    snapshot.available_actions.map(action => `
      <div style="display:flex; justify-content:space-between; align-items:center; gap:0.75rem; margin-bottom:0.5rem;">
        <span>${action.label}</span>
        <button data-action="${action.id}" class="action-button btn">Use</button>
      </div>`),
    'No scripted actions available here.'
  );

  el.transcript.innerHTML = snapshot.transcript_tail.map(entry => `
    <div>
      <div style="font-size:0.8rem; opacity:0.75;">${new Date(entry.at).toLocaleTimeString()}${entry.actor ? ` • ${entry.actor}` : ''}</div>
      <div>${entry.text}</div>
    </div>
  `).join('');
  el.transcript.scrollTop = el.transcript.scrollHeight;

  wireDynamicButtons();
}

function wireDynamicButtons() {
  document.querySelectorAll('.move-button').forEach(button => {
    button.onclick = () => sendCommand({ action: 'move', target_room_id: button.dataset.room });
  });
  document.querySelectorAll('.action-button').forEach(button => {
    button.onclick = () => sendCommand({ action: 'use_action', action_id: button.dataset.action });
  });
  document.querySelectorAll('.inspect-button').forEach(button => {
    button.onclick = () => sendCommand({ action: 'inspect', target_id: button.dataset.inspect });
  });
}

function connectSocket(ticketResponse) {
  if (state.socket) {
    state.socket.close();
  }
  const wsBaseUrl = (ticketResponse.ws_base_url || '').replace(/\/$/, '');
  if (!wsBaseUrl) {
    throw new Error('Missing ws_base_url from backend ticket response.');
  }
  state.socket = new WebSocket(`${wsBaseUrl}/ws?ticket=${encodeURIComponent(ticketResponse.ticket)}`);
  setStatus('Connecting...');

  state.socket.onopen = () => setStatus('Connected');
  state.socket.onclose = () => setStatus('Disconnected');
  state.socket.onerror = () => setStatus('Socket error');
  state.socket.onmessage = event => {
    const payload = JSON.parse(event.data);
    if (payload.type === 'snapshot') {
      renderSnapshot(payload.data);
    }
    if (payload.type === 'command_rejected') {
      alert(payload.reason);
    }
  };
}

async function createRun() {
  const result = await getJson(`${apiBase}/runs`, {
    method: 'POST',
    body: JSON.stringify({
      template_id: el.templateSelect.value,
      ...getCharacterPayload(),
    }),
  });
  state.currentRunId = result.run.id;
  await refreshRuns();
  await joinRun(result.run.id);
}

async function joinRun(runId = el.activeRunSelect.value) {
  const result = await getJson(`${apiBase}/tickets`, {
    method: 'POST',
    body: JSON.stringify({
      run_id: runId,
      ...getCharacterPayload(),
    }),
  });
  state.currentRunId = result.run_id;
  state.participantId = result.participant_id;
  connectSocket(result);
}

function sendCommand(payload) {
  if (!state.socket || state.socket.readyState !== WebSocket.OPEN) {
    alert('Not connected yet.');
    return;
  }
  state.socket.send(JSON.stringify(payload));
}

async function refreshTemplates() {
  const payload = await getJson(`${apiBase}/templates`);
  state.templates = payload.templates || [];
  renderSelectOptions();
}

async function refreshRuns() {
  const payload = await getJson(`${apiBase}/runs`);
  state.runs = payload.runs || [];
  renderSelectOptions();
}

el.createRunButton.onclick = () => createRun().catch(err => alert(err.message));
el.joinRunButton.onclick = () => joinRun().catch(err => alert(err.message));
el.sayButton.onclick = () => {
  const text = el.sayText.value.trim();
  if (text) {
    sendCommand({ action: 'say', text });
    el.sayText.value = '';
  }
};
el.emoteButton.onclick = () => {
  const text = el.emoteText.value.trim();
  if (text) {
    sendCommand({ action: 'emote', text });
    el.emoteText.value = '';
  }
};
el.inspectButton.onclick = () => {
  const text = el.inspectTarget.value.trim();
  if (text) {
    sendCommand({ action: 'inspect', target_id: text });
    el.inspectTarget.value = '';
  }
};

(async function bootstrap() {
  if (!config.playServiceConfigured) {
    setStatus('Play service not configured');
    return;
  }
  try {
    await refreshTemplates();
    await refreshRuns();
    setInterval(refreshRuns, 5000);
  } catch (err) {
    console.error(err);
    alert(err.message);
  }
})();
