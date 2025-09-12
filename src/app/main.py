from fastapi import FastAPI 
from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from agents import get_all_agent_info  , get_agent
import logging 
import httpx
from app.services import MusinsaAPIWrapper
from memory.postgres import get_postgres_connection_pool
# from aws import S3Manager

from .api import router


logging.basicConfig(level=logging.INFO , format="%(asctime)s - %(levelname)s - %(message)s  [%(filename)s:%(lineno)d]" , datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app:FastAPI):
    logger.info("Starting up...")
    try:
        # 모든 agent의 memory 초기화
        async with get_postgres_connection_pool() as pool:
            logger.info("DB 연결 완료")
            checkpointer = AsyncPostgresSaver(pool)
            await checkpointer.setup()
            agent_names =  get_all_agent_info()
            agents = {}
            for agent_name in agent_names:
                agent = get_agent(agent_name)
                agent.checkpointer = checkpointer
                agents[agent_name] = agent
            app.state.agents = agents
            app.state.connection_pool = pool
        
            app.state.musinsa_service_wrapper = MusinsaAPIWrapper()
            # app.state.s3_manager = S3Manager() 
            app.state.http_session = httpx.AsyncClient()
            logger.info("Starting up... done")
            yield
        
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error starting up: {e}")
        raise e
    finally:
        # app.state.s3_manager.close_connection()
        if app.state.http_session:
            await app.state.http_session.aclose()
        logger.info("httpx.AsyncClient closed.")



app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(router)


