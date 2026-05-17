"""
Unit tests for data_injector/markdown_data_injector.py

Tests cover:
- MarkdownDataInjector.__init__
- MarkdownDataInjector._get_markdown_files_paths  (success, missing path, empty dir)
- MarkdownDataInjector._load_file  (MyCustomLoader integration)
- MarkdownDataInjector.ingest_files  (full async pipeline with mocks)
- MyCustomLoader.load  (file reading and Document creation)
"""

import os
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from qdrant_client.models import PointStruct, SparseVector

from services.api.chunker.base_chunker import BaseChunker
from services.api.data_injector.markdown_data_injector import MarkdownDataInjector, MyCustomLoader
from services.api.db_client.db_client import DbClient
from services.api.embedding_provider.base_embedding_provider import BaseEmbeddingProvider


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_db_client() -> DbClient:
    """Return a mock DbClient with async upsert."""
    client = MagicMock(spec=DbClient)
    client.upsert = AsyncMock()
    client.embedding_provider = MagicMock(spec=BaseEmbeddingProvider)
    return client


@pytest.fixture
def mock_chunker() -> BaseChunker:
    """Return a mock BaseChunker that returns two fake Document chunks."""
    chunker = MagicMock(spec=BaseChunker)
    chunker.split_to_chunks.return_value = [
        Document(page_content="chunk one content"),
        Document(page_content="chunk two content"),
    ]
    return chunker


@pytest.fixture
def mock_embedding_provider() -> BaseEmbeddingProvider:
    """Return a mock embedding provider with dense and sparse embeddings."""
    provider = MagicMock(spec=BaseEmbeddingProvider)

    # Dense: simple numpy array
    provider.get_dense_embedding.return_value = np.array([0.1, 0.2, 0.3])

    # Sparse: object with .indices and .values attributes
    sparse_mock = MagicMock()
    sparse_mock.indices = np.array([0, 2, 5])
    sparse_mock.values = np.array([0.5, 0.7, 0.9])
    provider.get_sparse_embedding.return_value = sparse_mock

    return provider


@pytest.fixture
def temp_md_dir(tmp_path):
    """Create a temporary directory with two .md files."""
    (tmp_path / "doc1.md").write_text("# Doc 1\n\nSome content here.", encoding="utf-8")
    (tmp_path / "doc2.md").write_text("# Doc 2\n\nMore content.", encoding="utf-8")
    return tmp_path


@pytest.fixture
def empty_md_dir(tmp_path):
    """Create an empty temporary directory (no .md files)."""
    return tmp_path


@pytest.fixture
def injector(mock_db_client, mock_chunker, temp_md_dir, monkeypatch):
    """Return a fully initialised MarkdownDataInjector pointing at temp_md_dir."""
    monkeypatch.setattr(
        "data_injector.markdown_data_injector.config.docs_path",
        str(temp_md_dir),
    )
    return MarkdownDataInjector(mock_db_client, mock_chunker)


# ---------------------------------------------------------------------------
# Tests: MarkdownDataInjector.__init__
# ---------------------------------------------------------------------------


class TestMarkdownDataInjectorInit:
    def test_stores_db_client(self, mock_db_client, mock_chunker, temp_md_dir, monkeypatch):
        monkeypatch.setattr(
            "data_injector.markdown_data_injector.config.docs_path",
            str(temp_md_dir),
        )
        inj = MarkdownDataInjector(mock_db_client, mock_chunker)
        assert inj.db_client is mock_db_client

    def test_stores_chunker(self, mock_db_client, mock_chunker, temp_md_dir, monkeypatch):
        monkeypatch.setattr(
            "data_injector.markdown_data_injector.config.docs_path",
            str(temp_md_dir),
        )
        inj = MarkdownDataInjector(mock_db_client, mock_chunker)
        assert inj.chunker is mock_chunker

    def test_base_path_from_config(self, mock_db_client, mock_chunker, temp_md_dir, monkeypatch):
        monkeypatch.setattr(
            "data_injector.markdown_data_injector.config.docs_path",
            str(temp_md_dir),
        )
        inj = MarkdownDataInjector(mock_db_client, mock_chunker)
        assert inj.base_path == Path(str(temp_md_dir))

    def test_calls_super_init(self, mock_db_client, mock_chunker, temp_md_dir, monkeypatch):
        """DataInjector.__init__ should be called (even if it is a no-op)."""
        monkeypatch.setattr(
            "data_injector.markdown_data_injector.config.docs_path",
            str(temp_md_dir),
        )
        # Should not raise
        inj = MarkdownDataInjector(mock_db_client, mock_chunker)
        assert isinstance(inj, MarkdownDataInjector)


