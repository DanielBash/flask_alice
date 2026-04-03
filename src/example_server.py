from flask import Flask
import flask_alice
from nltk.chat.eliza import eliza_chatbot


app = Flask(__name__)
dialogs = flask_alice.Dialogs(app)


@dialogs.on_new_session()
def new_session(req):
    return flask_alice.AliceResponse(
        text="Hello. Tell me whats bothering you."
    )


@dialogs.on_text(r".*", regex=True)
def eliza_handler(req):
    user_text = req.original_utterance

    response = eliza_chatbot.respond(user_text)

    if not response:
        response = "Please, continue."

    return flask_alice.AliceResponse(text=response)


PORT = 5000
HOST = "127.0.0.1"

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)
