import uvicorn 
from dotenv import load_dotenv
from settings import settings

load_dotenv()

if __name__ == "__main__":
<<<<<<< HEAD
    uvicorn.run("app:app" , host=settings.HOST, port=settings.PORT, reload=settings.is_dev() , log_level="info" )
=======
    uvicorn.run("app:app" , host=settings.HOST, port=settings.PORT, reload=settings.is_dev() , log_level="info")
>>>>>>> 2df5b20 (sdsd)
