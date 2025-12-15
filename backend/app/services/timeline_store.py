"""
Timeline Store - Track all generations and edits with version history
"""

from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime
from pathlib import Path

from app.settings import settings


class TimelineEntry:
    """Represents a single entry in the timeline"""

    def __init__(
        self,
        run_id: str,
        seed: int,
        scene_snapshot: Dict[str, Any],
        patch_summary: str,
        output_urls: List[str],
        timestamp: Optional[str] = None,
    ):
        self.run_id = run_id
        self.seed = seed
        self.scene_snapshot = scene_snapshot
        self.patch_summary = patch_summary
        self.output_urls = output_urls
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "seed": self.seed,
            "scene_snapshot": self.scene_snapshot,
            "patch_summary": self.patch_summary,
            "output_urls": self.output_urls,
        }


class TimelineStore:
    """Manages timeline entries using file storage"""

    def __init__(self, storage_dir: str = None):
        self.storage_dir = storage_dir or settings.STORAGE_DIR
        self.timeline_file = os.path.join(self.storage_dir, "timeline.jsonl")
        os.makedirs(self.storage_dir, exist_ok=True)

    def add_entry(self, entry: TimelineEntry) -> None:
        """
        Add a new entry to the timeline.

        Args:
            entry: TimelineEntry to add
        """
        with open(self.timeline_file, "a") as f:
            f.write(json.dumps(entry.to_dict()) + "\n")

    def get_all_entries(self) -> List[TimelineEntry]:
        """
        Get all timeline entries in reverse chronological order.

        Returns:
            List of TimelineEntry objects
        """
        entries = []

        if not os.path.exists(self.timeline_file):
            return entries

        with open(self.timeline_file, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        entry = TimelineEntry(
                            run_id=data["run_id"],
                            seed=data["seed"],
                            scene_snapshot=data["scene_snapshot"],
                            patch_summary=data["patch_summary"],
                            output_urls=data["output_urls"],
                            timestamp=data.get("timestamp"),
                        )
                        entries.append(entry)
                    except json.JSONDecodeError:
                        continue

        # Return in reverse order (most recent first)
        return list(reversed(entries))

    def get_entry_by_run_id(self, run_id: str) -> Optional[TimelineEntry]:
        """
        Get a specific timeline entry by run_id.

        Args:
            run_id: Run ID to search for

        Returns:
            TimelineEntry if found, None otherwise
        """
        entries = self.get_all_entries()
        for entry in entries:
            if entry.run_id == run_id:
                return entry
        return None

    def get_recent_entries(self, limit: int = 10) -> List[TimelineEntry]:
        """
        Get the N most recent timeline entries.

        Args:
            limit: Number of entries to return

        Returns:
            List of TimelineEntry objects
        """
        entries = self.get_all_entries()
        return entries[:limit]

    def get_entries_by_date_range(
        self, start_date: str, end_date: str
    ) -> List[TimelineEntry]:
        """
        Get timeline entries within a date range.

        Args:
            start_date: ISO format start date
            end_date: ISO format end date

        Returns:
            List of TimelineEntry objects
        """
        entries = self.get_all_entries()
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        filtered = [
            e
            for e in entries
            if start <= datetime.fromisoformat(e.timestamp) <= end
        ]
        return filtered

    def clear_timeline(self) -> None:
        """Clear all timeline entries (use with caution)"""
        if os.path.exists(self.timeline_file):
            os.remove(self.timeline_file)

    def export_timeline(self, output_path: str) -> None:
        """
        Export timeline as JSON array.

        Args:
            output_path: File path to export to
        """
        entries = self.get_all_entries()
        data = [e.to_dict() for e in entries]

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get timeline statistics.

        Returns:
            Dictionary with timeline statistics
        """
        entries = self.get_all_entries()

        if not entries:
            return {
                "total_entries": 0,
                "total_generations": 0,
                "seed_range": None,
                "date_range": None,
            }

        seeds = [e.seed for e in entries]
        timestamps = [e.timestamp for e in entries]

        return {
            "total_entries": len(entries),
            "total_generations": len(entries),
            "seed_range": {"min": min(seeds), "max": max(seeds)},
            "date_range": {
                "earliest": min(timestamps),
                "latest": max(timestamps),
            },
        }


# Global timeline store instance
_timeline_store: Optional[TimelineStore] = None


def get_timeline_store() -> TimelineStore:
    """Get or create the global timeline store"""
    global _timeline_store
    if _timeline_store is None:
        _timeline_store = TimelineStore()
    return _timeline_store
