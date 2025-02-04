let ws = null;

function connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/stream`;
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        document.getElementById('connection-status').textContent = 'Connected';
    };

    ws.onclose = () => {
        document.getElementById('connection-status').textContent = 'Disconnected';
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'transcription' && data.is_final) {
            document.getElementById('live-transcription').textContent = data.transcription;
            document.getElementById('cleaned-transcription').textContent = data.cleaned_transcription;
        }
    };
}

connect();
