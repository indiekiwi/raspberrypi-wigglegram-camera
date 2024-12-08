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
        try:
            prefix, remainder = base_name.split('_')
            subset, index_with_ext = remainder.split('-')
            index = index_with_ext.split('.')[0]  # Strip the file extension
            index = int(index)  # Convert to integer
        except ValueError:
            print(f"Skipping invalid filename: {base_name}")
            continue  # Skip files with incorrect format

        if prefix not in image_sets:
            image_sets[prefix] = {'A': [], 'B': [], 'C': []}
        if subset not in image_sets[prefix]:
            print(f"Skipping unexpected subset: {subset}")
            continue  # Skip unexpected subsets

        image_sets[prefix][subset].append((index, base_name))

    # Sort each subset by index
    for prefix, subsets in image_sets.items():
        for subset, items in subsets.items():
            items.sort(key=lambda x: x[0])  # Sort by index

    # Sort sets by timestamp (prefix) in reverse order
    sorted_sets = sorted(image_sets.items(), key=lambda x: x[0], reverse=True)
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
            for subset in ['A', 'B', 'C']:
                for _, image in images[subset]:
                    image_path = os.path.join(IMAGE_DIR, image)
                    zip_file.write(image_path, os.path.basename(image_path))
    zip_io.seek(0)
    return send_file(zip_io, as_attachment=True, download_name="image_sets.zip", mimetype='application/zip')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