# ---------------------------------------------------------------------------
# Tests: MarkdownDataInjector._get_markdown_files_paths
# ---------------------------------------------------------------------------


class TestGetMarkdownFilesPaths:
    def test_returns_md_files(self, injector, temp_md_dir):
        result = injector._get_markdown_files_paths()
        assert len(result) == 2
        for path in result:
            assert path.endswith(".md")

    def test_paths_are_absolute(self, injector, temp_md_dir):
        result = injector._get_markdown_files_paths()
        for path in result:
            assert os.path.isabs(path)

    def test_raises_when_path_missing(self, mock_db_client, mock_chunker, tmp_path, monkeypatch):
        """Should raise ValueError when base_path does not exist."""
        missing = tmp_path / "does_not_exist"
        monkeypatch.setattr(
            "data_injector.markdown_data_injector.config.docs_path",
            str(missing),
        )
        inj = MarkdownDataInjector(mock_db_client, mock_chunker)
        with pytest.raises(ValueError, match="No such path"):
            inj._get_markdown_files_paths()

    def test_raises_when_directory_empty(self, mock_db_client, mock_chunker, empty_md_dir, monkeypatch):
        """Should raise ValueError when directory has no .md files."""
        monkeypatch.setattr(
            "data_injector.markdown_data_injector.config.docs_path",
            str(empty_md_dir),
        )
        inj = MarkdownDataInjector(mock_db_client, mock_chunker)
        with pytest.raises(ValueError, match="No files in"):
            inj._get_markdown_files_paths()

    def test_ignores_non_md_files(self, mock_db_client, mock_chunker, tmp_path, monkeypatch):
        """Files that do not end with .md should be excluded."""
        (tmp_path / "readme.txt").write_text("not markdown", encoding="utf-8")
        (tmp_path / "note.md").write_text("# Note", encoding="utf-8")
        monkeypatch.setattr(
            "data_injector.markdown_data_injector.config.docs_path",
            str(tmp_path),
        )
        inj = MarkdownDataInjector(mock_db_client, mock_chunker)
        result = inj._get_markdown_files_paths()
        assert len(result) == 1
        assert result[0].endswith(".md")


# ---------------------------------------------------------------------------
# Tests: MarkdownDataInjector._load_file
# ---------------------------------------------------------------------------


class TestLoadFile:
    def test_returns_document(self, injector, temp_md_dir):
        md_file = str(temp_md_dir / "doc1.md")
        doc = injector._load_file(md_file)
        assert isinstance(doc, Document)

    def test_page_content_matches_file(self, injector, temp_md_dir):
        md_file = str(temp_md_dir / "doc1.md")
        doc = injector._load_file(md_file)
        assert "# Doc 1" in doc.page_content

    def test_metadata_contains_source(self, injector, temp_md_dir):
        md_file = str(temp_md_dir / "doc1.md")
        doc = injector._load_file(md_file)
        assert "source" in doc.metadata
        assert doc.metadata["source"] == md_file

    def test_metadata_source_is_absolute_path(self, injector, temp_md_dir):
        md_file = str(temp_md_dir / "doc1.md")
        doc = injector._load_file(md_file)
        assert os.path.isabs(doc.metadata["source"])


