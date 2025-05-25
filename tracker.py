import tobii_research as tr
import pygame
import random
import os
import csv
import time


with open('ProbandUID.txt', 'r', encoding='utf-8') as f:
    proband = f.read().strip()
print("Proband",proband)
# Ensure the value read is a valid integer
proband = int(proband) if proband.isdigit() else 0
print("Proband",proband)



list = []
def gaze_data_callback(gaze_data):
    if(index < len(images)):
        gaze_data["Image"] = images[index]
    else: gaze_data["Image"] = None

    list.append(gaze_data)


def find_tracker():

    found_eyetrackers = tr.find_all_eyetrackers()

    if (len(found_eyetrackers) > 0):
        pTracker = found_eyetrackers[0]
        print("Eye-Tracker connected: " + pTracker.device_name)
        return pTracker
    else:
        print("No Eye-Trackers found!")


def calibrate_tracker(pTracker):
    screen_width, screen_height = screen.get_size()
    print("Trying Calibration")
    calibration = tr.ScreenBasedCalibration(pTracker)
    calibration.enter_calibration_mode()

    points_to_calibrate = [(0.5, 0.5), (0.1, 0.1), (0.1, 0.9), (0.9, 0.1), (0.9, 0.9)]
    for point in points_to_calibrate:
        x = int(point[0] * screen_width)
        y = int(point[1] * screen_height)
        r = 10

        screen.fill((0, 0, 0))
        pygame.draw.circle(screen, 'red', (x - r, y - r), r)
        pygame.display.flip()

        time.sleep(1)

        if calibration.collect_data(point[0], point[1]) != tr.CALIBRATION_STATUS_SUCCESS:
            calibration.collect_data(point[0], point[1])

    calibration_result = calibration.compute_and_apply()

    calibration.leave_calibration_mode()


def scale_image(pImage):
    width, height = pImage.get_size()
    swidth, sheight = screen.get_size()

    if swidth - width < sheight - height:
        pImage = pygame.transform.smoothscale(pImage, (swidth, int((swidth / width) * height)))
    else:
        pImage = pygame.transform.smoothscale(pImage, (int((sheight / height) * width), sheight))

    return pImage



folder_path = 'current_images'
images = [f for f in sorted(os.listdir(folder_path)) if f.lower().endswith('.png') or f.lower().endswith("jpeg") or f.lower().endswith("jpg")]
if not images:
    print("Keine Bilder im Ordner gefunden.")
else:
    print("Images set up")

random.shuffle(images)
index = 0


pygame.init()
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
tracker = None
tracker = find_tracker()
calibrate_tracker(tracker)
tracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback,as_dictionary=True)

image = pygame.image.load(r'' + folder_path + "/"+images[index])
image = scale_image(image)
print(images)
run = True
while run:
    screen.fill((0, 0, 0))
    screen.blit(image, (screen.get_width() / 2 - image.get_width() / 2, screen.get_height() / 2 - image.get_height() / 2))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False

            if event.key == pygame.K_SPACE:
                index += 1

                if index < len(images):
                    image = pygame.image.load(r'' + folder_path +"/"+ images[index])
                    image = scale_image(image)

                elif index == len(images):
                    image = pygame.font.Font(None, 74).render("Neuen Probanden kalibrieren? Dann jetzt '->' drücken", True, (255, 255, 255))
                   
                    with open('Proband' + str(proband) +'.csv', 'w', newline='', encoding='utf-8') as csvfile:
                        # Bestimme die Feldnamen basierend auf den Keys des ersten Dictionaries

                        feldnamen = list[0].keys()
                        writer = csv.DictWriter(csvfile, fieldnames=feldnamen)

                        # Schreibe die Kopfzeile
                        writer.writeheader()

                        # Schreibe die Datenzeilen
                        writer.writerows(list)

                else:
                    calibrate_tracker(tracker)
                    index = 0
                    random.shuffle(images)
                    image = pygame.image.load(r'' + folder_path + images[index])
                    image = scale_image(image)
                    list = []
                    proband += 1

        pygame.display.update()

tracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
# Increment the ProbandUID and write it back to the file
with open('ProbandUID.txt', 'w', encoding='utf-8') as f:
    f.write(str(proband+1))
    print(proband)
pygame.quit()
