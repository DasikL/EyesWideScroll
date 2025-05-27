
 - resizer.py ist eine Utility, die sämtliche Bilder des Ordners images_to_resize in 800x800px skaliert ggf. zuschneidet. Sollte nur für annähernd quadratische Bilder verwendet werden
 - tracker.py ist das Script zum Aufnahmen der Eyetracking-Daten.
Die Bilder im Ordner current_images werden in zufälliger Reihenfolge gezeigt.
Es kann mit Space geskippt werden.
Die Daten werden als Proband ProbandUID .csv gespeichert.
- Visualizer.py erstellt Heatmaps zu einer angegebenen csv-Datei.
- Die fortlaufende ID der Probanden wird in ProbandUID.txt gespeichert, damit diese über Sessions hinweg bestehen bleibt. Das Repo sollte ordnungsgemäßt gepullt/gepusht werden, damit jede ProbandUID einzigartig bleibt.

Der Ordner "new_images" enthält die Stimuli für das Pilottesting und darüber hinaus, der Ordner "current_images" die Stimuli, die im aktuellen Experiment verwendet werden. Alte Stimuli befinden sich im Ordner "old_images"
Die neuen Stimuli sind jeweils mit einer ID und Tags versehen. Die Tags sind: text, imgtext, meme, politik, person, ort, ncc. Der Tag NCC zeigt an, dass das Bild nicht unter Creative Commons Lizenz vorliegt
