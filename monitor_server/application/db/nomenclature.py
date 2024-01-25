def build_index_name(*column_names: str) -> str:
    names = '_'.join(column_names)
    return f'ix_{names}'


def build_unique_constraint_name(table_name: str, column_name: str) -> str:
    return f'uq_{table_name}_{column_name}'


def build_foreign_key_name(used_by_table_name: str, column_name: str, from_table_name: str) -> str:
    return f'fk_{used_by_table_name}_{column_name}_{from_table_name}'


def build_primary_key_name(*column_names: str) -> str:
    return f'pk_{"_".join(column_names)}'


def build_constraint_name(table_name: str, *column_name: str, quick_desc: str) -> str:
    desc = '_'.join(i.lower() for i in quick_desc.split(' '))
    return f'ck_{table_name}_{"_".join(column_name)}_{desc}'
