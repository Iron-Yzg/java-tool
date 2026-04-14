from __future__ import annotations

from codegen.models import GeneratorConfig, TableDefinition
from codegen.utils import render_imports


def render_mapper(config: GeneratorConfig, table: TableDefinition) -> str:
    imports = {
        "com.baomidou.mybatisplus.core.mapper.BaseMapper",
        f"{config.base_package}.{config.entity_package}.{table.class_name}",
        "org.apache.ibatis.annotations.Mapper",
    }
    return "\n".join(
        [
            f"package {config.base_package}.{config.mapper_package};",
            "",
            render_imports(imports),
            "",
            f"/** {table.comment or f'{table.class_name} mapper'} Mapper */",
            "@Mapper",
            f"public interface {table.class_name}Mapper extends BaseMapper<{table.class_name}> {{",
            "}",
        ]
    )
