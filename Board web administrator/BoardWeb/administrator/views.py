from pyexpat.errors import messages
from sqlite3 import IntegrityError
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse
from .models import Room, Reservation
from .forms import createMeetingForm, detailsMeetingForm
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.


def signup(request):
    if request.method == 'GET':
        # Renderiza a signup con el formulario de registro
        return render(request, 'pages/signup.html', {
            'formSignUp': UserCreationForm
        })
    else:
        print(request.POST)
        # Verifica si las contraseñas ingresadas en el formulario coinciden
        if request.POST['password1'] == request.POST['password2']:
            try:
                # Crea un nuevo usuario con los datos ingresados en el formulario
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                # Inicia sesión con el nuevo usuario
                login(request, user)
                # Redirige al usuario a la página de index
                return redirect('index')
            except:
                # Si ya existe un usuario con ese nombre de usuario, devuelve la misma plantilla de registro con un mensaje de error
                return render(request, 'pages/signup.html', {
                    'formSignUp': UserCreationForm,
                    'error': 'Este usuario ya existe'
                })
        else:
            # Si las contraseñas ingresadas no coinciden, devuelve la misma plantilla de registro con un mensaje de error
            return render(request, 'pages/signup.html', {
                'formSignUp': UserCreationForm,
                'error': 'Las contraseñas no coinciden'
            })

def loginUser(request):
    # Comprobamos si el usuario ya ha iniciado sesión previamente, y si es así, cerramos su sesión 
    if User.is_authenticated:
        logout(request)
    
    if request.method == 'GET':
        # Renderiza la pagina en caso de no recibir parametros
        return render(request, 'pages/login.html', {
            'formLogin': AuthenticationForm
        })
    else:
        # Si el método de solicitud no es GET, entonces es POST. Esto significa que el usuario ha enviado el formulario de inicio de sesión
        # Comprobamos las credenciales del usuario para iniciar sesión
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            # Si no se pudo autenticar al usuario, mostramos la página de inicio de sesión con un mensaje de error
            return render(request, 'pages/login.html', {
                'formLogin': AuthenticationForm,
                'error': 'El usuario no existe'
            })
        else:
            # Si las credenciales son correctas, iniciamos sesión con el usuario y redirigimos a la página index
            login(request, user)
            return redirect('index')

def index(request):
    # Obtiene todos los objetos Room de la base de datos
    rooms = Room.objects.all()
    # Renderiza la plantilla 'pages/index.html' con la lista de objetos Room obtenidos
    return render(request, 'pages/index.html', {
        'rooms': rooms
    })

#Es un decorado, sirvepara que solo el usuario que inicie sesion tenga acceso a la vista
@login_required
def createMeeting(request):
    # Obtener todas las salas
    rooms = Room.objects.all()
    if request.method == 'GET':
        # Si se hace una petición GET, renderizar la página de crear reunión con el formulario y las salas
        return render(request, 'pages/createMeeting.html', {
            'rooms': rooms,
            'form': createMeetingForm
        })
    else:
        # Si se hace una petición POST, validar el formulario y crear una nueva reserva
        forms = createMeetingForm(request.POST)
        if forms.is_valid():
            # Crear una nueva reserva guardandola en una variable
            newReservation = forms.save(commit=False)
            # Establecer al usuario que tiene iniciada la sesion como el propietario de la reserva
            newReservation.user = request.user
            roomData = "Nada"
            # Iterar a través de todas las salas disponibles para encontrar la que fue seleccionada en el formulario
            for room in rooms:
                try:
                    roomData = request.POST[room.nameRoom]
                    if room.nameRoom == roomData:
                        newReservation.room = room
                except:
                    continue
            # Verificar si ya existe una reserva en la misma sala y en el rango de fechas elegido
            if Reservation.objects.filter(
                    Q(room=newReservation.room) &
                    ((Q(startDate__lte=newReservation.startDate) & Q(endDate__gte=newReservation.startDate)) |
                     (Q(startDate__lte=newReservation.endDate) & Q(endDate__gte=newReservation.endDate)) |
                     (Q(startDate__gte=newReservation.startDate) & Q(endDate__lte=newReservation.endDate)))).exists():
                # Si ya existe una reserva en ese rango de fechas, mostrar un mensaje de error
                return render(request, 'pages/createMeeting.html', {
                    'rooms': rooms,
                    'form': createMeetingForm,
                    'error': 'Ya existe una reunión en esa sala y en ese rango de fechas',
                })
            else:
                # Si no existe una reserva en ese rango de fechas, guardar la nueva reserva en la base de datos
                if newReservation.startDate >= newReservation.endDate:
                    # Verificar que la hora de finalización sea posterior a la hora de inicio
                    return render(request, 'pages/createMeeting.html', {
                        'rooms': rooms,
                        'form': createMeetingForm,
                        'error': 'La hora final debe ser posterior a la hora inicial',
                    })
                newReservation.save()
                # En caso de que todo este correcto, guarda la en la base de datos y renderiza con un mensaje de exito
                return render(request, 'pages/createMeeting.html', {
                    'rooms': rooms,
                    'form': createMeetingForm,
                    'success': 'Se ha reservado la sala'
                })
        else:
            # Si el formulario no es válido, mostrar un mensaje de error
            return render(request, 'pages/createMeeting.html', {
                'rooms': rooms,
                'form': createMeetingForm,
                'error': 'No puede reservar una sala por mas de 2 horas',
            })

