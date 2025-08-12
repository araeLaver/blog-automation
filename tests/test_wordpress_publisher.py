"""
WordPress 발행 모듈 테스트
"""

import pytest
import json
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
from src.publishers.wordpress_publisher import WordPressPublisher


class TestWordPressPublisher:
    def setup_method(self):
        """테스트 초기화"""
        with patch.dict('os.environ', {
            'UNPRE_URL': 'https://unpre.co.kr',
            'UNPRE_USERNAME': 'test_user',
            'UNPRE_PASSWORD': 'test_pass'
        }):
            self.publisher = WordPressPublisher('unpre')
        
        # 테스트용 콘텐츠
        self.test_content = {
            "title": "테스트 포스트 제목",
            "meta_description": "테스트 포스트의 메타 설명입니다.",
            "introduction": "이것은 테스트 포스트의 서론입니다.",
            "sections": [
                {
                    "heading": "첫 번째 섹션",
                    "content": "첫 번째 섹션의 내용입니다."
                },
                {
                    "heading": "두 번째 섹션", 
                    "content": "두 번째 섹션의 내용입니다."
                }
            ],
            "conclusion": "테스트 포스트의 결론입니다.",
            "tags": ["테스트", "블로그"],
            "keywords": ["테스트", "워드프레스"],
            "categories": ["개발"]
        }
        
        # 테스트용 이미지
        self.test_images = [
            {
                "type": "thumbnail",
                "url": "/test/image1.jpg",
                "alt": "테스트 이미지 1"
            },
            {
                "type": "content",
                "url": "https://example.com/image2.jpg",
                "alt": "테스트 이미지 2"
            }
        ]
    
    @patch('requests.get')
    def test_connection_success(self, mock_get):
        """API 연결 성공 테스트"""
        mock_get.return_value = Mock(status_code=200)
        
        result = self.publisher.test_connection()
        
        assert result is True
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_connection_failure(self, mock_get):
        """API 연결 실패 테스트"""
        mock_get.return_value = Mock(status_code=401)
        
        result = self.publisher.test_connection()
        
        assert result is False
    
    @patch('requests.post')
    def test_publish_post_success(self, mock_post):
        """포스트 발행 성공 테스트"""
        # Mock responses
        mock_responses = [
            Mock(status_code=201, json=lambda: {"id": 123}),  # 미디어 업로드
            Mock(status_code=200, json=lambda: [{"id": 1, "name": "개발"}]),  # 카테고리 조회
            Mock(status_code=200, json=lambda: []),  # 태그 조회
            Mock(status_code=201, json=lambda: {"id": 456, "link": "https://unpre.co.kr/test-post"})  # 포스트 생성
        ]
        mock_post.side_effect = mock_responses
        
        # 파일 읽기 Mock
        with patch('builtins.open', mock_open(read_data=b'test image data')):
            with patch('pathlib.Path.exists', return_value=True):
                result, url = self.publisher.publish_post(self.test_content, self.test_images)
        
        assert result is True
        assert "unpre.co.kr" in url
        assert mock_post.call_count >= 2  # 최소 미디어 + 포스트
    
    @patch('requests.get')
    def test_load_categories(self, mock_get):
        """카테고리 로드 테스트"""
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: [
                {"id": 1, "name": "개발"},
                {"id": 2, "name": "IT"}
            ]
        )
        
        self.publisher._load_categories()
        
        assert self.publisher._categories_cache is not None
        assert len(self.publisher._categories_cache) == 2
        assert self.publisher._categories_cache[0]["name"] == "개발"
    
    @patch('requests.post')
    def test_create_category(self, mock_post):
        """카테고리 생성 테스트"""
        mock_post.return_value = Mock(
            status_code=201,
            json=lambda: {"id": 3, "name": "새 카테고리"}
        )
        
        result = self.publisher._create_category("새 카테고리")
        
        assert result == 3
        mock_post.assert_called_once()
    
    @patch('requests.post')
    @patch('requests.get')  
    def test_get_or_create_categories(self, mock_get, mock_post):
        """카테고리 조회/생성 통합 테스트"""
        # 기존 카테고리 조회
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: [{"id": 1, "name": "개발"}]
        )
        
        # 새 카테고리 생성
        mock_post.return_value = Mock(
            status_code=201,
            json=lambda: {"id": 2, "name": "AI"}
        )
        
        result = self.publisher._get_or_create_categories(["개발", "AI"])
        
        assert len(result) == 2
        assert 1 in result  # 기존 카테고리
        assert 2 in result  # 새로 생성된 카테고리
    
    @patch('requests.post')
    def test_upload_media_local_file(self, mock_post):
        """로컬 이미지 업로드 테스트"""
        mock_post.return_value = Mock(
            status_code=201,
            json=lambda: {"id": 123, "source_url": "https://example.com/uploaded.jpg"}
        )
        
        test_image = {"url": "/test/image.jpg", "alt": "테스트"}
        
        with patch('builtins.open', mock_open(read_data=b'image data')):
            with patch('pathlib.Path.exists', return_value=True):
                result = self.publisher._upload_media(test_image)
        
        assert result == 123
    
    @patch('requests.get')
    @patch('requests.post')
    def test_upload_media_remote_url(self, mock_post, mock_get):
        """원격 이미지 업로드 테스트"""
        # 이미지 다운로드
        mock_get.return_value = Mock(content=b'remote image data')
        
        # 미디어 업로드
        mock_post.return_value = Mock(
            status_code=201,
            json=lambda: {"id": 124}
        )
        
        test_image = {"url": "https://example.com/remote.jpg", "alt": "원격 이미지"}
        result = self.publisher._upload_media(test_image)
        
        assert result == 124
        mock_get.assert_called_once_with("https://example.com/remote.jpg")
    
    def test_format_content(self):
        """콘텐츠 HTML 포맷팅 테스트"""
        image_ids = [123, 124]
        
        html = self.publisher._format_content(self.test_content, image_ids)
        
        # HTML 구조 검증
        assert "<p>이것은 테스트 포스트의 서론입니다.</p>" in html
        assert "<h2>첫 번째 섹션</h2>" in html
        assert "<h2>두 번째 섹션</h2>" in html
        assert "<h2>마무리</h2>" in html
        assert "[gallery ids=" in html
    
    @patch('requests.post')
    def test_update_post(self, mock_post):
        """포스트 업데이트 테스트"""
        mock_post.return_value = Mock(status_code=200)
        
        updates = {"title": "업데이트된 제목"}
        result = self.publisher.update_post(123, updates)
        
        assert result is True
    
    @patch('requests.get')
    def test_get_recent_posts(self, mock_get):
        """최근 포스트 조회 테스트"""
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: [
                {
                    "id": 1,
                    "title": {"rendered": "포스트 1"},
                    "link": "https://example.com/post-1",
                    "date": "2024-01-01T00:00:00"
                },
                {
                    "id": 2,
                    "title": {"rendered": "포스트 2"},
                    "link": "https://example.com/post-2", 
                    "date": "2024-01-02T00:00:00"
                }
            ]
        )
        
        posts = self.publisher.get_recent_posts(2)
        
        assert len(posts) == 2
        assert posts[0]["title"] == "포스트 1"
        assert posts[1]["title"] == "포스트 2"
    
    @patch('requests.delete')
    def test_delete_post(self, mock_delete):
        """포스트 삭제 테스트"""
        mock_delete.return_value = Mock(status_code=200)
        
        result = self.publisher.delete_post(123, force=True)
        
        assert result is True
        mock_delete.assert_called_once()
    
    def test_invalid_credentials(self):
        """잘못된 인증 정보 테스트"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError):
                WordPressPublisher('invalid_site')
    
    @patch('requests.post')
    def test_publish_draft(self, mock_post):
        """초안 저장 테스트"""
        mock_post.return_value = Mock(
            status_code=201,
            json=lambda: {"id": 123, "link": "https://example.com/draft"}
        )
        
        result, url = self.publisher.publish_post(self.test_content, draft=True)
        
        # 초안으로 저장되었는지 확인
        call_args = mock_post.call_args
        post_data = json.loads(call_args[1]['data'])
        assert post_data['status'] == 'draft'
    
    @patch('requests.post')
    def test_api_error_handling(self, mock_post):
        """API 에러 처리 테스트"""
        mock_post.return_value = Mock(
            status_code=400,
            text="Bad Request"
        )
        
        result, error = self.publisher.publish_post(self.test_content)
        
        assert result is False
        assert "발행 실패" in error
        assert "400" in error
    
    def test_content_validation(self):
        """콘텐츠 검증 테스트"""
        # 필수 필드가 없는 콘텐츠
        invalid_content = {"meta_description": "설명만 있음"}
        
        # 실제로는 publish_post에서 KeyError가 발생할 것
        # 이를 적절히 처리하도록 개선 필요
        result, error = self.publisher.publish_post(invalid_content)
        assert result is False