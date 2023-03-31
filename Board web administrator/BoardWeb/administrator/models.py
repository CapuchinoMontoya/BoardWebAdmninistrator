from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
# Create your models here.

class Room(models.Model):
    # Modelo para representar una sala de reuniones.
    nameRoom = models.CharField(max_length=100) # El nombre de la sala, de longitud máxima 100.
    roomSize = models.IntegerField() # El tamaño de la sala, representado como un número entero.
    location = models.CharField(max_length=100) # La ubicación de la sala, de longitud máxima 100.

class Reservation(models.Model):
    # Modelo para representar una reserva de una sala de reuniones.
    room = models.ForeignKey(Room, on_delete=models.CASCADE) # La sala de reuniones que se ha reservado.
    user = models.ForeignKey(User, on_delete=models.CASCADE) # El usuario que ha realizado la reserva.
    startDate = models.DateTimeField() # La fecha y hora de inicio de la reserva.
    endDate = models.DateTimeField() # La fecha y hora de finalización de la reserva.

    class Meta:
        unique_together = ('room', 'startDate', 'endDate') # Las reservas son únicas por sala, fecha y hora de inicio y fin.

    def __str__(self):
        return f'{self.room} - {self.user} - {self.startDate} - {self.endDate}'

    def clean(self):
        super().clean()
        if(self.endDate - self.startDate).total_seconds() / 3600 > 2: # Comprueba que la duración de la reserva no supere las 2 horas.
            raise ValidationError("Error, excede más de dos horas")