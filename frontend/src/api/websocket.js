import { useState, useEffect, useRef, useCallback } from 'react';

export function createWebSocketClient(projectId, onMessage, onNudge, onAgentMessage) {
  const url = `ws://localhost:8000/ws/${projectId}`;
  let ws = null;
  let retries = 0;
  const maxRetries = 5;
  let isClosed = false;

  function connect() {
    ws = new WebSocket(url);

    ws.onopen = () => {
      retries = 0;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        switch (data.type) {
          case 'nudge':
            onNudge?.(data);
            break;
          case 'agent_message':
            onAgentMessage?.(data);
            break;
          default:
            onMessage?.(data);
        }
      } catch (e) {
        console.warn('WS parse error:', e);
      }
    };

    ws.onclose = () => {
      if (!isClosed && retries < maxRetries) {
        retries++;
        setTimeout(connect, 3000);
      }
    };

    ws.onerror = () => {
      ws?.close();
    };
  }

  connect();

  return {
    send: (msg) => {
      if (ws?.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(msg));
      }
    },
    close: () => {
      isClosed = true;
      ws?.close();
    },
    get isConnected() {
      return ws?.readyState === WebSocket.OPEN;
    },
  };
}

export function useWebSocket(projectId) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const clientRef = useRef(null);

  useEffect(() => {
    if (!projectId) return;

    const client = createWebSocketClient(
      projectId,
      (data) => setLastMessage(data),
      (data) => setLastMessage({ ...data, _type: 'nudge' }),
      (data) => setLastMessage({ ...data, _type: 'agent' })
    );
    clientRef.current = client;

    const interval = setInterval(() => {
      setIsConnected(client.isConnected);
    }, 1000);

    return () => {
      clearInterval(interval);
      client.close();
    };
  }, [projectId]);

  const sendMessage = useCallback((text) => {
    clientRef.current?.send({ message: text, memory_enabled: true });
  }, []);

  return { sendMessage, isConnected, lastMessage };
}
