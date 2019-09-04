const listeners = {};
let graphUpdateResponse; let
  functionUpdateResponse;

function subscribeToGraphUpdates(cb) {
  listeners.update_graph = cb;
}

function requestGraphUpdate() {
  listeners.update_graph(graphUpdateResponse);
}

function setGraphUpdateResponse(response) {
  graphUpdateResponse = response;
}

function unsubscribeToUpdates() {
  listeners.update_graph = undefined;
}

function subscribeToFunctionUpdates(cb) {
  listeners.update_function = cb;
}

function setFunctionUpdateResponse(response) {
  functionUpdateResponse = response;
}

function requestFunctionUpdate() {
  listeners.update_function(functionUpdateResponse);
}

export {
  subscribeToGraphUpdates,
  requestGraphUpdate,
  unsubscribeToUpdates,
  subscribeToFunctionUpdates,
  requestFunctionUpdate,
  setFunctionUpdateResponse,
  setGraphUpdateResponse,
};
