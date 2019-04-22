#!./venv/bin/python3
import os

from flask import request, Flask

app = Flask(__name__)


@app.route('/upload_logs', methods=['POST'])
def upload_logs():
    try:
        logs = request.json.get("logs")
        logs_dir = 'logs'
        os.makedirs(logs_dir, exist_ok=True)
        device_uuid = request.json.get("deviceUuid")
        filename = '{}/{}.txt'.format(logs_dir, device_uuid)
        import codecs
        write_file = codecs.open(filename, 'a', "utf-8")
        write_file.write(logs)
        write_file.close()

        if request.json.get("zipNow") or os.path.getsize(filename) >= 10 * 1024 * 1024:
            read_file = codecs.open(filename, 'r', "utf-8")
            read_file.readline()  # skip first line (it's empty).
            readline = read_file.readline(32)
            first_log_time = readline[:23]
            read_file.close()

            log_zips_dir = "log_zips"
            os.makedirs(log_zips_dir, exist_ok=True)

            import zipfile
            logs_zip = zipfile.ZipFile('{}/{}.zip'.format(log_zips_dir, device_uuid), 'a', zipfile.ZIP_DEFLATED)
            logs_zip.write(filename, '{}_{}.txt'.format(device_uuid, first_log_time))
            logs_zip.close()
            os.remove(filename)

        return 'ok'
    except Exception as e:
        return str(e), 409


app.run(
    host='0.0.0.0',
    port=1944
)
