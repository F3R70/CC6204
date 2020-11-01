from flask import Flask, request

import src.homeworks.homework1 as homework1
import src.homeworks.homework2 as homework2
import src.homeworks.homework2 as homework3
from src.handler import error

available_homeworks = {
    "1": homework1,
    "2": homework2,
    "3": homework3,
}


def load_tests():
    for homework_number, module in available_homeworks.items():
        try:
            module.load_tests()
        except OSError as e:
            print(f"Error when loading tests in module: {homework_number}")
            raise e


class PreFlask(Flask):
    def run(self, *args, **kwargs):
        with self.app_context():
            load_tests()
        super().run(*args, **kwargs)


app = PreFlask(__name__, instance_relative_config=True)
app.config.from_pyfile("configs.cfg")


@app.route("/ping")
def ping():
    # return {"message": "Not yet ready."}
    return "OK"


@app.route("/force_reload/<string:homework_number>", methods=["POST"])
def reload_tests(homework_number):
    if not request.is_json:
        return error("Sent format is not a json", "json")
    data = request.get_json()
    if "token" not in data:
        return error("The token is not included", "token_missing")
    if data["token"] != app.config["ADMIN_TOKEN"]:
        return error("The token is not correct/is invalid", "token_wrong")
    if homework_number not in available_homeworks:
        return error(f"There is no homework {homework_number}", "no_homework")

    available_homeworks[homework_number].reload_tests()

    return "OK"


@app.route("/api/autocheck/<string:homework_number>/<string:question_number>",
           methods=["POST"])
def autocheck(homework_number, question_number):
    if not request.is_json:
        return error("Sent format is not a json", "json")
    data = request.get_json()
    if "token" not in data:
        return error("The token is not included", "token_missing")
    if data["token"] != app.config["TOKEN"]:
        return error("The token is not correct/is invalid", "token_wrong")
    if homework_number not in available_homeworks:
        return error(f"There is no homework {homework_number}", "no_homework")

    return available_homeworks[homework_number].check(
        question_number=question_number,
        data=data)


@app.route("/api/tests/<string:homework_number>/<string:question_number>",
           methods=["GET"])
def process(homework_number, question_number):
    data = request.args
    if "token" not in data:
        return error("The token is not included", "token_missing")
    if data["token"] != app.config["TOKEN"]:
        return error("The token is not correct/is invalid", "token_wrong")
    if homework_number not in available_homeworks:
        return error(f"There is no homework {homework_number}", "no_homework")

    return available_homeworks[homework_number].get_test(
        question_number=question_number,
        data=data)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
