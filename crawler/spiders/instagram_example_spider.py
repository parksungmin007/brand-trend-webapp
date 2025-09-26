
# TODO: 인스타그램은 공식 API/Graph API 혹은 사업자/개발자 정책 준수 필요.
# 비공식 크롤링은 차단/약관 이슈가 있을 수 있습니다. 정책을 반드시 확인하세요.

import scrapy

class ExampleSpider(scrapy.Spider):
    name = "example_brand"
    start_urls = ["https://example.com/brands"]

    def parse(self, response):
        yield {"brand": "A", "text": "샘플 텍스트", "url": response.url}
