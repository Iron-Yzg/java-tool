from __future__ import annotations

from codegen.constants import JAVA_TYPE_IMPORTS
from codegen.models import GeneratorConfig, TableDefinition
from codegen.utils import render_imports


def render_vo(config: GeneratorConfig, table: TableDefinition) -> str:
    visible_columns = [
        column for column in table.columns if column.name not in config.ignore_field_set
    ]
    imports = {
        f"{config.base_entity_full_package}.{config.base_entity_name}",
        "java.io.Serial",
        "lombok.Data",
        "lombok.EqualsAndHashCode",
    }
    for column in visible_columns:
        java_import = JAVA_TYPE_IMPORTS.get(column.java_type)
        if java_import:
            imports.add(java_import)

    lines = [
        f"package {config.base_package}.{config.vo_package};",
        "",
        render_imports(imports),
        "",
        f"/** {table.comment or table.class_name}返回对象 */",
        "@Data",
        "@EqualsAndHashCode(callSuper = true)",
        f"public class {table.class_name}VO extends {config.base_entity_name} {{",
        "",
        "    @Serial",
        "    private static final long serialVersionUID = 1L;",
    ]

    for column in visible_columns:
        lines.extend(
            [
                "",
                f"    /** {column.comment or column.field_name} */",
                f"    private {column.java_type} {column.field_name};",
            ]
        )

    lines.extend(["", "}"])
    return "\n".join(lines)
