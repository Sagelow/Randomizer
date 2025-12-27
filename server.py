from flask import Flask, send_file, render_template_string, request, jsonify
import os, random, urllib.parse

app = Flask(__name__)

FOLDER_PATH = os.path.join(os.path.dirname(__file__), "img")

# Liste de toutes les images
images = [os.path.join(FOLDER_PATH, f) 
          for f in os.listdir(FOLDER_PATH) 
          if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))]

# Préchargement des chemins (simulé rapide car Flask envoie le fichier)
# On garde l'historique pour la navigation
history = []
history_index = -1

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Randomizer</title>
<style>
body { background-color:black; color:white; text-align:center; margin:0; padding:0; }
img { max-width:100vw; max-height:90vh; display:block; margin:auto; object-fit:contain; }
button { margin:10px; font-size:28px; padding:15px 30px; cursor:pointer; }
#controls { position:fixed; bottom:20px; left:50%; transform:translateX(-50%); }
</style>
</head>
<body>
<h2 id="filename">Image</h2>
<img id="randomImage" src="/random" />
<div id="controls">
<button onclick="prevImage()">Return</button>
<button onclick="togglePause()">Pause</button>
<button onclick="nextImage()">Next</button>
</div>

<script>
let paused = false;
let timer = null;
const intervalTime = 5000; // 5 secondes

function loadImage(imgData) {
    const img = document.getElementById('randomImage');
    img.src = '/file?path=' + encodeURIComponent(imgData.path) + '&rand=' + Math.random();
    document.getElementById('filename').innerText = imgData.name;
}

// Timer automatique
function startTimer() {
    if (timer) clearInterval(timer);
    timer = setInterval(() => {
        if (!paused) fetchNext();
    }, intervalTime);
}

function fetchNext() {
    fetch('/navigate?direction=next')
        .then(response => response.json())
        .then(data => loadImage(data));
}

function nextImage() {
    fetchNext();
    startTimer();  // Restart compteur après appui
}

function prevImage() {
    fetch('/navigate?direction=prev')
        .then(response => response.json())
        .then(data => loadImage(data));
    startTimer();  // Restart compteur après appui
}

function togglePause() {
    paused = !paused;
    document.querySelector('button[onclick="togglePause()"]').innerText = paused ? "Play" : "Pause";
}

// Initialisation
startTimer();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/random")
def random_image():
    global history, history_index
    if not images:
        return "Aucune image trouvée", 404
    img = random.choice(images)
    history = history[:history_index+1]
    history.append(img)
    history_index += 1
    return send_file(img, mimetype='image/jpeg')

@app.route("/navigate")
def navigate():
    global history, history_index
    direction = request.args.get('direction', 'next')
    if direction == 'next':
        if history_index < len(history)-1:
            history_index += 1
        else:
            img = random.choice(images)
            history.append(img)
            history_index += 1
    elif direction == 'prev':
        if history_index > 0:
            history_index -= 1
    img_path = history[history_index]
    return jsonify({
        'path': img_path,
        'name': os.path.basename(img_path)
    })

@app.route("/file")
def file():
    path = request.args.get('path')
    if not path:
        return "Fichier non spécifié", 400
    path = urllib.parse.unquote(path)
    return send_file(path, mimetype='image/jpeg')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
