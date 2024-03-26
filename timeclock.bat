call venv\Scripts\activate.bat
call waitress-serve --port 5050 --threads 8 --call app:create_app