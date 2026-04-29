from __future__ import annotations

from codegen.models import GeneratorConfig, TableDefinition
from codegen.renderers.service_renderer import resolve_primary_key
from codegen.utils import build_request_path, render_imports, snake_to_camel


def render_controller(config: GeneratorConfig, table: TableDefinition) -> str:
    primary_key_type, primary_key_field_name = resolve_primary_key(table)
    request_path = build_request_path(config.request_prefix, snake_to_camel(table.name))
    imports = {
        "com.baomidou.mybatisplus.core.metadata.IPage",
        f"{config.base_package}.{config.dto_package}.{table.class_name}CreateDTO",
        f"{config.base_package}.{config.dto_package}.{table.class_name}PageQueryDTO",
        f"{config.base_package}.{config.dto_package}.{table.class_name}UpdateDTO",
        f"{config.base_package}.{config.service_package}.{table.class_name}Service",
        f"{config.base_package}.{config.vo_package}.{table.class_name}VO",
        "lombok.RequiredArgsConstructor",
        "org.springframework.web.bind.annotation.DeleteMapping",
        "org.springframework.web.bind.annotation.GetMapping",
        "org.springframework.web.bind.annotation.PathVariable",
        "org.springframework.web.bind.annotation.PostMapping",
        "org.springframework.web.bind.annotation.PutMapping",
        "org.springframework.web.bind.annotation.RequestBody",
        "org.springframework.web.bind.annotation.RequestMapping",
        "org.springframework.web.bind.annotation.RestController",
    }
    return "\n".join(
        [
            f"package {config.base_package}.{config.controller_package};",
            "",
            render_imports(imports),
            "",
            f"/** {table.comment or table.class_name} Controller */",
            "@RestController",
            "@RequiredArgsConstructor",
            f'@RequestMapping("{request_path}")',
            f"public class {table.class_name}Controller {{",
            "",
            f"    private final {table.class_name}Service {table.entity_var_name}Service;",
            "",
            '    @PostMapping("/page")',
            f"    public IPage<{table.class_name}VO> page(@RequestBody(required = false) {table.class_name}PageQueryDTO queryDto) {{",
            f"        return {table.entity_var_name}Service.page(queryDto);",
            "    }",
            "",
            f'    @GetMapping("/{{{primary_key_field_name}}}")',
            f"    public {table.class_name}VO detail(@PathVariable {primary_key_type} {primary_key_field_name}) {{",
            f"        return {table.entity_var_name}Service.detail({primary_key_field_name});",
            "    }",
            "",
            "    @PostMapping",
            f"    public boolean create(@RequestBody {table.class_name}CreateDTO createDto) {{",
            f"        return {table.entity_var_name}Service.create(createDto);",
            "    }",
            "",
            "    @PutMapping",
            f"    public boolean update(@RequestBody {table.class_name}UpdateDTO updateDto) {{",
            f"        return {table.entity_var_name}Service.update(updateDto);",
            "    }",
            "",
            f'    @DeleteMapping("/{{{primary_key_field_name}}}")',
            f"    public boolean delete(@PathVariable {primary_key_type} {primary_key_field_name}) {{",
            f"        return {table.entity_var_name}Service.delete({primary_key_field_name});",
            "    }",
            "}",
        ]
    )
