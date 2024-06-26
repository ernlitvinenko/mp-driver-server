from ..base import MPDriverException


def unavailable_status():
    raise MPDriverException(403, "ProhibiitedStatus", "Вы не можете установить данный статус",
                            "You can't set this status")


def should_provide_error_text_with_cancelled_status():
    raise MPDriverException(400, "ShouldProvideAttribute",
                            "Вы должны указать причину, по которой вы не смогли завершить задачу",
                            "Attribute error_text should be provided")


def update_task_by_chain_failed(exc: Exception):
    raise MPDriverException(400, "ChainFailed", """Ошибка в отправке данных: Данные должны приходить в формате списка в следующем формате:
     task (InProgress) ->
      subtask (InProgress) ->
       subtask(Completed/Cancelled) ->
        subtask(InProgress) -> 
        subtask(Completed/Cancelled) ->
         task(Completed)
         
         Цепочка отправляется парами и валидна, только в том случае если пара имеет след вид:
            task (InProgress) -> subtask (InProgress);
                или
            subtask(Completed/Cancelled) -> subtask(InProgress);
                или
            subtask(Completed/Cancelled) -> task(Completed)
         """, f"<{type(exc)}> : {str(exc)}")