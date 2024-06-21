from flask import Flask, render_template, request, send_file
from waitress import serve
from option_scripts import Option_Screener_Runner as opt_runner
from io import StringIO, BytesIO

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/getOptionData', methods=['POST'])
def retrieveOptionData():
    print(request.form)
    tickers_inputted = request.form.get('ticker_input')
    if 'sub_user_input' in request.form:
        print(tickers_inputted)
    elif 'sub_txt_input' in request.form:
        print(request.files)
        file = request.files['txt_input']
        if file.filename == '':
            print('No file submitted')
        else:
            print(f'.txt file {file.filename} submitted')
        
            print(file)
            option_data_all_puts = opt_runner.get_put_data(file)
            put_data_output = StringIO()
            option_data_all_puts.to_csv(put_data_output, index=False)
            put_data_output.seek(0)

            put_data_output_bytes = BytesIO()
            put_data_output_bytes.write(put_data_output.getvalue().encode('utf-8'))
            put_data_output_bytes.seek(0)

            return send_file(put_data_output_bytes, mimetype='text/csv', as_attachment = True, download_name='put_data.csv')

    if tickers_inputted is None:
        tickers_inputted = ""
    return render_template('index.html', tickers_inputted = tickers_inputted)


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)