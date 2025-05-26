import tobii_research as tr
import pygame
import random
import os
import csv
import time


proband = 9
list = []
folder_path = 'current_images/'
max_time = 10 # Max Anzeigedauer in s
min_time = 5 # Min Anzeigedauer in s



def gaze_data_callback(gaze_data):
    #if(index < len(images)):
    #    gaze_data["Image"] = images[index]
    #else: gaze_data["Image"] = None
    list.append(gaze_data)


def find_tracker():

    found_eyetrackers = tr.find_all_eyetrackers()

    if (len(found_eyetrackers) > 0):
        pTracker = found_eyetrackers[0]
        print("Eye-Tracker connected: " + pTracker.device_name)
        return pTracker
    else:
        print("No Eye-Trackers found!")
        return None


def calibrate_tracker(pTracker):
    screen_width, screen_height = screen.get_size()

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

        time.sleep(3)

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


def next_image():
    global index, images, image, list, proband, skip

    index += 1

    if index < len(images):
        image = pygame.image.load(r'' + folder_path + images[index])
        image = scale_image(image)

        with open('Proband' + str(proband) + '_' + images[index - 1].split(".")[0] + '.csv', 'w', newline='', encoding='utf-8') as csvfile:
            # Bestimme die Feldnamen basierend auf den Keys des ersten Dictionaries
            feldnamen = list[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=feldnamen)
            # Schreibe die Kopfzeile
            writer.writeheader()
            # Schreibe die Datenzeilen
            writer.writerows(list)

        list = []
        pygame.time.set_timer(skippable, min_time * 1000)
        pygame.time.set_timer(force_skip, max_time * 1000)

    elif index == len(images):
        image = pygame.font.Font(None, 74).render("Neuen Probanden kalibrieren? Dann jetzt '->' drücken", True, (255, 255, 255))
        
        with open('Proband' + str(proband) + '_' + images[index - 1].split(".")[0] + '.csv', 'w', newline='', encoding='utf-8') as csvfile:
            # Bestimme die Feldnamen basierend auf den Keys des ersten Dictionaries
            feldnamen = list[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=feldnamen)
            # Schreibe die Kopfzeile
            writer.writeheader()
            # Schreibe die Datenzeilen
            writer.writerows(list)
            
        pygame.time.set_timer(force_skip, 0)

    else:
        calibrate_tracker(tracker)
        index = 0
        random.shuffle(images)
        image = pygame.image.load(r'' + folder_path + images[index])
        image = scale_image(image)
        list = []
        proband += 1
        pygame.time.set_timer(skippable, min_time * 1000)
        pygame.time.set_timer(force_skip, max_time * 1000)

    skip = False




images = [f for f in sorted(os.listdir(folder_path)) if f.lower().endswith('.png') or f.lower().endswith("jpeg") or f.lower().endswith("jpg")]
if not images:
    print("Keine Bilder im Ordner gefunden.")

random.shuffle(images)
index = 0


pygame.init()
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
tracker = None
tracker = find_tracker()
calibrate_tracker(tracker)


force_skip = pygame.USEREVENT
skippable = pygame.USEREVENT + 1


image = pygame.image.load(r'' + folder_path + images[index])
image = scale_image(image)

tracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback,as_dictionary=True)
skip = False
run = True
pygame.time.set_timer(skippable, min_time * 1000)
pygame.time.set_timer(force_skip, max_time * 1000)
while run:
    screen.fill((0, 0, 0))
    screen.blit(image, (screen.get_width() / 2 - image.get_width() / 2, screen.get_height() / 2 - image.get_height() / 2))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False

            if (event.key == pygame.K_RIGHT or event.key == pygame.K_SPACE) and skip:
                next_image()
                skip = False

        elif event.type == force_skip:
            next_image()
            skip = False

        elif event.type == skippable:
            skip = True


    pygame.display.update()

tracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
pygame.quit()