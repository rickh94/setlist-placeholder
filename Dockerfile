FROM kennethreitz/pipenv

VOLUME /socks
WORKDIR /app
ADD ./setlist_placeholder /app/setlist_placeholder

CMD uwsgi -s /socks/setlist_placeholder.sock --gid $GID --umask 0117 --wsgi-file setlist_placeholder/wsgi.py --callable app
