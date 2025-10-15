CLEANUP_ERROR = 'Cleanup error for {client_id}: {error}'
ERROR_CLOSING = 'Error closing connection for{client_id}: {error}'
ERROR_SENDING = 'Error sending to {client_id}: {error}'
NON_EXIST_CLIENT = 'Attempted to get non-existent client: {client_id}'
WEBSOCKET_CONNECTION = (
    'New WebSocket connection: {client_id}. Total: {len_connections}'
)
WEBSOCKET_DISCONNECTION = (
    'Disconnected: {client_id}. Total: {len_connections}'
)
