from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
import json
import requests
from .models import TicketCase
from .serializers import TicketCaseSerializer


class ZohoDeskCreateTicketView(APIView):

    def post(self, request):
        # Validar los datos del formulario utilizando el serializador
        serializer = TicketCaseSerializer(data=request.data)

        if serializer.is_valid():
            # Obtener las credenciales desde la configuración de Django
            client_id = settings.ZOHO_DESK_CONFIG['client_id']
            client_secret = settings.ZOHO_DESK_CONFIG['client_secret']
            refresh_token = settings.ZOHO_DESK_CONFIG['refresh_token']

            # Obtener el token de acceso actual o renovarlo si es necesario
            access_token = self.get_or_refresh_access_token(
                client_id, client_secret, refresh_token)

            # Obtener datos del ticket proporcionados por el usuario
            subject = request.data.get('subject', 'try')
            description = request.data.get('description', 'test-2')

            # Validar la presencia de los campos requeridos
            if not subject or not description:
                return Response({'error': 'Los campos "subject" y "description" son obligatorios.'}, status=status.HTTP_400_BAD_REQUEST)

            # Configurar la URL y los datos del ticket para la solicitud
            url = 'https://desk.zoho.com/api/v1/tickets'
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            }
            payload = json.dumps({
                "subject": subject,
                "description": description,
                "departmentId": "938962000000006907",
                "contactId": "938962000000255029",
                "priority": "alta",
            })

            try:
                # Realizar la solicitud para crear el ticket
                response = requests.post(url, headers=headers, data=payload)
                response.raise_for_status()

                # Verificar el código de estado de la respuesta
                print(response.status_code)
                if response.status_code == 200:
                    # Extraer el número de ticket y registrar en la base de datos
                    ticket_number = response.json().get('ticketNumber', None)
                    ticket_case = TicketCase(
                        subject=subject,
                        description=description,
                        department_id="938962000000006907",
                        contact_id="938962000000255029",
                        priority="alta",
                        ticket_number=ticket_number
                    )

                    ticket_case.save()

                    data = response.json()
                    return Response(data, status=status.HTTP_201_CREATED)
                else:
                    return Response({'error': response.json()}, status=response.status_code)

            except requests.RequestException as e:
                # Manejar errores de solicitud
                error_message = f'Error al crear el ticket: {str(e)}'
                response_data = {
                    'error': error_message,
                    'response_text': response.text
                }
                return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # Los datos no son válidos, devuelve un error de validación
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_or_refresh_access_token(self, client_id, client_secret, refresh_token):
        # Endpoint de Zoho Desk para la renovación del token
        token_refresh_url = 'https://accounts.zoho.com/oauth/v2/token'

        # Parámetros para la solicitud de renovación del token
        refresh_payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }

        try:
            # Realizar la solicitud para renovar el token
            response = requests.post(token_refresh_url, data=refresh_payload)
            response.raise_for_status()

            # Extraer el nuevo token de acceso desde la respuesta
            new_access_token = response.json().get('access_token')

            # Devolver el nuevo token de acceso
            return new_access_token

        except requests.RequestException as e:
            # Manejar errores de solicitud
            error_message = f'Error al renovar el token: {str(e)}'
            raise Exception(error_message) from e
