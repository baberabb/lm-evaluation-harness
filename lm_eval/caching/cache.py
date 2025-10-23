"""
Caching module for lm-evaluation-harness.

Provides a centralized cache management system for request instances
with statistics tracking, better error handling, and a clean API.
"""

import hashlib
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Optional, Dict
from pathlib import Path

import dill


eval_logger = logging.getLogger(__name__)


# Cache configuration
MODULE_DIR = Path(__file__).parent
OVERRIDE_PATH = os.getenv("LM_HARNESS_CACHE_PATH")
CACHE_PATH = Path(OVERRIDE_PATH) if OVERRIDE_PATH else MODULE_DIR / ".cache"

# Hash configuration for file suffix uniqueness
HASH_INPUT = "EleutherAI-lm-evaluation-harness"
HASH_PREFIX = hashlib.sha256(HASH_INPUT.encode("utf-8")).hexdigest()
FILE_SUFFIX = f".{HASH_PREFIX}.pickle"


class CacheError(Exception):
    """Base exception for cache operations."""
    pass


class CacheLoadError(CacheError):
    """Raised when cache loading fails."""
    pass


class CacheSaveError(CacheError):
    """Raised when cache saving fails."""
    pass


@dataclass
class CacheKey:
    """
    Type-safe representation of a cache key.

    Encapsulates all parameters that uniquely identify a cached request set.
    """
    task_name: str
    num_fewshot: int
    rank: int
    world_size: int
    apply_chat_template: bool = False
    fewshot_as_multiturn: bool = False
    system_instruction_hash: Optional[str] = None
    tokenizer_name: str = ""

    def to_string(self) -> str:
        """Convert cache key to a string identifier."""
        parts = [
            f"requests-{self.task_name}",
            f"{self.num_fewshot}shot",
            f"rank{self.rank}",
            f"world_size{self.world_size}",
        ]

        if self.apply_chat_template:
            parts.append("chat_template")
        if self.fewshot_as_multiturn:
            parts.append("fewshot_as_multiturn")
        if self.system_instruction_hash:
            parts.append(f"system_prompt_hash{self.system_instruction_hash}")
        if self.tokenizer_name:
            parts.append(f"tokenizer{self.tokenizer_name}")

        return "-".join(parts)

    @staticmethod
    def hash_string(text: str) -> str:
        """Create a hash of a string for cache key purposes."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


@dataclass
class CacheStatistics:
    """Track cache performance statistics."""
    hits: int = 0
    misses: int = 0
    saves: int = 0
    load_errors: int = 0
    save_errors: int = 0

    def record_hit(self) -> None:
        """Record a cache hit."""
        self.hits += 1

    def record_miss(self) -> None:
        """Record a cache miss."""
        self.misses += 1

    def record_save(self) -> None:
        """Record a successful save."""
        self.saves += 1

    def record_load_error(self) -> None:
        """Record a load error."""
        self.load_errors += 1

    def record_save_error(self) -> None:
        """Record a save error."""
        self.save_errors += 1

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def summary(self) -> Dict[str, Any]:
        """Get a summary of cache statistics."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "saves": self.saves,
            "load_errors": self.load_errors,
            "save_errors": self.save_errors,
            "hit_rate": f"{self.hit_rate:.2%}",
        }


