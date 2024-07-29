from django import forms
from .models import TestSchedule,Board
from django.utils.translation import gettext_lazy

class EnvReportForm(forms.Form):
    CHOICES=[('Valkyrie','Valkyrie'),('Bishop','Bishop'),('Divo','Divo')]
    project_name_select_field=forms.ChoiceField(choices=CHOICES, label='Choose an project name')
    project_config=forms.CharField(label='输入项目配置',max_length=100)
    subproject_field=forms.CharField(label='输入Build阶段',max_length=100)
    env_report_file_field=forms.FileField(label='Upload a env file')

class EditTestPlanForm(forms.ModelForm):
    class Meta:
        model=TestSchedule
        fields=['test_sequence','cp_nums']
        labels = {
            "cp_nums": gettext_lazy("Check Points"),
            "test_sequence": gettext_lazy("Test Plan"),
        }
        widgets = {
            'cp_nums': forms.NumberInput(attrs={'readonly': 'readonly'}),
        }
        help_texts = {
            "test_sequence": gettext_lazy("目前仅支持修改测试计划。符号→"),
        }
        error_messages = {
            "test_sequence": {
                "test_sequence": gettext_lazy("测试计划的字符长度超过了限制。"),
            },
        }

class DisplayEditTestPlanForm(forms.ModelForm):
    class Meta:
        model=Board
        fields=['project_name','project_config','subproject_name','serial_number','board_number']
        labels = {
            "project_name": gettext_lazy("Project"),
            "project_config": gettext_lazy("Config"),
            "subproject_name": gettext_lazy("Build"),
            "serial_number": gettext_lazy("SN"),
            "board_number": gettext_lazy("Board NO."),
        }
        widgets = {
            'project_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'project_config': forms.TextInput(attrs={'readonly': 'readonly'}),
            'subproject_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'serial_number': forms.TextInput(attrs={'readonly': 'readonly'}),
            'board_number': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

# class MyForm(forms.Form):
#     CHOICES = [('A', 'Option A'), ('B', 'Option B'), ('C', 'Option C')]
    
#     select_field = forms.ChoiceField(choices=CHOICES, label='Choose an option')
#     input_field = forms.CharField(label='Enter some text', max_length=100)
#     file_field = forms.FileField(label='Upload a file')
