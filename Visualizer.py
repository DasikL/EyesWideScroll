import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cv2


# with open('ProbandUID.txt', 'r', encoding='utf-8') as f:
#    probandnr = f.read().strip()
probandnr = 5

df = pd.read_csv("./data/Proband" + str(probandnr) + ".csv")
# list all csv files starting with Proband<probandnr> in the current directory


coordinates = list()
for i in df["left_gaze_point_on_display_area"]:
    item1 = float(i.split(",")[0].strip("("))
    item2 = float(i.split(",")[1].strip(")"))
    coordinates.append((item1, item2))

data = pd.DataFrame(coordinates, columns=["x", "y"])
data["system_time_stamp"] = df["system_time_stamp"]
data["Image"] = df["Image"]

# DataFrames are grouped by their image
dfs = dict(tuple(data.groupby("Image")))
print(dfs.keys())


def filter_noise(
    df: pd.DataFrame,
    vel_thresh: float = 1,  # [px/ms], z.B. 0.5 px/ms ≙ 500 px/s
    amp_thresh: float = 25,  # [px]
    dur_thresh: float = 50,  # [ms]
) -> pd.DataFrame:
    """
    Entfernt kurze Mikrosakkaden und Blinks aus den Gaze-Daten.

    Parameter:
    -----------
    df : DataFrame mit Spalten ['x','y','system_time_stamp']
    vel_thresh : Geschwindigkeits‑Threshold in px/ms
    amp_thresh : Amplituden‑Threshold in pxS
    dur_thresh : Dauer‑Threshold in ms

    Rückgabe:
    ---------
    DataFrame mit interpoliertem 'x' und 'y' ohne Noise.
    """

    df = df.sort_values("system_time_stamp").reset_index(drop=True)

    # Zeitdifferenzen (dt) in ms
    dt = df["system_time_stamp"].diff().bfill()

    # Positionsdifferenzen
    dx = df["x"].diff().fillna(0)
    dy = df["y"].diff().fillna(0)

    # Geschwindigkeit [px/ms]
    vel = np.sqrt((dx / dt) ** 2 + (dy / dt) ** 2)

    # Boolean-Array: potenzielle Sakkade-Samples
    is_sacc = vel > vel_thresh

    # Blink-Detektion: x oder y gleich 0 oder NaN
    is_blink = (df["x"] == 0) | (df["y"] == 0) | df["x"].isna() | df["y"].isna()

    # Noise-Maske initialisieren
    noise = is_blink.copy()

    # Segmente von aufeinanderfolgenden Sakkade-Samples finden
    sacc_indices = np.where(is_sacc)[0]
    if len(sacc_indices) > 0:
        # Lücken (Segmentbrüche) ermitteln
        breaks = np.where(np.diff(sacc_indices) > 1)[0]
        seg_starts = np.insert(sacc_indices[breaks + 1], 0, sacc_indices[0])
        seg_ends = np.append(sacc_indices[breaks], sacc_indices[-1])

        # Jedes Segment prüfen
        for start, end in zip(seg_starts, seg_ends):
            dur = df.loc[end, "system_time_stamp"] - df.loc[start, "system_time_stamp"]
            amp = np.hypot(
                df.loc[end, "x"] - df.loc[start, "x"],
                df.loc[end, "y"] - df.loc[start, "y"],
            )
            # Kurze, kleine Mikrosakkade?
            if (dur < dur_thresh) and (amp < amp_thresh):
                noise[start : end + 1] = True

    # Rausfiltern / Interpolieren
    clean = df.copy()
    clean.loc[noise, "x"] = np.nan
    clean.loc[noise, "y"] = np.nan
    clean["x"] = clean["x"].interpolate(method="linear").ffill().bfill()
    clean["y"] = clean["y"].interpolate(method="linear").ffill().bfill()

    return clean


filtered_df = filter_noise(data)
filtered_df

filtered_df_list = [filter_noise(dfs[i]) for i in dfs.keys()]

# Assume a virtual screen with a 16:9 ratio (e.g., 1920x1080)


