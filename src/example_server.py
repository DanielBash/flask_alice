from flask import Flask
import flask_alice

app = Flask(__name__)
dialogs = flask_alice.Dialogs(app)


@dialogs.on_new_session()
def greetings():
    return flask_alice.AliceResponse(text="Приветствую в навыке!")


@dialogs.on_meaning(["Как дела?", "Как поживаешь?", "Что как?"], threshold=0.85)
def greetings():
    return flask_alice.AliceResponse(text="Норм")

@dialogs.on_not_found()
def fallback():
    return flask_alice.AliceResponse(text="Я не понял команду.")


PORT = 5000
HOST = '127.0.0.1'
app.run(host=HOST, port=PORT, debug=True)
