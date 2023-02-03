# Main app entry point

from flask import Flask
from flask import request
from werkzeug.exceptions import BadRequest

from datetime import datetime

from error_buffer import ErrorBuffer

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

options = {
    "require_content_type": True  # Whether to require the correct Content-Type header on POSTs
}

# GET request at /
# Return something sensical if anyone connects to the root
@app.route("/")
def index_info():
    app.logger.info("index_info")
    return "Hello, world! This is a sample API I developed for an evaluation.\n-Gabriel Konar-Steenberg\ngabrielks.com\n"


# POST request at /temp
@app.route("/temp", methods=["POST"])
def post_temp():
    app.logger.info("post_temp")

    # Get JSON if possible
    try:
        if options["require_content_type"]:
            if request.is_json: sent_data = request.get_json()
            else: return handle_bad_post_temp(request)
        else:
            sent_data = request.get_json(force=True)
    except BadRequest:
        return handle_bad_post_temp(request)

    # Extract data
    if list(sent_data.keys()) != ["data"]: return handle_bad_post_temp(request)  # Ensure that the only key is "data"
    data_string = sent_data["data"]
    data_parts = data_string.split(":")
    if len(data_parts) != 4: return handle_bad_post_temp(request)  # Ensure that there are exactly 4 colon-separated values

    # Parse data
    try: device_id = int(data_parts[0])
    except ValueError: return handle_bad_post_temp(request)  # Fail if part 0 cannot parse as an int
    try: epoch_ms = int(data_parts[1])
    except ValueError: return handle_bad_post_temp(request)  # Fail if part 1 cannot parse as an int
    if data_parts[2] != "'Temperature'": return handle_bad_post_temp(request)  # Fail if part 2 is not the exact string 'Temperature'
    try: temperature = float(data_parts[3])
    except ValueError: return handle_bad_post_temp(request)  # Fail if part 3 cannot parse as a float

    # Compose response
    if temperature >= 90:
        formatted_time = datetime.utcfromtimestamp(epoch_ms/1000).strftime(r"%Y/%m/%d %H:%M:%S")
        return {
            "overtemp": True,
            "device_id": device_id,
            "formatted_time": formatted_time
        }
    else:
        return {"overtemp": False}

# Log a badly formatted POST request at /temp and formulate a response
def handle_bad_post_temp(request):
    ErrorBuffer().append(request.get_data(as_text=True))
    return {"error": "bad request"}, 400


# GET request at /errors
@app.route("/errors", methods=["GET"])
def get_errors():
    app.logger.info("get_errors")
    return {"errors": ErrorBuffer().to_list()}


# DELETE request at /errors
@app.route("/errors", methods=["DELETE"])
def delete_errors():
    app.logger.info("delete_errors")
    error_log = ErrorBuffer()
    n_entries = error_log.num_entries()
    error_log.clear()
    return {"msg": f"Cleared the errors buffer of {n_entries} entries"}

if __name__ == "__main__":
    app.run(debug=True)
