from __future__ import annotations

from abc import ABC, abstractmethod


class OverlayBackend(ABC):
    @abstractmethod
    def run(self) -> None:
        """Run the backend event loop until shutdown."""

    @abstractmethod
    def update(self, width_name: str, brightness: int) -> None:
        """Apply a new overlay configuration."""

    @abstractmethod
    def shutdown(self) -> None:
        """Stop and close the backend."""
