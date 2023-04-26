import os
import random
from flask import Flask, render_template, request, url_for, redirect
import png
from PIL import Image

# define the Flask app
app = Flask(__name__, static_folder='static')

# set the folder where uploaded PNG files will be stored
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# specify the allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'png'}

# define a function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# define a function to extract PNG metadata from a file
def get_png_metadata(filepath):
    try:
        with open(filepath, 'rb') as f:
            pngdata = png.Reader(file=f)
            metadata = {}
            for chunk_type, chunk_data in pngdata.chunks():
                if chunk_type == b'tEXt':
                    if b'parameters' in chunk_data:
                        metadata[chunk_type] = chunk_data
            return metadata
    except (png.FormatError, PermissionError) as e:
        print(f"Skipping file {filepath} due to {type(e).__name__}.")
        return None

# define a function to extract tags from PNG metadata
def extract_metadata_string(metadata):
    if b'tEXt' in metadata:
        metadata_str = metadata[b'tEXt'].decode("utf-8")
        start = metadata_str.find("parameters") + len("parameters")
        end = metadata_str.find("\n", start)
        if end == -1:
            end = len(metadata_str)
        return metadata_str[start:end].strip()
    else:
        return ""
@app.route('/', methods=['GET'])
def index():
    # Redirect to the extract_tags page
    return redirect(url_for('extract_tags'))

# define the route for the tag extraction page
@app.route('/extract_tags.html', methods=['GET', 'POST'])
def extract_tags():
    
    print(request.url)  # added for debugging
    uploaded_image_url = None
    if request.method == 'POST':
        # get the uploaded file
        file = request.files['file']

        # check if the file is valid
        if file and allowed_file(file.filename):
            # save the file to the UPLOAD_FOLDER
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            uploaded_image_url = url_for('static', filename='uploads/' + filename)

            # get the tag extraction ratio
            tag_extraction_ratio = float(request.form['tag_extraction_ratio'])

            # extract the tags from the uploaded file
            metadata = get_png_metadata(filepath)
            extracted_tags = []
            if metadata is not None:
                metadata_list = extract_metadata_string(metadata).split(',')
                num_tags_per_image = int(len(metadata_list) * tag_extraction_ratio)
                extracted_tags.extend(random.sample(metadata_list, num_tags_per_image))

            # render the template with the extracted tags
            return render_template('extract_tags.html', tags=extracted_tags, uploaded_image_url=uploaded_image_url)

        print("File upload unsuccessful") # added for debugging

    # if the request method is GET, simply render the form
    return render_template('extract_tags.html', uploaded_image_url=uploaded_image_url)

if __name__ == '__main__':
    app.run(debug=True)

