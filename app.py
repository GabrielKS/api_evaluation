# Main app entry point

from flask import Flask
app = Flask(__name__)

# GET request at /
# Return something sensical if anyone connects to the root
@app.route("/")
def index_info():
    app.logger.info("index_info")
    return "Hello, world! This is my solution to the ***REMOVED*** Energy Service Engineering Data Engineer Evaluation.\n-Gabriel Konar-Steenberg\ngabrielks.com\n"

# POST request at /temp
# TODO build out functionality
@app.route("/temp", methods=["POST"])
def post_temp():
    app.logger.info("post_temp")
    return "post_temp\n"

# GET request at /errors
# TODO build out functionality
@app.route("/errors", methods=["GET"])
def get_errors():
    app.logger.info("get_errors")
    return "get_errors\n"

# DELETE request at /errors
# TODO build out functionality
@app.route("/errors", methods=["DELETE"])
def delete_errors():
    app.logger.info("delete_errors")
    return "delete_errors\n"
