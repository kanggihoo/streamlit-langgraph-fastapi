from fastapi import FastAPI 
from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from agents import get_all_agent_info  , get_graph_builder
import logging 
import httpx
from memory.postgres import get_postgres_connection_pool
from aws import S3Manager , s3_config

from .api import router


logging.basicConfig(level=logging.INFO , format="%(asctime)s - %(levelname)s - %(message)s  [%(filename)s:%(lineno)d]" , datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app:FastAPI):
    logger.info("Starting up...")
    try:
        # 비동기 클라이언트 초기화 
        app.state.http_session = httpx.AsyncClient()
        # 모든 agent의 memory 초기화
        #CHECK : 굳이 db 관련해서 with 구문으로 감싸지 않아도 될듯 
        async with get_postgres_connection_pool() as pool:
            logger.info("DB 연결 완료")
            checkpointer = AsyncPostgresSaver(pool)
            await checkpointer.setup()
            agent_names =  get_all_agent_info()
            agents = {}
            for agent_name in agent_names:
                builder = get_graph_builder(agent_name)
                agent = builder(app.state.http_session)
    
                agent.checkpointer = checkpointer
                agents[agent_name] = agent
            app.state.agents = agents
            app.state.connection_pool = pool
        

            app.state.s3_manager = S3Manager(**s3_config) 
            app.state.http_session = httpx.AsyncClient()
            logger.info("Starting up... done")
            yield
        
        logger.info("Shutting down...")
        logger.info("DB Connection Pool closed.")
    except Exception as e:
        logger.error(f"Error starting up: {e}")
        raise e
    finally:
        if hasattr(app.state, "s3_manager") and app.state.s3_manager:
            app.state.s3_manager.close_connection()
            logger.info("S3Manager closed.")
        if hasattr(app.state, "http_session") and app.state.http_session:
            await app.state.http_session.aclose()
            logger.info("httpx.AsyncClient closed.")



app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(router)