screen_ratio = 16 / 9
img_h = 800
img_w = 800

# Compute corresponding screen width based on image height
screen_h = img_h
screen_w = int(screen_ratio * screen_h)

# Compute horizontal margins (image is centered)
margin_x = (screen_w - img_w) / 2
min_rel_x = margin_x / screen_w
max_rel_x = (margin_x + img_w) / screen_w

adjusted_df_list = list()
for filtered_df in filtered_df_list:
    adjusted_df = filtered_df[
        (filtered_df["x"] >= min_rel_x) & (filtered_df["x"] <= max_rel_x)
    ].copy()
    adjusted_df["x_px"] = (
        (adjusted_df["x"] - min_rel_x) / (max_rel_x - min_rel_x)
    ) * img_w
    adjusted_df["y_px"] = adjusted_df["y"] * img_h
    adjusted_df_list.append(adjusted_df)
# Filter and scale data
filtered = data[(data["x"] >= min_rel_x) & (data["x"] <= max_rel_x)].copy()
filtered["x_px"] = ((filtered["x"] - min_rel_x) / (max_rel_x - min_rel_x)) * img_w
filtered["y_px"] = filtered["y"] * img_h


from scipy.ndimage import gaussian_filter
import os

for screening in adjusted_df_list:
    image_name = screening["Image"].iloc[0].strip(".jpg")

    image = cv2.imread("current_images/" + screening["Image"].iloc[0])
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # 3. Erzeuge ein leeres Canvas mit gleicher Größe wie das Bild
    heatmap_data = np.zeros((image.shape[0], image.shape[1]))

    # 4. Fülle das Heatmap-Array mit Blickpunkten
    for _, row in screening.iterrows():
        x, y = int(row["x_px"]), int(row["y_px"])
        if 0 <= y < image.shape[0] and 0 <= x < image.shape[1]:
            heatmap_data[y, x] += 1

    # 5. Glätte die Heatmap (optional)
    heatmap_data = cv2.GaussianBlur(heatmap_data, (85, 85), 0)

    # 1. Create a 2D histogram of gaze points
    heatmap_data, xedges, yedges = np.histogram2d(
        screening["x_px"],
        screening["y_px"],
        bins=[img_w, img_h],  # match pixel resolution
        range=[[0, img_w], [0, img_h]],
    )

    # 2. Apply Gaussian blur to spread the heat
    heatmap_blurred = gaussian_filter(
        heatmap_data.T, sigma=25
    )  # .T to match image axes

    # 3. Normalize and mask
    heatmap_norm = heatmap_blurred / np.max(heatmap_blurred)
    heatmap_masked = np.ma.masked_where(
        heatmap_norm < 0.01, heatmap_norm
    )  # hide near-zero

    # 4. Display
    dpi = 100
    fig = plt.figure(figsize=(img_w / dpi, img_h / dpi), dpi=dpi)
    plt.imshow(image, zorder=1)
    plt.imshow(
        heatmap_masked,
        cmap="jet",  # blue → red
        alpha=0.6,
        interpolation="bilinear",
        zorder=2,
        origin="upper",  # top-left origin
    )
    plt.axis("off")
    folder = "heatmap_overlays/Proband" + str(probandnr) + "/" + image_name
    os.makedirs(folder, exist_ok=True)
    plt.savefig(
        folder + "/heatmap_overlay_" + image_name + ".png",
        dpi=dpi,
        bbox_inches="tight",
        pad_inches=0,
    )
    plt.close()
    fig = plt.figure(figsize=(img_w / dpi, img_h / dpi), dpi=dpi)

    plt.imshow(
        heatmap_masked, cmap="jet", alpha=1.0, interpolation="bilinear", origin="upper"
    )
    plt.axis("off")

    # Transparent background + tight save
    plt.savefig(
        folder + "/heatmap_only_" + image_name + ".png",
        dpi=dpi,
        bbox_inches="tight",
        pad_inches=0,
        transparent=True,
    )
    plt.close()

