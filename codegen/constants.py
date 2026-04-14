SQL_TYPE_TO_JAVA = {
    "bigint": "Long",
    "binary": "byte[]",
    "bit": "Boolean",
    "blob": "byte[]",
    "bool": "Boolean",
    "boolean": "Boolean",
    "char": "String",
    "date": "LocalDate",
    "datetime": "LocalDateTime",
    "decimal": "BigDecimal",
    "double": "Double",
    "float": "Float",
    "int": "Integer",
    "integer": "Integer",
    "json": "String",
    "longtext": "String",
    "mediumint": "Integer",
    "mediumtext": "String",
    "numeric": "BigDecimal",
    "smallint": "Integer",
    "text": "String",
    "time": "LocalTime",
    "timestamp": "LocalDateTime",
    "tinyint": "Integer",
    "varchar": "String",
}

JAVA_TYPE_IMPORTS = {
    "BigDecimal": "java.math.BigDecimal",
    "LocalDate": "java.time.LocalDate",
    "LocalDateTime": "java.time.LocalDateTime",
    "LocalTime": "java.time.LocalTime",
}

DEFAULT_BASE_ENTITY_FIELDS = {
    "id": ("Long", "主键ID"),
    "remark": ("String", "备注"),
    "create_by": ("Long", "创建人ID"),
    "create_time": ("Long", "创建时间"),
    "update_by": ("Long", "更新人ID"),
    "update_time": ("Long", "更新时间"),
    "delete_by": ("Long", "删除人ID"),
    "delete_time": ("Long", "删除时间"),
}

PACKAGE_KEYS = (
    "base_package",
    "package_name",
    "project_package",
    "package_path",
)

KNOWN_PACKAGE_SUFFIXES = (
    ".service.impl",
    ".common.entity",
    ".controller",
    ".service",
    ".mapper",
    ".entity",
    ".dto",
    ".vo",
)
