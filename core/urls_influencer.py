from django.urls import path
from .views_influencer import (
    influencer_signup_view,
    influencer_verify_email_view,
    influencer_dashboard_view,
    influencer_task_create_view,
    influencer_task_list_view,
    influencer_task_detail_view,
    influencer_proofs_view,
    influencer_approve_proof_view,
)

urlpatterns = [
    path('signup/', influencer_signup_view, name='influencer_signup'),
    path('verify-email/', influencer_verify_email_view, name='influencer_verify_email'),
    path('dashboard/', influencer_dashboard_view, name='influencer_dashboard'),
    path('tasks/', influencer_task_list_view, name='influencer_task_list'),
    path('tasks/create/', influencer_task_create_view, name='influencer_task_create'),
    path('tasks/<int:task_id>/', influencer_task_detail_view, name='influencer_task_detail'),
    path('proofs/', influencer_proofs_view, name='influencer_proofs'),
    path('proofs/<int:proof_id>/approve/', influencer_approve_proof_view, name='influencer_approve_proof'),
]
