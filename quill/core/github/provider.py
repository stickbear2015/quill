"""Abstract remote provider interface for the GitHub integration."""

from __future__ import annotations

from abc import ABC, abstractmethod

from quill.core.github.models import (
    RemoteAccount,
    RemoteFile,
    RemoteNode,
    RemoteRef,
    RemoteRepository,
)


class RemoteProvider(ABC):
    """Contract that every remote provider must satisfy."""

    provider_id: str = ""

    @abstractmethod
    def get_identity(self) -> RemoteAccount | None:
        """Return the authenticated account, or None for anonymous access."""

    @abstractmethod
    def get_repository(self, full_name: str) -> RemoteRepository:
        """Return metadata for ``owner/repo``.

        Raises:
            KeyError: repository not found or no access.
            PermissionError: authentication required or insufficient scope.
            RuntimeError: unexpected API error.
        """

    @abstractmethod
    def list_refs(
        self,
        repository: RemoteRepository,
        *,
        limit: int = 100,
    ) -> list[RemoteRef]:
        """Return up to *limit* branches then up to *limit* tags for *repository*.

        The default ``limit`` of 100 keeps repos with thousands of refs (e.g.
        ``kubernetes/kubernetes``) from burning the anonymous 60-req/hour rate
        limit on a single browse dialog (finding #34).  Callers that need the
        full list may pass a larger ``limit``; the dialog uses a "Show all
        refs" affordance for that case.
        """

    @abstractmethod
    def list_directory(
        self,
        repository: RemoteRepository,
        path: str,
        ref: str,
    ) -> list[RemoteNode]:
        """Return sorted contents of *path* on *ref* (dirs first, then files).

        Pass ``path=""`` for the repository root.

        Raises:
            KeyError: path not found.
            RuntimeError: API error.
        """

    @abstractmethod
    def get_file(
        self,
        repository: RemoteRepository,
        path: str,
        ref: str,
    ) -> RemoteFile:
        """Fetch a single file's raw bytes.

        Raises:
            KeyError: file not found.
            ValueError: path is a directory, or file exceeds API size limit.
            RuntimeError: API error.
        """

    @abstractmethod
    def write_file(
        self,
        full_name: str,
        path: str,
        ref: str,
        content: bytes,
        sha: str,
        message: str,
    ) -> str:
        """Commit updated *content* to *path* on *ref*.

        *sha* must be the SHA of the existing file (optimistic concurrency).
        Returns the new file SHA after the commit.

        Raises:
            PermissionError: no write access.
            RuntimeError: API error or SHA conflict.
        """
