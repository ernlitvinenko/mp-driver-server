from ..base import MPDriverException


def incorrect_phone_number():
    raise MPDriverException(422,
                            "IncorrectPhone",
                            "Формат телефона указан некорректно.\nПожалуйста, проверьте правильность набранного номера")


def profile_not_founded():
    raise MPDriverException(404,
                            "SotrNotFounded",
                            "Не найден сотрудник по введенному номеру телефона")


def no_task_for_current_user():
    raise MPDriverException(404, "NoTaskForUser", "Нет задачи с указанным ID для данного пользователя")
