import os
import glob
from flask import Flask, render_template, request, send_file
import zipfile
import io

app = Flask(__name__, static_folder='images')
IMAGE_DIR = 'images/'

def get_newest_image_sets(num_sets):
    image_files = glob.glob(os.path.join(IMAGE_DIR, '*.jpg'))
    image_sets = {}
    for image in image_files:
        base_name = os.path.basename(image)
        prefix = base_name.split('_')[0]
        if prefix not in image_sets:
            image_sets[prefix] = {}
        suffix = base_name.split('_')[1][0]
        image_sets[prefix][suffix] = image

    complete_sets = [(prefix, images) for prefix, images in image_sets.items() if len(images) == 3]
    sorted_sets = sorted(complete_sets, key=lambda x: x[0], reverse=True)
    return sorted_sets[:num_sets], len(sorted_sets)

@app.route('/')
def index():
    num_sets = int(request.args.get('sets', 3))
    newest_image_sets, total_sets = get_newest_image_sets(num_sets)
    return render_template('index.html', image_sets=newest_image_sets, num_sets=num_sets, max_sets=total_sets)

@app.route('/download_all')
def download_all():
    num_sets = int(request.args.get('sets', 3))
    newest_image_sets, _ = get_newest_image_sets(num_sets)
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for prefix, images in newest_image_sets:
            for suffix in ['A', 'B', 'C']:
                image_path = images[suffix]
                zip_file.write(image_path, os.path.basename(image_path))
    zip_io.seek(0)
    return send_file(zip_io, as_attachment=True, download_name="image_sets.zip", mimetype='application/zip')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
