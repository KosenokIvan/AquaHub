# AquaHub Project

## How to run

 1. Install libraries
    
        pip install -r requirements.txt

 2. Create file jwt_key.py

 3. Run command

        openssl rand -hex 32

 4. Insert code to jwt_key.py:

```python
SECRET_KEY = "..." # key obtained in the previous step
```
    
 5. Run uvicorn
 
        uvicorn main:app --reload

## Documentation (when uvicorn is running)

 - <http://127.0.0.1:8000/docs>
