from fastapi import Depends , Request  , HTTPException
from langgraph.graph.state import CompiledStateGraph
from typing import Annotated , AsyncGenerator , Any
from app.services import MusinsaAPIWrapper , VectorSearchAPIWrapper
from psycopg import AsyncConnection


import logging

logger = logging.getLogger(__name__)

#===============================================================================================================
# 에이전트 관련 의존성 
#===============================================================================================================
def get_agents(request: Request , agent_name:str) -> CompiledStateGraph:
    logger.info(f"agent_name: {agent_name}")
    return request.app.state.agents[agent_name]


#===============================================================================================================
# Service 관련 의존성 
#===============================================================================================================
def get_musinsa_service(request: Request) -> MusinsaAPIWrapper:
    """
    MusinsaService의 싱글톤 인스턴스를 반환합니다.
    FastAPI의 의존성 주입에서 사용됩니다.
    """
    return request.app.state.musinsa_service_wrapper

#===============================================================================================================
# DB 관련 의존성 (Postgres 데이터베이스 연결)
#===============================================================================================================

#TODO : 에러 처리 다 따로 빼고 
async def get_db_connection(request: Request) -> AsyncGenerator[AsyncConnection, None]:
    async with request.app.state.connection_pool.connection() as conn:
        try:
            yield conn
        except Exception as e:
            logger.error(f"Error getting db connection: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
        
        
AgentDep = Annotated[CompiledStateGraph, Depends(get_agents)]
MusinsaServiceDep = Annotated[MusinsaAPIWrapper, Depends(get_musinsa_service)]
DBConnectionDep = Annotated[AsyncConnection, Depends(get_db_connection)]



VectorSearchAPIWrapperDep = Annotated[Any, Depends(VectorSearchAPIWrapper)]
