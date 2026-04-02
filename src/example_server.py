from flask import Flask
import flask_alice

app = Flask(__name__)
dialogs = flask_alice.Dialogs(app)


@dialogs.on_text("привет")
def hello(req):
    return flask_alice.YandexDialogResponse(text="Здравствуйте!", tts="Здравствуйте!")


@dialogs.on_not_found()
def fallback(req):
    return flask_alice.YandexDialogResponse(text="Я не понял команду.", tts="Я не понял команду.")


PORT = 5000
HOST = '0.0.0.0'
app.run(host=HOST, port=PORT, debug=True)
