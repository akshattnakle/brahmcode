from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder=None)

# Each skill: [learning link, practice task]. Prerequisites are listed first in each job.
SKILLS = {
  "HTML": ["https://developer.mozilla.org/en-US/docs/Web/HTML", "Build a personal profile page"],
  "CSS": ["https://developer.mozilla.org/en-US/docs/Web/CSS", "Make that page mobile friendly"],
  "JavaScript": ["https://javascript.info/", "Build a to-do list app"],
  "Git": ["https://git-scm.com/book/en/v2", "Push a project to GitHub"],
  "React": ["https://react.dev/learn", "Build a weather dashboard"],
  "Node.js": ["https://nodejs.org/en/learn", "Create a small REST API"],
  "SQL": ["https://sqlbolt.com/", "Write queries with joins and grouping"],
  "Python": ["https://docs.python.org/3/tutorial/", "Write a file organiser script"],
  "Statistics": ["https://www.khanacademy.org/math/statistics-probability", "Summarise a real dataset"],
  "Excel": ["https://support.microsoft.com/en-us/excel", "Build a pivot table report"],
  "Pandas": ["https://pandas.pydata.org/docs/getting_started/index.html", "Clean a messy CSV file"],
  "Data Visualization": ["https://matplotlib.org/stable/tutorials/index.html", "Chart three insights from a dataset"],
  "Machine Learning": ["https://developers.google.com/machine-learning/crash-course", "Train and evaluate a simple model"],
  "Networking": ["https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Web_mechanics", "Explain what happens when a URL loads"],
  "Linux": ["https://linuxjourney.com/", "Manage files and permissions in a terminal"],
  "Web Security": ["https://portswigger.net/web-security", "Complete five beginner labs"],
  "Figma": ["https://help.figma.com/", "Design a three-screen mobile app"],
  "User Research": ["https://www.nngroup.com/articles/which-ux-research-methods/", "Interview three users"],
  "Wireframing": ["https://www.nngroup.com/articles/ux-prototype-hi-lo-fidelity/", "Sketch and test a prototype"]
}

JOBS = {
  "Frontend Developer": ["HTML","CSS","JavaScript","Git","React"],
  "Full Stack Developer": ["HTML","CSS","JavaScript","Git","React","Node.js","SQL"],
  "Data Analyst": ["Excel","SQL","Statistics","Python","Pandas","Data Visualization"],
  "ML Engineer": ["Python","Git","Statistics","SQL","Pandas","Machine Learning"],
  "Cybersecurity Analyst": ["Networking","Linux","Python","Web Security"],
  "UI/UX Designer": ["User Research","Wireframing","Figma","HTML","CSS"]
}

# Other spellings students may type
ALIASES = {"js":"javascript","html5":"html","css3":"css","reactjs":"react","react.js":"react",
  "node":"node.js","nodejs":"node.js","ml":"machine learning","stats":"statistics",
  "ms excel":"excel","github":"git","data visualisation":"data visualization"}


def normalize(text):
    t = " ".join(text.lower().split())
    return ALIASES.get(t, t)


@app.get("/")
def home():
    return send_from_directory(app.root_path, "index.html")


@app.get("/<any('style.css', 'script.js'):name>")
def assets(name):
    return send_from_directory(app.root_path, name)


@app.get("/api/jobs")
def jobs():
    return jsonify(list(JOBS))


@app.post("/api/analyze")
def analyze():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Invalid request"), 400
    job, text, ticked = data.get("job"), data.get("input"), data.get("completed")
    if not (isinstance(job, str) and job in JOBS
            and isinstance(text, str) and isinstance(ticked, list)):
        return jsonify(error="Invalid request"), 400

    required = JOBS[job]
    known = {normalize(s) for s in text.split(",")}
    initial = [s for s in required if s.lower() in known]
    gaps = [s for s in required if s.lower() not in known]
    completed = [s for s in gaps if s in ticked]
    have = initial + completed

    return jsonify(
        have=have,
        missing=[s for s in gaps if s not in completed],
        completed=completed,
        percent=round(len(have) / len(required) * 100),
        total=len(required),
        roadmap=[{"skill": s, "url": SKILLS[s][0], "task": SKILLS[s][1]} for s in gaps],
    )


if __name__ == "__main__":
    app.run()
