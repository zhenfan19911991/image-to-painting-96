from flask import Flask, render_template, flash, request, session
from werkzeug.utils import secure_filename
import os
import time
import cloudmersive_image_api_client
from cloudmersive_image_api_client.rest import ApiException


UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def api_transform(style_choosen, file_path):
    API_KEY = '884af8d3-f98e-4aa2-820d-30af4ebf1cbb'

    # Configure API key authorization: Apikey
    configuration = cloudmersive_image_api_client.Configuration()
    configuration.api_key['Apikey'] = API_KEY
    # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
    # configuration.api_key_prefix['Apikey'] = 'Bearer'

    # create an instance of the API class
    api_instance = cloudmersive_image_api_client.ArtisticApi(cloudmersive_image_api_client.ApiClient(configuration))
    style = style_choosen  # str | The style of the painting to apply.
    # To start, try \"udnie\" a painting style.
    # Possible values are: \"udnie\", \"wave\", \"la_muse\", \"rain_princess\".
    image_file = file_path # file | Image file to perform the operation on.  Common file formats such as PNG, JPEG are supported.

    try:
        # Transform an image into an artistic painting automatically
        api_response = api_instance.artistic_painting(style, image_file)

    except ApiException as e:
        print("Exception when calling ArtisticApi->artistic_painting: %s\n" % e)

    result_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'converted_image.png')

    with open(result_file_path, "wb") as fh:
        fh.write(eval(api_response))

    return result_file_path



@app.route('/', methods=['GET', 'POST'])
def home():
    session['file_path'] = ''
    session['result_file_path'] = ''

    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
        elif not allowed_file(file.filename):
            flash('Only .png, .jpg and .jpeg files are acceptable')
        elif file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            session['file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], f'uploaded_image.{filename.rsplit('.', 1)[1].lower()}')
            file.save(session['file_path'])
            print(session['file_path'])
            print(session['result_file_path'])
    return render_template('index.html', image = f'{session['file_path']}', converted_image = f'{session['result_file_path']}')

@app.route('/transform', methods=['GET', 'POST'])
def transform():
    if request.method == 'POST':
        style = request.form.get('style')
        if style == '1':
            style_c = 'udnie'
        elif style == '2':
            style_c = 'wave'
        session['result_file_path']= api_transform(style_c, session['file_path'])

    return render_template('index.html', image = f'{session['file_path']}', converted_image = f'{session['result_file_path']}')



if __name__ == "__main__":
    app.run(port = 5001)