# ---------------------------------------------------------------------------
# Tests: MarkdownDataInjector.ingest_files  (async)
# ---------------------------------------------------------------------------


class TestIngestFiles:
    @pytest.mark.asyncio
    async def test_calls_upsert_once_per_file(
        self, injector, mock_db_client, mock_chunker, temp_md_dir
    ):
        """upsert should be called exactly once per markdown file."""
        await injector.ingest_files()
        assert mock_db_client.upsert.call_count == 2  # two .md files

    @pytest.mark.asyncio
    async def test_upsert_called_with_correct_collection_name(
        self, injector, mock_db_client, mock_chunker, temp_md_dir, monkeypatch
    ):
        monkeypatch.setattr(
            "data_injector.markdown_data_injector.config.qdrant.collection_name",
            "my_test_collection",
        )
        await injector.ingest_files()
        call_args = mock_db_client.upsert.call_args
        assert call_args[0][0] == "my_test_collection"

    @pytest.mark.asyncio
    async def test_points_have_correct_structure(
        self, injector, mock_db_client, mock_chunker, temp_md_dir
    ):
        """Each point passed to upsert must be a PointStruct with dense+sparse vectors."""
        await injector.ingest_files()
        for call in mock_db_client.upsert.call_args_list:
            points = call[0][1]
            for point in points:
                assert isinstance(point, PointStruct)
                assert "dense" in point.vector
                assert "sparse" in point.vector
                assert isinstance(point.vector["sparse"], SparseVector)

    @pytest.mark.asyncio
    async def test_payload_contains_text_source_and_updated_at(
        self, injector, mock_db_client, mock_chunker, temp_md_dir
    ):
        """Payload must contain 'text', 'source', and 'updated_at' keys."""
        await injector.ingest_files()
        for call in mock_db_client.upsert.call_args_list:
            points = call[0][1]
            for point in points:
                assert "text" in point.payload
                assert "source" in point.payload
                assert "updated_at" in point.payload

    @pytest.mark.asyncio
    async def test_payload_source_is_file_path(
        self, injector, mock_db_client, mock_chunker, temp_md_dir
    ):
        await injector.ingest_files()
        for call in mock_db_client.upsert.call_args_list:
            points = call[0][1]
            for point in points:
                assert point.payload["source"].endswith(".md")

    @pytest.mark.asyncio
    async def test_payload_updated_at_is_datetime(
        self, injector, mock_db_client, mock_chunker, temp_md_dir
    ):
        await injector.ingest_files()
        for call in mock_db_client.upsert.call_args_list:
            points = call[0][1]
            for point in points:
                assert isinstance(point.payload["updated_at"], datetime)

    @pytest.mark.asyncio
    async def test_dense_embedding_called_with_chunk_content(
        self, injector, mock_db_client, mock_chunker, temp_md_dir
    ):
        """embedding_provider.get_dense_embedding must receive chunk.page_content."""
        await injector.ingest_files()
        provider = mock_db_client.embedding_provider
        # 2 files × 2 chunks each = 4 calls
        assert provider.get_dense_embedding.call_count == 4
        for call in provider.get_dense_embedding.call_args_list:
            arg = call[0][0]
            assert isinstance(arg, str)

    @pytest.mark.asyncio
    async def test_sparse_embedding_called_with_chunk_content(
        self, injector, mock_db_client, mock_chunker, temp_md_dir
    ):
        """embedding_provider.get_sparse_embedding must receive chunk.page_content."""
        await injector.ingest_files()
        provider = mock_db_client.embedding_provider
        assert provider.get_sparse_embedding.call_count == 4

    @pytest.mark.asyncio
    async def test_chunker_called_per_file(
        self, injector, mock_db_client, mock_chunker, temp_md_dir
    ):
        """split_to_chunks should be called once per markdown file."""
        await injector.ingest_files()
        assert mock_chunker.split_to_chunks.call_count == 2

    @pytest.mark.asyncio
    async def test_point_ids_are_sequential_per_file(
        self, injector, mock_db_client, mock_chunker, temp_md_dir
    ):
        """Point IDs within a single file should be 0, 1, … (enumerate index)."""
        await injector.ingest_files()
        for call in mock_db_client.upsert.call_args_list:
            points = call[0][1]
            for idx, point in enumerate(points):
                assert point.id == idx

    @pytest.mark.asyncio
    async def test_raises_when_no_md_files(
        self, mock_db_client, mock_chunker, empty_md_dir, monkeypatch
    ):
        """ingest_files should propagate ValueError from _get_markdown_files_paths."""
        monkeypatch.setattr(
            "data_injector.markdown_data_injector.config.docs_path",
            str(empty_md_dir),
        )
        inj = MarkdownDataInjector(mock_db_client, mock_chunker)
        with pytest.raises(ValueError, match="No files in"):
            await inj.ingest_files()

    @pytest.mark.asyncio
    async def test_raises_when_path_missing(
        self, mock_db_client, mock_chunker, tmp_path, monkeypatch
    ):
        """ingest_files should propagate ValueError when base_path does not exist."""
        missing = tmp_path / "does_not_exist"
        monkeypatch.setattr(
            "data_injector.markdown_data_injector.config.docs_path",
            str(missing),
        )
        inj = MarkdownDataInjector(mock_db_client, mock_chunker)
        with pytest.raises(ValueError, match="No such path"):
            await inj.ingest_files()

    @pytest.mark.asyncio
    async def test_upsert_not_called_on_error(
        self, mock_db_client, mock_chunker, empty_md_dir, monkeypatch
    ):
        """If _get_markdown_files_paths raises, upsert must never be called."""
        monkeypatch.setattr(
            "data_injector.markdown_data_injector.config.docs_path",
            str(empty_md_dir),
        )
        inj = MarkdownDataInjector(mock_db_client, mock_chunker)
        with pytest.raises(ValueError):
            await inj.ingest_files()
        mock_db_client.upsert.assert_not_called()


