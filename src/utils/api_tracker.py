"""
API 사용 내역 추적 시스템
Claude API 사용량과 비용을 실시간으로 추적하고 기록
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import os

class APITracker:
    def __init__(self, db_path: str = "data/api_usage.db"):
        """API 추적기 초기화"""
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # Claude API 가격 (1M 토큰당)
        self.pricing = {
            "claude-3-opus": {"input": 15.0, "output": 75.0},
            "claude-3-sonnet": {"input": 3.0, "output": 15.0},
            "claude-3-haiku": {"input": 0.25, "output": 1.25},
            "claude-3.5-sonnet": {"input": 3.0, "output": 15.0}
        }
    
    def _init_database(self):
        """데이터베이스 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # API 사용 내역 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    service TEXT NOT NULL,
                    model TEXT NOT NULL,
                    endpoint TEXT,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    total_tokens INTEGER,
                    cost_usd REAL,
                    site TEXT,
                    purpose TEXT,
                    success BOOLEAN,
                    error_message TEXT,
                    metadata TEXT
                )
            """)
            
            # 일별 집계 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_usage (
                    date TEXT PRIMARY KEY,
                    total_requests INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    total_cost_usd REAL DEFAULT 0,
                    by_service TEXT,
                    by_site TEXT,
                    updated_at TEXT
                )
            """)
            
            conn.commit()
    
    def log_api_call(self, 
                     service: str,
                     model: str,
                     input_tokens: int,
                     output_tokens: int,
                     site: str = None,
                     purpose: str = None,
                     success: bool = True,
                     error_message: str = None,
                     endpoint: str = None,
                     metadata: Dict = None) -> float:
        """API 호출 기록"""
        
        # 총 토큰 수 계산
        total_tokens = input_tokens + output_tokens
        
        # 비용 계산 (USD)
        model_key = model.lower()
        cost = 0.0
        
        # 모델명 매칭
        if "opus" in model_key:
            pricing = self.pricing["claude-3-opus"]
        elif "sonnet" in model_key:
            pricing = self.pricing.get("claude-3.5-sonnet", self.pricing["claude-3-sonnet"])
        elif "haiku" in model_key:
            pricing = self.pricing["claude-3-haiku"]
        else:
            pricing = self.pricing["claude-3-sonnet"]  # 기본값
        
        # 비용 계산 (토큰 수 / 1,000,000 * 가격)
        cost = (input_tokens / 1_000_000 * pricing["input"]) + \
               (output_tokens / 1_000_000 * pricing["output"])
        
        # 데이터베이스에 기록
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO api_usage (
                    timestamp, service, model, endpoint, input_tokens, 
                    output_tokens, total_tokens, cost_usd, site, purpose, 
                    success, error_message, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                service,
                model,
                endpoint,
                input_tokens,
                output_tokens,
                total_tokens,
                cost,
                site,
                purpose,
                success,
                error_message,
                json.dumps(metadata) if metadata else None
            ))
            
            # 일별 집계 업데이트
            today = datetime.now().date().isoformat()
            self._update_daily_usage(cursor, today, service, site, cost, total_tokens)
            
            conn.commit()
        
        # 콘솔에 출력
        print(f"\n💰 API 사용 기록:")
        print(f"   - 서비스: {service}")
        print(f"   - 모델: {model}")
        print(f"   - 입력 토큰: {input_tokens:,}")
        print(f"   - 출력 토큰: {output_tokens:,}")
        print(f"   - 총 토큰: {total_tokens:,}")
        print(f"   - 비용: ${cost:.4f} USD")
        if site:
            print(f"   - 사이트: {site}")
        if purpose:
            print(f"   - 용도: {purpose}")
        if not success:
            print(f"   ❌ 실패: {error_message}")
        
        return cost
    
    def _update_daily_usage(self, cursor, date: str, service: str, site: str, cost: float, tokens: int):
        """일별 사용량 업데이트"""
        
        # 기존 데이터 조회
        cursor.execute("SELECT * FROM daily_usage WHERE date = ?", (date,))
        existing = cursor.fetchone()
        
        if existing:
            # 업데이트
            cursor.execute("""
                UPDATE daily_usage 
                SET total_requests = total_requests + 1,
                    total_tokens = total_tokens + ?,
                    total_cost_usd = total_cost_usd + ?,
                    updated_at = ?
                WHERE date = ?
            """, (tokens, cost, datetime.now().isoformat(), date))
        else:
            # 새로 추가
            by_service = {service: {"requests": 1, "tokens": tokens, "cost": cost}}
            by_site = {site: {"requests": 1, "tokens": tokens, "cost": cost}} if site else {}
            
            cursor.execute("""
                INSERT INTO daily_usage (
                    date, total_requests, total_tokens, total_cost_usd, 
                    by_service, by_site, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                date, 1, tokens, cost,
                json.dumps(by_service),
                json.dumps(by_site),
                datetime.now().isoformat()
            ))
    
    def get_today_usage(self) -> Dict:
        """오늘의 사용량 조회"""
        today = datetime.now().date().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 오늘 총 사용량
            cursor.execute("""
                SELECT COUNT(*) as count, 
                       SUM(total_tokens) as tokens,
                       SUM(cost_usd) as cost
                FROM api_usage
                WHERE DATE(timestamp) = ?
            """, (today,))
            
            result = cursor.fetchone()
            
            # 서비스별 집계
            cursor.execute("""
                SELECT service, 
                       COUNT(*) as count,
                       SUM(total_tokens) as tokens,
                       SUM(cost_usd) as cost
                FROM api_usage
                WHERE DATE(timestamp) = ?
                GROUP BY service
            """, (today,))
            
            by_service = {}
            for row in cursor.fetchall():
                by_service[row[0]] = {
                    "requests": row[1],
                    "tokens": row[2] or 0,
                    "cost": row[3] or 0
                }
            
            # 사이트별 집계
            cursor.execute("""
                SELECT site, 
                       COUNT(*) as count,
                       SUM(total_tokens) as tokens,
                       SUM(cost_usd) as cost
                FROM api_usage
                WHERE DATE(timestamp) = ? AND site IS NOT NULL
                GROUP BY site
            """, (today,))
            
            by_site = {}
            for row in cursor.fetchall():
                by_site[row[0]] = {
                    "requests": row[1],
                    "tokens": row[2] or 0,
                    "cost": row[3] or 0
                }
            
            return {
                "date": today,
                "total_requests": result[0] or 0,
                "total_tokens": result[1] or 0,
                "total_cost_usd": result[2] or 0,
                "by_service": by_service,
                "by_site": by_site
            }
    
    def get_monthly_usage(self) -> Dict:
        """이번 달 사용량 조회"""
        month_start = datetime.now().replace(day=1).date().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) as count,
                       SUM(total_tokens) as tokens,
                       SUM(cost_usd) as cost
                FROM api_usage
                WHERE DATE(timestamp) >= ?
            """, (month_start,))
            
            result = cursor.fetchone()
            
            # 일별 추이
            cursor.execute("""
                SELECT DATE(timestamp) as date,
                       COUNT(*) as count,
                       SUM(cost_usd) as cost
                FROM api_usage
                WHERE DATE(timestamp) >= ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            """, (month_start,))
            
            daily_trend = []
            for row in cursor.fetchall():
                daily_trend.append({
                    "date": row[0],
                    "requests": row[1],
                    "cost": row[2] or 0
                })
            
            return {
                "month": datetime.now().strftime("%Y-%m"),
                "total_requests": result[0] or 0,
                "total_tokens": result[1] or 0,
                "total_cost_usd": result[2] or 0,
                "daily_trend": daily_trend,
                "days_in_month": len(daily_trend),
                "avg_daily_cost": (result[2] or 0) / max(len(daily_trend), 1)
            }
    
    def get_recent_calls(self, limit: int = 10) -> List[Dict]:
        """최근 API 호출 내역 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT timestamp, service, model, input_tokens, output_tokens,
                       cost_usd, site, purpose, success, error_message
                FROM api_usage
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            calls = []
            for row in cursor.fetchall():
                calls.append({
                    "timestamp": row[0],
                    "service": row[1],
                    "model": row[2],
                    "input_tokens": row[3],
                    "output_tokens": row[4],
                    "cost_usd": row[5],
                    "site": row[6],
                    "purpose": row[7],
                    "success": row[8],
                    "error_message": row[9]
                })
            
            return calls
    
    def export_report(self, output_file: str = None) -> str:
        """사용 내역 리포트 생성"""
        if not output_file:
            output_file = f"data/api_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        today_usage = self.get_today_usage()
        monthly_usage = self.get_monthly_usage()
        recent_calls = self.get_recent_calls(50)
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "today": today_usage,
            "month": monthly_usage,
            "recent_calls": recent_calls
        }
        
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 API 사용 리포트 생성: {output_file}")
        print(f"   - 오늘 요청: {today_usage['total_requests']}건")
        print(f"   - 오늘 비용: ${today_usage['total_cost_usd']:.4f}")
        print(f"   - 이번달 요청: {monthly_usage['total_requests']}건")
        print(f"   - 이번달 비용: ${monthly_usage['total_cost_usd']:.2f}")
        
        return output_file


# 전역 인스턴스
api_tracker = APITracker()