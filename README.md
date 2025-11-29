# django

To install/run locally using sqllite for database:

1.  git clone https://github.com/rekjrc-online/rekjrc.git
2.  cd rekjrc
3.  pip install -r requirements.txt
4.  copy .env.template to .env
5.  edit .env
6.  provide secret key at least 50 characters
7.  configure postgres db fields in .env
8.  edit /rekjrc/rekjrc/settings.py
    a. comment out either the sqllite block or the postgres block
    b. update ALLOWED_HOSTS
    c. update CSRF_TRUSTED_ORIGINS
9.  "migrate.bat" ("python manage.py migrate")
    or "migrate.sh" ("chmod +x migrate.sh")
10. runserver.bat / runserver.sh ("chmod +x runserver.sh")
    (runs "python manage.py runserver")
11. browse to http://localhost:8000

To run your localhost:8000 version live with Ngrok

1.  run ngrok.bat ("ngrok http 8000")
2.  copy the random domain name
    ex: https://d34f8c7e2d53.ngrok-free.app
3.  open /rekjrc/rekjrc/settings.py
4.  add to CSRF_TRUSTED_ORIGINS
    'https://d34f8c7e2d53.ngrok-free.app'
5.  add to ALLOWED_HOSTS
    'd34f8c7e2d53.ngrok-free.app'
6.  url should now work in a remote browser
