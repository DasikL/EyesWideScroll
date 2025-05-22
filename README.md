 - resizer.py ist eine Utility, die sämtliche Bilder des Ordners images_to_resize in 800x800px skaliert ggf. zuschneidet. Sollte nur für annähernd quadratische Bilder verwendet werden
 - tracker.py ist das Script zum Aufnahmen der Eyetracking-Daten.
Die Bilder im Ordner images werden in zufälliger Reihenfolge gezeigt.
Es kann mit Space geskippt werden.
Die Daten werden als Proband ProbandUID .csv gespeichert.
- Visualizer.py erstellt Heatmaps zu einer angegebenen csv-Datei.
- Die fortlaufende ID der Probanden wird in ProbandUID.txt gespeichert, damit diese über Sessions hinweg bestehen bleibt. Das Repo sollte ordnungsgemäßt gepullt/gepusht werden, damit jede ProbandUID einzigartig bleibt.

Der Ordner "complete_images" enthält sämtliche Stimuli, der Ordner "images" die Stimuli, die im aktuellen Experiment verwendet werden. 
