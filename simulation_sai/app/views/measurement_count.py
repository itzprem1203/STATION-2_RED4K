from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from app.models import MeasurementData
from collections import defaultdict
from django.db.models import Count

@csrf_exempt
def measurement_count(request):
    if request.method == 'POST':
        input_date = request.POST.get('date')
        input_shift = request.POST.get('shift')
        input_partModel = request.POST.get('part_model')

        print("Received Date:", input_date)
        print("Received Shift:", input_shift)
        print("Received partModel:", input_partModel)

        formatted_date = None
        if input_date:
            try:
                input_date_obj = datetime.strptime(input_date, '%Y/%m/%d %I:%M:%S %p')
                formatted_date = input_date_obj.date().strftime('%Y-%m-%d')
            except ValueError as e:
                print(f"Error parsing date: {e}")

        # ---- Query for aggregated counts (your original logic) ----
        filtered_data = (
            MeasurementData.objects
            .filter(part_model=input_partModel, date__date=formatted_date, shift=input_shift)
            .values('date', 'part_status')
            .annotate(count=Count('part_status'))
            .order_by('date')
        )

        print('your data for filtered data is this:', filtered_data)

        distinct_status_counts = defaultdict(int)
        status_with_datetime = defaultdict(list)
        last_occurrence = {'accept': None, 'reject': None, 'rework': None}
        total_occurrence = 0

        for entry in filtered_data:
            status = entry['part_status'].lower()
            date_time = entry['date']
            formatted_date_time = date_time.strftime('%d/%m/%Y %I:%M:%S %p')

            distinct_status_counts[status] += 1

            status_with_datetime[formatted_date_time].append({
                'status': status,
                'count': entry['count'],
                'occurrence': distinct_status_counts[status]
            })

            if status in last_occurrence:
                last_occurrence[status] = {
                    'formatted_date': formatted_date_time,
                    'count': entry['count'],
                    'occurrence': distinct_status_counts[status]
                }

        for status in ['accept', 'reject', 'rework']:
            occurrence = last_occurrence[status]
            if occurrence:
                total_occurrence += occurrence['occurrence']

        print("\nLast Occurrence for Each Status:")
        for status in ['accept', 'reject', 'rework']:
            occurrence = last_occurrence[status]
            if occurrence:
                print(f"{status.capitalize()} -> {occurrence}")
        print(f"\nTotal Occurrence: {total_occurrence}")

        # Get last 5 records
        last_five = (
            MeasurementData.objects
            .filter(part_model=input_partModel, date__date=formatted_date, shift=input_shift)
            .order_by('-date')[:5]   # get last 5 by date
        )
        print('Last five data:', last_five)

        # Check if all last 5 records are 'reject' (or whatever status you want)
        reject_in_last_five = all(obj.part_status.lower() == 'reject' for obj in last_five)

        notification_message = ""
        if reject_in_last_five and last_five:
            notification_message = "YOUR LAST 5 JOBS ARE REJECTED PLEASE CHECK"



        # ---- Prepare Response ----
        response_data = {
            'accept_occurrence': last_occurrence['accept']['occurrence'] if last_occurrence['accept'] else 0,
            'reject_occurrence': last_occurrence['reject']['occurrence'] if last_occurrence['reject'] else 0,
            'rework_occurrence': last_occurrence['rework']['occurrence'] if last_occurrence['rework'] else 0,
            'total_occurrence': total_occurrence,
            'notification': notification_message  # True if last 5 contain reject
        }

        return JsonResponse(response_data)

    return render(request, "app/measurement.html")
