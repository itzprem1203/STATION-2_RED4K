from collections import defaultdict
from datetime import datetime
import json
import threading
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render
import pytz
from django.utils import timezone  
from django.db.models import Q
import serial.tools.list_ports

from app.models import MasterIntervalSettings, MeasurementData, ParameterFactor, ResetCount, ShiftSettings,PunchData
from app.models import TableOneData, Master_settings, comport_settings, measure_data, parameter_settings,InterlinkData



def clearmeasurement(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            print("data:", data)
            form_id = data.get('id')
            print("form_id:", form_id)

            if form_id == 'punch_value':
                punch_value = data.get('punch_value')
                part_model = data.get('part_model_value')

                # Save or update single record
                punch_obj, created = PunchData.objects.update_or_create(
                    id=1,  # Force only one record
                    defaults={
                        'punch_value': punch_value,
                        'part_model': part_model,
                        'is_active': True
                    }
                )

                return JsonResponse({
                    'status': 'success',
                    'punch_value': punch_obj.punch_value if punch_obj.is_active else '',
                    'part_model': punch_obj.part_model,
                    'is_active': punch_obj.is_active
                })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Only if you are testing; otherwise keep CSRF token
def deactivate_punch(request):
    if request.method == 'POST':
        try:
            # Get the punch object, or create if it doesn't exist
            punch_obj, created = PunchData.objects.get_or_create(id=1)
            punch_obj.is_active = False
            punch_obj.save()
            return JsonResponse({'status': 'success', 'is_active': punch_obj.is_active})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)




from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from app.models import PunchData

@csrf_exempt
def get_active_punch(request):
    if request.method == 'GET':
        try:
            punch_obj = PunchData.objects.get(id=1)
            return JsonResponse({
                'status': 'success',
                'punch_value': punch_obj.punch_value if punch_obj.is_active else '',
                'is_active': punch_obj.is_active
            })
        except PunchData.DoesNotExist:
            return JsonResponse({'status': 'success', 'punch_value': '', 'is_active': False})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
