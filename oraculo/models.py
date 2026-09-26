from django.db import models


class Treinamentos(models.Model):
    site = models.URLField()
    conteudo = models.TextField()
    documento = models.FileField(upload_to="documentos/")

    def __str__(self):
        return self.site


class DataTreinamento(models.Model):
    metadata = models.JSONField(null=True, blank=True)
    texto = models.TextField(null=True, blank=True)


class Pergunta(models.Model):
    data_treinamento = models.DateField(null=True, blank=True)
    pergunta = models.TextField()

    def __str__(self):
        return self.pergunta
