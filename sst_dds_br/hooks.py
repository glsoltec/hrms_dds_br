app_name = "sst_dds_br"
app_title = "SST DDS BR"
app_publisher = "GL SOLTEC"
app_description = "Registros de Saude e Seguranca do Trabalho"
app_email = "dev@glsoltec.com.br"
app_license = "MIT"

required_apps = ["erpnext", "hrms"]

before_install = "sst_dds_br.setup.ensure_workflow_masters"
before_migrate = "sst_dds_br.setup.ensure_workflow_masters"

add_to_apps_screen = [
    {
        "name": "sst_dds_br",
        "logo": "/assets/sst_dds_br/images/sst-dds-br.svg",
        "title": "SST DDS BR",
        "route": "/desk/seguranca-do-trabalho",
    }
]

permission_query_conditions = {
    "DDS": "sst_dds_br.permissions.dds_query_conditions",
}

has_permission = {
    "DDS": "sst_dds_br.permissions.dds_has_permission",
}
