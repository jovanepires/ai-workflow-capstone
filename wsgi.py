import os
from app.api import create_app

app = create_app()

if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=os.getenv('PORT', 5000))
    except:
    	print("Server is exited unexpectedly. Please contact server admin.")
