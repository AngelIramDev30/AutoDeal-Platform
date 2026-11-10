cd "C:\Users\Angel\Documents\autos_app"
.\venv\Scripts\Activate.ps1
uvicorn servidor.main:app --reload

cd "C:\Users\Angel\Documents\autos_app"
.\venv\Scripts\Activate.ps1
python -m cliente.main

se ocupa corren en 2 terminales diferentes