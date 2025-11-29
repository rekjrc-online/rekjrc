gunicorn
--chdir /opt/rekjrc/django --workers 1 \
--access-logfile /opt/rekjrc/django/logs/access.log \
--error-logfile /opt/rekjrc/django/logs/error.log \
--capture-output /opt/rekjrc/django/logs/capture.log \
rekjrc.wsgi:application