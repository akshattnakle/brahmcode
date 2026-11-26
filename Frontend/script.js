const KEY = "skillGapPlan";
const $ = id => document.getElementById(id);
let plan = null; // {job, input, completed: []}


function save(){
  try { localStorage.setItem(KEY, JSON.stringify(plan)); $("msg").textContent = "Plan saved on this device."; }
  catch(e) { $("msg").textContent = "Could not save: browser storage is blocked."; }
}

function load(){
  try {
    const p = JSON.parse(localStorage.getItem(KEY));
    return p && typeof p.job === "string" && typeof p.input === "string" && Array.isArray(p.completed) ? p : null;
  } catch(e) { return null; }
}

function chips(el, list, cls){
  el.textContent = list.length ? "" : "None";
  list.forEach(s => {
    const span = document.createElement("span");
    span.className = "chip " + cls;
    span.textContent = s;
    el.appendChild(span);
  });
}

async function render(){
  const current = plan;
  let r;
  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(current)
    });
    if (!res.ok) throw new Error();
    r = await res.json();
  } catch(e) {
    $("msg").textContent = "Cannot reach the Python server. Is app.py running?";
    return;
  }
  if (current !== plan) return; // plan was reset or replaced while waiting
  const {have, missing, completed, percent: pct, total, roadmap} = r;
  const gaps = roadmap.map(item => item.skill);

  $("result").classList.remove("hidden");
  $("percent").textContent = pct + "%";
  $("fill").style.width = pct + "%";
  $("summary").textContent = `You have ${have.length} of ${total} skills for ${plan.job}.`;
  chips($("haveList"), have, "have");
  chips($("missList"), missing, "miss");
  $("progress").textContent = gaps.length
    ? `Roadmap progress: ${completed.length} of ${gaps.length} completed`
    : "No gaps found. You have all the listed skills.";

  $("roadmap").textContent = "";
  roadmap.forEach(({skill, url, task}, i) => {
    const row = document.createElement("div");
    row.className = "step" + (completed.includes(skill) ? " done" : "");
    row.innerHTML = `<input type="checkbox" aria-label="Completed ${skill}">
      <div><b>Step ${i+1}: ${skill}</b><br>Practice: ${task}<br>
      <a href="${url}" target="_blank" rel="noopener">Start learning</a></div>`;
    const box = row.querySelector("input");
    box.checked = completed.includes(skill);
    box.onchange = () => {
      plan.completed = box.checked
        ? [...new Set([...plan.completed, skill])]
        : plan.completed.filter(s => s !== skill);
      save(); render();
    };
    $("roadmap").appendChild(row);
  });
}

$("analyze").onclick = () => {
  // Completed ticks are kept when the same skill is needed again
  plan = {job: $("job").value, input: $("skills").value, completed: plan ? plan.completed : []};
  save(); render();
};

$("reset").onclick = () => {
  if (!confirm("Delete your saved plan?")) return;
  try { localStorage.removeItem(KEY); } catch(e) {}
  plan = null;
  $("skills").value = "";
  $("result").classList.add("hidden");
  $("msg").textContent = "Plan cleared.";
};

async function start(){
  try {
    const res = await fetch("/api/jobs");
    (await res.json()).forEach(j => $("job").add(new Option(j, j)));
  } catch(e) {
    $("msg").textContent = "Cannot reach the Python server. Is app.py running?";
    return;
  }
  plan = load();
  if (plan) { $("job").value = plan.job; $("skills").value = plan.input; render(); }
}
start();
