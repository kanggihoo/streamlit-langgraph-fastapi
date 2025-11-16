from .config.config import Config
from .repository.fashion_async import AsyncFashionRepository

_config = Config()
_mongodb_atlas_config = _config.get_atlas_config()
_mongodb_atlas_sku_config = _config.get_atlas_sku_config()
_mongodb_local_config = _config.get_local_config()

# ===================================================================
# 비동기/FastAPI 환경을 위한 팩토리 함수
# ===================================================================


async def get_async_fashion_repo() -> AsyncFashionRepository:
    """
    [비동기] Atlas DB에 연결하는 비동기 Fashion Repository를 반환합니다.
    FastAPI와 같은 비동기 프레임워크에서 사용하기 위해 설계되었습니다.
    """
    repo = AsyncFashionRepository(
        connection_string=_mongodb_atlas_config['MONGODB_ATLAS_CONNECTION_STRING'],
        database_name=_mongodb_atlas_config['MONGODB_ATLAS_DATABASE_NAME'],
        collection_name=_mongodb_atlas_config['MONGODB_ATLAS_COLLECTION_NAME'],
    )
    await repo.connect()  # 비동기 연결 초기화
    return repo


async def get_async_fashion_sku_repo() -> AsyncFashionRepository:
    """
    [비동기] Atlas DB의 products_by_sku 컬렉션에 연결하는 비동기 Fashion Repository를 반환합니다.
    비정규화된 SKU 중심 데이터에 접근할 때 사용합니다.
    """
    repo = AsyncFashionRepository(
        connection_string=_mongodb_atlas_sku_config['MONGODB_ATLAS_CONNECTION_STRING'],
        database_name=_mongodb_atlas_sku_config['MONGODB_ATLAS_DATABASE_NAME'],
        collection_name=_mongodb_atlas_sku_config['MONGODB_ATLAS_COLLECTION_NAME'],
    )
    await repo.connect()  # 비동기 연결 초기화
    return repo



