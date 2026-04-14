from __future__ import annotations

from codegen.models import GeneratorConfig, TableDefinition
from codegen.utils import getter_name, render_imports


def render_service_interface(config: GeneratorConfig, table: TableDefinition) -> str:
    primary_key_type, _ = resolve_primary_key(table)
    imports = {
        "com.baomidou.mybatisplus.core.metadata.IPage",
        "com.baomidou.mybatisplus.extension.service.IService",
        f"{config.base_package}.{config.dto_package}.{table.class_name}CreateDTO",
        f"{config.base_package}.{config.dto_package}.{table.class_name}PageQueryDTO",
        f"{config.base_package}.{config.dto_package}.{table.class_name}UpdateDTO",
        f"{config.base_package}.{config.entity_package}.{table.class_name}",
        f"{config.base_package}.{config.vo_package}.{table.class_name}VO",
    }
    return "\n".join(
        [
            f"package {config.base_package}.{config.service_package};",
            "",
            render_imports(imports),
            "",
            f"/** {table.comment or table.class_name} Service */",
            f"public interface I{table.class_name}Service extends IService<{table.class_name}> {{",
            "",
            f"    IPage<{table.class_name}VO> page({table.class_name}PageQueryDTO queryDto);",
            "",
            f"    {table.class_name}VO detail({primary_key_type} id);",
            "",
            f"    boolean create({table.class_name}CreateDTO createDto);",
            "",
            f"    boolean update({table.class_name}UpdateDTO updateDto);",
            "",
            f"    boolean delete({primary_key_type} id);",
            "}",
        ]
    )


def render_service_impl(config: GeneratorConfig, table: TableDefinition) -> str:
    primary_key_type, _ = resolve_primary_key(table)
    imports = {
        "com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper",
        "com.baomidou.mybatisplus.core.metadata.IPage",
        "com.baomidou.mybatisplus.core.toolkit.Wrappers",
        "com.baomidou.mybatisplus.extension.plugins.pagination.Page",
        "com.baomidou.mybatisplus.extension.service.impl.ServiceImpl",
        f"{config.base_package}.{config.dto_package}.{table.class_name}CreateDTO",
        f"{config.base_package}.{config.dto_package}.{table.class_name}PageQueryDTO",
        f"{config.base_package}.{config.dto_package}.{table.class_name}UpdateDTO",
        f"{config.base_package}.{config.entity_package}.{table.class_name}",
        f"{config.base_package}.{config.mapper_package}.{table.class_name}Mapper",
        f"{config.base_package}.{config.service_package}.I{table.class_name}Service",
        f"{config.base_package}.{config.vo_package}.{table.class_name}VO",
        "java.util.stream.Collectors",
        "org.springframework.beans.BeanUtils",
        "org.springframework.stereotype.Service",
        "org.springframework.util.StringUtils",
    }

    wrapper_lines = build_query_wrapper_lines(table, config)
    order_line = build_order_line(table)
    if order_line:
        wrapper_lines.append(order_line)

    lines = [
        f"package {config.base_package}.{config.service_impl_package};",
        "",
        render_imports(imports),
        "",
        f"/** {table.comment or table.class_name} ServiceImpl */",
        "@Service",
        f"public class {table.class_name}ServiceImpl extends ServiceImpl<{table.class_name}Mapper, {table.class_name}> implements I{table.class_name}Service {{",
        "",
        "    @Override",
        f"    public IPage<{table.class_name}VO> page({table.class_name}PageQueryDTO queryDto) {{",
        f"        {table.class_name}PageQueryDTO safeQuery = queryDto == null ? new {table.class_name}PageQueryDTO() : queryDto;",
        f"        Page<{table.class_name}> page = new Page<>(safeQuery.getPageNum(), safeQuery.getPageSize());",
        f"        IPage<{table.class_name}> result = this.page(page, buildQueryWrapper(safeQuery));",
        f"        Page<{table.class_name}VO> voPage = new Page<>(result.getCurrent(), result.getSize(), result.getTotal());",
        "        voPage.setRecords(result.getRecords().stream().map(this::toVO).collect(Collectors.toList()));",
        "        return voPage;",
        "    }",
        "",
        "    @Override",
        f"    public {table.class_name}VO detail({primary_key_type} id) {{",
        "        return toVO(this.getById(id));",
        "    }",
        "",
        "    @Override",
        f"    public boolean create({table.class_name}CreateDTO createDto) {{",
        f"        {table.class_name} entity = new {table.class_name}();",
        "        BeanUtils.copyProperties(createDto, entity);",
        "        return this.save(entity);",
        "    }",
        "",
        "    @Override",
        f"    public boolean update({table.class_name}UpdateDTO updateDto) {{",
        f"        {table.class_name} entity = new {table.class_name}();",
        "        BeanUtils.copyProperties(updateDto, entity);",
        "        return this.updateById(entity);",
        "    }",
        "",
        "    @Override",
        f"    public boolean delete({primary_key_type} id) {{",
        "        return this.removeById(id);",
        "    }",
        "",
        f"    private LambdaQueryWrapper<{table.class_name}> buildQueryWrapper({table.class_name}PageQueryDTO queryDto) {{",
        f"        LambdaQueryWrapper<{table.class_name}> wrapper = Wrappers.lambdaQuery();",
    ]

    for wrapper_line in wrapper_lines:
        lines.append(f"        {wrapper_line}")

    lines.extend(
        [
            "        return wrapper;",
            "    }",
            "",
            f"    private {table.class_name}VO toVO({table.class_name} entity) {{",
            "        if (entity == null) {",
            "            return null;",
            "        }",
            f"        {table.class_name}VO vo = new {table.class_name}VO();",
            "        BeanUtils.copyProperties(entity, vo);",
            "        return vo;",
            "    }",
            "}",
        ]
    )
    return "\n".join(lines)


def build_query_wrapper_lines(
    table: TableDefinition, config: GeneratorConfig
) -> list[str]:
    columns = [
        column for column in table.columns if column.name not in config.ignore_field_set
    ]
    primary_key = table.primary_key
    if primary_key and primary_key.name in config.ignore_field_set:
        columns = [primary_key, *columns]

    lines: list[str] = []
    seen: set[str] = set()
    for column in columns:
        if column.name in seen:
            continue
        seen.add(column.name)
        getter = getter_name(column.field_name)
        if column.java_type == "String":
            lines.append(
                f"wrapper.like(StringUtils.hasText(queryDto.{getter}()), {table.class_name}::{getter}, queryDto.{getter}());"
            )
        else:
            lines.append(
                f"wrapper.eq(queryDto.{getter}() != null, {table.class_name}::{getter}, queryDto.{getter}());"
            )
    return lines


def build_order_line(table: TableDefinition) -> str:
    if any(column.name == "create_time" for column in table.columns):
        return f"wrapper.orderByDesc({table.class_name}::getCreateTime);"

    primary_key = table.primary_key
    if primary_key:
        return f"wrapper.orderByDesc({table.class_name}::{getter_name(primary_key.field_name)});"
    return ""


def resolve_primary_key(table: TableDefinition) -> tuple[str, str]:
    primary_key = table.primary_key
    if primary_key:
        return primary_key.java_type, primary_key.field_name
    return "Long", "id"
