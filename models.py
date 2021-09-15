from tortoise.models import Model
from tortoise import fields


class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)
    age = fields.IntField(null=True)

    def __str__(self):
        # return self.name
        return f"{self.id}, {self.name}, {self.age}"

    class Meta:
        table = "users"