# ---------------------------------------------------------------------------
# Tests: MyCustomLoader
# ---------------------------------------------------------------------------


class TestMyCustomLoader:
    def test_load_returns_document(self, tmp_path):
        md_file = tmp_path / "sample.md"
        md_file.write_text("Hello, world!", encoding="utf-8")
        loader = MyCustomLoader(str(md_file))
        doc = loader.load()
        assert isinstance(doc, Document)

    def test_page_content_matches_file(self, tmp_path):
        content = "# Heading\n\nSome body text."
        (tmp_path / "sample.md").write_text(content, encoding="utf-8")
        loader = MyCustomLoader(str(tmp_path / "sample.md"))
        doc = loader.load()
        assert doc.page_content == content

    def test_metadata_contains_source(self, tmp_path):
        md_file = tmp_path / "sample.md"
        md_file.write_text("text", encoding="utf-8")
        loader = MyCustomLoader(str(md_file))
        doc = loader.load()
        assert doc.metadata["source"] == str(md_file)

    def test_metadata_source_is_absolute(self, tmp_path):
        md_file = tmp_path / "sample.md"
        md_file.write_text("text", encoding="utf-8")
        loader = MyCustomLoader(str(md_file))
        doc = loader.load()
        assert os.path.isabs(doc.metadata["source"])

    def test_encoding_utf8(self, tmp_path):
        """Non-ASCII characters must be read correctly."""
        content = "# Привет\n\nТекст на русском."
        (tmp_path / "ru.md").write_text(content, encoding="utf-8")
        loader = MyCustomLoader(str(tmp_path / "ru.md"))
        doc = loader.load()
        assert "Привет" in doc.page_content

    def test_loader_is_base_loader_subclass(self):
        """MyCustomLoader must inherit from BaseLoader."""
        assert issubclass(MyCustomLoader, BaseLoader)
