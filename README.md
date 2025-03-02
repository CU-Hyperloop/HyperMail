# HyperMail

## To migrate the DB when you are updating the models do these commands:  
Create migrations:
```
docker exec -it backend python manage.py makemigrations app
```

Apply the migration:
```
docker exec -it backend python manage.py migrate
```
