import os
import glob
from flask import Flask, render_template

app = Flask(__name__, static_folder='images')
IMAGE_DIR = 'images/'

def get_newest_image_sets():
    image_files = glob.glob(os.path.join(IMAGE_DIR, '*.jpg'))
    image_sets = {}
    for image in image_files:
        base_name = os.path.basename(image)
        prefix = base_name.split('_')[0]
        if prefix not in image_sets:
            image_sets[prefix] = {}
        suffix = base_name.split('_')[1][0]
        image_sets[prefix][suffix] = image

    # Filter for only complete sets and sort by timestamp (newest first)
    complete_sets = [(prefix, images) for prefix, images in image_sets.items() if len(images) == 3]
    sorted_sets = sorted(complete_sets, key=lambda x: x[0], reverse=True)

    # Return the last 3 complete sets
    return sorted_sets[:3]

@app.route('/')
def index():
    # Get the three newest complete sets of images
    newest_image_sets = get_newest_image_sets()

    # Pass the image sets to the template
    return render_template('index.html', image_sets=newest_image_sets)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
