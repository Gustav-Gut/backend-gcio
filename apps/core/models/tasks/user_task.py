from django.db import models
from ..user import UserGcli as User
from .task import Task

class UserTask(models.Model):
    database = 'gcli'

    sso_username = models.ForeignKey(User, on_delete=models.CASCADE, db_column="username_sso", related_name="user_task", blank=True, null=True)
    id = models.ForeignKey(Task, primary_key=True, on_delete=models.CASCADE, db_column="id_tarea", related_name="task_user")

    class Meta:
        db_table = 'tarea_usuario'
        managed = False

    def __str__(self):
        return f"Task {self.id} - User {self.sso_username}"