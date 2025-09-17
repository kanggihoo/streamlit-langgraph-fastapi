from fastapi import Depends , Request  , HTTPException
from langgraph.graph.state import CompiledStateGraph
from typing import Annotated , AsyncGenerator , Any
from wrapper import MusinsaAPIWrapper , VectorSearchAPIWrapper
from psycopg import AsyncConnection
from aws import S3Manager


import logging

logger = logging.getLogger(__name__)

#===============================================================================================================
# 에이전트 관련 의존성 
#===============================================================================================================
def get_agent(request: Request , agent_name:str) -> CompiledStateGraph:
    if agent_name not in request.app.state.agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
    return request.app.state.agents[agent_name]

def get_agents(request: Request) -> dict[str, CompiledStateGraph]:
    return request.app.state.agents
#===============================================================================================================
# Service 관련 의존성 
#===============================================================================================================
def get_musinsa_service(request: Request) -> MusinsaAPIWrapper:
    """
    MusinsaService의 싱글톤 인스턴스를 반환합니다.
    FastAPI의 의존성 주입에서 사용됩니다.
    """
    return request.app.state.musinsa_service_wrapper
    
def get_s3_manager(request: Request) -> S3Manager:
    return request.app.state.s3_manager
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
        
        
AgentDep = Annotated[CompiledStateGraph, Depends(get_agent)]
MusinsaServiceDep = Annotated[MusinsaAPIWrapper, Depends(get_musinsa_service)]
DBConnectionDep = Annotated[AsyncConnection, Depends(get_db_connection)]
S3ManagerDep = Annotated[S3Manager, Depends(get_s3_manager)]



VectorSearchAPIWrapperDep = Annotated[Any, Depends(VectorSearchAPIWrapper)]
