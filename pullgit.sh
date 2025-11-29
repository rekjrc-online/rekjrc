git fetch origin
git pull origin main
pip install -r ./requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
