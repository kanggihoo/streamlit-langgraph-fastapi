import datetime
from zoneinfo import ZoneInfo # Python 3.9+ 내장 라이브러리

def get_current_utc_timestamp() -> datetime.datetime:
    """
    현재 시간을 UTC 기준의 timezone-aware datetime 객체로 반환합니다.
    이 객체는 Pydantic과 psycopg2에서 추가 가공 없이 바로 사용할 수 있습니다.
    """
    return datetime.datetime.now(tz=ZoneInfo("UTC"))
# 함수 사용 예시
current_time = get_current_utc_timestamp()
print(f"생성된 시간 객체: {current_time}")
print(f"객체 타입: {type(current_time)}")


from pydantic import BaseModel, Field
import datetime
# 위에서 정의한 get_current_utc_timestamp 함수가 있다고 가정

class EventModel(BaseModel):
    event_name: str
    # Pydantic 모델에 datetime.datetime 타입으로 필드 정의
    created_at: datetime.datetime = Field(default_factory=get_current_utc_timestamp)

# Pydantic 모델 생성
event = EventModel(event_name="New User Signup")

# 1. Python 객체 확인
print(f"Pydantic 모델 내의 datetime 객체: {event.created_at}")

# 2. JSON으로 변환 (API 응답 시)
# model_dump_json()을 호출하면 datetime 객체가 ISO 8601 문자열로 자동 변환됩니다.
json_output = event.model_dump_json(indent=2)
print("\n--- API JSON 출력 ---")
print(json_output)