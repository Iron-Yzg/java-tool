from __future__ import annotations

from codegen.constants import JAVA_TYPE_IMPORTS
from codegen.models import ColumnDefinition, GeneratorConfig, TableDefinition
from codegen.utils import render_imports, snake_to_pascal


def render_entity(config: GeneratorConfig, table: TableDefinition) -> str:
    visible_columns = [
        column for column in table.columns if column.name not in config.ignore_field_set
    ]
    imports = {
        "com.baomidou.mybatisplus.annotation.TableField",
        "com.baomidou.mybatisplus.annotation.TableName",
        f"{config.base_entity_full_package}.{config.base_entity_name}",
        "java.io.Serial",
        "lombok.Data",
        "lombok.EqualsAndHashCode",
    }
    if any(column.primary_key for column in visible_columns):
        imports.update(
            {
                "com.baomidou.mybatisplus.annotation.IdType",
                "com.baomidou.mybatisplus.annotation.TableId",
            }
        )
    for column in visible_columns:
        java_import = JAVA_TYPE_IMPORTS.get(column.java_type)
        if java_import:
            imports.add(java_import)

    lines = [
        f"package {config.base_package}.{config.entity_package};",
        "",
        render_imports(imports),
        "",
        f"/** {table.comment or f'{table.class_name} entity'} */",
        "@Data",
        "@EqualsAndHashCode(callSuper = true)",
        f'@TableName("{table.name}")',
        f"public class {table.class_name} extends {config.base_entity_name} {{",
        "",
        "    @Serial",
        "    private static final long serialVersionUID = 1L;",
    ]

    for column in visible_columns:
        lines.extend(["", render_field(column)])

    lines.extend(["", "}"])
    return "\n".join(lines)


def render_field(column: ColumnDefinition) -> str:
    annotation = (
        f'@TableId(value = "{column.name}", type = IdType.{"AUTO" if column.auto_increment else "INPUT"})'
        if column.primary_key
        else f'@TableField("{column.name}")'
    )
    comment = column.comment or snake_to_pascal(column.name)
    return "\n".join(
        [
            f"    /** {comment} */",
            f"    {annotation}",
            f"    private {column.java_type} {column.field_name};",
        ]
    )
