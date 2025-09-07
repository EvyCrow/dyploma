from label_studio_sdk import Client
import json
from PIL import Image, ImageDraw
import requests

# The files appear in the browser after the program finishes running.

LABEL_STUDIO_URL = 'http://88.83.201.153:8080/'
# I deleted it for security
API_KEY = ''
# Base URL for download (URL without final /)
BASE_URL = LABEL_STUDIO_URL.rstrip('/')
# Needed for authorization when downloading. Otherwise, it does not give access
HEADERS = {"Authorization": f"Token {API_KEY}"}

ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)
# ls.check_connection()

Pr_list = ls.get_projects()

# list of everything
for pr in Pr_list:
    print(pr.id, pr.title)


def mask_generator(id_json):
    file_path = f"{id_json}.json"
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # image size
    if data.get("annotations"):
        first_annotation = data["annotations"][0]
        if first_annotation.get("result"):
            first_result = first_annotation["result"][0]
            width = first_result.get("original_width")
            height = first_result.get("original_height")

    # coordinates
    all_points = []
    for annotation in data.get("annotations", []):
        for result in annotation.get("result", []):
            points = result.get("value", {}).get("points", [])
            all_points.append(points)

    # pic must be SQUARE
    points1 = [tuple((x * width) / 100 for x in row) for row in all_points[0]]
    points2 = [tuple((x * width) / 100 for x in row) for row in all_points[1]]

    # FOR A LIMB
    limb = Image.new('1', (width, height), 'black')
    draw = ImageDraw.Draw(limb)
    draw.polygon(points1, fill="white")
    # limb.show()
    limb.save(f'limb_{id_json}.jpeg')
    print(f"Generated: limb_{id_json}.jpeg")

    # FOR A WOUND
    wound = Image.new('1', (width, height), 'black')
    draw = ImageDraw.Draw(wound)
    draw.polygon(points2, fill="white")
    # wound.show()
    wound.save(f'wound_{id_json}.jpeg')
    print(f"Generated: wound_{id_json}.jpeg")


''' !!!!!!!!!!!!!!!!!!!!! '''
# purely a user thing, can be painlessly removed by correcting the formatting
# # and replacing project_id with a number
while True:
    # as I understand it, only id 6-11 and 13-21 are relevant (why not 12 is a mystery)
    try:
        project_id = int(input("Enter id (6-11, 13-21) or 0 to exit >"))

        if project_id == 0:
            print("\nInput interrupted. Exiting...")
            break
        # change it here if necessary
        #if project_id not in list(range(6, 12)) + list(range(13, 22)):
        #    print("Invalid ID")
        #    continue


    except ValueError:
        print("Error: Please enter a valid number!")
    except KeyboardInterrupt:
        # ctrl+f2 in pycharm
        print("\nInput interrupted. Exiting...")
        break

    project = ls.get_project(project_id)
    print(project.get_tasks())
    _labeled_tasks = project.get_labeled_tasks_ids()
    # ID of tasks in the project, masks and photos will be named after them
    print("YOU NEED THIS -> ", _labeled_tasks)

    ''' !!!!!!!!!!!!!!!!!!!!!!! '''

    # loading info into json and downloading images
    for tasks in _labeled_tasks:
        annotation = project.get_task(tasks)
        print(annotation)
        # print(annotation['data']['image'])

        image_url = f"{BASE_URL}" + annotation['data']['image']
        print("Downloading:", image_url)
        image_name = f"{annotation['id']}.png"

        try:
            response = requests.get(image_url, headers=HEADERS)
            # HTTP Error Checking
            response.raise_for_status()

            # Save the image to the root folder
            with open(image_name, 'wb') as img_file:
                img_file.write(response.content)
            print(f"Saved: {image_name}")

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")

        except Exception as e:
            print(f"Download error occurred: {image_url}: {e}")

        with open(str(annotation['id']) + '.json', 'w') as f:
            json.dump(annotation, f)
            print(f"Generated: {annotation['id']}.json")

    # as an example
    for i in _labeled_tasks:
        mask_generator(i)
