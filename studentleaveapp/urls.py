from django.urls import path
from . import views




urlpatterns = [
    path('',views.index,name='index'),
    path('registration/',views.registration,name='registration'),
    path('login/',views.login,name='login'),
    path('home/',views.home,name='home'),
    path('profile/',views.profile,name='profile'),
    path('logout/',views.logout,name='logout'),
    path('editprofile/',views.editprofile,name='editprofile'),
    path('adminlogin/',views.adminlogin,name='adminlogin'),
    
    path('userlist/',views.userlist,name='userlist'),
    path('leavelist/',views.leavelist,name='leavelist'),
    path('deleteuser/<int:id>',views.deleteuser,name='deleteuser'),
    path('apply-leave/', views.apply_leave, name='apply_leave'),
    path('approve/<int:id>',views.approve,name='approve'),
    path('rejected/<int:id>',views.rejected,name='rejected'),
    path('userleave/', views.userleave, name='userleave'),
    path('admin-remark/<int:leave_id>/', views.admin_remark, name='admin_remark'),
    path('submitcertificate/<int:id>', views.submitcertificate, name='submitcertificate'),
    path('medlist/',views.medlist,name='medlist'),
    path("my_leave/", views.user_leave_summary, name="user_leave_summary"),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    
    path('adminhome2/',views.adminhome2,name='adminhome2'),
    
    path('adminhome_software_dev/',views.adminhome_software_dev,name='adminhome_software_dev'),
    path('adminhome_multimedia/',views.adminhome_multimedia,name='adminhome_multimedia'),
    path('adminhome_ft/',views.adminhome_ft,name='adminhome_ft'),
    path('adminhome_at/',views.adminhome_at,name='adminhome_at'),
    
    
    path('userlist_sd/',views.userlist_sd,name='userlist_sd'),
    path('userlist_mm/',views.userlist_mm,name='userlist_mm'),
    path('userlist_ft/',views.userlist_ft,name='userlist_ft'),
    path('userlist_at/',views.userlist_at,name='userlist_at'),

    path('medlist_sd/',views.medlist_sd,name='medlist_sd'),
    path('medlist_mm/',views.medlist_mm,name='medlist_mm'),
    path('medlist_ft/',views.medlist_ft,name='medlist_ft'),
    path('medlist_at/',views.medlist_at,name='medlist_at'),


    path('leavelist_at/',views.leavelist_at,name='leavelist_at'),
    path('leavelist_mm/',views.leavelist_mm,name='leavelist_mm'),
    path('leavelist_sd/',views.leavelist_sd,name='leavelist_sd'),
    path('leavelist_ft/',views.leavelist_ft,name='leavelist_ft'),
    path("adminhome/", views.adminhome2, name="adminhome"), 
    path('leave/cancel/<int:leave_id>/', views.cancel_leave, name='cancel_leave'),
    path('my_leave_report_pdf_view/',views.my_leave_report_pdf_view, name='my_leave_report_pdf_view'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),

    ]
