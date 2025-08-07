from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from .views import home,index,comport,probe,trace,parameter,master,measurebox,measurement,get_plc_status,write_coil,reset_counter
from .views import utility,report,spc,srno,withoutsrno,paraReport,jobReport,xBar,xBarRchart,backup,xBarSchart,shift_change_alert,get_time,save_time
from .views import histogram,pieChart,measure,masterReport,measurement_count,shift_report,get_parameters, get_parameter_value,zzz,post_part_status
urlpatterns = [
    path('',home,name="home"),
    path('index/',index,name="index"),
    path('comport/',comport,name="comport"),
    path('probe/',probe,name="probe"),
    path('trace/',trace,name="trace"),
    path('parameter/',parameter,name="parameter"),
    path('master/',master,name="master"),
    path('measurebox/',measurebox,name="measurebox"),
    path('measurement/',measurement,name="measurement"),
    path('utility/',utility,name="utility"),
    path('report/',report,name="report"),
    path('spc/',spc,name="spc"),
    path('srno/',srno,name="srno"),
    path('withoutsrno/',withoutsrno,name="withoutsrno"),
    path('paraReport/',paraReport,name="paraReport"),
    path('jobReport/',jobReport,name="jobReport"),
    path('xBar/',xBar,name="xBar"),
    path('xBarRchart/',xBarRchart,name="xBarRchart"),
    path('xBarSchart/',xBarSchart,name="xBarSchart"),
    path('histogram/',histogram,name="histogram"),
    path('pieChart/',pieChart,name="pieChart"),
    path('backup/',backup,name="backup"),
    path('measure/',measure,name="measure"),
    path('masterReport/',masterReport,name="masterReport"),
    path('measurement_count/',measurement_count,name="measurement_count"),
    path('shift_report/',shift_report,name="shift_report"), 
    path('get_parameters/', get_parameters, name='get_parameters'),
    path('get_parameter_value/', get_parameter_value, name='get_parameter_value'),
    path('zzz/', zzz, name='zzz'),
    path('get_plc_status/', get_plc_status, name='get_plc_status'),
    path('write_coil/', write_coil, name='write_coil'),
    path('post_part_status/', post_part_status, name='post_part_status'),
    path('shift_change_alert/', shift_change_alert, name='shift_change_alert'),
    path('get_time/', get_time, name='get_time'),
    path('save_time/', save_time, name='save_time'),
    path('reset_counter/', reset_counter, name='reset_counter'),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)