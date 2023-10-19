"""Common functions to be reused across scripts"""
import inductiva


def get_successfull_tasks(task_ids):
    """Gets the tasks that were successfully completed"""
    successfull_tasks = []
    for task_id in task_ids:
        task = inductiva.tasks.Task(task_id)
        status = task.get_status()
        if status == "success":
            successfull_tasks.append(task)
    return successfull_tasks
