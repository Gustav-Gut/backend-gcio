from django.db import models
from ..user import User
from .task import Task

class UserTask(models.Model):
    database = 'gcli'

    id = models.AutoField(primary_key=True)
    sso_username = models.ForeignKey(User, on_delete=models.CASCADE, db_column="username_sso", related_name="user_task", blank=True, null=True)
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE, db_column="id_tarea", related_name="task_user")

    class Meta:
        managed = False
        db_table = 'tarea_usuario'

    def __str__(self):
        return f"Task {self.task_id} - User {self.sso_username}"