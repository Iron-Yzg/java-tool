from __future__ import annotations

import re
from pathlib import Path

from codegen.constants import SQL_TYPE_TO_JAVA
from codegen.models import ColumnDefinition, TableDefinition


def parse_sql_file(sql_file: Path) -> list[TableDefinition]:
    content = sql_file.read_text(encoding="utf-8")
    create_table_pattern = re.compile(
        r"CREATE TABLE\s+`(?P<name>[^`]+)`\s*\((?P<body>.*?)\)\s*(?P<tail>ENGINE=.*?;)",
        re.IGNORECASE | re.DOTALL,
    )

    tables: list[TableDefinition] = []
    for match in create_table_pattern.finditer(content):
        comment_match = re.search(
            r"COMMENT\s*=\s*'(?P<comment>(?:[^'\\]|\\.)*)'",
            match.group("tail"),
            re.IGNORECASE,
        )
        table_comment = (
            comment_match.group("comment").replace("\\'", "'") if comment_match else ""
        )
        tables.append(
            TableDefinition(
                name=match.group("name"),
                comment=table_comment,
                columns=parse_columns(match.group("body")),
            )
        )
    return tables


def parse_columns(table_body: str) -> list[ColumnDefinition]:
    lines = [
        line.strip().rstrip(",") for line in table_body.splitlines() if line.strip()
    ]
    primary_key_names: set[str] = set()
    columns: list[ColumnDefinition] = []

    for line in lines:
        upper_line = line.upper()
        if upper_line.startswith("PRIMARY KEY"):
            primary_key_names.update(re.findall(r"`([^`]+)`", line))
            continue

        if not line.startswith("`"):
            continue

        column_match = re.match(
            r"`(?P<name>[^`]+)`\s+(?P<sql_type>[^\s]+)(?P<extra>.*)", line
        )
        if not column_match:
            continue

        extra = column_match.group("extra") or ""
        comment_match = re.search(
            r"COMMENT\s+'(?P<comment>(?:[^'\\]|\\.)*)'", extra, re.IGNORECASE
        )
        columns.append(
            ColumnDefinition(
                name=column_match.group("name"),
                sql_type=column_match.group("sql_type"),
                java_type=sql_type_to_java_type(column_match.group("sql_type")),
                comment=comment_match.group("comment").replace("\\'", "'")
                if comment_match
                else "",
                nullable="NOT NULL" not in upper_line,
                primary_key="PRIMARY KEY" in upper_line,
                auto_increment="AUTO_INCREMENT" in upper_line,
            )
        )

    for column in columns:
        column.primary_key = column.primary_key or column.name in primary_key_names

    return columns


def sql_type_to_java_type(sql_type: str) -> str:
    return SQL_TYPE_TO_JAVA.get(sql_type.split("(", 1)[0].lower(), "String")