#Es un decorado, sirvepara que solo el usuario que inicie sesion tenga acceso a la vista
@login_required
def myMeetings(request):
    # Se obtienen las reservas del usuario actual
    rooms = Reservation.objects.filter(user=request.user)
    if request.method == 'GET':
        # Renderizar la página de reuniones del usuario con la lista de reservas
        return render(request, 'pages/myMeetings.html', {
            'rooms': rooms,
        })

#Es un decorado, sirvepara que solo el usuario que inicie sesion tenga acceso a la vista
@login_required
def detailsMyMeeting(request, id):
    if request.method == 'GET':
        # Obtiene la sala por medio del id y la reservacion para despues pasarla a un fromulario.
        rooms = Reservation.objects.filter(pk=id)
        meeting = get_object_or_404(Reservation, pk=id)
        form = detailsMeetingForm(instance=meeting)
        # Renderiza a la pagina detailsMyMeeting con los detalles de la reunión, formulario y la sala 
        return render(request, 'pages/detailsMyMeeting.html', {'meeting': meeting, 'form': form, 'rooms': rooms})
    else:
        # Obtiene la sala por medio del id y la reservacion para despues pasarla a un fromulario para poder mandar los datos.
        rooms = Reservation.objects.filter(pk=id)
        meeting = get_object_or_404(Reservation, pk=id)
        form = detailsMeetingForm(request.POST, instance=meeting)
        # Inicializa el contexto con los detalles de la reunión, el formulario, todas las salas y un valor de error inicial nulo
        context = {'meeting': meeting, 'form': form, 'rooms': Room.objects.all(), 'error': None}
        if form.is_valid():
            # Si el formulario es válido, crea una instancia de la reserva y lo guarda en una variable
            reservation = form.save(commit=False)
            # Comprueba si la fecha de inicio de la reserva es superior a la fecha de finalización
            if reservation.startDate < reservation.endDate:
                # Comprueba si hay alguna reserva para la misma sala y fechas en el mismo rango de horas
                overlapping_reservations = Reservation.objects.filter(
                    Q(room=reservation.room) &
                    Q(startDate__lte=reservation.endDate) &
                    Q(endDate__gte=reservation.startDate)
                ).exclude(pk=reservation.pk)

                if overlapping_reservations.exists():
                    # Si ya hay una reserva en la misma sala y fechas en el mismo rango de horas, se establece un mensaje de error y se actualiza el contexto
                    context['error'] = 'Ya existe una reunión programada para esta sala en este rango de tiempo'
                    context['meeting'] = meeting
                    context['form'] = form
                    context['rooms'] = rooms
                else:
                    # Si no hay reservas en el mismo rango de horas, se guarda la reserva en la base de datos y se redirige a la página myMeetings
                    reservation.save()
                    return redirect('myMeetings')
            else:
                # Si la fecha de finalización es anterior a la fecha de inicio, se establece un mensaje de error y se actualiza el contexto
                context['error'] = 'La fecha de finalización debe ser posterior a la fecha de inicio'
                context['meeting'] = meeting
                context['form'] = form
                context['rooms'] = rooms
        else:
            # Si el formulario no es válido, se establece un mensaje de error y se actualiza el contexto
            context['error'] = 'Error, excede mas de dos horas'
            context['meeting'] = meeting
            context['form'] = form
            context['rooms'] = rooms
        # Renderiza a la pagina detailsMyMeeting con el contexto actualizado
        return render(request, 'pages/detailsMyMeeting.html', context)

#Es un decorado, sirvepara que solo el usuario que inicie sesion tenga acceso a la vista
@login_required
def deleteMyMeeting(request, id):
    # Se obtienen todas las reservaciones del usuario que tiene iniciada la sesion
    rooms = Reservation.objects.filter(user=request.user)
    # Se obtiene la reserva correspondiente al id especificado
    post = get_object_or_404(Reservation, pk=id)
    # Si la petición es de tipo GET se elimina la reserva y se redirige a la vista myMeetings
    if request.method == 'GET':
        post.delete()
        print('Eliminado')
        return render(request, 'pages/myMeetings.html', {
            'rooms': rooms,
        })

#Es un decorado, sirvepara que solo el usuario que inicie sesion tenga acceso a la vista
@login_required
def allMeetings(request):
    # Obtener todas las reservas
    rooms = Reservation.objects.all()
    if request.method == 'GET':
        # Renderizar la página de todas las reuniones con la lista de reservas
        return render(request, 'pages/allMeetings.html', {
            'rooms': rooms,
        })