from django.http import JsonResponse
from django.db import connection
import subprocess

def healthcheck(request):
    db_status = 'unknown'
    nginx_status = 'unknown'
    
    # Check database connection
    try:
        connection.ensure_connection()
        db_status = 'ok'
    except:
        db_status = 'error'

   
    # Check nginx status
    try:
        result = subprocess.run(['systemctl', 'is-active', 'nginx'], stdout=subprocess.PIPE)
        if result.stdout.decode('utf-8').strip() == 'active':
            nginx_status = 'ok'
        else:
            nginx_status = 'error'
    except:
        nginx_status = 'error'

    return JsonResponse({
        'nginx': nginx_status,
        'database': db_status,
        'django': 'ok',
    })