class RequestCacheManager:
    """
    Centralized cache manager for request instances.

    Provides a clean API for cache operations with statistics tracking,
    better error handling, and separation of concerns.
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize the cache manager.

        Args:
            cache_dir: Optional custom cache directory. Uses default if None.
        """
        self.cache_dir = cache_dir or CACHE_PATH
        self.statistics = CacheStatistics()
        self._ensure_cache_dir()

    def _ensure_cache_dir(self) -> None:
        """Ensure the cache directory exists."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, cache_key: CacheKey) -> Path:
        """Get the full file path for a cache key."""
        filename = f"{cache_key.to_string()}{FILE_SUFFIX}"
        return self.cache_dir / filename

    def load(self, cache_key: CacheKey) -> Optional[Any]:
        """
        Load data from cache.

        Args:
            cache_key: The cache key to load

        Returns:
            The cached data if found, None otherwise
        """
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            eval_logger.debug(f"Cache miss: {cache_key.to_string()}")
            self.statistics.record_miss()
            return None

        try:
            with open(cache_path, "rb") as f:
                data = dill.loads(f.read())

            eval_logger.debug(f"Cache hit: {cache_key.to_string()}")
            self.statistics.record_hit()
            return data

        except Exception as e:
            eval_logger.warning(
                f"Failed to load cache {cache_key.to_string()}: {e}. "
                "Will rebuild from scratch."
            )
            self.statistics.record_load_error()
            return None

    def save(self, cache_key: CacheKey, data: Any) -> bool:
        """
        Save data to cache.

        Args:
            cache_key: The cache key to save under
            data: The data to cache

        Returns:
            True if save successful, False otherwise
        """
        cache_path = self._get_cache_path(cache_key)

        try:
            self._ensure_cache_dir()

            with open(cache_path, "wb") as f:
                f.write(dill.dumps(data))

            eval_logger.debug(f"Saved to cache: {cache_key.to_string()}")
            self.statistics.record_save()
            return True

        except Exception as e:
            eval_logger.error(f"Failed to save cache {cache_key.to_string()}: {e}")
            self.statistics.record_save_error()
            return False

    def exists(self, cache_key: CacheKey) -> bool:
        """
        Check if a cache entry exists.

        Args:
            cache_key: The cache key to check

        Returns:
            True if cache exists, False otherwise
        """
        return self._get_cache_path(cache_key).exists()

    def delete(self, cache_key: CacheKey) -> bool:
        """
        Delete a cache entry.

        Args:
            cache_key: The cache key to delete

        Returns:
            True if deletion successful, False otherwise
        """
        cache_path = self._get_cache_path(cache_key)

        try:
            if cache_path.exists():
                cache_path.unlink()
                eval_logger.debug(f"Deleted cache: {cache_key.to_string()}")
                return True
            return False
        except Exception as e:
            eval_logger.error(f"Failed to delete cache {cache_key.to_string()}: {e}")
            return False

    def clear_by_prefix(self, prefix: str) -> int:
        """
        Delete all cache entries matching a prefix.

        Args:
            prefix: The prefix to match (e.g., task name)

        Returns:
            Number of files deleted
        """
        if not self.cache_dir.exists():
            return 0

        deleted = 0
        try:
            for cache_file in self.cache_dir.iterdir():
                if cache_file.name.startswith(prefix) and cache_file.name.endswith(FILE_SUFFIX):
                    cache_file.unlink()
                    deleted += 1

            eval_logger.info(f"Deleted {deleted} cache entries with prefix '{prefix}'")
            return deleted

        except Exception as e:
            eval_logger.error(f"Error clearing cache with prefix '{prefix}': {e}")
            return deleted

    def clear_all(self) -> int:
        """
        Clear all cache entries.

        Returns:
            Number of files deleted
        """
        if not self.cache_dir.exists():
            return 0

        deleted = 0
        try:
            for cache_file in self.cache_dir.iterdir():
                if cache_file.name.endswith(FILE_SUFFIX):
                    cache_file.unlink()
                    deleted += 1

            eval_logger.info(f"Deleted all {deleted} cache entries")
            return deleted

        except Exception as e:
            eval_logger.error(f"Error clearing all cache: {e}")
            return deleted

    def get_statistics(self) -> Dict[str, Any]:
        """Get current cache statistics."""
        return self.statistics.summary()

    def reset_statistics(self) -> None:
        """Reset cache statistics."""
        self.statistics = CacheStatistics()


# Global cache manager instance
_global_cache_manager: Optional[RequestCacheManager] = None


def get_cache_manager() -> RequestCacheManager:
    """
    Get the global cache manager instance.

    Creates a new instance if one doesn't exist.

    Returns:
        The global RequestCacheManager instance
    """
    global _global_cache_manager
    if _global_cache_manager is None:
        _global_cache_manager = RequestCacheManager()
    return _global_cache_manager


# Legacy compatibility functions - these wrap the new cache manager
def load_from_cache(file_name: str, cache: bool = False):
    """
    Legacy function for backward compatibility.

    DEPRECATED: Use RequestCacheManager directly.
    """
    if not cache:
        return None

    try:
        cache_path = CACHE_PATH / f"{file_name}{FILE_SUFFIX}"

        if not cache_path.exists():
            eval_logger.debug(f"{file_name} is not cached, generating...")
            return None

        with open(cache_path, "rb") as file:
            return dill.loads(file.read())

    except Exception as e:
        eval_logger.debug(f"Failed to load {file_name}: {e}")
        return None


def save_to_cache(file_name: str, obj: Any) -> None:
    """
    Legacy function for backward compatibility.

    DEPRECATED: Use RequestCacheManager directly.
    """
    try:
        CACHE_PATH.mkdir(parents=True, exist_ok=True)
        cache_path = CACHE_PATH / f"{file_name}{FILE_SUFFIX}"

        eval_logger.debug(f"Saving {cache_path} to cache...")
        with open(cache_path, "wb") as file:
            file.write(dill.dumps(obj))

    except Exception as e:
        eval_logger.error(f"Failed to save {file_name}: {e}")


def delete_cache(key: str = "") -> None:
    """
    Legacy function for backward compatibility.

    DEPRECATED: Use RequestCacheManager.clear_by_prefix() or clear_all().
    """
    if not CACHE_PATH.exists():
        return

    try:
        for cache_file in CACHE_PATH.iterdir():
            if cache_file.name.startswith(key) and cache_file.name.endswith(FILE_SUFFIX):
                cache_file.unlink()
    except Exception as e:
        eval_logger.error(f"Error deleting cache: {e}")
