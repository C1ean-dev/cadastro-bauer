def validate_fields(data, validation_rules):
    """
    Valida os dados de entrada em relação a regras predefinidas.
    Retorna uma lista de mensagens de erro.
    """
    errors = []
    for field, (max_length, required) in validation_rules.items():
        value = data.get(field)
        if value is not None:
            value = str(value).strip()
        else:
            value = "" # Treat None as an empty string for validation purposes

        if required and not value:
            errors.append(f"'{field}' is required.")
        elif value and len(value) > max_length:
            if field == "LOGRA":
                # This part modifies the data dictionary directly, which might be unexpected
                # but is part of the original logic.
                data[field] = value[:max_length]
            else:
                errors.append(f"'{field}' o campo passou do maximo de {max_length} characters.")
    return errors
