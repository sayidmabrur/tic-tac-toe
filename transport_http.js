// Transport for the local server (python visualizer.py): talk to it over HTTP.
window.LIMITS = {size: 8, iterations: 20000};

async function call(path, body) {
  const res = await fetch(path, body === undefined ? {} :
    {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)});
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}
