# from app.services import VectorSearchAPIWrapper
# import pytest
# from urllib.parse import urlparse
# # from aws import S3Manager
# vector_search_api_wrapper = VectorSearchAPIWrapper()
# s3_manager = S3Manager(region_name="ap-northeast-2", bucket_name="sw-fashion-image-data")
# @pytest.fixture
# def get_url():
#     url = "https://sw-fashion-image-data.s3.amazonaws.com/TOP/1002/4989731/segment/4989731_seg_001.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIAQKZOLTDIWQ2I6NZF%2F20250910%2Fap-northeast-2%2Fs3%2Faws4_request&X-Amz-Date=20250910T093427Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEID%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaDmFwLW5vcnRoZWFzdC0yIkgwRgIhAPjdww0h2s8HleSmJ%2FMo6tMtzkDSw1QZJNDX51z0Xh7GAiEA1l4KXipN%2BG2P0nC6XCTT6W8d9GR031tXN8oTolbzxmkq1QUI6f%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgwwMjMxODI2NzgyMjUiDL2jb7WfrJB1SXztDSqpBd%2FG%2B3ynufpnbj6P%2BA9rCgjFq0EYwq96VLM04sbFSMAbmZ1o2caDfpBwoVsujEJRmzC50vv19iRGilKq6Lerg0bUbVPncaVolMzUKtuVpPxhFyrmElEnaaAZbdS%2FiRAryIuw9%2B2KU1JrUY8QcXERGI4UENjdDsBnSEWYI7OqbTXJ4VvUHafJJbTV1Whcf9oFEj6T6hW8zkp80MVde0LXpzBnbs%2BQtE%2BaSK%2FNsTW3LLCWrPbQt%2FQYzmt4A7gKxbE9uGesWzLUFqgmcnUaV3rplZ%2Fvo3gab0l1Em9p44xV8IYWNLqBB5I5j26OUxYFPIoq4d1kfJiIGN8DrSuZghQF6JP7izY15KxmGE%2BD2r7JSCRPJBAXhPqRam0G%2BdyicvXwe8wJzNyopX%2BMK%2FgBfsDbEf%2FZYH7UTSZKi7cxXk7fG48YDJKWt2OZayrPTROB7zKQhbcxqcNAp94%2BmWghY6N5o0k5eiUAjdlhJfIiYOnajiLPbni0Fxmmovc6%2FEqn68kPECJBojcGlyD5Sk7n%2Bxo7K0c1Wx0r%2B4bplrpICIfZSpGHRdoNTImuipfal6WY%2FntNBUNqXjUGHNKH%2Beyjq524uiDhpBa4KwZ7O4xluFSuf0SOlNa2%2BFfkQxE3RNLUsBJELq4pIs4gA5LDLw6n2BInYvVruVq%2BLk9oe2Qgz5l8Tcsn03g%2F0rFOE2oSo%2BXrUCekz975Z2%2Bopa6fUhtXQOp4CazIPswZwV1YLLFKkenSMzisRAsvyXQgl1ja1TE9gZKwJXr9Z%2FdwJWB8oL0lxpZX6p7wSdQAYFBSlkGCkhcqnHPc3%2BuHcpfGpSYv0mC%2BQUmhAEmtXXL1SmAuTbWPh2IXIxtW1%2Fe33mDvBI5fOOXgnDfJcI2haiWGXMBej2k5PrbUVhkjCNg%2FwtHvUTD42YTGBjqwASdsMvGw6RbyVPnABUmbNpjWatGf2qGyOBbIkN3bB2eYT4zFmElgZMYUtzks80fYVu6aV7RfBLT%2BOunbPVpo%2Fyjt3yhhgEZ2EbtoJ5415cymt6BjarFOkwVbYxF4ZrTT4GpKTgDIakD2LSkFeaAj7M8bjwW0BofxovsmxEmGIjWwTuOClJFoPMGiutFsl6DnU2upoxm9DAYromRiBpcpr%2BB44MqWzBC5ahXL2Czxrpaa&X-Amz-Signature=54a9314d367aaa299d66674dc0154a50e7a85d564b856fefcd0a35daa81a2526"
#     return url

# @pytest.mark.asyncio
# async def test_vector_search():
#     result:dict = await vector_search_api_wrapper.search("test")

#     print(result)


# def parse_s3_key(url_string: str) -> str:
#     """
#     Parses an S3 URL to extract the key.
    
#     Args:
#         url_string: The full S3 URL string, including bucket and query parameters.
    
#     Returns:
#         The S3 key as a string.
#     """
#     # Parse the URL into components
#     parsed_url = urlparse(url_string)
    
#     # The S3 key is the path, which starts with a '/'
#     s3_key_with_leading_slash = parsed_url.path
    
    
#     # Remove the leading '/'
#     s3_key = s3_key_with_leading_slash.lstrip('/')

#     return s3_key

# def test_parse_s3_key(get_url):
#     s3_key = parse_s3_key(get_url)
#     print(s3_key)
#     print(s3_manager.generate_presigned_url(s3_key))

