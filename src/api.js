import openSocket from 'socket.io-client';

const socket = openSocket('http://localhost:15555');

function subscribeToGraphUpdates(cb) {
  socket.on('update_graph', (data) => cb(data));
}

function requestGraphUpdate(params) {
  socket.emit('get_graph_update', params);
}

function unsubscribeToUpdates() {
  socket.off('update_graph');
}

function subscribeToFunctionUpdates(cb) {
  socket.on('update_function', (data) => cb(data));
}

function requestFunctionUpdate(params) {
  socket.emit('get_function_update', params);
}

export {
  subscribeToGraphUpdates,
  requestGraphUpdate,
  unsubscribeToUpdates,
  subscribeToFunctionUpdates,
  requestFunctionUpdate,
};
