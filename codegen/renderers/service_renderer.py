from __future__ import annotations

from codegen.models import GeneratorConfig, TableDefinition
from codegen.utils import getter_name, render_imports
from codegen.renderers.dto_renderer import queryable_columns


def render_service_interface(config: GeneratorConfig, table: TableDefinition) -> str:
    primary_key_type, _ = resolve_primary_key(table)
    comment = table.comment or table.class_name
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
            f"/** {comment} Service */",
            f"public interface {table.class_name}Service extends IService<{table.class_name}> {{",
            "",
            "    /**",
            f"     * {comment}分页查询",
            "     *",
            "     * @param queryDto 分页查询参数",
            "     * @return 分页结果",
            "     */",
            f"    IPage<{table.class_name}VO> page({table.class_name}PageQueryDTO queryDto);",
            "",
            "    /**",
            f"     * {comment}详情",
            "     *",
            "     * @param id 主键ID",
            "     * @return 详情",
            "     */",
            f"    {table.class_name}VO detail({primary_key_type} id);",
            "",
            "    /**",
            f"     * {comment}新增",
            "     *",
            "     * @param createDto 新增参数",
            "     * @return 是否成功",
            "     */",
            f"    boolean create({table.class_name}CreateDTO createDto);",
            "",
            "    /**",
            f"     * {comment}修改",
            "     *",
            "     * @param updateDto 修改参数",
            "     * @return 是否成功",
            "     */",
            f"    boolean update({table.class_name}UpdateDTO updateDto);",
            "",
            "    /**",
            f"     * {comment}删除",
            "     *",
            "     * @param id 主键ID",
            "     * @return 是否成功",
            "     */",
            f"    boolean delete({primary_key_type} id);",
            "}",
        ]
    )


def render_service_impl(config: GeneratorConfig, table: TableDefinition) -> str:
    primary_key_type, _ = resolve_primary_key(table)
    merge_service = config.should_merge_service

    imports: set[str] = {
        "com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper",
        "com.baomidou.mybatisplus.core.metadata.IPage",
        "com.baomidou.mybatisplus.core.toolkit.Wrappers",
        "com.baomidou.mybatisplus.extension.plugins.pagination.Page",
        "com.lysztech.mybatis.page.PageResult",
        "com.lysztech.mybatis.service.MyBaseServiceImpl",
        "com.lysztech.core.utils.MapstructUtils",
        f"{config.base_package}.{config.dto_package}.{table.class_name}CreateDTO",
        f"{config.base_package}.{config.dto_package}.{table.class_name}PageQueryDTO",
        f"{config.base_package}.{config.dto_package}.{table.class_name}UpdateDTO",
        f"{config.base_package}.{config.entity_package}.{table.class_name}",
        f"{config.base_package}.{config.mapper_package}.{table.class_name}Mapper",
        f"{config.base_package}.{config.vo_package}.{table.class_name}VO",
        "org.springframework.stereotype.Service",
        "org.springframework.util.StringUtils",
    }

    if not merge_service:
        imports.add("com.baomidou.mybatisplus.extension.service.IService")
        imports.add(
            f"{config.base_package}.{config.service_package}.{table.class_name}Service"
        )

    wrapper_lines = build_query_wrapper_lines(table, config)
    order_line = build_order_line(table)
    if order_line:
        wrapper_lines.append(order_line)

    # Build class declaration
    if merge_service:
        class_name = f"{table.class_name}Service"
        class_decl = f"public class {class_name} extends MyBaseServiceImpl<{table.class_name}Mapper, {table.class_name}> {{"
    else:
        class_name = f"{table.class_name}ServiceImpl"
        class_decl = f"public class {class_name} extends MyBaseServiceImpl<{table.class_name}Mapper, {table.class_name}> implements {table.class_name}Service {{"

    override = "" if merge_service else "    @Override\n"
    comment = table.comment or table.class_name

    lines = [
        f"package {config.base_package}.{config.service_impl_package};",
        "",
        render_imports(imports),
        "",
        f"/** {comment} Service */",
        "@Service",
        class_decl,
        "",
        "    /**",
        f"     * {comment}分页查询",
        "     *",
        "     * @param queryDto 分页查询参数",
        "     * @return 分页结果",
        "     */",
        f"{override}    public PageResult<{table.class_name}VO> page({table.class_name}PageQueryDTO queryDto) {{",
        f"        {table.class_name}PageQueryDTO safeQuery = queryDto == null ? new {table.class_name}PageQueryDTO() : queryDto;",
        f"        Page<{table.class_name}> page = new Page<>(safeQuery.getPageNum(), safeQuery.getPageSize());",
        f"        IPage<{table.class_name}> result = this.page(page, buildQueryWrapper(safeQuery));",
        f"        return PageResult.of(result).convert(this::toVO);",
        "    }",
        "",
        "    /**",
        f"     * {comment}详情",
        "     *",
        "     * @param id 主键ID",
        "     * @return 详情",
        "     */",
        f"{override}    public {table.class_name}VO detail({primary_key_type} id) {{",
        "        return toVO(this.getById(id));",
        "    }",
        "",
        "    /**",
        f"     * {comment}新增",
        "     *",
        "     * @param createDto 新增参数",
        "     * @return 是否成功",
        "     */",
        f"{override}    public boolean create({table.class_name}CreateDTO createDto) {{",
        f"        {table.class_name} entity = MapstructUtils.convert(createDto, {table.class_name}.class);",
        "        return this.save(entity);",
        "    }",
        "",
        "    /**",
        f"     * {comment}修改",
        "     *",
        "     * @param updateDto 修改参数",
        "     * @return 是否成功",
        "     */",
        f"{override}    public boolean update({table.class_name}UpdateDTO updateDto) {{",
        f"        {table.class_name} entity = MapstructUtils.convert(updateDto, {table.class_name}.class);",
        "        return this.updateById(entity);",
        "    }",
        "",
        "    /**",
        f"     * {comment}删除",
        "     *",
        "     * @param id 主键ID",
        "     * @return 是否成功",
        "     */",
        f"{override}    public boolean delete({primary_key_type} id) {{",
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
            f"        return MapstructUtils.convert(entity, {table.class_name}VO.class);",
            "    }",
            "}",
        ]
    )
    return "\n".join(lines)


def build_query_wrapper_lines(
    table: TableDefinition, config: GeneratorConfig
) -> list[str]:
    columns = queryable_columns(table, config)

    lines: list[str] = []
    seen: set[str] = set()
    soft_delete_columns: list[ColumnDefinition] = []
    for column in columns:
        if column.name in seen:
            continue
        seen.add(column.name)

        # Handle is_deleted as a fixed soft-delete filter
        if column.name == "is_deleted":
            soft_delete_columns.append(column)
            continue

        getter = getter_name(column.field_name)
        if column.java_type == "String":
            lines.append(
                f"wrapper.like(StringUtils.hasText(queryDto.{getter}()), {table.class_name}::{getter}, queryDto.{getter}());"
            )
        else:
            lines.append(
                f"wrapper.eq(queryDto.{getter}() != null, {table.class_name}::{getter}, queryDto.{getter}());"
            )

    # Append soft delete filter before ordering
    for column in soft_delete_columns:
        getter = getter_name(column.field_name)
        lines.append(f"wrapper.eq({table.class_name}::{getter}, 0);")

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
