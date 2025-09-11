import uvicorn 
from dotenv import load_dotenv
from settings import settings

load_dotenv()

if __name__ == "__main__":
    uvicorn.run("app:app" , host=settings.HOST, port=settings.PORT, reload=settings.is_dev() , log_level="info" , workers=4)