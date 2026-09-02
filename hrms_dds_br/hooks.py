app_name = "hrms_dds_br"
app_title = "HRMS DDS BR"
app_publisher = "GL SOLTEC"
app_description = "Registros de Saude e Seguranca do Trabalho (DDS) integrados ao HRMS - Brasil"
app_email = "dev@glsoltec.com.br"
app_license = "mit"

required_apps = ["erpnext", "hrms"]

before_install = "hrms_dds_br.setup.ensure_workflow_masters"
before_migrate = "hrms_dds_br.setup.ensure_workflow_masters"

add_to_apps_screen = [
    {
        "name": "hrms_dds_br",
        "logo": "/assets/hrms_dds_br/images/hrms-dds-br.svg",
        "title": "HRMS DDS BR",
        "route": "/desk/seguranca-do-trabalho",
    }
]

# Permission hooks: aplicam o isolamento por participante/responsavel no DocType DDS.
permission_query_conditions = {
    "DDS": "hrms_dds_br.permissions.dds_query_conditions",
}

has_permission = {
    "DDS": "hrms_dds_br.permissions.dds_has_permission",
}

# Integracao HRMS: injeta o botao "Historico de DDS" no formulario do Employee.
doctype_js = {
    "Employee": "public/js/employee.js",
}

# Protecao de dados (LGPD): permite exportar/eliminar registros do titular.
user_data_fields = [
    {
        "doctype": "DDS",
        "filter_by": "responsible",
        "redact_fields": ["observations"],
        "partial": 1,
    },
    {
        "doctype": "DDS Participante",
        "filter_by": "employee",
        "partial": 1,
    },
]