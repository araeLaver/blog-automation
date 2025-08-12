"""
고급 로깅 및 모니터링 시스템
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger
import functools
import time


class BlogAutomationLogger:
    def __init__(self, log_dir: str = "./data/logs"):
        """로거 초기화"""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Loguru 설정
        logger.remove()  # 기본 핸들러 제거
        
        # 콘솔 로그 (컬러링)
        logger.add(
            lambda msg: print(msg, end=''),
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            level="INFO",
            colorize=True
        )
        
        # 파일 로그 (일반)
        logger.add(
            self.log_dir / "automation.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="30 days",
            compression="zip"
        )
        
        # 에러 로그 (별도 파일)
        logger.add(
            self.log_dir / "errors.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="ERROR",
            rotation="5 MB",
            retention="60 days"
        )
        
        # 성과 추적 로그 (JSON)
        self.performance_log = self.log_dir / "performance.jsonl"
        
        # 통계 저장
        self.stats = {
            "posts_created": 0,
            "posts_published": 0,
            "images_generated": 0,
            "api_calls": 0,
            "errors": 0,
            "start_time": datetime.now().isoformat()
        }
    
    def info(self, message: str, **kwargs):
        """정보 로그"""
        logger.info(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """디버그 로그"""
        logger.debug(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """경고 로그"""
        logger.warning(message, **kwargs)
    
    def error(self, message: str, error: Exception = None, **kwargs):
        """에러 로그"""
        if error:
            logger.error(f"{message}: {str(error)}", **kwargs)
            logger.exception("Exception details:")
        else:
            logger.error(message, **kwargs)
        
        self.stats["errors"] += 1
    
    def success(self, message: str, **kwargs):
        """성공 로그 (INFO 레벨, 특별한 표시)"""
        logger.success(message, **kwargs)
    
    def log_performance(self, site: str, action: str, duration: float, 
                       success: bool = True, metadata: Dict[str, Any] = None):
        """성과 로그 기록"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "site": site,
            "action": action,
            "duration_seconds": round(duration, 3),
            "success": success,
            "metadata": metadata or {}
        }
        
        # JSON Lines 형식으로 저장
        with open(self.performance_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        # 통계 업데이트
        if action == "create_content":
            self.stats["posts_created"] += 1
        elif action == "publish_post":
            self.stats["posts_published"] += 1
        elif action == "generate_image":
            self.stats["images_generated"] += 1
        
        self.stats["api_calls"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """현재 통계 반환"""
        stats = self.stats.copy()
        stats["uptime_hours"] = (
            datetime.now() - datetime.fromisoformat(stats["start_time"])
        ).total_seconds() / 3600
        return stats
    
    def log_site_performance(self, site: str, metrics: Dict[str, Any]):
        """사이트별 성과 로그"""
        self.info(
            f"[{site.upper()}] Performance Metrics",
            site=site,
            posts_today=metrics.get("posts_today", 0),
            total_views=metrics.get("total_views", 0),
            revenue=metrics.get("revenue", 0),
            avg_engagement=metrics.get("avg_engagement", 0)
        )
        
        self.log_performance(
            site=site,
            action="daily_summary",
            duration=0,
            metadata=metrics
        )
    
    def create_daily_report(self) -> Dict[str, Any]:
        """일일 리포트 생성"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 오늘의 성과 로그 분석
        daily_stats = {
            "date": today,
            "total_posts": 0,
            "successful_posts": 0,
            "failed_posts": 0,
            "sites": {}
        }
        
        if self.performance_log.exists():
            with open(self.performance_log, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        entry_date = entry["timestamp"][:10]
                        
                        if entry_date == today:
                            site = entry["site"]
                            if site not in daily_stats["sites"]:
                                daily_stats["sites"][site] = {
                                    "posts": 0,
                                    "success": 0,
                                    "errors": 0,
                                    "avg_duration": 0
                                }
                            
                            if entry["action"] == "publish_post":
                                daily_stats["total_posts"] += 1
                                daily_stats["sites"][site]["posts"] += 1
                                
                                if entry["success"]:
                                    daily_stats["successful_posts"] += 1
                                    daily_stats["sites"][site]["success"] += 1
                                else:
                                    daily_stats["failed_posts"] += 1
                                    daily_stats["sites"][site]["errors"] += 1
                    
                    except (json.JSONDecodeError, KeyError):
                        continue
        
        # 리포트 저장
        report_file = self.log_dir / f"daily_report_{today}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(daily_stats, f, ensure_ascii=False, indent=2)
        
        return daily_stats
    
    def cleanup_old_logs(self, days: int = 30):
        """오래된 로그 파일 정리"""
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for log_file in self.log_dir.glob("*.log*"):
            if log_file.stat().st_mtime < cutoff_date:
                try:
                    log_file.unlink()
                    self.info(f"Cleaned up old log: {log_file.name}")
                except Exception as e:
                    self.error(f"Failed to cleanup {log_file.name}", e)


def timing_decorator(logger_instance: BlogAutomationLogger):
    """실행 시간 측정 데코레이터"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            result = None
            error = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error = e
                raise
            finally:
                duration = time.time() - start_time
                
                # 함수명과 클래스명 추출
                class_name = ""
                if args and hasattr(args[0], '__class__'):
                    class_name = args[0].__class__.__name__ + "."
                
                action = f"{class_name}{func.__name__}"
                
                # 사이트 정보 추출 (있는 경우)
                site = "unknown"
                if "site" in kwargs:
                    site = kwargs["site"]
                elif len(args) > 1 and isinstance(args[1], str):
                    site = args[1]
                
                logger_instance.log_performance(
                    site=site,
                    action=action,
                    duration=duration,
                    success=success,
                    metadata={"error": str(error) if error else None}
                )
                
                if success:
                    logger_instance.debug(
                        f"{action} completed in {duration:.3f}s"
                    )
                else:
                    logger_instance.error(
                        f"{action} failed after {duration:.3f}s: {error}"
                    )
        
        return wrapper
    return decorator


def setup_logger() -> BlogAutomationLogger:
    """글로벌 로거 설정"""
    return BlogAutomationLogger()


# 글로벌 로거 인스턴스
blog_logger = setup_logger()


# 편의 함수들
def log_info(message: str, **kwargs):
    """정보 로그 단축 함수"""
    blog_logger.info(message, **kwargs)


def log_error(message: str, error: Exception = None, **kwargs):
    """에러 로그 단축 함수"""
    blog_logger.error(message, error, **kwargs)


def log_success(message: str, **kwargs):
    """성공 로그 단축 함수"""
    blog_logger.success(message, **kwargs)


def timing(func):
    """실행 시간 측정 데코레이터 (글로벌 로거 사용)"""
    return timing_decorator(blog_logger)(func)