test:
	flake8 . --max-line-length=120 --exclude=.git,*/migrations/*,*/static/*
	coverage run --source='main,dlogr_api' --omit='*tests*,*commands*,*migrations*,*admin*,*config*,*wsgi*,*apps*' ./manage.py test main${ARGS}
	coverage report

serve:
	./manage.py runserver${ARGS}

shell:
	./manage.py shell${ARGS}

doc:
	DLOGR_DOCMAKER=1 ./manage.py test main.docmaker
