# apprenticeship-tracker-and-site API

To launch this api locally, follow these steps:
    1. On line 80 of main.py change the host string to your local host - likely 127.0.0.1
    2. Run the main.py file, it should output at the top of the terminal "INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)"
    3. Navigate to that page on a browser and the api will be there.

If you want to launch via terminal, ensure the line is changed as stated above then run "uvicorn main:app --reload"
