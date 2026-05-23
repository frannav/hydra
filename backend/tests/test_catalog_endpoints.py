from __future__ import annotations

import unittest
from datetime import date

from fastapi.testclient import TestClient

from hydra_api.catalog_service import CatalogService
from hydra_api.main import app


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows
        self.executed_sql = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql: str) -> None:
        self.executed_sql = sql

    def fetchall(self):
        return list(self.rows)


class FakeConnection:
    def __init__(self, rows):
        self.rows = rows
        self.closed = False

    def cursor(self):
        return FakeCursor(self.rows)

    def close(self) -> None:
        self.closed = True


class CatalogEndpointsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        if hasattr(app.state, "catalog_service"):
            del app.state.catalog_service

    def tearDown(self) -> None:
        if hasattr(app.state, "catalog_service"):
            del app.state.catalog_service

    def test_documents_returns_empty_list(self) -> None:
        app.state.catalog_service = CatalogService(
            connection_factory=lambda: FakeConnection([]),
        )

        response = self.client.get("/documents")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"documents": []})

    def test_documents_returns_public_contract_fields_only(self) -> None:
        rows = [
            ("doc_002", "Beta", "Fuente B", None, "processing"),
            ("doc_001", "Alpha", "Fuente A", date(2026, 5, 15), "processed"),
        ]
        app.state.catalog_service = CatalogService(
            connection_factory=lambda: FakeConnection(rows),
        )

        response = self.client.get("/documents")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(
            body,
            {
                "documents": [
                    {
                        "document_id": "doc_001",
                        "title": "Alpha",
                        "source": "Fuente A",
                        "published_at": "2026-05-15",
                        "processed": True,
                    },
                    {
                        "document_id": "doc_002",
                        "title": "Beta",
                        "source": "Fuente B",
                        "published_at": None,
                        "processed": False,
                    },
                ]
            },
        )
        self.assertEqual(
            set(body["documents"][0].keys()),
            {"document_id", "title", "source", "published_at", "processed"},
        )

    def test_narratives_returns_empty_list(self) -> None:
        app.state.catalog_service = CatalogService(
            connection_factory=lambda: FakeConnection([]),
        )

        response = self.client.get("/narratives")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"narratives": []})

    def test_narratives_aggregate_safely_and_ignore_invalid_rows(self) -> None:
        rows = [
            (
                "ext_001",
                "doc_010",
                {
                    "document_id": "doc_010",
                    "title": "Doc 10",
                    "source": "Fuente 10",
                    "narrative_frame_id": "coordinated_campaign",
                    "actors": [{"name": "Actor Z"}, {"name": "Actor A"}],
                    "risk_level": "alto",
                    "confidence": "alta",
                    "evidence_fragments": [
                        {"text": "Fragmento 1", "source_document_id": "doc_010"},
                        {"text": "Fragmento 2", "source_document_id": "doc_010"},
                    ],
                },
            ),
            (
                "ext_002",
                "doc_002",
                {
                    "document_id": "doc_002",
                    "title": "Doc 2",
                    "source": "Fuente 2",
                    "narrative_frame_id": "coordinated_campaign",
                    "actors": [{"name": "Actor A"}, {"name": "Actor B"}],
                    "risk_level": "medio",
                    "confidence": "baja",
                    "evidence_fragments": [
                        {"text": "Fragmento 2", "source_document_id": "doc_002"},
                        {"text": "Fragmento 3", "source_document_id": "doc_002"},
                        {"text": "Fragmento 4", "source_document_id": "doc_002"},
                    ],
                },
            ),
            (
                "ext_003",
                "doc_bad",
                {
                    "document_id": "doc_bad",
                    "narrative_frame_id": "coordinated_campaign",
                },
            ),
            (
                "ext_004",
                "doc_020",
                {
                    "document_id": "doc_020",
                    "title": "Doc 20",
                    "source": "Fuente 20",
                    "narrative_frame_id": "custom_frame",
                    "actors": [{"name": "Actor C"}],
                    "risk_level": "bajo",
                    "confidence": "media",
                    "evidence_fragments": [
                        {"text": "Fragmento custom", "source_document_id": "doc_020"},
                    ],
                },
            ),
        ]
        app.state.catalog_service = CatalogService(
            connection_factory=lambda: FakeConnection(rows),
        )

        response = self.client.get("/narratives")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "narratives": [
                    {
                        "narrative_frame_id": "coordinated_campaign",
                        "label": "Coordinated Campaign",
                        "document_ids": ["doc_002", "doc_010"],
                        "actors": ["Actor A", "Actor B", "Actor Z"],
                        "risk_level": "alto",
                        "confidence": "baja",
                        "evidence_fragments": [
                            "Fragmento 1",
                            "Fragmento 2",
                            "Fragmento 3",
                        ],
                    },
                    {
                        "narrative_frame_id": "custom_frame",
                        "label": "custom_frame",
                        "document_ids": ["doc_020"],
                        "actors": ["Actor C"],
                        "risk_level": "bajo",
                        "confidence": "media",
                        "evidence_fragments": ["Fragmento custom"],
                    },
                ]
            },
        )

    def test_documents_db_unavailable_returns_safe_error(self) -> None:
        def broken_connection():
            raise RuntimeError("/tmp/private-dsn secret")

        app.state.catalog_service = CatalogService(connection_factory=broken_connection)

        response = self.client.get("/documents")

        self.assertEqual(response.status_code, 503)
        body = response.json()
        self.assertEqual(body["error"]["message"], "Documents service is unavailable.")
        self.assertNotIn("/tmp/private-dsn", str(body))
        self.assertNotIn("secret", str(body))


if __name__ == "__main__":
    unittest.main()
