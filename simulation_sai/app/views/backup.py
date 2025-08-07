import os
import json
import psycopg2
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from app.models import BackupSettings  # Import your BackupSettings model
from threading import Thread
from datetime import datetime
import openpyxl
import time
import pyodbc


# Database credentials
db_name = 'CHECKDB'
db_host = 'SAC-GATE'

def backup(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        id_value = data.get('idValue')
        confirm_value = data.get('confirm')
        date_back = data.get('backup_date')
        print('Your changed id values are:', id_value, confirm_value, date_back)

        # Update the existing BackupSettings instance
        backup_setting = get_object_or_404(BackupSettings, id=id_value)
        backup_setting.backup_date = date_back
        backup_setting.confirm_backup = confirm_value
        backup_setting.save()

        # Create a new BackupSettings instance after 2 seconds
        Thread(target=create_new_backup_setting, args=(date_back, confirm_value)).start()

        return JsonResponse({'status': 'success', 'message': 'Backup settings updated and new entry will be created! and backup also saved in your downloads!'})

    return render(request, 'app/login.html')


def create_new_backup_setting(existing_backup_date, confirm_value):
    if confirm_value == 'True':  # Check if the backup is confirmed
        time.sleep(2)  # Delay for 2 seconds

        # Parse the existing backup date (ensure the input format is correct)
        existing_date = datetime.strptime(existing_backup_date, '%d-%m-%Y %I:%M:%S %p')

        # Call the backup function to save to .xlsx format
        backup_database_to_sql()

        # Calculate new backup date (same day, next month)
        new_month = existing_date.month + 1 if existing_date.month < 12 else 1
        new_year = existing_date.year if existing_date.month < 12 else existing_date.year + 1

        # Replace with the new month and year, keeping other components the same
        new_backup_date = existing_date.replace(month=new_month, year=new_year)

        # Format the new backup date to the desired format (dd-mm-yy hh:mm:ss AM/PM)
        formatted_new_backup_date = new_backup_date.strftime('%d-%m-%Y %I:%M:%S %p')

        # Print the new formatted backup date
        print('Your new backup_date is this:', formatted_new_backup_date)

        # Create a new BackupSettings record with the new date and confirm_backup set to False
        BackupSettings.objects.create(
            backup_date=formatted_new_backup_date,  # Save the formatted date
            confirm_backup=False  # Set confirm_backup to False for the new record
        )

def backup_database_to_sql():
    import pyodbc  # ensure this is imported
    main_backup_folder = r"C:\Program Files\Gauge_Logic\backup_files"
    os.makedirs(main_backup_folder, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_folder = os.path.join(main_backup_folder, f'backup_{timestamp}')
    os.makedirs(backup_folder, exist_ok=True)

    conn = None
    cursor = None
    try:
        # Correct ODBC connection string for SQL Server
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=SAC-GATE;"
            "DATABASE=CHECKDB;"
            "Trusted_Connection=yes;"  # Use this if using Windows Authentication
        )
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        models = [
            "app_probe_calibrations",
            "app_tableonedata",
            "app_tabletwodata",
            "app_tablethreedata",
            "app_tablefourdata",
            "app_tablefivedata",
            "app_comport_settings",
            "app_master_settings",
            "app_parameter_settings",
            "app_measurementdata",
            "app_masterintervalsettings",
            "app_shiftsettings",
            "app_measure_data",
            "app_customerdetails",
            "app_userlogin",
            "app_consolidate_with_srno",
            "app_consolidate_without_srno",
            "app_parameterwise_report",
            "app_jobwise_report",
            "app_resetcount",
            "app_x_bar_chart",
            "app_x_bar_r_chart",
            "app_x_bar_s_chart",
            "app_histogram_chart",
            "app_pie_chart",
            "app_backupsettings",
            "app_master_report",
            "app_parameterfactor",
        ]

        sql_file_path = os.path.join(backup_folder, f'database_backup_{timestamp}.sql')
        with open(sql_file_path, 'w', encoding='utf-8') as sql_file:
            sql_file.write("-- Database Backup SQL File\n")
            sql_file.write(f"-- Backup created on {timestamp}\n\n")

            for model in models:
                try:
                    cursor.execute(f'SELECT * FROM {model} ORDER BY id ASC;')
                    rows = cursor.fetchall()
                    column_names = [desc[0] for desc in cursor.description]

                    for row in rows:
                        values = []
                        for value in row:
                            if isinstance(value, str):
                                values.append(f"'{value.replace("'", "''")}'")
                            elif isinstance(value, datetime):
                                values.append(f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'")
                            elif value is None:
                                values.append('NULL')
                            else:
                                values.append(str(value))
                        sql_file.write(f"INSERT INTO {model} ({', '.join(column_names)}) VALUES ({', '.join(values)});\n")

                    sql_file.write("\n")
                except Exception as model_error:
                    print(f"Error backing up model {model}: {model_error}")
                    continue

        print(f"Backup saved to {sql_file_path}")

    except Exception as e:
        print(f"An error occurred while backing up the database: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
