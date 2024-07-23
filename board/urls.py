from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("smt/", views.smt, name="smt"),
    path("upload/", views.upload, name="upload"),
    path("get_env_report/", views.get_env_report, name="get_env_report"),
    path("checkout/", views.check_out, name="check_out"),
    path("checkin/", views.check_in, name="check_in"),
    path("checkin_ajax/<str:sn_str>/", views.checkin_ajax, name="checkin_ajax"),
    path("checkout_ajax/<str:sn_str>/", views.checkout_ajax, name="checkout_ajax"),
    path("enter_test_plan/", views.enter_test_plan, name="enter_test_plan"),
    path("search_test_plan/", views.search_test_plan, name="search_test_plan"),
    path("update_summary/", views.update_summary, name="update_summary"),
    path('edit_test_plan/<int:item_id>/', views.edit_test_plan, name='edit_test_plan'),
    path('show_history/<str:type>/', views.show_history, name='show_history'),
    path('eception_page/', views.eception_page, name='eception_page'),
    path('search_eception/', views.search_eception, name='search_eception'),
    path('create_error_record/', views.create_error_record, name='create_error_record'),
    path('edit_error_record/<int:error_record_id>/', views.edit_error_record, name='edit_error_record'),
    path('get_error_record/<int:error_record_serial_number>/', views.get_error_record, name='get_error_record'),
    path('update_error_record/<int:error_record_serial_number>/', views.update_error_record, name='update_error_record'),
    path('search_serial_number_in_eception_page/', views.search_serial_number_in_eception_page, name='search_serial_number_in_eception_page'),
]