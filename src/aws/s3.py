import boto3
import logging
from botocore.exceptions import ClientError
from pathlib import Path
from urllib.parse import urlparse
from .config import s3_config
logger = logging.getLogger(__name__)

class S3Manager:
    def __init__(self , region_name: str, bucket_name: str):
        self.region_name = region_name
        self.bucket_name = bucket_name
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        try:
            self.client = boto3.client('s3', region_name=self.region_name)
        except ClientError as e:
            logger.error(f"S3 클라이언트 초기화 실패: {e}")
            raise 
        logger.info(f"S3 클라이언트 초기화 완료: {self.bucket_name}")
    
    def test_connection(self) -> bool:
        
        if not self.client:
            return False
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError as e:
            logger.error(f"S3 연결 테스트 실패: {e}")
            return False
        except Exception as e:
            logger.error(f"S3 연결 테스트 예상치 못한 오류: {e}")
            return False
    
    
    def get_s3_object_key(self, main_category: str, sub_category: int, product_id: str, relative_path: str) -> str:
        '''
        S3 객체 키를 생성합니다.
        
        Args:
            main_category: 대분류
            sub_category: 소분류
            product_id: 제품 ID
            relative_path: 상대 경로 (예: 'detail/0.jpg', 'meta.json' , "segment/0.jpg")
        Returns:
            str: S3 객체 키 (예: 'main_category/sub_category/product_id/segment/0.jpg')
        '''
        return f"{main_category}/{sub_category}/{product_id}/{relative_path}"
    
    def generate_presigned_url(self, key: str, client_method: str="get_object", expires_in: int = 3600) -> str|None:
        try:
            response = self.client.generate_presigned_url(
                client_method,
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expires_in
            )
            return response
        except ClientError as e:
            logger.error(f"Presigned URL 생성 실패: {e}")
            return None
    def parse_s3_key(url_string: str) -> str:
        """
        pre signed url로 부터 S3 값 추출

        Returns: str: "main_category/sub_category/product_id/relative_path"
        """
        # Parse the URL into components
        parsed_url = urlparse(url_string)
        
        # The S3 key is the path, which starts with a '/'
        s3_key_with_leading_slash = parsed_url.path
        
        
        # Remove the leading '/'
        return s3_key_with_leading_slash.lstrip('/')
    
    def close_connection(self):
        if self.client:
            self.client.close()
            self.client = None
            logger.info(f"S3 클라이언트 연결 종료: {self.bucket_name}")

s3manager = S3Manager(**s3_config)


