"""
성능 최적화 유틸리티
메모리 관리, 실행 속도 최적화, 캐싱 등의 기능
"""
import time
import threading
import gc
import psutil
import os
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
from collections import OrderedDict


class PerformanceOptimizer:
    """성능 최적화 클래스"""
    
    def __init__(self):
        """초기화"""
        self.cache = OrderedDict()
        self.cache_size_limit = 100
        self.performance_metrics = {}
        self.optimization_enabled = True
    
    def enable_optimization(self, enabled: bool = True):
        """최적화 활성화/비활성화"""
        self.optimization_enabled = enabled
    
    def cache_result(self, max_age: int = 300):
        """
        함수 결과 캐싱 데코레이터
        
        Args:
            max_age: 캐시 유효 시간 (초)
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.optimization_enabled:
                    return func(*args, **kwargs)
                
                # 캐시 키 생성
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
                
                # 캐시에서 결과 확인
                if cache_key in self.cache:
                    cached_result, timestamp = self.cache[cache_key]
                    if time.time() - timestamp < max_age:
                        return cached_result
                    else:
                        # 만료된 캐시 제거
                        del self.cache[cache_key]
                
                # 함수 실행 및 결과 캐싱
                result = func(*args, **kwargs)
                self.cache[cache_key] = (result, time.time())
                
                # 캐시 크기 제한
                if len(self.cache) > self.cache_size_limit:
                    self.cache.popitem(last=False)
                
                return result
            
            return wrapper
        return decorator
    
    def measure_performance(self, func_name: str = None):
        """
        함수 성능 측정 데코레이터
        
        Args:
            func_name: 함수 이름 (None이면 자동 감지)
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                name = func_name or func.__name__
                start_time = time.time()
                start_memory = self.get_memory_usage()
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                except Exception as e:
                    result = None
                    success = False
                    raise e
                finally:
                    end_time = time.time()
                    end_memory = self.get_memory_usage()
                    
                    execution_time = end_time - start_time
                    memory_delta = end_memory - start_memory
                    
                    # 성능 메트릭 저장
                    if name not in self.performance_metrics:
                        self.performance_metrics[name] = {
                            "calls": 0,
                            "total_time": 0,
                            "avg_time": 0,
                            "min_time": float('inf'),
                            "max_time": 0,
                            "success_count": 0,
                            "error_count": 0,
                            "memory_usage": []
                        }
                    
                    metrics = self.performance_metrics[name]
                    metrics["calls"] += 1
                    metrics["total_time"] += execution_time
                    metrics["avg_time"] = metrics["total_time"] / metrics["calls"]
                    metrics["min_time"] = min(metrics["min_time"], execution_time)
                    metrics["max_time"] = max(metrics["max_time"], execution_time)
                    
                    if success:
                        metrics["success_count"] += 1
                    else:
                        metrics["error_count"] += 1
                    
                    metrics["memory_usage"].append(memory_delta)
                    if len(metrics["memory_usage"]) > 100:
                        metrics["memory_usage"] = metrics["memory_usage"][-100:]
                
                return result
            
            return wrapper
        return decorator
    
    def get_memory_usage(self) -> float:
        """현재 메모리 사용량 반환 (MB)"""
        try:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except Exception:
            return 0.0
    
    def get_system_memory_info(self) -> Dict[str, Any]:
        """시스템 메모리 정보 반환"""
        try:
            memory = psutil.virtual_memory()
            return {
                "total": memory.total / 1024 / 1024,  # MB
                "available": memory.available / 1024 / 1024,  # MB
                "used": memory.used / 1024 / 1024,  # MB
                "percent": memory.percent,
                "free": memory.free / 1024 / 1024  # MB
            }
        except Exception:
            return {}
    
    def optimize_memory(self):
        """메모리 최적화"""
        if not self.optimization_enabled:
            return
        
        try:
            # 가비지 컬렉션 실행
            collected = gc.collect()
            
            # 오래된 캐시 정리
            current_time = time.time()
            expired_keys = []
            
            for key, (_, timestamp) in self.cache.items():
                if current_time - timestamp > 600:  # 10분 이상 된 캐시
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
            
            print(f"메모리 최적화 완료: {collected}개 객체 수집, {len(expired_keys)}개 캐시 정리")
            
        except Exception as e:
            print(f"메모리 최적화 중 오류: {e}")
    
    def clear_cache(self):
        """캐시 완전 정리"""
        self.cache.clear()
        print("캐시가 정리되었습니다.")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """성능 리포트 반환"""
        report = {
            "memory_usage": self.get_memory_usage(),
            "system_memory": self.get_system_memory_info(),
            "cache_size": len(self.cache),
            "cache_hit_rate": self._calculate_cache_hit_rate(),
            "function_metrics": self.performance_metrics.copy(),
            "optimization_enabled": self.optimization_enabled
        }
        
        return report
    
    def _calculate_cache_hit_rate(self) -> float:
        """캐시 히트율 계산"""
        if not hasattr(self, '_cache_hits'):
            self._cache_hits = 0
            self._cache_misses = 0
        
        total = self._cache_hits + self._cache_misses
        return (self._cache_hits / total * 100) if total > 0 else 0.0
    
    def optimize_execution_speed(self, target_fps: int = 60):
        """
        실행 속도 최적화
        
        Args:
            target_fps: 목표 FPS
        """
        if not self.optimization_enabled:
            return
        
        try:
            # 스레드 우선순위 조정
            current_thread = threading.current_thread()
            if hasattr(current_thread, 'setPriority'):
                current_thread.setPriority(threading.Thread.MAX_PRIORITY)
            
            # CPU 사용률 제한
            if hasattr(psutil, 'cpu_percent'):
                cpu_percent = psutil.cpu_percent(interval=0.1)
                if cpu_percent > 90:
                    time.sleep(0.001)  # CPU 부하 감소
            
            # 메모리 사용량 모니터링
            memory_usage = self.get_memory_usage()
            if memory_usage > 500:  # 500MB 이상
                self.optimize_memory()
            
        except Exception as e:
            print(f"실행 속도 최적화 중 오류: {e}")
    
    def start_performance_monitoring(self, interval: int = 30):
        """
        성능 모니터링 시작
        
        Args:
            interval: 모니터링 간격 (초)
        """
        def monitor():
            while True:
                try:
                    report = self.get_performance_report()
                    
                    # 메모리 사용량이 높으면 최적화
                    if report["memory_usage"] > 300:  # 300MB 이상
                        self.optimize_memory()
                    
                    # 성능 메트릭 로깅
                    if report["function_metrics"]:
                        print("=== 성능 모니터링 리포트 ===")
                        for func_name, metrics in report["function_metrics"].items():
                            if metrics["calls"] > 0:
                                print(f"{func_name}: {metrics['calls']}회 호출, "
                                      f"평균 {metrics['avg_time']:.4f}초, "
                                      f"성공률 {metrics['success_count']/metrics['calls']*100:.1f}%")
                        print("================================")
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    print(f"성능 모니터링 중 오류: {e}")
                    time.sleep(interval)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def get_optimization_recommendations(self) -> List[str]:
        """최적화 권장사항 반환"""
        recommendations = []
        
        try:
            report = self.get_performance_report()
            
            # 메모리 사용량 권장사항
            memory_usage = report["memory_usage"]
            if memory_usage > 500:
                recommendations.append("메모리 사용량이 높습니다. 불필요한 프로젝트를 닫아주세요.")
            elif memory_usage > 300:
                recommendations.append("메모리 최적화를 권장합니다.")
            
            # 캐시 히트율 권장사항
            cache_hit_rate = report["cache_hit_rate"]
            if cache_hit_rate < 50:
                recommendations.append("캐시 효율성이 낮습니다. 자주 사용하는 기능을 확인해주세요.")
            
            # 함수 성능 권장사항
            for func_name, metrics in report["function_metrics"].items():
                if metrics["calls"] > 10 and metrics["avg_time"] > 1.0:
                    recommendations.append(f"{func_name} 함수의 실행 시간이 느립니다. 최적화를 고려해주세요.")
                
                if metrics["error_count"] > 0:
                    error_rate = metrics["error_count"] / metrics["calls"] * 100
                    if error_rate > 10:
                        recommendations.append(f"{func_name} 함수의 오류율이 높습니다. 코드를 점검해주세요.")
            
            # 시스템 메모리 권장사항
            system_memory = report["system_memory"]
            if system_memory.get("percent", 0) > 80:
                recommendations.append("시스템 메모리 사용량이 높습니다. 다른 프로그램을 종료해주세요.")
            
        except Exception as e:
            recommendations.append(f"권장사항 생성 중 오류: {e}")
        
        return recommendations


# 전역 성능 최적화 인스턴스
performance_optimizer = PerformanceOptimizer() 